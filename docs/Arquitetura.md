### Introdução 
O projeto LicitaNow visa verificar e mostrar aos usuários os gastos públicos do Distrito Federal na modalidade dispensa de licitação. Tendo como objetivo apresentar, de forma organizada, quais empresas recebem mais dinheiro e quais são os órgãos públicos que gastam mais.



### Front-End

#### HTML, CSS e JavaScript:
- Estrutura e Estilo: Para criar a interface inicial do nosso projeto, utilizamos HTML para estruturar o conteúdo e CSS para estilizar os elementos. Além disso, utilizamos JavaScript para adicionar interatividade à página.
- Conteúdo Principal: O HTML define a estrutura básica da página, incluindo cabeçalho, seções de conteúdo, e rodapé. O CSS é responsável pela aparência visual, incluindo cores, espaçamentos, e fontes. O JavaScript adiciona comportamento dinâmico, como animações e reações a eventos de usuário.

#### Integração com Streamlit:
- Incorporação de HTML/CSS/JS no Streamlit: Utilizamos a biblioteca streamlit.components.v1 para incorporar o nosso código HTML, CSS e JavaScript dentro do aplicativo Streamlit. Isso nos permitiu combinar a flexibilidade do desenvolvimento web tradicional com a simplicidade e o poder do Streamlit.
- Código de Integração:

```python
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# Função para carregar o conteúdo do arquivo
def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Carregar o HTML, CSS e JavaScript
html_content = load_file('index.html')
css_content = load_file('style.css')
js_content = load_file('script.js')

# Injetar o CSS e JavaScript no HTML
html_with_css_js = f"""
    <style>
    html, body, [class*="css"]  {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
    }}
    {css_content}
    </style>
    <div style="width:100vw; height:100vh; overflow: hidden;">
        {html_content}
    </div>
    <script>
    {js_content}
    </script>
"""

# Exibir o HTML com CSS e JavaScript no Streamlit
components.html(html_with_css_js, height=1000, scrolling=True)
```