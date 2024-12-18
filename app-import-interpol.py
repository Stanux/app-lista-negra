import requests
import mysql.connector

# URL base da API
url = "https://ws-public.interpol.int/notices/v1/red"

# Configuração do banco de dados
db_config = {
    "host": "localhost",
    "user": "phpmyadmin",
    "password": "Lcstanke@2018*",
    "database": "lista-negra"
}

# Função para criar tabelas, se não existirem
def criar_tabelas():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interpol_notices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                forename VARCHAR(255),
                name VARCHAR(255),
                nationality TEXT,
                link VARCHAR(500) UNIQUE
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabelas: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Função para inserir dados no banco, se não existir
def inserir_no_banco(forename, name, nationality, link):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verificar se o link já existe para evitar duplicação
        cursor.execute("SELECT 1 FROM interpol_notices WHERE link = %s", (link,))
        if cursor.fetchone():
            print(f"Registro com link {link} já existe. Pulando...")
            return

        cursor.execute("""
            INSERT INTO interpol_notices (forename, name, nationality, link)
            VALUES (%s, %s, %s, %s)
        """, (forename, name, nationality, link))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir no banco: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Função principal para buscar todos os registros
def buscar_todos_registros():
    page = 1
    total = None  # Total de registros (será definido na primeira requisição)
    result_per_page = 200  # Máximo permitido pela API

    while total is None or page <= (total // result_per_page) + 1:
        print(f"Buscando página {page}...")

        params = {
            # "resultPerPage": result_per_page,
            # "page": page
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Obter total de registros apenas na primeira iteração
            if total is None:
                total = data.get("total", 0)
                print(f"Total de registros: {total}")

            notices = data["_embedded"]["notices"]
            for notice in notices:
                forename = notice.get("forename", "N/A")
                name = notice.get("name", "N/A")
                nationality = ", ".join(notice.get("nationalities", []) or [])
                link = notice["_links"]["self"]["href"]

                # Inserir no banco, verificando duplicidade
                inserir_no_banco(forename, name, nationality, link)
                print(f"Inserido: {forename} {name}")

            page += 1
        else:
            print(f"Erro na página {page}: {response.status_code}")
            break

# Fluxo principal
if __name__ == "__main__":
    criar_tabelas()
    buscar_todos_registros()
