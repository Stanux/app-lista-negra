import xml.etree.ElementTree as ET
from collections import defaultdict

# Função para coletar e consolidar as tags internas de cada nó, considerando subnós
def consolidar_tags(elemento, caminho=""):
    # Cria um dicionário para armazenar as tags encontradas para um nó específico
    tags_internas = defaultdict(set)
    
    # Percorrer todos os subelementos do nó e adicionar as tags ao dicionário
    for sub_elemento in elemento:
        # Adiciona a tag do sub-elemento com o caminho completo
        novo_caminho = f"{caminho}.{sub_elemento.tag}" if caminho else sub_elemento.tag
        tags_internas[caminho].add(sub_elemento.tag)
        
        # Agora, recursivamente, vamos procurar as sub-tags dos sub-elementos
        tags_internas.update(consolidar_tags(sub_elemento, novo_caminho))
    
    return tags_internas

# Carregar o arquivo XML
tree = ET.parse('consolidated.xml')  # Substitua pelo caminho do seu arquivo XML
root = tree.getroot()

# Inicializa o dicionário que vai armazenar as tags consolidadas por nó
tags_consolidadas = defaultdict(set)

# Loop para encontrar as tags e consolidar as tags internas
# for individual in root.findall('INDIVIDUALS/INDIVIDUAL'):
for individual in root.findall('ENTITIES/ENTITY'):
    tags_internas = consolidar_tags(individual, "1.1 - ENTITIES")
    for caminho, tags in tags_internas.items():
        tags_consolidadas[caminho].update(tags)

# Exibir a consolidação das tags para cada nó
print("Consolidação das tags internas:")
for caminho, tags in tags_consolidadas.items():
    print(f"{caminho}")
    for tag in sorted(tags):
        print(f"  - {tag}")
