import requests
import json
import logging

# Configure logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_resultados(session, contrato):
    empresasContratadas = {}

    try:
        codigo = contrato['numeroControlePNCP'].split('-')[0]
        ano = contrato['anoCompra']
        sequencial = contrato['numeroControlePNCP'].split('-')[2].split('/')[0]

        link_nItem = f'https://pncp.gov.br/api/pncp/v1/orgaos/{codigo}/compras/{ano}/{sequencial}/itens/quantidade'
        requestItem = session.get(link_nItem, headers={'accept': '*/*'})
        if requestItem.status_code == 200:
            try:
                nItens = requestItem.json()
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from {link_nItem}")
                return None

            if nItens != 0:
                for i in range(1, nItens + 1):
                    url = f'https://pncp.gov.br/api/pncp/v1/orgaos/{codigo}/compras/{ano}/{sequencial}/itens/{i}/resultados'
                    response = session.get(url, headers={'accept': '*/*'})

                    url_descricao = f'https://pncp.gov.br/api/pncp/v1/orgaos/{codigo}/compras/{ano}/{sequencial}/itens/{i}'
                    request_descricao = session.get(url_descricao, headers={'accept': '*/*'})

                    if response.status_code == 200 and request_descricao.status_code == 200:
                        try:
                            data = response.json()
                            data_descricao = request_descricao.json()
                        except json.JSONDecodeError:
                            logging.error(f"Error decoding JSON from {url} or {url_descricao}")
                            return None

                        if data:
                            resultadoItem = data[0]
                            empresasContratadas[f'Empresa Contratada -{i}'] = resultadoItem['nomeRazaoSocialFornecedor']
                            empresasContratadas[f'CNPJ -{i}'] = resultadoItem["niFornecedor"]
                            empresasContratadas[f'Valor Recebido -{i}'] = resultadoItem["valorTotalHomologado"]
                            empresasContratadas[f'Descrição -{i}'] = data_descricao["descricao"]
                    else:
                        logging.warning(f"Failed request for item {i}: {response.status_code} or {request_descricao.status_code}")
                        return None

        return empresasContratadas if empresasContratadas else None

    except Exception as e:
        logging.error(f"Error in get_resultados: {e}")
        return None

def main():
    pag = 1
    diaDt = 2
    anoDt = 2021
    ano_Dt = 2022
    mes = 1

    dtInicial = f'{anoDt}0{mes}0{diaDt}'
    dtFinal = f'{ano_Dt}0{mes}0{diaDt-1}'

    with open('contratos_OFICIAL.json', 'w', encoding='utf-8') as f:
        f.write('[\n')

        with requests.Session() as session:
            while ano_Dt <= 2025:
                url = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao'
                params = {
                    'dataInicial': dtInicial,
                    'dataFinal': dtFinal,
                    'codigoModalidadeContratacao': '8',
                    'uf': 'df',
                    'pagina': str(pag)
                }

                response = session.get(url, params=params)
                if response.status_code == 200:
                    try:
                        dados = response.json()
                    except json.JSONDecodeError:
                        logging.error(f"Error decoding JSON from {url} with params {params}")
                        break

                    for contrato in dados['data']:
                        if contrato['valorTotalHomologado'] is not None:
                            empresasContratadas = get_resultados(session, contrato)
                            if empresasContratadas:
                                contrato_data = {
                                    "Modalidade": contrato["modalidadeNome"],
                                    "Código": contrato["numeroControlePNCP"],
                                    "UF": contrato["unidadeOrgao"]["ufNome"],
                                    "Órgão Entidade": contrato['orgaoEntidade']['razaoSocial'],
                                    "Objeto da Compra": contrato['objetoCompra'],
                                    "Ano da Compra": contrato['anoCompra'],
                                    "Valor Total Estimado": contrato['valorTotalEstimado'],
                                    "Valor Total Homologado": contrato['valorTotalHomologado'],
                                    "Empresas Contratadas": empresasContratadas
                                }
                                numeroControlePNCP = contrato["numeroControlePNCP"]
                                logging.info(f"Processing contrato: {numeroControlePNCP}")
                                json.dump(contrato_data, f, ensure_ascii=False, indent=4)
                                f.write(',\n')

                    pag += 1
                else:
                    logging.warning(f"Failed request to {url} with params {params}, status code: {response.status_code}")
                    pag = 1
                    anoDt = ano_Dt
                    ano_Dt += 1
                    dtInicial = f'{anoDt}0{mes}0{diaDt}'
                    dtFinal = f'{ano_Dt}0{mes}0{diaDt-1}'

        f.seek(f.tell() - 3)
        f.truncate()
        f.write('\n]')

if __name__ == "__main__":
    main()
