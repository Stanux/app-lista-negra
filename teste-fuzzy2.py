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

# Função para buscar nomes e apelidos do banco de dados
def buscar_nomes_e_alias():
    conn = conectar_banco()
    cursor = conn.cursor()

    # Buscar primary_name
    cursor.execute("SELECT primary_name FROM ofac_sdn")
    nomes = [{"tipo": "primary_name", "nome": row[0].lower()} for row in cursor.fetchall()]

    # Buscar alias_names
    cursor.execute("SELECT alias_names FROM ofac_sdn WHERE alias_names IS NOT NULL")
    apelidos = [{"tipo": "alias_names", "nome": alias.lower()} for row in cursor.fetchall() for alias in row[0].split(";")]

    conn.close()
    return nomes + apelidos

# Função para realizar busca fuzzy
def busca_fuzzy(nome_busca, lista_nomes, limiar=90):
    nome_busca = nome_busca.lower()  # Convertendo string de busca para minúsculas
    resultados = process.extract(nome_busca, lista_nomes, scorer=fuzz.ratio, score_cutoff=limiar)
    return resultados

# Principal
if __name__ == "__main__":
    # Nome a ser pesquisado
    nome_procurado = "viuva negra"

    # Buscar todos os nomes e apelidos do banco de dados
    registros = buscar_nomes_e_alias()

    # Separar nomes e mapear para a busca fuzzy
    lista_nomes = [registro["nome"] for registro in registros]
    resultados_fuzzy = busca_fuzzy(nome_procurado, lista_nomes, limiar=60)

    # Exibir resultados com tipo correspondente
    if resultados_fuzzy:
        print(f"Resultados com 90% ou mais de similaridade para '{nome_procurado}':")
        for nome_encontrado, similaridade, idx in resultados_fuzzy:
            tipo = registros[idx]["tipo"]
            print(f"- {nome_encontrado} (Similaridade: {similaridade}%, Tipo: {tipo})")
    else:
        print(f"Nenhuma correspondência encontrada para '{nome_procurado}'.")
