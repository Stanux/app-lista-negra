from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Função para resumir texto em português
def summarize_text(text, max_length=100, min_length=30):
    if not text or len(text.strip()) < min_length:
        return "Erro: O texto é muito curto para ser resumido."
    
    try:
        # Carregar modelo e tokenizador
        tokenizer = AutoTokenizer.from_pretrained(
            "unicamp-dl/ptt5-base-portuguese-vocab",
            use_fast=False,
            legacy=False  # Ativa o novo comportamento
        )

        # tokenizer = AutoTokenizer.from_pretrained("unicamp-dl/ptt5-base-portuguese-vocab", use_fast=False)
        model = AutoModelForSeq2SeqLM.from_pretrained("unicamp-dl/ptt5-base-portuguese-vocab")
        
        summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]["summary_text"]
    except ValueError as ve:
        return f"Erro no modelo de resumo: {ve}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
        
# Exemplo de texto
news_text = """
Jovem Pan

mude a cidade 

 

ouça ao vivo 

Minha conta 
Política
Brasil
Economia
Mundo
Esportes
Saúde
Entretenimento
Colunistas
Programas
Bem-estar
Áudios
Últimas
Especiais
JP NEWS:
Juiz que xingou Klopp é demitido da Premier League por conduta inadequada e investigações de apostas
Premiê da Síria concorda em entregar o poder a grupo rebelde que derrubou regime de Bashar al-Assad
Suspeito de matar executivo da UnitedHealth é detido na Pensilvânia
Dólar sobe a R$ 6,08 e renova recorde histórico com desconforto fiscal
CJJ da Câmara vota nesta terça proposta que proíbe celulares em salas de aula
Reforma tributária: CCJ do Senado cancela reunião em que relatório seria lido por falta de quórum
Dudu se despede do Palmeiras após temporada conturbada
PM da Bahia investiga policiais suspeitos de homicídios e formação de grupos de extermínio
2024 pode ser o ano mais quente da história, aponta agência da UE
Gleisi Hoffmann diz que PT deve manter sua posição à esquerda e preservar laços com a base social
Max Verstappen vai fazer trabalho comunitário em Ruanda após sanção da FIA
Roberto Jefferson recebe primeiro voto a favor de condenação a nove anos de prisão
Estado de SP quer aumentar impostos em 300%; comer fora de casa ficará mais caro e restaurantes temem o pior
Dino nega pedido da AGU para mudanças de regras para pagamento de emendas parlamentares
Governo brasileiro evacua embaixada do Brasil em Damasco
STF determina uso obrigatório de câmeras pela Polícia Militar de São Paulo
Relator da regulamentação da reforma tributária define prazo de 90 dias para ajustes se alíquota padrão estourar limite
Em meio à crise da PM, Tarcísio desmarca compromisso em Brasília por testes de novas câmeras corporais
Inflação de 2024 sobe para 6,35% em nova previsão do mercado financeiro
Mais de 370 mil alunos das capitais do Brasil estudam em escolas em áreas vulneráveis a desastres climáticos
STF começa julgamento de Roberto Jefferson nesta segunda-feira
STF discute direitos de motoristas de aplicativo e vínculo com as plataformas
Brasil brilha no Globo de Ouro 2025 com ‘Ainda Estou Aqui’ entre os indicados a Melhor Filme Internacional
Israel afirma que atacou depósitos de ‘armas químicas’ na Síria
Presidente da Mancha Verde renuncia e deve se entregar na próxima quinta
Ministério da Saúde vai distribuir 1,5 milhão de vacinas contra a covid-19
STF retoma julgamento sobre regulação das redes sociais
Tarcísio, Nunes e prefeitos de 24 cidades se reúnem para discutir apagão em São Paulo
Justiça proíbe o presidente da Coreia do Sul de deixar o país
Brasil demonstra ‘preocupação’ após queda de Assad e orienta seus cidadãos a deixarem a Síria
PL que obriga bancos a devolver dinheiro de golpes traz mais segurança, afirmam especialistas
2024 será o primeiro ano a superar o limite de 1,5°C de aquecimento climático
Seleção do Brasileiro tem 6 do Botafogo, estrela do Corinthians e só um palmeirense; Luiz Henrique é eleito o craque
Jay-Z é acusado de estuprar menina de 13 anos junto com Diddy
Ana de Armas encanta a CCXP e fala sobre ‘Bailarina’, filme do universo de John Wick
Conselho de Segurança da ONU convoca reunião de emergência sobre a Síria
Gabigol se despede do Flamengo, critica direção e diz que virou ‘imortal’ no clube: ‘Acho que um dia eu volto’
Fernanda Torres divide com Demi Moore o segundo lugar em premiação dos críticos de Los Angeles
Deslizamento em mina tira 79 pessoas de suas casas em Conceição do Pará
Multidão vai às ruas na Síria para comemorar a queda do governo de Bashar al-Assad
Botafogo chega ao seu terceiro título do Campeonato Brasileiro; confira todos os campeões
Athletico-PR é rebaixado à Série B após derrota para o Atlético-MG
Corinthians encerra temporada com vitória, recorde, golaço de bicicleta de Memphis e Yuri Alberto artilheiro do Brasileirão
Botafogo vence o São Paulo, sai da fila do Brasileirão e coroa melhor ano de sua história
Trump considera perdão a invasores do Capitólio e prioriza deportação de imigrantes ilegais
Lewis Hamilton troca a Mercedes pela Ferrari e encerra história de sucesso de 12 anos
Chelsea vence clássico com o Tottenham de virada e diminui vantagem do Liverpool no Inglês
Líder de grupo rebelde da Síria discursa após tomar Damasco e diz que ‘vitória é da nação islâmica’
Ofensiva rebelde na Síria deixa mais de 900 mortos
Rússia afirma que Assad deixou instruções para ‘transferência pacífica de poder’ na Síria                        
Juiz que xingou Klopp é demitido da Premier League por conduta inadequada e investigações de apostas
Premiê da Síria concorda em entregar o poder a grupo rebelde que derrubou regime de Bashar al-Assad
Suspeito de matar executivo da UnitedHealth é detido na Pensilvânia
Dólar sobe a R$ 6,08 e renova recorde histórico com desconforto fiscal
CJJ da Câmara vota nesta terça proposta que proíbe celulares em salas de aula
Reforma tributária: CCJ do Senado cancela reunião em que relatório seria lido por falta de quórum
Dudu se despede do Palmeiras após temporada conturbada
PM da Bahia investiga policiais suspeitos de homicídios e formação de grupos de extermínio
2024 pode ser o ano mais quente da história, aponta agência da UE
Gleisi Hoffmann diz que PT deve manter sua posição à esquerda e preservar laços com a base social
Max Verstappen vai fazer trabalho comunitário em Ruanda após sanção da FIA
Roberto Jefferson recebe primeiro voto a favor de condenação a nove anos de prisão
Estado de SP quer aumentar impostos em 300%; comer fora de casa ficará mais caro e restaurantes temem o pior
Dino nega pedido da AGU para mudanças de regras para pagamento de emendas parlamentares
Governo brasileiro evacua embaixada do Brasil em Damasco
STF determina uso obrigatório de câmeras pela Polícia Militar de São Paulo
Relator da regulamentação da reforma tributária define prazo de 90 dias para ajustes se alíquota padrão estourar limite
Em meio à crise da PM, Tarcísio desmarca compromisso em Brasília por testes de novas câmeras corporais
Inflação de 2024 sobe para 6,35% em nova previsão do mercado financeiro
Mais de 370 mil alunos das capitais do Brasil estudam em escolas em áreas vulneráveis a desastres climáticos
STF começa julgamento de Roberto Jefferson nesta segunda-feira
STF discute direitos de motoristas de aplicativo e vínculo com as plataformas
Brasil brilha no Globo de Ouro 2025 com ‘Ainda Estou Aqui’ entre os indicados a Melhor Filme Internacional
Israel afirma que atacou depósitos de ‘armas químicas’ na Síria
Presidente da Mancha Verde renuncia e deve se entregar na próxima quinta
Ministério da Saúde vai distribuir 1,5 milhão de vacinas contra a covid-19
STF retoma julgamento sobre regulação das redes sociais
Tarcísio, Nunes e prefeitos de 24 cidades se reúnem para discutir apagão em São Paulo
Justiça proíbe o presidente da Coreia do Sul de deixar o país
Brasil demonstra ‘preocupação’ após queda de Assad e orienta seus cidadãos a deixarem a Síria
PL que obriga bancos a devolver dinheiro de golpes traz mais segurança, afirmam especialistas
2024 será o primeiro ano a superar o limite de 1,5°C de aquecimento climático
Seleção do Brasileiro tem 6 do Botafogo, estrela do Corinthians e só um palmeirense; Luiz Henrique é eleito o craque
Jay-Z é acusado de estuprar menina de 13 anos junto com Diddy
Ana de Armas encanta a CCXP e fala sobre ‘Bailarina’, filme do universo de John Wick
Conselho de Segurança da ONU convoca reunião de emergência sobre a Síria
Gabigol se despede do Flamengo, critica direção e diz que virou ‘imortal’ no clube: ‘Acho que um dia eu volto’
Fernanda Torres divide com Demi Moore o segundo lugar em premiação dos críticos de Los Angeles
Deslizamento em mina tira 79 pessoas de suas casas em Conceição do Pará
Multidão vai às ruas na Síria para comemorar a queda do governo de Bashar al-Assad
Botafogo chega ao seu terceiro título do Campeonato Brasileiro; confira todos os campeões
Athletico-PR é rebaixado à Série B após derrota para o Atlético-MG
Corinthians encerra temporada com vitória, recorde, golaço de bicicleta de Memphis e Yuri Alberto artilheiro do Brasileirão
Botafogo vence o São Paulo, sai da fila do Brasileirão e coroa melhor ano de sua história
Trump considera perdão a invasores do Capitólio e prioriza deportação de imigrantes ilegais
Lewis Hamilton troca a Mercedes pela Ferrari e encerra história de sucesso de 12 anos
Chelsea vence clássico com o Tottenham de virada e diminui vantagem do Liverpool no Inglês
Líder de grupo rebelde da Síria discursa após tomar Damasco e diz que ‘vitória é da nação islâmica’
Ofensiva rebelde na Síria deixa mais de 900 mortos
Rússia afirma que Assad deixou instruções para ‘transferência pacífica de poder’ na Síria                        
Erro:
Jovem Pan > Programas > Mala Pronta
Mala Pronta

Patty Leone, influenciadora digital de turismo, percorre os quatro cantos do planeta para mostrar os roteiros mais interessantes e descolados.

O UNIVERSO MÁGICO DE ORLANDO, NOS EUA | MALA PRONTA – 07/12/2024
EXPLORE A CULTURA E AS PRAIAS DESLUMBRANTES DE ALAGOAS | MALA PRONTA – 30/11/2024
GRÉCIA: NAVEGUE PELAS ILHAS PARADISÍACAS DO PAÍS | MALA PRONTA – 16/11/2024
Mala Pronta
09/11/2024 14h00
PERU: CONHEÇA O TESOURO DA AMÉRICA DO SUL (PARTE 2) | MALA PRONTA – 09/11/2024
Mala Pronta
02/11/2024 14h00
PERU: CONHEÇA O TESOURO DA AMÉRICA DO SUL | MALA PRONTA – 02/11/2024
Mala Pronta
19/10/2024 14h00
SEGREDOS POR TRÁS DA GASTRONOMIA DO CHILE (PARTE 2) | MALA PRONTA – 19/10/2024
Mala Pronta
12/10/2024 14h00
SEGREDOS POR TRÁS DA GASTRONOMIA DO CHILE: VINHOS E SABORES QUE ENCANTAM | MALA PRONTA – 12/10/2024
Mala Pronta
05/10/2024 14h00
A BELEZA ENCANTADORA DE NATAL, A CAPITAL DO SOL | MALA PRONTA- 05/10/2024
Mala Pronta
28/09/2024 14h00
CONHEÇA AS MARAVILHAS DO RIO GRANDE DO NORTE | MALA PRONTA- 28/09/2024
Mala Pronta
21/09/2024 14h00
EXPLORE AS BELEZAS DA PARAÍBA (PARTE 2) | MALA PRONTA – 21/09/2024
Mala Pronta
14/09/2024 14h00
EXPLORE AS BELEZAS DA PARAÍBA | MALA PRONTA – 14/09/2024
Mala Pronta
31/08/2024 14h00
MALA PRONTA – FLÓRIDA (ESTADOS UNIDOS) PARTE 2 | 31/08/2024
Mala Pronta
17/08/2024 14h00
MALA PRONTA – FLÓRIDA (ESTADOS UNIDOS) | 17/08/2024
Mala Pronta
10/08/2024 14h00
MALA PRONTA – BERLIM (ALEMANHA) PARTE 2 | 10/08/2024
Mala Pronta
03/08/2024 14h00
MALA PRONTA – BERLIM (ALEMANHA) | 03/08/2024
Brasil
26/07/2024 13h49
Apresentadora do programa Mala Pronta, Patty Leone é condecorada com título de cidadã de João Pessoa
Mala Pronta
06/07/2024 14h00
MALA PRONTA – LISBOA (PORTUGAL) | 29/06/2024
Mala Pronta
22/06/2024 14h00
MALA PRONTA – CRUZEIRO PELA TURQUIA | 15/06/2024
Mala Pronta
22/06/2024 14h00
MALA PRONTA – ATENAS | 21/06/2024
Mala Pronta
15/06/2024 14h00
MALA PRONTA – CRUZEIRO PELA TURQUIA | 15/06/2024
Página 1 de 12
1
(current)
2
3
4
5
Próxima ›
Última »

Últimos Posts

Notícias

Premiê da Síria concorda em entregar o poder a ...

Notícias

Suspeito de matar executivo da UnitedHealth é detido na ...

Notícias

Dólar sobe a R$ 6,08 e renova recorde histórico ...

Veja Mais
Mais JP
Últimas Notícias
Opinião Jovem Pan
Videos
 
Podcasts
JP News
 
Afiliadas
Ouça a Rádio Jovem Pan Ao Vivo
 
Atlas de cobertura
Sobre a Jovem Pan
Anuncie Feed RSS Aplicativos Política de Privacidade Política de Ética Nossa Redação
(11) 93117-0620
Todos os direitos reservados - Portal Jovem Pan Online - Rádio Panamericana S/A
Av. Paulista, 807 - 24º andar - Cerqueira César - São Paulo - SP

+55 11 2870-9700 - jovempanonline@jovempan.com.br

Bem-vindo!
A JOVEM PAN usa cookies para armazenar informações sobre como você usa o nosso site e APPs e as páginas que visita. Tudo para tornar sua experiência a mais agradável possível. Para entender os tipos de cookies que utilizamos, clique em 'Termos de Uso e Política de Privacidade'. Ao clicar em 'Aceitar', você consente com a utilização de cookies e com os termos de uso e política de privacidade.
ACEITAR
TERMOS DE USO

AÚDIOJOVEM PAN NEWSSão Paulo - SP

Programação Ao Vivo
×
"""

# Resumo do texto em português
resultado = summarize_text(news_text, max_length=100, min_length=30)
print(resultado)

