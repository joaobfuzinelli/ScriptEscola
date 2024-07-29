from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def obter_conteudo_pagina(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()
        page.goto(url)
        page.wait_for_load_state('networkidle')  # Aguarda até o carregamento completo
        conteudo = page.content()
        browser.close()
        return conteudo

def obter_links_municipios(conteudo_pagina):
    sopa = BeautifulSoup(conteudo_pagina, 'html.parser')
    links = []
    for link in sopa.select('a[href^="/municipio"]'):
        href = link.get('href')
        if href:
            links.append('https://qedu.org.br' + href)
    return links

def extrair_escolas_particulares(url_municipio):
    conteudo_pagina = obter_conteudo_pagina(url_municipio)
    sopa = BeautifulSoup(conteudo_pagina, 'html.parser')
    
    # Seletor ajustado com base na estrutura fornecida
    containers_escolas = sopa.select('div.border.bg-white.border-gray-200.rounded-xl')

    escolas = []

    for container in containers_escolas:
        nome = container.select_one('a')  # Ajuste conforme necessário
        endereco = container.select_one('div.flex.flex-row.justify-start.items-center')
        
        if nome and endereco:
            escolas.append({
                'nome': nome.get_text(strip=True),
                'endereco': endereco.get_text(strip=True)
            })
    return escolas

def main():
    url_base = 'https://qedu.org.br/uf/33-rio-de-janeiro/busca'
    conteudo_pagina = obter_conteudo_pagina(url_base)
    links_municipios = obter_links_municipios(conteudo_pagina)

    print("Links dos Municípios:")
    for link in links_municipios:
        print(link)

    todas_as_escolas = []

    for link in links_municipios:
        print(f'Processando {link}...')
        escolas = extrair_escolas_particulares(link)
        todas_as_escolas.extend(escolas)

    print(f'Total de escolas encontradas: {len(todas_as_escolas)}')
    for escola in todas_as_escolas:
        print(f"Nome: {escola['nome']}, Endereço: {escola['endereco']}")

if __name__ == '__main__':
    main()
