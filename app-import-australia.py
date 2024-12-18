import pandas as pd
import mysql.connector
from playwright.sync_api import sync_playwright
import os
import requests
import re


# Definindo o nome do arquivo
NOME_ARQUIVO = 'regulation8_consolidated.xlsx'

def baixar_excel():
    try:
        # URL completa para o arquivo Excel
        arquivo_url = 'https://www.dfat.gov.au/sites/default/files/regulation8_consolidated.xlsx'
        print(f"Baixando o arquivo de: {arquivo_url}")

        # Fazer o download com requests
        response = requests.get(arquivo_url, stream=True)

        if response.status_code == 200:
            with open(NOME_ARQUIVO, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Arquivo baixado com sucesso: {os.path.join(os.getcwd(), NOME_ARQUIVO)}")
        else:
            raise Exception(f"Falha ao baixar o arquivo. Status Code: {response.status_code}")
    
    except Exception as e:
        print(f"Erro ao baixar o arquivo: {e}")


def processar_excel():
    """
    Processa o Excel e organiza os dados em registros principais e aliases.
    """
    # Carregar o Excel
    df = pd.read_excel(NOME_ARQUIVO, sheet_name=0)
    df.columns = df.columns.str.strip()
    
    # Verifique novamente as colunas após a limpeza
    df = df.where(pd.notnull(df), None)

    registros_principais = []
    aliases = []

    # Iterar pelos registros
    for _, row in df.iterrows():
        reference = str(row["Reference"]).strip()
        name_type = row["Name Type"]
        # reference_base = ''.join(filter(str.isdigit, reference))  # Apenas números
        reference_base = re.match(r'^\d+', reference)
        reference_base = reference_base.group() if reference_base else reference  # Se não encontrar números, usa a referência original

        registro = {
            "reference": reference_base,
            "alias_ref": reference,
            "name": row["Name of Individual or Entity"],
            "type": row["Name Type"],
            "date_of_birth": row["Date of Birth"],
            "place_of_birth": row["Place of Birth"],
            "citizenship": row["Citizenship"],
            "address": row["Address"],
            "additional_info": row["Additional Information"],
            "listing_info": row["Listing Information"],
            "committees": row["Committees"],
            "control_date": row["Control Date"]
        }

        if reference == reference_base:
            registros_principais.append(registro)
        elif name_type != "Original Script":
            aliases.append(registro)
    return registros_principais, aliases

def criar_tabelas():
    """
    Cria as tabelas no banco de dados caso ainda não existam.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="phpmyadmin",
            password="Lcstanke@2018*",
            database="lista-negra"
        )
        cursor = conn.cursor()

        # Criar tabela principal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS au_names (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reference VARCHAR(50) UNIQUE,
                name TEXT,
                type VARCHAR(50),
                date_of_birth TEXT,
                place_of_birth TEXT,
                citizenship TEXT,
                address TEXT,
                additional_info TEXT,
                listing_info TEXT,
                committees TEXT,
                control_date DATE
            )
        """)

        # Criar tabela de aliases
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS au_aliases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reference VARCHAR(50),
                alias_ref VARCHAR(10),
                name TEXT,
                type VARCHAR(50),
                date_of_birth TEXT,
                place_of_birth TEXT,
                citizenship TEXT,
                address TEXT,
                additional_info TEXT,
                listing_info TEXT,
                committees TEXT,
                control_date DATE,
                FOREIGN KEY (reference) REFERENCES au_names(reference)
            )
        """)

        conn.commit()
        print("Tabelas criadas com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabelas: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def inserir_no_banco(registros_principais, aliases):
    """
    Insere os registros no banco de dados.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="phpmyadmin",
            password="Lcstanke@2018*",
            database="lista-negra"
        )
        cursor = conn.cursor()

        # Inserir registros principais
        for registro in registros_principais:
            cursor.execute("""
                INSERT INTO au_names (reference, name, type, date_of_birth, place_of_birth, citizenship, address, additional_info, listing_info, committees, control_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                type = VALUES(type),
                date_of_birth = VALUES(date_of_birth),
                place_of_birth = VALUES(place_of_birth),
                citizenship = VALUES(citizenship),
                address = VALUES(address),
                additional_info = VALUES(additional_info),
                listing_info = VALUES(listing_info),
                committees = VALUES(committees),
                control_date = VALUES(control_date)
            """, (
                registro["reference"],
                registro["name"],
                registro["type"],
                registro["date_of_birth"],
                registro["place_of_birth"],
                registro["citizenship"],
                registro["address"],
                registro["additional_info"],
                registro["listing_info"],
                registro["committees"],
                registro["control_date"]
            ))
        conn.commit()
        cursor = conn.cursor()

        #Inserir aliases
        for alias in aliases:
            cursor.execute("""
                INSERT INTO au_aliases (reference, alias_ref, name, type, date_of_birth, place_of_birth, citizenship, address, additional_info, listing_info, committees, control_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                alias["reference"],
                alias["alias_ref"],
                alias["name"],
                alias["type"],
                alias["date_of_birth"],
                alias["place_of_birth"],
                alias["citizenship"],
                alias["address"],
                alias["additional_info"],
                alias["listing_info"],
                alias["committees"],
                alias["control_date"]
            ))

        conn.commit()
        print(f"{len(registros_principais)} registros principais inseridos/atualizados com sucesso.")
        print(f"{len(aliases)} aliases inseridos com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao inserir dados no banco: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fluxo principal
if __name__ == "__main__":
    baixar_excel()
    registros_principais, aliases = processar_excel()
    criar_tabelas()
    inserir_no_banco(registros_principais, aliases)
