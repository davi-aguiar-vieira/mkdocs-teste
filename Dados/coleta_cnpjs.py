import json
import requests
import time
from collections import defaultdict

# Cache para respostas de CNPJ
cache_cnpjs = defaultdict(dict)

# Função para realizar requisições com tratamento de erros e cache
def get_cnpj_data(cnpj):
    if cnpj in cache_cnpjs:
        return cache_cnpjs[cnpj]
    
    url = f'https://api.cnpjs.dev/v1/{cnpj}'
    for _ in range(3):  # Tenta 3 vezes em caso de falha
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                cache_cnpjs[cnpj] = data  # Armazena no cache
                return data
            elif response.status_code == 429:
                # Limite de taxa atingido, espera 5 segundos e tenta novamente
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao solicitar dados para {cnpj}: {e}")
        time.sleep(1)  # Pausa curta entre as tentativas
    return None

# Caminho do arquivo JSON de saída
output_path = 'Dados/infos_cnpj_OFICIAL.json'

# Caminho do arquivo JSON de entrada
input_path = 'Dados/contratos_OFICIAL.json'

with open(output_path, 'w', encoding='utf-8') as f_out:
    f_out.write('[\n')
    # Abre o arquivo JSON para leitura
    with open(input_path, 'r', encoding='utf-8') as f_in:
        dados_json = json.load(f_in)

        cnpjs_processados = set()

        for item in dados_json:
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
                        json.dump(informations, f_out, ensure_ascii=False, indent=4)
                        f_out.write(',\n')
                        cnpjs_processados.add(valor)

    f_out.seek(f_out.tell() - 2)
    f_out.truncate()
    f_out.write('\n]')

