from rapidfuzz import process, fuzz
import mysql.connector

# Conexão com o banco de dados
def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="phpmyadmin",
        password="Lcstanke@2018*",
        database="lista-negra"
    )

# Função para buscar nomes do banco de dados
def buscar_nomes_do_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT primary_name FROM ofac_sdn")
    resultados = [row[0].lower() for row in cursor.fetchall()]  # Convertendo para minúsculas
    conn.close()
    return resultados

# Função para realizar busca fuzzy
def busca_fuzzy(nome_busca, lista_nomes, limiar=90):
    nome_busca = nome_busca.lower()  # Convertendo string de busca para minúsculas
    resultados = process.extract(nome_busca, lista_nomes, scorer=fuzz.ratio, score_cutoff=limiar)
    return resultados

# Principal
if __name__ == "__main__":
    # Nome a ser pesquisado
    nome_procurado = "MuHAMMEDd FA ABDULAH"

    # Buscar todos os nomes do banco de dados
    nomes = buscar_nomes_do_banco()

    # Realizar busca fuzzy com 90% ou mais de similaridade
    resultados = busca_fuzzy(nome_procurado, nomes, limiar=2)

    # Exibir resultados
    if resultados:
        print(f"Nomes encontrados com 90% ou mais de similaridade para '{nome_procurado}':")
        for nome, similaridade, _ in resultados:
            print(f"- {nome} (Similaridade: {similaridade}%)")
    else:
        print(f"Nenhum nome encontrado com 90% ou mais de similaridade para '{nome_procurado}'.")
