import requests
import mysql.connector

# URL base da API inicial
BASE_URL = "https://ws-public.interpol.int/notices/v1/red"

# Configuração do banco de dados
DB_CONFIG = {
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
    "YE", "ZM", "ZW", ""
]

# Faixas etárias (5 em 5 anos, de 0 a 120)
faixas_etarias = [(i+9, i + 10) for i in range(0, 121, 21)]


def criar_tabelas():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interpol_lista (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entity_id VARCHAR(255) UNIQUE,
                name VARCHAR(255),
                forename VARCHAR(255),
                date_of_birth VARCHAR(255),
                nationalities TEXT,
                distinguishing_marks TEXT,
                weight INT,
                eyes_colors_id VARCHAR(50),
                sex_id VARCHAR(50),
                place_of_birth VARCHAR(255),
                country_of_birth_id VARCHAR(50),
                hairs_id VARCHAR(50),
                height INT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interpol_mandados (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_interpol_lista INT,
                entity_id VARCHAR(255),
                charge TEXT,
                issuing_country_id VARCHAR(50),
                charge_translation TEXT,
                FOREIGN KEY (id_interpol_lista) REFERENCES interpol_lista(id)
            )
        """)
        
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabelas: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def buscar_dados_complementares(link):
    """Busca os dados complementares da API secundária."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar dados complementares: {response.status_code}")
    except Exception as e:
        print(f"Erro na requisição de dados complementares: {e}")
    return None

def inserir_ou_atualizar_dados(notice, dados_complementares):
    """Insere ou atualiza os dados principais e complementares no banco."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        with conn.cursor() as cursor:

            # Preparar os dados
            entity_id = notice["entity_id"]
            name = notice.get("name", "N/A")
            forename = notice.get("forename", "N/A")
            date_of_birth = notice.get("date_of_birth")

            # Garantir que nationalities seja uma lista antes de aplicar join
            nationalities = notice.get("nationalities", [])
            if not isinstance(nationalities, list):
                nationalities = []
            nationalities_str = ", ".join(nationalities)

            # Dados complementares
            distinguishing_marks = dados_complementares.get("distinguishing_marks", None)
            weight = dados_complementares.get("weight", 0)
            
            # Garantir que eyes_colors_id seja uma lista antes de aplicar join
            eyes_colors_id = dados_complementares.get("eyes_colors_id", [])
            if not isinstance(eyes_colors_id, list):
                eyes_colors_id = []
            eyes_colors_str = ", ".join(eyes_colors_id)

            sex_id = dados_complementares.get("sex_id", None)
            place_of_birth = dados_complementares.get("place_of_birth", None)
            country_of_birth_id = dados_complementares.get("country_of_birth_id", None)
            
            # Garantir que hairs_id seja uma lista antes de aplicar join
            hairs_id = dados_complementares.get("hairs_id", [])
            if not isinstance(hairs_id, list):
                hairs_id = []
            hairs_str = ", ".join(hairs_id)

            height = dados_complementares.get("height", 0)

            # Verificar se o registro já existe
            cursor.execute("SELECT id FROM interpol_lista WHERE entity_id = %s", (entity_id,))
            result = cursor.fetchone()

            if result:
                # Atualizar registro existente
                interpol_id = result[0]
                cursor.execute("""
                    UPDATE interpol_lista
                    SET name = %s, forename = %s, date_of_birth = %s, nationalities = %s,
                        distinguishing_marks = %s, weight = %s, eyes_colors_id = %s,
                        sex_id = %s, place_of_birth = %s, country_of_birth_id = %s,
                        hairs_id = %s, height = %s
                    WHERE id = %s
                """, (name, forename, date_of_birth, nationalities_str, distinguishing_marks, weight,
                      eyes_colors_str, sex_id, place_of_birth, country_of_birth_id, hairs_str, height, interpol_id))
            else:
                # Inserir novo registro
                cursor.execute("""
                    INSERT INTO interpol_lista (
                        entity_id, name, forename, date_of_birth, nationalities,
                        distinguishing_marks, weight, eyes_colors_id, sex_id,
                        place_of_birth, country_of_birth_id, hairs_id, height
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (entity_id, name, forename, date_of_birth, nationalities_str, distinguishing_marks,
                      weight, eyes_colors_str, sex_id, place_of_birth, country_of_birth_id, hairs_str, height))
                interpol_id = cursor.lastrowid

            # Inserir mandados
            cursor.execute("DELETE FROM interpol_mandados WHERE entity_id = %s", (entity_id,))
            for mandado in dados_complementares.get("arrest_warrants", []):
                charge = mandado.get("charge", None)
                issuing_country_id = mandado.get("issuing_country_id", None)
                charge_translation = mandado.get("charge_translation", None)
                cursor.execute("""
                    INSERT INTO interpol_mandados (
                        id_interpol_lista, entity_id, charge, issuing_country_id, charge_translation
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (interpol_id, entity_id, charge, issuing_country_id, charge_translation))

            conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir/atualizar no banco: {err}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        if conn.is_connected():
            conn.close()


def buscar_todos_registros():
    """Busca todos os registros da API inicial e seus complementares."""
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    params = {
        "resultPerPage": 50,  # Define 150 registros por página
    }
    pagina = 1

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    while True:
        print(f"Pagina {pagina}!")

        params["page"] = pagina  # Adiciona o número da página aos parâmetros
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            notices = data.get("_embedded", {}).get("notices", [])
            
            if len(notices) == 0:
                print(f"Nenhum registros, pulando.")
                break  # Sai do loop para a próxima nacionalidade
            
            for notice in notices:
                dados_complementares = buscar_dados_complementares(notice["_links"]["self"]["href"])
                if dados_complementares:
                    inserir_ou_atualizar_dados(notice, dados_complementares)

            # Verifica se há mais páginas para buscar
            if "_links" in data and "next" in data["_links"]:
                pagina += 1  # Avança para a próxima página
            else:
                break  # Não há mais páginas, encerra o loop
        else:
            print(f"Erro ao acessar a API inicial: {response.status_code}")
            break  # Em caso de erro, interrompe a execução
        
def buscar_todos_registros_faixa():
    """Busca todos os registros da API inicial e seus complementares."""
    
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

            response = requests.get(BASE_URL, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                notices = data.get("_embedded", {}).get("notices", [])
                
                # if len(notices) == 0:
                #     print(f"Nenhum registros, pulando.")
                #     break  # Sai do loop para a próxima nacionalidade
                
                for notice in notices:
                    dados_complementares = buscar_dados_complementares(notice["_links"]["self"]["href"])
                    if dados_complementares:
                        inserir_ou_atualizar_dados(notice, dados_complementares)
            else:
                print(f"Erro ao acessar a API inicial: {response.status_code}")
                break  # Em caso de erro, interrompe a execução

if __name__ == "__main__":
    criar_tabelas()
    # buscar_todos_registros()
    buscar_todos_registros_faixa()

