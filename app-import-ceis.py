import requests
import mysql.connector
from datetime import datetime

# Função para converter datas no formato DD/MM/YYYY para YYYY-MM-DD
def format_date(date_str):
    if date_str:  # Verifica se a data não está vazia
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Erro ao formatar a data: {date_str}")
            return None
    return None

# Conexão com o MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="phpmyadmin",
    password="Lcstanke@2018*",
    database="lista-negra"
)

cursor = conn.cursor()

# Criar a tabela (caso ainda não exista)
create_table_query = """
CREATE TABLE IF NOT EXISTS ceis_sancoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skSancao INT NULL,
    skFatAcordosLeniencia INT NULL,
    skFatCepim INT NULL,
    cadastro VARCHAR(255) NULL,
    cpfCnpj VARCHAR(255) NULL,
    nomeSancionado TEXT NULL,
    ufSancionado VARCHAR(10),
    categoriaSancao VARCHAR(255),
    orgao TEXT NULL,
    dataPublicacao DATE,
    valorMulta VARCHAR(255),
    dataInicialSancao DATE,
    dataFinalSancao DATE,
    quantidade INT NULL,
    linkDetalhamento TEXT NULL
);
"""

cursor.execute(create_table_query)
conn.commit()

# URL da API
api_url = "https://portaldatransparencia.gov.br/sancoes/consulta/resultado?paginacaoSimples=true&tamanhoPagina=1000000000&offset=0&direcaoOrdenacao=asc&colunaOrdenacao=nomeSancionado&colunasSelecionadas=linkDetalhamento%2Ccadastro%2CcpfCnpj%2CnomeSancionado%2CufSancionado%2Corgao%2CcategoriaSancao%2CdataPublicacao%2CvalorMulta%2Cquantidade&_=1733245637601"  # Substitua pela URL real

# Fazer a chamada GET para a API
try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Verifica se ocorreu algum erro
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Erro ao chamar a API: {e}")
    exit()

# Inserir os dados da API na tabela
insert_query = """
INSERT INTO ceis_sancoes (
    skSancao, skFatAcordosLeniencia, skFatCepim, cadastro, cpfCnpj,
    nomeSancionado, ufSancionado, categoriaSancao, orgao, dataPublicacao,
    valorMulta, dataInicialSancao, dataFinalSancao, quantidade, linkDetalhamento
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

for item in data["data"]:
    values = (
        item["skSancao"],
        item["skFatAcordosLeniencia"],
        item["skFatCepim"],
        item["cadastro"],
        item["cpfCnpj"],
        item["nomeSancionado"],
        item.get("ufSancionado"),  # Pode ser NULL
        item.get("categoriaSancao"),  # Pode ser NULL
        item["orgao"],
        format_date(item.get("dataPublicacao")),  # Formata para YYYY-MM-DD
        item["valorMulta"],
        format_date(item.get("dataInicialSancao")),  # Formata para YYYY-MM-DD
        format_date(item.get("dataFinalSancao")),  # Formata para YYYY-MM-DD
        item["quantidade"],
        item["linkDetalhamento"]
    )
    cursor.execute(insert_query, values)

conn.commit()

print("Dados inseridos com sucesso!")

# Fechar conexão
cursor.close()
conn.close()
