import os
import requests
import zipfile
import mysql.connector
from xml.etree import ElementTree as ET

# URL para download do arquivo ZIP
URL_ZIP = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ENHANCED.ZIP"
NOME_ARQUIVO_ZIP = "SDN_ENHANCED.ZIP"
NOME_ARQUIVO_XML = "SDN_ENHANCED.XML"

# Função para fazer o download do arquivo ZIP
def baixar_arquivo():
    print(f"Baixando arquivo de: {URL_ZIP}")
    resposta = requests.get(URL_ZIP, stream=True)
    if resposta.status_code == 200:
        with open(NOME_ARQUIVO_ZIP, "wb") as arquivo:
            for chunk in resposta.iter_content(chunk_size=8192):
                arquivo.write(chunk)
        print(f"Arquivo {NOME_ARQUIVO_ZIP} baixado com sucesso.")
    else:
        print(f"Erro ao baixar o arquivo: {resposta.status_code}")

# Função para descompactar o arquivo ZIP
def descompactar_arquivo():
    print(f"Descompactando arquivo {NOME_ARQUIVO_ZIP}...")
    with zipfile.ZipFile(NOME_ARQUIVO_ZIP, 'r') as zip_ref:
        zip_ref.extractall(".")
    print(f"Arquivo {NOME_ARQUIVO_XML} extraído com sucesso.")

# Função para processar o XML
def processar_xml():
    registros = []
    print(f"Processando arquivo {NOME_ARQUIVO_XML}...")
    tree = ET.parse(NOME_ARQUIVO_XML)
    root = tree.getroot()

    # Namespaces usados no XML
    namespaces = {'ns': "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ENHANCED_XML"}

    # Processar entidades
    for entity in root.findall("ns:entities/ns:entity", namespaces):
        identity_id = entity.find("ns:generalInfo/ns:identityId", namespaces).text
        entity_type = entity.find("ns:generalInfo/ns:entityType", namespaces).text

        # Primary name
        primary_name = None
        alias_names = []
        for name in entity.findall("ns:names/ns:name", namespaces):
            is_primary = name.find("ns:isPrimary", namespaces).text == "true"
            full_name = name.find("ns:translations/ns:translation/ns:formattedFullName", namespaces).text
            if is_primary:
                primary_name = full_name
            else:
                alias_names.append(full_name)

        # Address
        address = None
        address_node = entity.find("ns:addresses/ns:address/ns:translations/ns:translation/ns:addressParts/ns:addressPart", namespaces)
        if address_node is not None:
            address = address_node.find("ns:value", namespaces).text

        # Adicionar ao registro
        registros.append({
            "identity_id": int(identity_id),
            "entity_type": entity_type,
            "primary_name": primary_name,
            "alias_names": alias_names,
            "address": address
        })
    print(f"Registros encontrados: {len(registros)}")
    return registros

# Função para inserir no banco de dados MySQL
def inserir_no_banco(registros):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="phpmyadmin",
            password="Lcstanke@2018*",
            database="lista-negra"
        )

        if conn.is_connected():
            print("Conexão com o banco de dados estabelecida com sucesso.")

        cursor = conn.cursor()

        # Criar a tabela, se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ofac_sdn (
                id INT AUTO_INCREMENT PRIMARY KEY,
                identity_id INT,
                entity_type VARCHAR(255),
                primary_name TEXT,
                alias_names TEXT,
                address TEXT
            )
        """)

        # Criar índice FULLTEXT
        cursor.execute("CREATE FULLTEXT INDEX idx_primary_name ON ofac_sdn(primary_name)")
        cursor.execute("CREATE FULLTEXT INDEX idx_alias_names ON ofac_sdn(alias_names)")

        # Inserir os registros no banco
        for registro in registros:
            cursor.execute("""
                INSERT INTO ofac_sdn (identity_id, entity_type, primary_name, alias_names, address)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                registro['identity_id'],
                registro['entity_type'],
                registro['primary_name'],
                ', '.join(registro['alias_names']),
                registro['address']
            ))

        # Commit e fechar a conexão
        conn.commit()
        print(f"{len(registros)} registros inseridos com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

# Fluxo principal
if __name__ == "__main__":
    baixar_arquivo()
    descompactar_arquivo()
    registros = processar_xml()
    inserir_no_banco(registros)

    # Limpeza opcional
    if os.path.exists(NOME_ARQUIVO_ZIP):
        os.remove(NOME_ARQUIVO_ZIP)
    if os.path.exists(NOME_ARQUIVO_XML):
        os.remove(NOME_ARQUIVO_XML)
