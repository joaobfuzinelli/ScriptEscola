from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import time

def obter_conteudo_pagina(url, page=None):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            if page is None:
                page = context.new_page()
            page.goto(url)
            page.wait_for_load_state('networkidle')  # Aguarda até o carregamento completo
            time.sleep(2)  # Adiciona um pequeno atraso para garantir que a página foi carregada completamente
            conteudo = page.content()
            browser.close()
            return conteudo
    except Exception as e:
        print(f"Erro ao obter conteúdo da página {url}: {e}")
        return None

def obter_links_municipios(conteudo_pagina):
    sopa = BeautifulSoup(conteudo_pagina, 'html.parser')
    links = []
    for link in sopa.select('a[href^="/municipio"]'):
        href = link.get('href')
        if href:
            links.append('https://qedu.org.br' + href)
    return links

def aplicar_filtro_privada(page):
    try:
        # Espera pelo seletor do filtro e aplica
        page.wait_for_selector('select[x-model="dependencia_id"]', timeout=10000)
        page.select_option('select[x-model="dependencia_id"]', value='4')  # Seleciona a opção "Privada"
        page.wait_for_load_state('networkidle')  # Aguarda o carregamento da página após aplicar o filtro
        time.sleep(2)  # Adiciona um pequeno atraso para garantir que a página foi carregada completamente
        print("Filtro de escola privada aplicado com sucesso.")
    except Exception as e:
        print(f"Erro ao aplicar o filtro: {e}")

def extrair_dados_escola(container):
    nome = container.select_one('h1.font-bold')
    endereco = container.select_one('p.text-gray-500')
    dependencia_e_localizacao = container.select_one('p.text-xs.font-bold')
    
    return {
        'nome': nome.get_text(strip=True) if nome else 'N/A',
        'endereco': endereco.get_text(strip=True) if endereco else 'N/A',
        'dependencia_e_localizacao': dependencia_e_localizacao.get_text(strip=True) if dependencia_e_localizacao else 'N/A',
    }

def extrair_escolas_particulares(url_municipio):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = context.new_page()
            page.goto(url_municipio)
            
            # Aplica o filtro para escolas particulares
            aplicar_filtro_privada(page)
            
            # Obtém o conteúdo da página após o filtro
            conteudo_pagina = page.content()
            browser.close()
    except Exception as e:
        print(f"Erro ao acessar a página {url_municipio}: {e}")
        return []

    sopa = BeautifulSoup(conteudo_pagina, 'html.parser')
    
    # Seletor ajustado com base na estrutura fornecida
    containers_escolas = sopa.select('a[href^="/escola/"]')

    if not containers_escolas:
        print(f"Nenhuma escola encontrada na página: {url_municipio}")

    escolas = []

    for container in containers_escolas:
        dados_escola = extrair_dados_escola(container)
        escolas.append(dados_escola)
    
    return escolas

def salvar_dados_em_csv(dados, arquivo):
    if not dados:
        print("Nenhum dado para salvar.")
        return
    
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

def main():
    url_base = 'https://qedu.org.br/uf/33-rio-de-janeiro/busca'
    conteudo_pagina = obter_conteudo_pagina(url_base)
    if not conteudo_pagina:
        print("Falha ao obter a página principal.")
        return

    links_municipios = obter_links_municipios(conteudo_pagina)

    print("Links dos Municípios:")
    for link in links_municipios:
        print(link)

    todas_as_escolas = []

    for link in links_municipios:
        print(f'Processando {link}...')
        escolas = extrair_escolas_particulares(link)
        if escolas:
            todas_as_escolas.extend(escolas)
        else:
            print(f"Sem escolas encontradas em {link}.")

    print(f'Total de escolas encontradas: {len(todas_as_escolas)}')
    
    # Salvar os dados das escolas em um arquivo CSV
    salvar_dados_em_csv(todas_as_escolas, 'dados_escolas.csv')
    print(f"Dados das escolas salvos em 'dados_escolas.csv'.")

if __name__ == '__main__':
    main()
