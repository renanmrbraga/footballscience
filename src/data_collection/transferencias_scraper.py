import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from dotenv import load_dotenv

# Carregar o arquivo .env
load_dotenv()

# Carregar a URL base e o User-Agent de forma segura
BASE_URL = os.getenv("BASE_URL")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")

# Configuração de caminhos
CLUBES_CSV = 'data/processed/clubes.csv'
SAIDA_CSV = 'data/raw/transferencias.csv'

# Configuração de delays
DELAY_MIN = 3
DELAY_MAX = 6

# Gerar temporadas de 14/15 até a atual
def gerar_temporadas():
    """Gera a lista de temporadas no formato correto."""
    return [f"{str(ano)[-2:]}/{str(ano+1)[-2:]}" for ano in range(2014, 2026)]


def carregar_clubes():
    """Carrega os dados dos clubes a partir do CSV."""
    return pd.read_csv(CLUBES_CSV, sep=';')


def extrair_transferencias(nome_clube, codigo_clube):
    """Extrai as transferências de um clube específico para as temporadas definidas."""
    dados_transferencias = []
    url = BASE_URL.format(nome_clube, codigo_clube)
    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    
    if response.status_code != 200:
        print(f"[ERRO] Falha ao acessar {url} - Status: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    boxes = soup.find_all("div", class_="box")
    
    for box in boxes:
        titulo = box.find("h2").text.strip() if box.find("h2") else ""
        
        tipo_transferencia = "Entradas" if "Arrivals" in titulo else "Saídas"
        tabela = box.find("table")
        if not tabela:
            continue
        
        temporada = titulo.split()[-1] if any(char.isdigit() for char in titulo) else "Desconhecido"
        
        for row in tabela.find("tbody").find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            
            jogador = cols[0].text.strip()
            clube_origem_destino = cols[2].text.strip()
            valor_transferencia = cols[3].text.strip()
            
            dados_transferencias.append([
                nome_clube, temporada, tipo_transferencia, jogador, clube_origem_destino, valor_transferencia
            ])
    
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    return dados_transferencias


def coletar_dados_transferencias():
    """Percorre todos os clubes do CSV e coleta as transferências."""
    clubes_df = carregar_clubes()
    dados_gerais = []
    
    for _, row in clubes_df.iterrows():
        clube_nome = row["Nome Transfermarkt"].replace(" ", "-").lower()
        codigo_clube = row["Código Transfermarkt"]
        
        print(f"[INFO] Coletando dados para {clube_nome}...")
        dados_clube = extrair_transferencias(clube_nome, codigo_clube)
        dados_gerais.extend(dados_clube)
        
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    
    return dados_gerais


def salvar_dados_transferencias(dados):
    """Salva os dados coletados em um arquivo CSV."""
    colunas = ["Clube", "Temporada", "Tipo", "Jogador", "Clube_origem_destino", "Valor"]
    df_transferencias = pd.DataFrame(dados, columns=colunas)
    df_transferencias.to_csv(SAIDA_CSV, sep=';', index=False, encoding='utf-8')
    print(f"[INFO] Scraping finalizado! Dados salvos em {SAIDA_CSV}")


if __name__ == "__main__":
    dados_coletados = coletar_dados_transferencias()
    salvar_dados_transferencias(dados_coletados)
