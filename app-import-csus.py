import xml.etree.ElementTree as ET
import requests
import mysql.connector
from datetime import datetime
from playwright.sync_api import sync_playwright

URL_PRINCIPAL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
NOME_ARQUIVO_XML = "consolidated.xml"

# Função para baixar o arquivo XML usando Playwright
def baixar_arquivo_xml():
    print(f"Baixando arquivo de: {URL_PRINCIPAL}")
    resposta = requests.get(URL_PRINCIPAL, stream=True)
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
    
    # Parse do XML
    tree = ET.parse(NOME_ARQUIVO_XML)
    root = tree.getroot()

    # Processar indivíduos
    for entity in root.findall(".//INDIVIDUAL"):
        unique_id = entity.find("DATAID").text if entity.find("DATAID") is not None else ""
        versionnum = entity.find("VERSIONNUM").text if entity.find("VERSIONNUM") is not None else ""
        first_name = entity.find("FIRST_NAME").text if entity.find("FIRST_NAME") is not None else ""
        second_name = entity.find("SECOND_NAME").text if entity.find("SECOND_NAME") is not None else ""
        third_name = entity.find("THIRD_NAME").text if entity.find("THIRD_NAME") is not None else ""
        fourth_name = entity.find("FOURTH_NAME").text if entity.find("FOURTH_NAME") is not None else ""
        gender = entity.find("GENDER").text if entity.find("GENDER") is not None else ""
        full_name = f"{first_name} {second_name} {third_name} {fourth_name}".strip()
        un_list_type = entity.find("UN_LIST_TYPE").text if entity.find("UN_LIST_TYPE") is not None else ""
        reference_number = entity.find("REFERENCE_NUMBER").text if entity.find("REFERENCE_NUMBER") is not None else ""
        listed_on = entity.find("LISTED_ON").text if entity.find("LISTED_ON") is not None else ""
        comments = entity.find("COMMENTS1").text if entity.find("COMMENTS1") is not None else ""
        title = entity.find(".//TITLE/VALUE").text if entity.find(".//TITLE/VALUE") is not None else ""
        
        designations = ""
        for designation in entity.findall('.//DESIGNATION'):
            value = designation.find('VALUE')
            if value is not None:
                designations += value.text + " "

        nationality = entity.find(".//NATIONALITY/VALUE").text if entity.find(".//NATIONALITY/VALUE") is not None else ""
        list_type = entity.find(".//LIST_TYPE/VALUE").text if entity.find(".//LIST_TYPE/VALUE") is not None else ""
        
        date_of_birth = entity.find(".//INDIVIDUAL_DATE_OF_BIRTH")
        if date_of_birth is not None:
            date_of_birth_date = date_of_birth.find("DATE").text if date_of_birth.find("DATE") is not None else ""
            date_of_birth_type_of_date = date_of_birth.find("TYPE_OF_DATE").text if date_of_birth.find("TYPE_OF_DATE") is not None else ""
            date_of_birth_from_year = date_of_birth.find("FROM_YEAR").text if date_of_birth.find("FROM_YEAR") is not None else ""
            date_of_birth_year = date_of_birth.find("YEAR").text if date_of_birth.find("YEAR") is not None else ""
            date_of_birth_to_year = date_of_birth.find("TO_YEAR").text if date_of_birth.find("TO_YEAR") is not None else ""
            date_of_birth_note = date_of_birth.find("NOTE").text if date_of_birth.find("NOTE") is not None else ""
            
        place_of_birth = entity.find(".//INDIVIDUAL_PLACE_OF_BIRTH")
        if place_of_birth is not None:
            place_of_birth_city = place_of_birth.find("CITY").text if place_of_birth.find("CITY") is not None else ""
            place_of_birth_country = place_of_birth.find("COUNTRY").text if place_of_birth.find("COUNTRY") is not None else ""
            place_of_birth_note = place_of_birth.find("NOTE").text if place_of_birth.find("NOTE") is not None else ""
            place_of_birth_state = place_of_birth.find("STATE_PROVINCE").text if place_of_birth.find("STATE_PROVINCE") is not None else ""
            place_of_birth_address = place_of_birth.find("STREET").text if place_of_birth.find("STREET") is not None else ""
            
        individual_address = entity.find(".//INDIVIDUAL_ADDRESS/STREET").text if entity.find(".//INDIVIDUAL_ADDRESS/STREET") is not None else ""
        individual_city = entity.find(".//INDIVIDUAL_ADDRESS/CITY").text if entity.find(".//INDIVIDUAL_ADDRESS/CITY") is not None else ""
        individual_zip_code = entity.find(".//INDIVIDUAL_ADDRESS/ZIP_CODE").text if entity.find(".//INDIVIDUAL_ADDRESS/ZIP_CODE") is not None else ""
        individual_country = entity.find(".//INDIVIDUAL_ADDRESS/COUNTRY").text if entity.find(".//INDIVIDUAL_ADDRESS/COUNTRY") is not None else ""
        individual_state = entity.find(".//INDIVIDUAL_ADDRESS/STATE_PROVINCE").text if entity.find(".//INDIVIDUAL_ADDRESS/STATE_PROVINCE") is not None else "" 
        individual_note = entity.find(".//INDIVIDUAL_ADDRESS/NOTE").text if entity.find(".//INDIVIDUAL_ADDRESS/NOTE") is not None else "" 

        individual_document = entity.find(".//INDIVIDUAL_DOCUMENT")
        if individual_document is not None:
            individual_document_city_of_issue = individual_document.find("CITY_OF_ISSUE").text if individual_document.find("CITY_OF_ISSUE") is not None else ""
            individual_document_country_of_issue = individual_document.find("COUNTRY_OF_ISSUE").text if individual_document.find("COUNTRY_OF_ISSUE") is not None else ""
            individual_document_date_of_issue = individual_document.find("DATE_OF_ISSUE").text if individual_document.find("DATE_OF_ISSUE") is not None else ""
            individual_document_issuing_country = individual_document.find("ISSUING_COUNTRY").text if individual_document.find("ISSUING_COUNTRY") is not None else ""
            individual_document_note = individual_document.find("NOTE").text if individual_document.find("NOTE") is not None else ""
            individual_document_number = individual_document.find("NUMBER").text if individual_document.find("NUMBER") is not None else ""
            individual_document_type_of_document = individual_document.find("TYPE_OF_DOCUMENT").text if individual_document.find("TYPE_OF_DOCUMENT") is not None else ""
            individual_document_type_of_document2 = individual_document.find("TYPE_OF_DOCUMENT2").text if individual_document.find("TYPE_OF_DOCUMENT2") is not None else ""
        
        # Adicionando aliases de indivíduos
        for alias in entity.findall(".//INDIVIDUAL_ALIAS"):
            if alias is not None:
                alias_name = alias.find("ALIAS_NAME").text if alias.find("ALIAS_NAME") is not None else ""
                alias_city_of_birth = alias.find("CITY_OF_BIRTH").text if alias.find("CITY_OF_BIRTH") is not None else ""
                alias_country_of_birth = alias.find("COUNTRY_OF_BIRTH").text if alias.find("COUNTRY_OF_BIRTH") is not None else ""
                alias_date_of_birth = alias.find("DATE_OF_BIRTH").text if alias.find("DATE_OF_BIRTH") is not None else ""
                alias_note = alias.find("NOTE").text if alias.find("NOTE") is not None else ""
                alias_quality = alias.find("QUALITY").text if alias.find("QUALITY") is not None else ""
            
                aliases.append({
                    "individual_unique_id": unique_id,
                    "alias_name" : alias_name,
                    "alias_city_of_birth" : alias_city_of_birth,
                    "alias_country_of_birth" : alias_country_of_birth,
                    "alias_date_of_birth" : alias_date_of_birth,
                    "alias_note" : alias_note,
                    "alias_quality" : alias_quality,
                })

        # Adicionar registro de indivíduo
        registros.append({
            "unique_id" : unique_id,
            "type" : 'Individual',
            "versionnum" : versionnum,
            "first_name" : first_name,
            "second_name" : second_name,
            "third_name" : third_name,
            "fourth_name" : fourth_name,
            "gender" : gender,
            "full_name" : full_name,
            "un_list_type" : un_list_type,
            "reference_number" : reference_number,
            "listed_on" : listed_on,
            "comments" : comments,
            "title" : title,
            "designations" : designations,
            "nationality" : nationality,
            "list_type" : list_type,
            "date_of_birth_date" : date_of_birth_date,
            "date_of_birth_type_of_date" : date_of_birth_type_of_date,
            "date_of_birth_from_year" : date_of_birth_from_year,
            "date_of_birth_year" : date_of_birth_year,
            "date_of_birth_to_year" : date_of_birth_to_year,
            "date_of_birth_note" : date_of_birth_note,
            "place_of_birth_city" : place_of_birth_city,
            "place_of_birth_country" : place_of_birth_country,
            "place_of_birth_note" : place_of_birth_note,
            "place_of_birth_state" : place_of_birth_state,
            "place_of_birth_address" : place_of_birth_address,
            "address" : individual_address,
            "city" : individual_city,
            "zip_code" : individual_zip_code,
            "country" : individual_country,
            "state" : individual_state,
            "note" : individual_note,
            "document_city_of_issue" : individual_document_city_of_issue,
            "document_country_of_issue" : individual_document_country_of_issue,
            "document_date_of_issue" : individual_document_date_of_issue,
            "document_issuing_country" : individual_document_issuing_country,
            "document_note" : individual_document_note,
            "document_number" : individual_document_number,
            "document_type_of_document" : individual_document_type_of_document,
            "document_type_of_document2" : individual_document_type_of_document2,
        })

    # Processar indivíduos
    for entity in root.findall(".//ENTITY"):
        unique_id = entity.find("DATAID").text if entity.find("DATAID") is not None else ""
        versionnum = entity.find("VERSIONNUM").text if entity.find("VERSIONNUM") is not None else ""
        full_name = entity.find("FIRST_NAME").text if entity.find("FIRST_NAME") is not None else ""
        # full_name = f"{first_name} {second_name} {third_name} {fourth_name}".strip()
        un_list_type = entity.find("UN_LIST_TYPE").text if entity.find("UN_LIST_TYPE") is not None else ""
        reference_number = entity.find("REFERENCE_NUMBER").text if entity.find("REFERENCE_NUMBER") is not None else ""
        listed_on = entity.find("LISTED_ON").text if entity.find("LISTED_ON") is not None else ""
        comments = entity.find("COMMENTS1").text if entity.find("COMMENTS1") is not None else ""
        list_type = entity.find(".//LIST_TYPE/VALUE").text if entity.find(".//LIST_TYPE/VALUE") is not None else ""
        entity_address = entity.find(".//ENTITY_ADDRESS/STREET").text if entity.find(".//ENTITY_ADDRESS/STREET") is not None else ""
        entity_city = entity.find(".//ENTITY_ADDRESS/CITY").text if entity.find(".//ENTITY_ADDRESS/CITY") is not None else ""
        entity_zip_code = entity.find(".//ENTITY_ADDRESS/ZIP_CODE").text if entity.find(".//ENTITY_ADDRESS/ZIP_CODE") is not None else ""
        entity_country = entity.find(".//ENTITY_ADDRESS/COUNTRY").text if entity.find(".//ENTITY_ADDRESS/COUNTRY") is not None else ""
        entity_state = entity.find(".//ENTITY_ADDRESS/STATE_PROVINCE").text if entity.find(".//ENTITY_ADDRESS/STATE_PROVINCE") is not None else "" 
        entity_note = entity.find(".//ENTITY_ADDRESS/NOTE").text if entity.find(".//ENTITY_ADDRESS/NOTE") is not None else "" 
        

        # Adicionando aliases de indivíduos
        for alias in entity.findall(".//ENTITY_ALIAS"):
            if alias is not None:
                alias_name = alias.find("ALIAS_NAME").text if alias.find("ALIAS_NAME") is not None else ""
                alias_note = alias.find("NOTE").text if alias.find("NOTE") is not None else ""
                alias_quality = alias.find("QUALITY").text if alias.find("QUALITY") is not None else ""
            
                aliases.append({
                    "individual_unique_id": unique_id,
                    "alias_name" : alias_name,
                    "alias_city_of_birth" : alias_city_of_birth,
                    "alias_country_of_birth" : alias_country_of_birth,
                    "alias_date_of_birth" : alias_date_of_birth,
                    "alias_note" : alias_note,
                    "alias_quality" : alias_quality,
                })

        # Adicionar registro de entidades
        
        registros.append({
            "unique_id" : unique_id,
            "type" : 'Individual',
            "versionnum" : versionnum,
            "first_name" : "",
            "second_name" : "",
            "third_name" : "",
            "fourth_name" : "",
            "gender" : "",
            "full_name" : full_name,
            "un_list_type" : un_list_type,
            "reference_number" : reference_number,
            "listed_on" : listed_on,
            "comments" : comments,
            "title" : title,
            "designations" : "",
            "nationality" : "",
            "list_type" : list_type,
            "date_of_birth_date" : date_of_birth_date,
            "date_of_birth_type_of_date" : date_of_birth_type_of_date,
            "date_of_birth_from_year" : date_of_birth_from_year,
            "date_of_birth_year" : date_of_birth_year,
            "date_of_birth_to_year" : date_of_birth_to_year,
            "date_of_birth_note" : date_of_birth_note,
            "place_of_birth_city" : place_of_birth_city,
            "place_of_birth_country" : place_of_birth_country,
            "place_of_birth_note" : place_of_birth_note,
            "place_of_birth_state" : place_of_birth_state,
            "place_of_birth_address" : place_of_birth_address,
            "address" : entity_address,
            "city" : entity_city,
            "zip_code" : entity_zip_code,
            "country" : entity_country,
            "state" : entity_state,
            "note" : entity_note,
            "document_city_of_issue" : "",
            "document_country_of_issue" : "",
            "document_date_of_issue" : "",
            "document_issuing_country" : "",
            "document_note" : "",
            "document_number" : "",
            "document_type_of_document" : "",
            "document_type_of_document2" : "",
        })
    print(f"Registros de indivíduos processados: {len(registros)}")
    print(f"Registros de aliases de indivíduos processados: {len(aliases)}")
    return registros, aliases

# Função para verificar e criar as tabelas no banco de dados
def verificar_e_criar_tabelas(cursor):
    # Verificar e criar a tabela csus_entities
    cursor.execute("""
        CREATE TABLE csnu_nomes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(50) NOT NULL,               -- 'Individual' ou 'Entity'
            unique_id VARCHAR(255) NULL,              -- Pode ser NULL para entidades
            versionnum VARCHAR(50) NULL,
            first_name VARCHAR(255) NULL,             -- Apenas para indivíduos
            second_name VARCHAR(255) NULL,            -- Apenas para indivíduos
            third_name VARCHAR(255) NULL,             -- Apenas para indivíduos
            fourth_name VARCHAR(255) NULL,            -- Apenas para indivíduos
            gender VARCHAR(255) NULL,                  -- Apenas para indivíduos
            full_name TEXT NULL,              -- Ambos (indivíduos e entidades)
            un_list_type VARCHAR(100) NULL,           -- Ambos
            reference_number VARCHAR(100) NULL,       -- Ambos
            listed_on DATE NULL,                      -- Ambos
            comments TEXT NULL,                        -- Ambos
            title VARCHAR(255) NULL,                  -- Apenas para indivíduos
            designations TEXT NULL,                   -- Apenas para indivíduos
            nationality VARCHAR(255) NULL,            -- Apenas para indivíduos
            list_type VARCHAR(100) NULL,              -- Ambos
            date_of_birth_date VARCHAR(255) NULL,             -- Apenas para indivíduos
            date_of_birth_type_of_date VARCHAR(255) NULL, -- Apenas para indivíduos
            date_of_birth_from_year VARCHAR(255) NULL,        -- Apenas para indivíduos
            date_of_birth_year VARCHAR(255) NULL,             -- Apenas para indivíduos
            date_of_birth_to_year VARCHAR(255) NULL,          -- Apenas para indivíduos
            date_of_birth_note TEXT NULL,             -- Apenas para indivíduos
            place_of_birth_city VARCHAR(255) NULL,    -- Apenas para indivíduos
            place_of_birth_country VARCHAR(255) NULL, -- Apenas para indivíduos
            place_of_birth_note TEXT NULL,            -- Apenas para indivíduos
            place_of_birth_state VARCHAR(255) NULL,   -- Apenas para indivíduos
            place_of_birth_address VARCHAR(255) NULL, -- Apenas para indivíduos
            address VARCHAR(255) NULL,                -- Apenas para entidades
            city VARCHAR(255) NULL,                   -- Apenas para entidades
            zip_code VARCHAR(255) NULL,                -- Apenas para entidades
            country VARCHAR(255) NULL,                -- Apenas para entidades
            state VARCHAR(255) NULL,                  -- Apenas para entidades
            note TEXT NULL,                           -- Ambos
            document_city_of_issue VARCHAR(255) NULL, -- Ambos
            document_country_of_issue VARCHAR(255) NULL, -- Ambos
            document_date_of_issue VARCHAR(255) NULL,         -- Ambos
            document_issuing_country VARCHAR(255) NULL, -- Ambos
            document_note TEXT NULL,                  -- Ambos
            document_number VARCHAR(255) NULL,        -- Ambos
            document_type_of_document VARCHAR(255) NULL, -- Ambos
            document_type_of_document2 VARCHAR(255) NULL, -- Ambos
            UNIQUE INDEX idx_unique_id (unique_id) -- Adiciona um índice único para o campo unique_id
        )
    """)

    # Verificar e criar a tabela csus_aliases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS csnu_aliases (
            individual_unique_id VARCHAR(255),
            alias_name TEXT,
            alias_quality VARCHAR(255),
            alias_city_of_birth VARCHAR(255),
            alias_country_of_birth VARCHAR(255),
            alias_date_of_birth VARCHAR(255),
            alias_note VARCHAR(255),
            FOREIGN KEY (individual_unique_id) REFERENCES csnu_nomes(unique_id)
        )
    """)
    
# Função para inserir dados no MySQL
def inserir_dados_no_mysql(registros, aliases):
    try:
        # Conexão com o banco de dados
        conn = mysql.connector.connect(
            host="localhost",
            user="phpmyadmin",
            password="Lcstanke@2018*",
            database="lista-negra"
        )
        cursor = conn.cursor()
        
        verificar_e_criar_tabelas(cursor)

        # Query de inserção para registros de indivíduos
        query_individual = """
            INSERT INTO csnu_nomes (
                unique_id, type, versionnum, first_name, second_name, third_name, fourth_name,
                gender, full_name, un_list_type, reference_number, listed_on, comments, title,
                designations, nationality, list_type, date_of_birth_date, date_of_birth_type_of_date,
                date_of_birth_from_year, date_of_birth_year, date_of_birth_to_year, date_of_birth_note,
                place_of_birth_city, place_of_birth_country, place_of_birth_note, place_of_birth_state,
                place_of_birth_address, address, city, zip_code, country, state, note,
                document_city_of_issue, document_country_of_issue, document_date_of_issue, document_issuing_country,
                document_note, document_number, document_type_of_document, document_type_of_document2
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Query de inserção para aliases
        query_alias = """
            INSERT INTO csnu_aliases (
                individual_unique_id, alias_name, alias_city_of_birth, alias_country_of_birth,
                alias_date_of_birth, alias_note, alias_quality
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Definir tamanho do batch
        batch_size = 1000

        # Inserir registros de indivíduos em lotes
        for i in range(0, len(registros), batch_size):
            batch = registros[i:i + batch_size]
            valores = [
                (
                    registro['unique_id'], registro['type'], registro['versionnum'], registro['first_name'],
                    registro['second_name'], registro['third_name'], registro['fourth_name'], registro['gender'],
                    registro['full_name'], registro['un_list_type'], registro['reference_number'],
                    registro['listed_on'], registro['comments'], registro['title'], registro['designations'],
                    registro['nationality'], registro['list_type'], registro['date_of_birth_date'],
                    registro['date_of_birth_type_of_date'], registro['date_of_birth_from_year'],
                    registro['date_of_birth_year'], registro['date_of_birth_to_year'], registro['date_of_birth_note'],
                    registro['place_of_birth_city'], registro['place_of_birth_country'], registro['place_of_birth_note'],
                    registro['place_of_birth_state'], registro['place_of_birth_address'], registro['address'],
                    registro['city'], registro['zip_code'], registro['country'], registro['state'], registro['note'],
                    registro['document_city_of_issue'], registro['document_country_of_issue'],
                    registro['document_date_of_issue'], registro['document_issuing_country'],
                    registro['document_note'], registro['document_number'], registro['document_type_of_document'],
                    registro['document_type_of_document2']
                )
                for registro in batch
            ]
            print("Valores:", valores)  # Verificar os dados

            cursor.executemany(query_individual, valores)

        # Inserir aliases em lotes
        for i in range(0, len(aliases), batch_size):
            batch = aliases[i:i + batch_size]
            valores = [
                (
                    alias['individual_unique_id'], alias['alias_name'], alias['alias_city_of_birth'],
                    alias['alias_country_of_birth'], alias['alias_date_of_birth'], alias['alias_note'],
                    alias['alias_quality']
                )
                for alias in batch
            ]
            cursor.executemany(query_alias, valores)

        # Commit das transações
        conn.commit()
        print(f"Dados inseridos com sucesso!")

    except mysql.connector.Error as erro:
        print(f"Erro ao inserir dados no MySQL: {erro}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Função para armazenar os dados no banco de dados
# def salvar_no_banco(registros, aliases):
#     conn = mysql.connector.connect(
#             host="localhost",
#             user="phpmyadmin",
#             password="Lcstanke@2018*",
#             database="lista-negra"
#         )
#     cursor = conn.cursor()

#     # Verificar e criar as tabelas se necessário
#     verificar_e_criar_tabelas(cursor)

#     # Salvar indivíduos na tabela 'csus_entities'
#     for reg in registros:
#         cursor.execute("""
#             INSERT INTO csus_entities (unique_id, full_name, nationality, dob, address, city, country, document_type, document_number)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (reg["unique_id"], reg["full_name"], reg["nationality"], reg["dob"], reg["address"], reg["city"], reg["country"], reg["document_type"], reg["document_number"]))

#     # Salvar aliases de indivíduos na tabela 'csus_aliases'
#     for alias in aliases:
#         cursor.execute("""
#             INSERT INTO csus_aliases (individual_id, alias_name, alias_quality)
#             VALUES (%s, %s, %s)
#         """, (alias["individual_id"], alias["alias_name"], alias["alias_quality"]))

    
#     # Commit e fechamento da conexão
#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("Dados salvos no banco de dados com sucesso.")

# Função principal para rodar o processo
def main():
    baixar_arquivo_xml()
    registros, aliases = processar_xml()
    # salvar_no_banco(registros, aliases)
    inserir_dados_no_mysql(registros, aliases)

if __name__ == "__main__":
    main()
