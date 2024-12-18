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

# Lista de nacionalidades
nacionalidades = [
    "AF", "AL", "DZ", "AS", "AD", "AO", "AI", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH",
    "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BR", "VG", "BN", "BG",
    "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD", "CL", "CN", "CO", "KM", "CG", "CD", "CR",
    "HR", "CU", "CW", "CY", "CZ", "CI", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE",
    "SZ", "ET", "AT,BE,BG,CY,DE,DK,EE,ES,FI,FR,GR,HR,HU,IE,IT,LT,LU,LV,MT,NL", "FM", "FJ", "FI",
    "FR", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GD", "GT", "GN", "GW", "GY", "HT", "HN", "HK",
    "HU", "914", "IS", "IN", "ID", "IR", "IQ", "IE", "IL", "IT", "JM", "JP", "JO", "KZ", "KE", "KI",
    "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MG", "MW",
    "MY", "MV", "ML", "MT", "MH", "MR", "MU", "MX", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM",
    "NA", "NR", "NP", "NL", "NZ", "NI", "NE", "NG", "MK", "NO", "OM", "PK", "PW", "PS", "PA", "PG",
    "PY", "PE", "PH", "PL", "PT", "PR", "QA", "RO", "RU", "RW", "KN", "LC", "VC", "WS", "SM", "ST",
    "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "SS", "ES", "LK", "916",
    "SD", "SR", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TO", "TT", "TN", "TM", "TC",
    "TV", "TR", "UG", "UA", "922", "UNK", "AE", "GB", "US", "UY", "UZ", "VU", "VA", "VE", "VN",
    "YE", "ZM", "ZW"
]

# Faixas etárias (5 em 5 anos, de 0 a 120)
faixas_etarias = [(i, i + 2) for i in range(0, 121, 3)]

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
                age_min INT,
                age_max INT,
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
    for nacionalidade in nacionalidades:
        for age_min, age_max in faixas_etarias:
            print(f"Buscando para nacionalidade {nacionalidade}, idade {age_min}-{age_max}...")

            params = {
                "nationality": nacionalidade,
                "ageMin": age_min,
                "ageMax": age_max
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()

                notices = data["_embedded"]["notices"]
                for notice in notices:
                    forename = notice.get("forename", "N/A")
                    name = notice.get("name", "N/A")
                    nationality = ", ".join(notice.get("nationalities", []) or [])
                    link = notice["_links"]["self"]["href"]

                    # Inserir no banco, verificando duplicidade
                    inserir_no_banco(forename, name, nationality,link)
                    print(f"Inserido: {forename} {name}")
            else:
                print(f"Erro ao buscar para nacionalidade {nacionalidade}, idade {age_min}-{age_max}: {response.status_code}")

# Fluxo principal
if __name__ == "__main__":
    criar_tabelas()
    buscar_todos_registros()
