import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração dos arquivos e scraper
ARQUIVO_BRASILEIRAO_RAW = os.getenv("ARQUIVO_BRASILEIRAO_RAW")
BRASILEIRAO_SCRAPER = os.getenv("BRASILEIRAO_SCRAPER")
USER_AGENT = os.getenv("USER_AGENT")

# Configuração de tempos de espera
ATRASO_MINIMO = 3
ATRASO_MAXIMO = 6

# Número de colunas da tabela que queremos extrair (antes de adicionar a coluna "Ano")
TARGET_COLS = 10  # Queremos as 10 primeiras colunas

def configurar_driver():
    """Configura e retorna um WebDriver para automação do navegador."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extrair_tabela(driver, ano):
    """
    Acessa a página para o ano informado e extrai a tabela de classificação.
    Se a coluna "Classificação ou descenso" existir, ela é removida.
    São extraídas exatamente as primeiras TARGET_COLS colunas da tabela.
    Ao final, é adicionada a coluna "Ano".
    Retorna (headers, rows).
    """
    url = BRASILEIRAO_SCRAPER.format(ano)
    print(f"[INFO] Acessando URL: {url}")
    driver.get(url)
    time.sleep(random.uniform(ATRASO_MINIMO, ATRASO_MAXIMO))
    soup = BeautifulSoup(driver.page_source, "html.parser")

    secao_classificacao = soup.find("h2", id="Classificação")
    if not secao_classificacao:
        print(f"[ALERTA] Seção 'Classificação' não encontrada para o ano {ano}")
        return None, []

    tabela = secao_classificacao.find_next("table", {"class": "wikitable"})
    if not tabela:
        print(f"[ALERTA] Tabela de classificação não encontrada para o ano {ano}")
        return None, []

    header_row = tabela.find("tr")
    raw_headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

    # Se a coluna indesejada estiver presente, guarda seu índice e remove-a
    index_classificacao = raw_headers.index("Classificação ou descenso") if "Classificação ou descenso" in raw_headers else None
    if index_classificacao is not None:
        raw_headers.pop(index_classificacao)
        print(f"[INFO] Removendo a coluna 'Classificação ou descenso' dos cabeçalhos para o ano {ano}.")

    # Força a pegar somente as primeiras TARGET_COLS colunas e adiciona "Ano"
    headers = raw_headers[:TARGET_COLS] + ["Ano"]

    rows = []
    for row in tabela.find_all("tr")[1:]:
        raw_cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        # Se a coluna indesejada existia, remove a célula correspondente (se houver)
        if index_classificacao is not None and len(raw_cells) > index_classificacao:
            raw_cells.pop(index_classificacao)
        # Garante que pegamos somente as primeiras TARGET_COLS células
        row_cells = raw_cells[:TARGET_COLS]
        # Se houver menos células, preenche com vazio
        if len(row_cells) < TARGET_COLS:
            row_cells += [""] * (TARGET_COLS - len(row_cells))
        # Adiciona o ano
        row_cells.append(str(ano))
        rows.append(row_cells)

    print(f"[INFO] Extraído {len(rows)} linhas para o ano {ano}")
    return headers, rows

def coletar_dados():
    """
    Itera de 2015 a 2024, extraindo a tabela de cada ano e acumulando os dados.
    Retorna (header_final, dados_gerais).
    """
    driver = configurar_driver()
    dados_gerais = []
    header_final = None

    for ano in range(2015, 2025):
        headers, rows = extrair_tabela(driver, ano)
        if rows:
            if header_final is None:
                header_final = headers
            dados_gerais.extend(rows)
        else:
            print(f"[ALERTA] Nenhum dado encontrado para o ano {ano}")
        time.sleep(random.uniform(ATRASO_MINIMO, ATRASO_MAXIMO))
    driver.quit()
    return header_final, dados_gerais

def corrigir_saldo_gols(valor):
    """
    Corrige os valores de saldo de gols (SG), garantindo que os números negativos sejam mantidos.
    """
    if isinstance(valor, str):
        valor = valor.replace("−", "-").replace("+", "").strip()
        valor_corrigido = re.sub(r"[^\d-]", "", valor)
        return valor_corrigido if valor_corrigido else "0"
    return "0"

def salvar_dados(headers, dados):
    """Salva os dados extraídos em um arquivo CSV formatado."""
    if not dados:
        print("[ERRO] Nenhum dado extraído!")
        return
    df = pd.DataFrame(dados, columns=headers)
    df.sort_values(by=["Ano"], inplace=True)
    df.to_csv(ARQUIVO_BRASILEIRAO_RAW, sep=";", index=False, encoding="utf-8")
    print(f"[INFO] Dados corrigidos e salvos em {ARQUIVO_BRASILEIRAO_RAW}")

if __name__ == "__main__":
    header_final, dados = coletar_dados()
    salvar_dados(header_final, dados)
