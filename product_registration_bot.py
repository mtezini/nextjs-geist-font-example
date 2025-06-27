import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright

CONFIG_FILE = "config.json"
EXCEL_FILE = "produtos.xlsx"

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def login(page, username, password):
    logging.info("Navigating to login page")
    await page.goto("http://erp.waychef.com.br/")
    await page.fill('input[placeholder="Login"]', username)
    await page.fill('input[placeholder="Senha"]', password)
    await page.click('text=ENTRAR', timeout=60000)
    await page.wait_for_load_state('networkidle')

async def navigate_to_product_registration(page):
    logging.info("Navigating to product registration")
    # Click menu Produto
    await page.click('text=Produto', timeout=60000)
    # Click submenu Cadastro
    await page.click('text=Cadastro', timeout=60000)
    # Click Novo
    await page.click('text=Novo', timeout=60000)

async def search_or_create_group(page, group_name):
    logging.info(f"Searching or creating group: {group_name}")
    # Click lupa (magnifying glass) to search group
    await page.click('css=button[title="Pesquisar grupo"]', timeout=60000)  # Adjust selector as needed
    await page.wait_for_selector('css=div.group-search-results', timeout=60000)  # Adjust selector as needed

    # Check if group exists in search results
    group_exists = await page.locator(f'text="{group_name}"').count() > 0
    if group_exists:
        # Select the group and click selecionar
        await page.click(f'text="{group_name}"', timeout=60000)
        await page.click('text=Selecionar', timeout=60000)
    else:
        # Click novo grupo
        await page.click('text=Novo grupo', timeout=60000)
        # Fill group name
        await page.fill('input[name="Nome do grupo"]', group_name)  # Adjust selector as needed
        # Click gravar
        await page.click('text=Gravar', timeout=60000)

async def register_product(page, product):
    logging.info(f"Registering product: {product['descricao']}")
    await navigate_to_product_registration(page)

    # Fill product code
    await page.fill('input[name="codigoProduto"]', str(product['codigoProduto']), timeout=60000)
    # Fill description
    await page.fill('input[name="descricao"]', product['descricao'], timeout=60000)
    # Fill abbreviated description (limit to 29 chars)
    abbreviated = product['descricaoAbreviada'][:29]
    await page.fill('input[name="descricaoAbreviada"]', abbreviated, timeout=60000)

    # Search or create group
    await search_or_create_group(page, product['nome do grupo'])

    # Fill sale price
    await page.fill('input[name="preco_vendaa"]', str(product['preco_venda']), timeout=60000)

    # Click gravar to save product
    await page.click('text=GRAVAR', timeout=60000)

async def main():
    # Load config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    username = config.get('username')
    password = config.get('password')

    # Load Excel data
    df = pd.read_excel(EXCEL_FILE)
    print("Colunas do DataFrame:", df.columns.tolist())  # Adicionado para debug das colunas

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        page = await browser.new_page()

        await login(page, username, password)

        for _, product in df.iterrows():
            try:
                await register_product(page, product)
            except KeyError as e:
                logging.error(f"Chave ausente no produto: {e}")
                continue

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
