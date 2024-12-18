from pytrends.request import TrendReq
import pandas as pd

def buscar_google_trends(termo):
    # Configurar o cliente pytrends
    pytrends = TrendReq(hl='pt-BR', tz=360)
    
    # Definir o termo de busca
    pytrends.build_payload([termo], cat=0, timeframe='today 12-m', geo='BR', gprop='')
    
    # Interesse geral
    interesse_geral = pytrends.interest_over_time()
    if interesse_geral.empty:
        print("Nenhum dado encontrado para o termo buscado.")
        return

    # Interesse por região (estados no Brasil)
    interesse_por_estado = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
    
    # Exibir resultados
    print(f"Interesse geral por '{termo}':")
    print(interesse_geral.head())  # Mostra as primeiras linhas do DataFrame
    print("\nInteresse por estado:")
    print(interesse_por_estado.sort_values(by=termo, ascending=False).head())  # Mostra os estados com maior interesse

    # Opcional: salvar em arquivos CSV
    interesse_geral.to_csv(f"{termo}_interesse_geral.csv")
    interesse_por_estado.to_csv(f"{termo}_interesse_por_estado.csv")

# Termo a ser buscado
termo = input("Digite o termo a ser buscado no Google Trends: ")
buscar_google_trends(termo)
