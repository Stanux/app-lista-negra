from playwright.sync_api import sync_playwright
import re

def obter_estatisticas_reclame_aqui(url_empresa):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Modo headless (sem interface gráfica)
        page = browser.new_page()

        # Definindo o user-agent e cabeçalhos personalizados
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        })

        try:
            print(f"Acessando página da empresa: {url_empresa}...")
            page.goto(url_empresa)
            # page.wait_for_load_state("networkidle")  # Aguarda o carregamento completo da página
            page.wait_for_timeout(6000)  # Aguarda carregamento inicial

            # Verifica e clica no banner de cookies, se presente
            if page.locator('a.cc-btn.cc-allow').is_visible():
                print("Aceitando cookies...")
                page.locator('a.cc-btn.cc-allow').click()
                page.wait_for_timeout(1000)  # Pequeno delay para garantir o clique

            # Aguarda e fecha o banner de survey, se presente
            print("Verificando presença de banner de survey...")
            if page.locator('svg.vwo-survey-close-icon').is_visible(timeout=10000):
                print("Fechando banner de survey...")
                close_button = page.locator('svg.vwo-survey-close-icon')
                close_button.click()
                page.wait_for_timeout(1000)

            # Coletando as estatísticas da página
            print("Coletando estatísticas...")
            # Obtenção do conteúdo da página
            reputacao_empresa = page.locator('div#ra-new-reputation').text_content().strip()

            # Quebra de linha após "?", adiciona um espaço após "Reputação" e quebra de linha antes de "A empresa"
            reputacao_empresa_formatada = re.sub(r'\?', '?\n', reputacao_empresa)  # Adiciona quebra de linha após "?"
            reputacao_empresa_formatada = re.sub(r'Reputação', 'Reputação ', reputacao_empresa_formatada)  # Adiciona um espaço após "Reputação"
            reputacao_empresa_formatada = re.sub(r'(?<=\n)A empresa', '\nA empresa', reputacao_empresa_formatada)  # Adiciona quebra de linha antes de "A empresa"

            estatisticas = {
                "reputacao_empresa": reputacao_empresa_formatada,
                "empresa_recebeu": page.locator('span:has-text("Esta empresa recebeu")').text_content().strip(),
                "estatistica_resposta": page.locator('span:has-text("Respondeu")').text_content().strip(),
                "aguardando_resposta": page.locator('span:has-text("aguardando resposta")').text_content().strip(),
                "reclamacoes_avaliadas": page.locator('span:has-text("avaliadas, e a nota média dos consumidores")').text_content().strip(),
                "voltar_fazer_negocio": page.locator('span:has-text("Dos que avaliaram")').text_content().strip(),
                "empresa_resolveu": page.locator('span:has-text("A empresa resolveu")').text_content().strip(),
                "tempo_medio": page.locator('span:has-text("O tempo médio de resposta é")').text_content().strip(),
            }

            # Usando expressões regulares para limpar e extrair números
            # estatisticas["empresa_recebeu"] = re.sub(r'\D', '', estatisticas["empresa_recebeu"])  # Extrai apenas números
            # estatisticas["estatistica_resposta"] = re.sub(r'\D', '', estatisticas["estatistica_resposta"])

            # Captura de tela para depuração, caso necessário
            page.screenshot(path="screenshot.png")

            return estatisticas

        except Exception as e:
            print(f"Erro ao obter informações: {e}")
            return None

        finally:
            browser.close()

# Uso
url_empresa = "https://www.reclameaqui.com.br/empresa/magazine-luiza-loja-online/"
# url_empresa = "https://www.reclameaqui.com.br/empresa/cebrac/"
estatisticas = obter_estatisticas_reclame_aqui(url_empresa)
if estatisticas:
    print("Estatísticas obtidas:")
    for chave, valor in estatisticas.items():
        print(f"{chave}: {valor}")
else:
    print("Não foi possível obter as estatísticas.")
