import requests
import mysql.connector
from xml.etree import ElementTree as ET
import os
from playwright.sync_api import sync_playwright

# URL principal para obter o XML
# URL_PRINCIPAL = "https://main.un.org/securitycouncil/en/sanctions/1267/aq_sanctions_list"
# NOME_ARQUIVO_XML = "n4k7jen-al-qaida.xml"

URL_PRINCIPAL = "https://main.un.org/securitycouncil/en/content/un-sc-consolidated-list"
NOME_ARQUIVO_XML = "consolidated.xml"


def obter_link_xml():
    """
    Extrai o link dinâmico do botão "XML" na página principal.
    """
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(URL_PRINCIPAL)
        
        try:
            # Localizar o primeiro botão "XML"
            # botao_xml = pagina.locator("a.uw-link-btn", has_text="XML").first
            botao_xml = pagina.locator("a.documentlinks", has_text="XML").first
            
            link_xml = botao_xml.get_attribute("href")
            print(f"Link XML encontrado: {link_xml}")
            return link_xml
        except Exception as e:
            print(f"Erro ao obter o link XML: {e}")
            return None
        finally:
            navegador.close()

# Função para baixar o XML
def baixar_arquivo(link_xml):
    print(f"Baixando arquivo de: {link_xml}")
    resposta = requests.get(link_xml, stream=True)
    if resposta.status_code == 200:
        with open(NOME_ARQUIVO_XML, "wb") as arquivo:
            for chunk in resposta.iter_content(chunk_size=8192):
                arquivo.write(chunk)
        print(f"Arquivo {NOME_ARQUIVO_XML} baixado com sucesso.")
    else:
        print(f"Erro ao baixar o arquivo: {resposta.status_code}")

# Função para processar o XML
def processar_xml():
    registros = []
    aliases = []
    print(f"Processando arquivo {NOME_ARQUIVO_XML}...")
    
    tree = ET.parse(NOME_ARQUIVO_XML)
    root = tree.getroot()

    # Iterar sobre as entradas de entidades
    for entity in root.findall(".//INDIVIDUAL"):
        unique_id = entity.find("DATAID").text if entity.find("DATAID") is not None else None

        # Montar o nome completo a partir das partes
        name_parts = []
        for tag in ["FIRST_NAME", "SECOND_NAME", "THIRD_NAME", "FOURTH_NAME"]:
            part = entity.find(tag)
            if part is not None and part.text:
                name_parts.append(part.text)
        full_name = " ".join(name_parts)

        # Outros dados
        nationality = entity.find(".//NATIONALITY/VALUE").text.strip() if entity.find(".//NATIONALITY/VALUE") is not None else None
        dob = entity.find(".//INDIVIDUAL_DATE_OF_BIRTH/DATE").text if entity.find(".//INDIVIDUAL_DATE_OF_BIRTH/DATE") is not None else None
        address = entity.find(".//INDIVIDUAL_ADDRESS/STREET").text if entity.find(".//INDIVIDUAL_ADDRESS/STREET") is not None else None
        city = entity.find(".//INDIVIDUAL_ADDRESS/CITY").text if entity.find(".//INDIVIDUAL_ADDRESS/CITY") is not None else None
        country = entity.find(".//INDIVIDUAL_ADDRESS/COUNTRY").text if entity.find(".//INDIVIDUAL_ADDRESS/COUNTRY") is not None else None
        document_type = entity.find(".//INDIVIDUAL_DOCUMENT/TYPE_OF_DOCUMENT").text if entity.find(".//INDIVIDUAL_DOCUMENT/TYPE_OF_DOCUMENT") is not None else None
        document_number = entity.find(".//INDIVIDUAL_DOCUMENT/NUMBER").text if entity.find(".//INDIVIDUAL_DOCUMENT/NUMBER") is not None else None

        # Processar aliases
        for alias in entity.findall(".//INDIVIDUAL_ALIAS"):
            alias_name = alias.find("ALIAS_NAME").text if alias.find("ALIAS_NAME") is not None else None
            alias_quality = alias.find("QUALITY").text if alias.find("QUALITY") is not None else None

            aliases.append({
                "unique_id": unique_id,
                "alias_name": alias_name,
                "alias_quality": alias_quality
            })

        registros.append({
            "unique_id": unique_id,
            "full_name": full_name,
            "nationality": nationality,
            "dob": dob,
            "address": address,
            "city": city,
            "country": country,
            "document_type": document_type,
            "document_number": document_number
        })

    print(f"Registros processados: {len(registros)}")
    print(f"Aliases processados: {len(aliases)}")
    return registros, aliases

# Função para inserir dados no banco
def inserir_no_banco(registros, aliases):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="phpmyadmin",
            password="Lcstanke@2018*",
            database="lista-negra"
        )
        cursor = conn.cursor()

        # Criar a tabela principal se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csus_entities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(255) UNIQUE,
                full_name TEXT,
                nationality VARCHAR(255),
                dob DATE,
                address TEXT,
                city VARCHAR(255),
                country VARCHAR(255),
                document_type VARCHAR(255),
                document_number VARCHAR(255),
                KEY unique_id_idx (unique_id)  -- Adiciona índice explícito para unique_id
            )
        """)

        # Criar a tabela de aliases se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csus_aliases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(255),
                alias_name TEXT,
                alias_quality TEXT,
                FOREIGN KEY (unique_id) REFERENCES csus_entities(unique_id)
            )
        """)

        # Inserir registros principais
        for registro in registros:
            cursor.execute("""
                INSERT INTO csus_entities (unique_id, full_name, nationality, dob, address, city, country, document_type, document_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                registro["unique_id"],
                registro["full_name"],
                registro["nationality"],
                registro["dob"],
                registro["address"],
                registro["city"],
                registro["country"],
                registro["document_type"],
                registro["document_number"]
            ))

        # Inserir aliases
        for alias in aliases:
            cursor.execute("""
                INSERT INTO csus_aliases (unique_id, alias_name, alias_quality)
                VALUES (%s, %s, %s)
            """, (
                alias["unique_id"],
                alias["alias_name"],
                alias["alias_quality"]
            ))

        conn.commit()
        print(f"{len(registros)} registros principais inseridos com sucesso.")
        print(f"{len(aliases)} aliases inseridos com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

# Fluxo principal
if __name__ == "__main__":
    link_xml = obter_link_xml()
    if link_xml:
        baixar_arquivo(link_xml)
        registros, aliases = processar_xml()
        inserir_no_banco(registros, aliases)

        # Limpeza opcional
        if os.path.exists(NOME_ARQUIVO_XML):
            os.remove(NOME_ARQUIVO_XML)
