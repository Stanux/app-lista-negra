import requests
import mysql.connector
from xml.etree import ElementTree as ET
from datetime import datetime
import os

# URL para download do arquivo XML
URL_XML = "https://assets.publishing.service.gov.uk/media/673f0ecb4a6dd5b06db95a3a/UK_Sanctions_List.xml"
NOME_ARQUIVO_XML = "UK_Sanctions_List.xml"

def formatar_data(data):
    if data is None:
        return None  # Retorna None se a data for None
    try:
        # Tentativa de converter a data de dd/mm/yyyy para yyyy-mm-dd
        return datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        # Caso a data seja inválida, retorna None
        return None
    
# Função para fazer o download do arquivo XML
def baixar_arquivo():
    print(f"Baixando arquivo de: {URL_XML}")
    resposta = requests.get(URL_XML, stream=True)
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
    print(f"Processando arquivo {NOME_ARQUIVO_XML}...")
    
    tree = ET.parse(NOME_ARQUIVO_XML)
    root = tree.getroot()

    # Processar as Designações
    for designation in root.findall("Designation"):
        unique_id = designation.find("UniqueID").text if designation.find("UniqueID") is not None else None
        
        # Verificar se o nome está estruturado com Name1, Name2, Name6, etc.
        name = None
        names = designation.findall("Names/Name")
        
        # Tentativa de encontrar o nome primário
        for name_elem in names:
            if name_elem.find("NameType") is not None and name_elem.find("NameType").text == "Primary name":
                # Verificar se temos Name1, Name2 ou Name6 para montar o nome
                name_parts = []
                for part in name_elem.findall("Name1"):
                    name_parts.append(part.text)
                for part in name_elem.findall("Name2"):
                    name_parts.append(part.text)
                for part in name_elem.findall("Name6"):
                    name_parts.append(part.text)
                
                # Juntar partes do nome
                name = " ".join(name_parts)
                break
        
        # Agora capturamos os aliases
        aliases = []
        for name_elem in names:
            if name_elem.find("NameType") is not None and name_elem.find("NameType").text == "Alias":
                alias = name_elem.find("Name6").text if name_elem.find("Name6") is not None else None
                if alias:
                    aliases.append(alias)
        
        # Continuar com a coleta dos outros dados
        regime_name = designation.find("RegimeName").text if designation.find("RegimeName") is not None else None
        sanctions_imposed = designation.find("SanctionsImposed").text if designation.find("SanctionsImposed") is not None else None
        address_country = designation.find("Addresses/Address/AddressCountry").text if designation.find("Addresses/Address/AddressCountry") is not None else None
        gender = designation.find("IndividualDetails/Individual/Genders/Gender").text if designation.find("IndividualDetails/Individual/Genders/Gender") is not None else None
        nationality = designation.find("IndividualDetails/Individual/Nationalities/Nationality").text if designation.find("IndividualDetails/Individual/Nationalities/Nationality") is not None else None
        
        positions = []
        for position in designation.findall("IndividualDetails/Individual/Positions/Position"):
            positions.append(position.text)
        
        # Formatar a data de nascimento (dob)
        dob = designation.find("IndividualDetails/Individual/DOBs/DOB").text if designation.find("IndividualDetails/Individual/DOBs/DOB") is not None else None
        dob = formatar_data(dob)  # Aqui aplicamos a formatação

        passport = designation.find("IndividualDetails/Individual/PassportDetails/Passport/PassportNumber").text if designation.find("IndividualDetails/Individual/PassportDetails/Passport/PassportNumber") is not None else None
        
        # Montar o registro
        registros.append({
            "unique_id": unique_id,
            "name": name,
            "aliases": ", ".join(aliases),  # Concatena os aliases em uma string
            "regime_name": regime_name,
            "sanctions_imposed": sanctions_imposed,
            "address_country": address_country,
            "gender": gender,
            "nationality": nationality,
            "positions": ", ".join(positions),  # Concatena as posições em uma string
            "dob": dob,
            "passport": passport
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

        # Criar as tabelas, se não existirem
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uk_entities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(255),
                regime_name VARCHAR(255),
                sanctions_imposed VARCHAR(255),
                address_country VARCHAR(255),
                gender VARCHAR(50),
                nationality VARCHAR(255),
                dob DATE,
                passport VARCHAR(255)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uk_names (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entity_id INT,
                name TEXT,
                alias TEXT,
                FOREIGN KEY (entity_id) REFERENCES uk_entities(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uk_addresses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entity_id INT,
                address_country TEXT,
                FOREIGN KEY (entity_id) REFERENCES uk_entities(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uk_sanctions_indicators (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entity_id INT,
                asset_freeze BOOLEAN,
                arms_embargo BOOLEAN,
                targeted_arms_embargo BOOLEAN,
                prohibition_of_port_entry BOOLEAN,
                travel_ban BOOLEAN,
                FOREIGN KEY (entity_id) REFERENCES uk_entities(id)
            )
        """)

        # Inserir os registros no banco
        for registro in registros:
            # Inserir dados na tabela de entidades
            cursor.execute("""
                INSERT INTO uk_entities (unique_id, regime_name, sanctions_imposed, address_country, gender, nationality, dob, passport)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                registro['unique_id'],
                registro['regime_name'],
                registro['sanctions_imposed'],
                registro['address_country'],
                registro['gender'],
                registro['nationality'],
                registro['dob'],
                registro['passport']
            ))

            entity_id = cursor.lastrowid  # Obter o ID da última inserção

            # Inserir nomes
            if registro['name']:
                cursor.execute("""
                    INSERT INTO uk_names (entity_id, name, alias)
                    VALUES (%s, %s, %s)
                """, (entity_id, registro['name'], registro['aliases']))

            # Inserir endereços
            if registro['address_country']:
                cursor.execute("""
                    INSERT INTO uk_addresses (entity_id, address_country)
                    VALUES (%s, %s)
                """, (entity_id, registro['address_country']))

            # Inserir indicadores de sanção (aqui é só um exemplo, você pode adicionar os valores necessários)
            cursor.execute("""
                INSERT INTO uk_sanctions_indicators (entity_id, asset_freeze, arms_embargo, targeted_arms_embargo, prohibition_of_port_entry, travel_ban)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entity_id, None, None, None, None, None))  # Defina os valores para os indicadores

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
    registros = processar_xml()
    inserir_no_banco(registros)

    # Limpeza opcional
    if os.path.exists(NOME_ARQUIVO_XML):
        os.remove(NOME_ARQUIVO_XML)
