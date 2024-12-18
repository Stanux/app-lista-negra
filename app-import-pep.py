import requests
import mysql.connector
from datetime import datetime

# Configuração do banco de dados
db_config = {
    "host": "localhost",
    "user": "phpmyadmin",
    "password": "Lcstanke@2018*",
    "database": "lista-negra"
}

# Função para criar a tabela, se não existir
def create_table_if_not_exists():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peps (
            cpf VARCHAR(14) PRIMARY KEY,
            nome VARCHAR(255),
            sigla_funcao VARCHAR(50),
            descricao_funcao VARCHAR(100),
            nivel_funcao VARCHAR(50),
            cod_orgao VARCHAR(10),
            nome_orgao VARCHAR(255),
            dt_inicio_exercicio DATE,
            dt_fim_exercicio DATE,
            dt_fim_carencia DATE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Função para inserir dados no banco de dados
def insert_into_db(data_batch):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    existing_records = set()
    cursor.execute("SELECT cpf, nome FROM peps")
    existing_records = {(row[0], row[1]) for row in cursor.fetchall()}

    data_to_insert = []
    novos = 0
    for data in data_batch:
        cpf = data['cpf'].strip()
        nome = data['nome'].strip()

        if (cpf, nome) not in existing_records:
            dt_fim_exercicio = data.get('dt_fim_exercicio', '').strip() or None
            dt_fim_carencia = data.get('dt_fim_carencia', '').strip() or None
            dt_inicio_exercicio = data.get('dt_inicio_exercicio', '').strip() or None

            data_to_insert.append((
                cpf, nome,
                data.get('sigla_funcao', '').strip(),
                data.get('descricao_funcao', '').strip(),
                data.get('nivel_funcao', '').strip(),
                data.get('cod_orgao', '').strip(),
                data.get('nome_orgao', '').strip(),
                dt_inicio_exercicio,
                dt_fim_exercicio,
                dt_fim_carencia
            ))
            novos += 1
            print(f"> {novos}")

    if data_to_insert:
        try:
            cursor.executemany("""
                INSERT INTO peps (cpf, nome, sigla_funcao, descricao_funcao, nivel_funcao, cod_orgao, nome_orgao, dt_inicio_exercicio, dt_fim_exercicio, dt_fim_carencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data_to_insert)
            conn.commit()
            print(f"Novos registros: {novos}")
        except mysql.connector.IntegrityError:
            conn.rollback()

    cursor.close()
    conn.close()

# Função para obter e agregar dados por letra
def fetch_and_aggregate_by_letter(letter):
    aggregated_data = []
    page = 1
    while True:
        url = f'https://api.portaldatransparencia.gov.br/api-de-dados/peps?nome={letter}&pagina={page}'
        headers = {'accept': '*/*', 'chave-api-dados': '35d98c70ac9767a6a567e76af908e621'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200 or not response.text.strip():
                break
            data = response.json()
            if not data:
                break
            aggregated_data.extend(data)
            page += 1
        except Exception as e:
            print(f"Erro ao fazer a requisição: {e}")
            break

    return aggregated_data

# Função para obter e agregar dados por período
def fetch_and_aggregate_by_date_range(data_fim_exercicio_de, data_fim_exercicio_ate):
    aggregated_data = []
    page = 1
    while True:
        url = (
            f'https://api.portaldatransparencia.gov.br/api-de-dados/peps?dataFimExercicioDe={data_fim_exercicio_de}'
            f'&dataFimExercicioAte={data_fim_exercicio_ate}&pagina={page}'
        )
        headers = {'accept': '*/*', 'chave-api-dados': '35d98c70ac9767a6a567e76af908e621'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200 or not response.text.strip():
                break
            data = response.json()
            if not data:
                break
            aggregated_data.extend(data)
            page += 1
        except Exception as e:
            print(f"Erro ao fazer a requisição: {e}")
            break

    return aggregated_data

# Menu para escolha do método
def main():
    create_table_if_not_exists()
    print("Escolha o método de importação:")
    print("1. Importar por letras (vogais e Y)")
    print("2. Importar por intervalo de datas")
    choice = input("Digite o número da opção desejada: ")

    if choice == '1':
        selected_letters = ['A', 'E', 'I', 'O', 'U', 'Y']
        for letter in selected_letters:
            print(f"Iniciando agregação para a letra: {letter}")
            data = fetch_and_aggregate_by_letter(letter)
            print(f"Inserindo {len(data)} registros para a letra {letter}")
            insert_into_db(data)
    elif choice == '2':
        data_fim_exercicio_de = input("Digite a data inicial (DD/MM/YYYY): ")
        data_fim_exercicio_ate = input("Digite a data final (DD/MM/YYYY): ")
        try:
            datetime.strptime(data_fim_exercicio_de, "%d/%m/%Y")
            datetime.strptime(data_fim_exercicio_ate, "%d/%m/%Y")
            data = fetch_and_aggregate_by_date_range(data_fim_exercicio_de, data_fim_exercicio_ate)
            print(f"Inserindo {len(data)} registros para o intervalo de datas")
            insert_into_db(data)
        except ValueError:
            print("Datas inválidas. Por favor, tente novamente.")
    else:
        print("Opção inválida. Encerrando.")

if __name__ == "__main__":
    main()
