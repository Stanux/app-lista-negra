import re
import mysql.connector
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import requests
from urllib.parse import urljoin, urlparse

# Configurações do banco de dados
db_config = {
    "host": "localhost",
    "user": "phpmyadmin",
    "password": "Lcstanke@2018*",
    "database": "lista-negra"
}

palavras_chave = ["influencers", "influenciador", "instagramer", "blogueiro", "blogueira", "tiktoker", "criador de conteúdo"]

def conectar_banco():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        exit(1)

def criar_tabela_mysql():
    conn = conectar_banco()    
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS web_noticias (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url_origem VARCHAR(255),
        url_texto VARCHAR(255),
        palavras_match VARCHAR(255),
        titulo TEXT,
        texto LONGTEXT,
        data_identificada DATETIME
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def salvar_no_banco(url_origem, url_texto, palavras, titulo, texto):
    conexao = conectar_banco()
    try:
        cursor = conexao.cursor()
        sql = """
        INSERT INTO web_noticias (url_origem, url_texto, palavras_match, titulo, texto, data_identificada)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (url_origem, url_texto, ", ".join(palavras), titulo, texto, datetime.now())
        cursor.execute(sql, valores)
        conexao.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao salvar no banco de dados: {err}")
    finally:
        cursor.close()
        conexao.close()

def obter_urls_ultimos_3_dias():
    conn = conectar_banco()
    try:
        cursor = conn.cursor()
        data_limite = datetime.now() - timedelta(days=3)
        query = "SELECT url_texto FROM web_noticias WHERE data_identificada >= %s"
        cursor.execute(query, (data_limite,))
        urls = cursor.fetchall()
        return set(url[0] for url in urls)
    except mysql.connector.Error as err:
        print(f"Erro ao consultar URLs no banco: {err}")
        return set()
    finally:
        cursor.close()
        conn.close()

def analisar_robots_txt(base_url):
    robots_url = f"{base_url}/robots.txt"
    disallow_paths = []
    try:
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.startswith("Disallow:"):
                    disallow_path = line.split(":")[1].strip()
                    disallow_paths.append(disallow_path)
    except Exception as e:
        print(f"Erro ao acessar robots.txt: {e}")
    return disallow_paths

def url_permitida(url, disallow_paths):
    parsed_url = urlparse(url)
    for path in disallow_paths:
        if path and parsed_url.path.startswith(path):
            return False
    return True

def iniciar_scraping(url_inicial):
    visitados = set()
    disallow_paths = analisar_robots_txt(url_inicial)  # Obtendo paths de exclusão do robots.txt
    urls_recentemente_processadas = obter_urls_ultimos_3_dias()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        page = context.new_page()

        def extrair_links(url, origem):
            if url in visitados or url in urls_recentemente_processadas or not url_permitida(url, disallow_paths) or '#' in url:
                return
            visitados.add(url)

            try:
                page.goto(url, timeout=20000, wait_until="networkidle")
                links = page.eval_on_selector_all("a[href]", "elements => elements.map(e => e.href)")

                # Título da página
                titulo = page.title()
                texto_principal = page.inner_text("body")

                # Verificar palavras-chave
                palavras_encontradas = [palavra for palavra in palavras_chave if palavra.lower() in texto_principal.lower()]

                if palavras_encontradas:
                    print(f"<<<< Notícia encontrada: {url}")
                    salvar_no_banco(origem, url, palavras_encontradas, titulo, texto_principal)
                else:
                    print(f">>>> Notícia ignorada: {url}")

                # Continuar para links internos
                for link in links:
                    link = urljoin(url, link)  # Resolver links relativos
                    if url_permitida(link, disallow_paths) and urlparse(link).netloc == urlparse(url_inicial).netloc:
                        extrair_links(link, url)

            except Exception as e:
                print(f"Erro ao processar {url}: {e}")

        try:
            extrair_links(url_inicial, url_inicial)
        finally:
            browser.close()

# Executar o robô
if __name__ == "__main__":
    criar_tabela_mysql()
    url_inicio = "https://jovempan.com.br/"
    iniciar_scraping(url_inicio)
