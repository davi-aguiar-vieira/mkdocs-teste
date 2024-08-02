import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Função para realizar requisições com tratamento de erros
def get_cnpj_data(cnpj):
    url = f'https://api.cnpjs.dev/v1/{cnpj}'
    for _ in range(3):  # Tenta 3 vezes em caso de falha
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Limite de taxa atingido, espera 5 segundos e tenta novamente
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao solicitar dados para {cnpj}: {e}")
        time.sleep(1)  # Pausa curta entre as tentativas
    return None

# Caminho do arquivo JSON de entrada e saída
input_path = 'Dados/contratos_OFICIAL.json'
output_path = 'Dados/infos_cnpj_OFICIAL.json'

# Cache de respostas para CNPJs processados
cnpjs_processados = set()

# Função para processar um item e coletar informações
def process_item(item):
    result = []
    for chave, valor in item['Empresas Contratadas'].items():
        if chave.startswith('CNPJ') and valor not in cnpjs_processados:
            data = get_cnpj_data(valor)
            if data:
                informations = {
                    "CNPJ": data.get("cnpj"),
                    "Razão social": data.get("razao_social"),
                    "Porte": data.get("porte"),
                    "Nome Fantasia": data.get("nome_fantasia"),
                    "Situação Cadastral": data.get("situacao_cadastral"),
                    "Data da Situação Cadastral": data.get("data_situacao_cadastral"),
                    "CNAE fiscal principal": data.get("cnae_fiscal_principal"),
                    "Endereço UF": data.get("endereco", {}).get("uf"),
                    "Endereço Município": data.get("endereco", {}).get("municipio"),
                    "Data de Início da Atividade": data.get("data_inicio_atividade"),
                    "Sócios": data.get("socios")
                }
                result.append(informations)
                cnpjs_processados.add(valor)
    return result

with open(input_path, 'r', encoding='utf-8') as f_in:
    dados_json = json.load(f_in)

    with open(output_path, 'w', encoding='utf-8') as f_out:
        f_out.write('[\n')

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_item, item) for item in dados_json]
            
            for future in as_completed(futures):
                results = future.result()
                for informations in results:
                    json.dump(informations, f_out, ensure_ascii=False, indent=4)
                    f_out.write(',\n')
        
        # Remover a última vírgula e fechar o JSON corretamente
        f_out.seek(f_out.tell() - 2)
        f_out.truncate()
        f_out.write('\n]')

print("Processamento concluído")
