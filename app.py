import mysql.connector
import xml.etree.ElementTree as ET





import xml.etree.ElementTree as ET
import mysql.connector

# Função para processar o arquivo XML
def processar_xml(filepath):
    # Carregar o arquivo XML
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Namespace do XML (extraído do exemplo que você forneceu)
    namespaces = {
        'ns': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ENHANCED_XML'
    }

    # Lista para armazenar os registros extraídos
    registros = []

    # Iterar sobre as entidades no XML
    for entity in root.findall(".//ns:entities/ns:entity", namespaces):
        # Extrair os dados principais de cada entidade
        general_info = entity.find('ns:generalInfo', namespaces)
        identity_id = general_info.find('ns:identityId', namespaces).text if general_info is not None else None
        entity_type = general_info.find('ns:entityType', namespaces).text if general_info is not None else None

        names = entity.findall('ns:names/ns:name', namespaces)
        primary_name = None
        alias_names = []

        # Procurar o nome primário e aliases
        for name in names:
            is_primary = name.find('ns:isPrimary', namespaces).text
            formatted_full_name = name.find('ns:translations/ns:translation/ns:formattedFullName', namespaces).text

            if is_primary == 'true':
                primary_name = formatted_full_name
            else:
                alias_names.append(formatted_full_name)

        # Obter informações do endereço
        addresses = entity.findall('ns:addresses/ns:address', namespaces)
        address = None
        for addr in addresses:
            country = addr.find('ns:country', namespaces).text if addr.find('ns:country', namespaces) is not None else None
            city = addr.find('ns:translations/ns:translation/ns:addressParts/ns:addressPart/ns:value', namespaces).text if addr.find('ns:translations/ns:translation/ns:addressParts/ns:addressPart/ns:value', namespaces) is not None else None
            if country and city:
                address = f"{city}, {country}"

        # Armazenar os dados extraídos em um dicionário
        registro = {
            'identity_id': identity_id,
            'entity_type': entity_type,
            'primary_name': primary_name,
            'alias_names': alias_names,
            'address': address
        }
        registros.append(registro)

    print(f"Registros encontrados: {len(registros)}")
    return registros

# Função para inserir no banco de dados MySQL
def inserir_no_banco(registros):
    # Conectar ao banco de dados MySQL
    # Configurações do banco de dados MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="phpmyadmin",
        password="Lcstanke@2018*",
        database="lista-negra"
    )
    
    cursor = conn.cursor()

    # Criar a tabela, se não existir (ajuste conforme necessário)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ofac_sdn (
            id INT AUTO_INCREMENT PRIMARY KEY,
            identity_id INT,
            entity_type VARCHAR(255),
            primary_name TEXT,
            alias_names TEXT,
            address TEXT
        )
    """)

    # Inserir os registros no banco
    for registro in registros:
        cursor.execute("""
            INSERT INTO ofac_sdn (identity_id, entity_type, primary_name, alias_names, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            registro['identity_id'],
            registro['entity_type'],
            registro['primary_name'],
            ', '.join(registro['alias_names']),  # Armazenar aliases como uma string separada por vírgulas
            registro['address']
        ))

    # Commit e fechar a conexão
    conn.commit()
    cursor.close()
    conn.close()
    print("Dados inseridos com sucesso.")

# Executar o processo
if __name__ == "__main__":
    # Caminho para o arquivo XML
    filepath = "sdn_enhanced.xml"
    
    # Processar o XML e obter os registros
    registros = processar_xml(filepath)
    
    # Inserir os registros no banco de dados
    if registros:
        inserir_no_banco(registros)
    else:
        print("Nenhum registro encontrado para inserir no banco de dados.")
