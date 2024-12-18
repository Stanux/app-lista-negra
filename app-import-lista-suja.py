import pdfplumber
import mysql.connector
import requests
from datetime import datetime

# Configurações do banco de dados
conn = mysql.connector.connect(
    host="localhost",
    user="phpmyadmin",
    password="Lcstanke@2018*",
    database="lista-negra"
)

def tratar_data(data_str):
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print(f"Data inválida encontrada: {data_str}")
        return None

# URL do PDF
url = "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/cadastro_de_empregadores.pdf"
pdf_path = "cadastro_de_empregadores.pdf"

# 1. Baixar o PDF
def baixar_pdf(url, pdf_path):
    print("Baixando o PDF...")
    response = requests.get(url)
    with open(pdf_path, "wb") as file:
        file.write(response.content)
    print(f"PDF baixado em: {pdf_path}")

def tratar_int(valor):
    try:
        return int(valor) if valor.isdigit() else None
    except ValueError:
        return None
    
# 2. Criar a tabela no banco de dados
def criar_tabela(conexao):
    print("Criando a tabela no banco de dados...")
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cadastro_empregadores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ano_acao_fiscal VARCHAR(255),
            uf CHAR(2),
            empregador VARCHAR(255),
            cnpj_cpf VARCHAR(20),
            estabelecimento VARCHAR(255),
            trabalhadores_envolvidos VARCHAR(255),
            cnae VARCHAR(50),
            decisao_administrativa TEXT,
            inclusao_cadastro TEXT
        )
    """)
    conexao.commit()
    print("Tabela criada com sucesso!")

# 3. Processar e extrair dados do PDF
def extrair_dados_pdf(pdf_path):
    print("Extraindo dados do PDF...")
    dados_extraidos = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                # Ignorar cabeçalhos (ajuste conforme o layout do PDF)
                for row in table[1:]:
                    if row:  # Ignorar linhas vazias
                        dados_extraidos.append(row)
    print(f"{len(dados_extraidos)} registros extraídos.")
    return dados_extraidos

# 4. Inserir os dados no banco de dados
def inserir_dados(conexao, dados):
    print("Inserindo dados no banco de dados...")
    cursor = conexao.cursor()
    for row in dados:
        try:
            # Ignorar linhas irrelevantes (exemplo: linha de cabeçalhos ou inválida)
            if not row[0].isdigit():
                continue

            # Ajuste os índices conforme a estrutura do PDF
            ano_acao_fiscal = tratar_int(row[1])  # Ano da ação fiscal
            uf = row[2].strip() if row[2] else None
            empregador = row[3].strip() if row[3] else None
            cnpj_cpf = row[4].strip() if row[4] else None
            estabelecimento = row[5].strip() if row[5] else None
            trabalhadores_envolvidos = tratar_int(row[6]) if row[6] else None
            cnae = row[7].strip() if row[7] else None
            decisao_administrativa = row[8].strip() if row[8] else None
            inclusao_cadastro = row[9].strip() if row[9] else None

            cursor.execute("""
                INSERT INTO cadastro_empregadores (
                    ano_acao_fiscal, uf, empregador, cnpj_cpf, estabelecimento,
                    trabalhadores_envolvidos, cnae, decisao_administrativa, inclusao_cadastro
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ano_acao_fiscal, uf, empregador, cnpj_cpf, estabelecimento,
                trabalhadores_envolvidos, cnae, decisao_administrativa, inclusao_cadastro
            ))
        except Exception as e:
            print(f"Erro ao inserir registro: {row} -> {e}")
    conexao.commit()
    print("Dados inseridos com sucesso!")

# 5. Fluxo principal
def main():
    # Passo 1: Baixar o PDF
    baixar_pdf(url, pdf_path)

    # Passo 2: Criar a tabela
    criar_tabela(conn)

    # Passo 3: Extrair dados do PDF
    dados = extrair_dados_pdf(pdf_path)
    # print(dados)
    # exit()
    # Passo 4: Inserir dados no banco
    inserir_dados(conn, dados)

if __name__ == "__main__":
    try:
        main()
    finally:
        conn.close()
        print("Conexão com o banco de dados encerrada.")
