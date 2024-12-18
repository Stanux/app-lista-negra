import mysql.connector
from playwright.sync_api import sync_playwright
import time

# Função para criar a tabela no MySQL caso ela não exista
def criar_tabela_mysql():
    conn = mysql.connector.connect(
        host="localhost",
        user="phpmyadmin",
        password="Lcstanke@2018*",
        database="lista-negra"
    )
    
    cursor = conn.cursor()
    
    # Comando SQL para criar a tabela caso ela não exista
    create_table_query = """
    CREATE TABLE IF NOT EXISTS inidoneos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome_responsavel VARCHAR(255),
        cpf_cnpj VARCHAR(20),
        uf VARCHAR(2),
        processo VARCHAR(50),
        deliberação VARCHAR(50),
        transito_em_julgado VARCHAR(50),
        data_final VARCHAR(50),
        data_acordao VARCHAR(50)
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()  # Confirmar criação da tabela
    cursor.close()
    conn.close()

# Função para capturar os dados da tabela
def capturar_dados_tabela():
    with sync_playwright() as p:
        # Lançando o navegador
        browser = p.chromium.launch(headless=True)  # Set to True para rodar em background
        page = browser.new_page()

        # Acessando a página
        page.goto('https://contas.tcu.gov.br/ords/f?p=1660:2:::NO:2::')

        # Esperar até que o seletor da lista de páginas seja carregado
        page.wait_for_selector('select.a-IRR-selectList')

        # Alterar o valor da opção para 1000 (exibir 1000 itens por página)
        page.select_option('select.a-IRR-selectList', value='1000')

        # Esperar a tabela ser atualizada após a seleção
        page.wait_for_selector('table.a-IRR-table')

        # Rolagem da página até o final para garantir que todos os dados sejam carregados
        last_height = page.evaluate("document.body.scrollHeight")
        while True:
            # Rolar para baixo
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Esperar um pouco para garantir que os dados sejam carregados
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break  # Se a altura não mudou, significa que carregou todos os dados
            last_height = new_height

        # Capturar as linhas da tabela
        linhas = page.locator('table.a-IRR-table tbody tr').all()

        dados = []
        
        # Iterar sobre as linhas e capturar as colunas
        for linha in linhas:
            colunas = linha.locator('td').all()
            dados_linha = [coluna.text_content().strip() for coluna in colunas]
            if dados_linha:  # Ignorar linhas vazias
                dados.append(dados_linha)

        # Fechar o navegador
        browser.close()

        # Retornar os dados coletados
        return dados

# Função para inserir dados no MySQL
def inserir_dados_mysql(dados):
    conn = mysql.connector.connect(
        host="localhost",
        user="phpmyadmin",
        password="Lcstanke@2018*",
        database="lista-negra"
    )
    
    cursor = conn.cursor()

    # Comando SQL para inserir os dados
    query = """
    INSERT INTO inidoneos (nome_responsavel, cpf_cnpj, uf, processo, deliberação, transito_em_julgado, data_final, data_acordao)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Inserir cada linha de dados
    for dado in dados:
        # Garantir que as datas estão no formato correto
        nome_responsavel = dado[0]
        cpf_cnpj = dado[1]
        uf = dado[2]
        processo = dado[3]
        deliberacao = dado[4]
        transito_em_julgado = dado[5]
        data_final = dado[6]
        data_acordao = dado[7]
        
        # Converter as datas de formato de string para o formato de data se necessário
        # Exemplo de conversão de string para data no formato 'YYYY-MM-DD'
        # Não é necessário fazer a conversão, pois o MySQL lida com isso automaticamente
        valores = (nome_responsavel, cpf_cnpj, uf, processo, deliberacao, transito_em_julgado, data_final, data_acordao)

        cursor.execute(query, valores)
    
    # Commit para garantir que as mudanças sejam salvas
    conn.commit()

    # Fechar a conexão
    cursor.close()
    conn.close()

# Executar a função de criação da tabela
criar_tabela_mysql()

# Executar a função de captura e inserção
dados = capturar_dados_tabela()
inserir_dados_mysql(dados)
