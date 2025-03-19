import os
import time
import random
import pandas as pd
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup

# Carrega as variáveis de ambiente
load_dotenv(find_dotenv())

# Configuração de caminhos para os arquivos de entrada e saída
ARQUIVO_CLUBES_RAW = os.getenv("ARQUIVO_CLUBES_RAW")  # Arquivo CSV de entrada com os times
ARQUIVO_TRANSFERENCIAS_RAW= os.getenv("ARQUIVO_TRANSFERENCIAS_RAW")  # CSV com as transferências extraídas

# Nomes das colunas no CSV de entrada
COLUNA_ID = os.getenv("COLUNA_ID")  # ID do clube
COLUNA_NOME = os.getenv("COLUNA_NOME_TRANSFER")  # Nome do clube
COLUNA_CODIGO = os.getenv("COLUNA_CODIGO_TRANSFER")  # Código identificador do clube

# URL Base para acessar os dados
TRANSFERENCIAS_SCRAPER = os.getenv("TRANSFERENCIAS_SCRAPER")
USER_AGENT = os.getenv("USER_AGENT")  # Agente de usuário para evitar bloqueios automáticos

# Configuração de tempos de espera para evitar bloqueios e garantir carregamento da página
ATRASO_MINIMO = 3  # Tempo mínimo de espera entre requisições
ATRASO_MAXIMO = 6  # Tempo máximo de espera entre requisições

# Obtém a temporada atual automaticamente
ano_atual = datetime.now().year
temporada_atual = f"{str(ano_atual)[-2:]}/{str(ano_atual + 1)[-2:]}"  # Exemplo: "23/24"

# Configuração do WebDriver para automação do navegador
def configurar_driver():
    """
    Configura e retorna um WebDriver para controle do navegador.
    """
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Desativa GPU para melhorar desempenho
    chrome_options.add_argument("--no-sandbox")  # Evita restrições ao rodar o Chrome no modo root
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita o uso excessivo de memória
    chrome_options.add_argument("--headless")  # Executa o navegador sem abrir interface gráfica
    chrome_options.add_argument(f"user-agent={USER_AGENT}")  # Define um agente de usuário para evitar bloqueios

    # Configuração para evitar pop-ups e notificações
    chrome_prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.popups": 2,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    # Instala e inicializa o WebDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Fechar popups e notificações caso existam na página
def fechar_popup(driver):
    """
    Fecha pop-ups de cookies e notificações caso apareçam na página.
    """
    try:
        time.sleep(random.uniform(ATRASO_MINIMO, ATRASO_MAXIMO))  # Aguarda para evitar detecção como bot

        popups = [
            ("//button[contains(text(), 'Aceitar') or contains(text(), 'Accept')]", "[INFO] Popup de cookies fechado!"),
            ("//button[contains(text(), 'Bloquear') or contains(text(), 'Block')]", "[INFO] Popup de notificações bloqueado!")
        ]

        for xpath, message in popups:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(message)
            except:
                pass  # Se não encontrar o botão, ignora

    except Exception as e:
        print(f"[INFO] Erro ao tentar fechar popups: {e}")

# Função para verificar se a temporada está no intervalo permitido
def temporada_valida(season):
    """ Retorna True se a temporada estiver entre 14/15 e a atual """
    if re.match(r"^\d{2}/\d{2}$", season):
        ano_inicio, ano_fim = map(int, season.split('/'))
        return (14 <= ano_inicio <= int(temporada_atual.split('/')[0])) and (ano_fim == ano_inicio + 1)
    elif re.match(r"^\d{4}$", season):  # Garante que temporadas completas (ex: 2024) sejam convertidas corretamente
        return 2014 <= int(season) <= ano_atual
    return False

# Extração de transferências com filtro por temporada
def extrair_transferencias(driver, nome_clube, codigo_clube, nome_oficial):
    """
    Extrai as transferências de jogadores para um clube específico,
    incluindo a coluna de Tipo (Entrada/Saída) e o ID do Clube.
    """
    dados_transferencias = []
    url_formatada = TRANSFERENCIAS_SCRAPER.format(nome_clube, codigo_clube)

    try:
        print(f"[INFO] Acessando URL: {url_formatada}")
        driver.get(url_formatada)
        fechar_popup(driver)  # Fecha pop-ups antes de continuar

        time.sleep(random.uniform(ATRASO_MINIMO, ATRASO_MAXIMO))  # Aguarda o carregamento da página

        # Captura o código HTML da página
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Encontra todas as seções de transferências
        sections = soup.find_all("h2", class_="content-box-headline")

        for section in sections:
            season = section.text.strip().replace("Arrivals ", "").replace("Departures ", "")

            # Define se é entrada ou saída com base no título
            tipo_transferencia = "Entrada" if "Arrivals" in section.text else "Saída"

            # Verifica se a temporada está no intervalo válido
            if not temporada_valida(season):
                print(f"[ALERTA] Temporada fora do intervalo permitido: {season}, ignorando essa seção.")
                continue  # Ignora temporadas inválidas ou fora do intervalo

            table = section.find_next("table")  # Localiza a tabela de transferências

            if not table:
                continue  # Se a tabela não for encontrada, ignora a seção

            rows = table.find("tbody").find_all("tr")  # Encontra todas as linhas de jogadores

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue  # Se não houver colunas suficientes, ignora a linha

                player = cols[0].text.strip()  # Nome do jogador
                club = cols[2].text.strip()  # Clube de origem/destino
                transfer_sum_raw = cols[3].text.strip()  # Valor da transferência

                # Corrige valores inconsistentes
                transfer_sum = (
                    transfer_sum_raw.replace("Loan fee:\n", "").strip()
                    if "Loan fee" in transfer_sum_raw else transfer_sum_raw or "Unknown"
                )

                # Adiciona os dados à lista, incluindo o tipo de transferência e ID do clube
                dados_transferencias.append([season, nome_oficial, tipo_transferencia, player, club, transfer_sum])

                print(f"[DEBUG] {season} | {nome_oficial} | {tipo_transferencia} | {player} -> {club} ({transfer_sum})")

    except Exception as e:
        print(f"[ERRO] Falha ao acessar {url_formatada}: {e}")

    return dados_transferencias

# Função para coletar os dados de todos os clubes
def coletar_dados():
    """
    Coleta as transferências de todos os clubes listados no arquivo de entrada.
    """
    df = pd.read_csv(ARQUIVO_CLUBES_RAW, sep=';', dtype=str).fillna("")
    driver = configurar_driver()
    dados_gerais = []

    for _, row in df.iterrows():
        clube_nome = row[COLUNA_NOME].strip().replace(" ", "-").lower()  # Formata o nome do clube
        codigo_clube = row[COLUNA_CODIGO].strip()
        nome_oficial = row[COLUNA_ID].strip()

        print(f"[INFO] Coletando {nome_oficial}...")
        dados_clube = extrair_transferencias(driver, clube_nome, codigo_clube, nome_oficial)

        if not dados_clube:
            print(f"[ALERTA] Nenhum dado encontrado para {nome_oficial}.")

        dados_gerais.extend(dados_clube)
        time.sleep(random.uniform(ATRASO_MINIMO, ATRASO_MAXIMO))

    driver.quit()
    return dados_gerais

# Salvar os dados extraídos em um arquivo CSV
def salvar_dados(dados):
    """
    Salva os dados extraídos em um arquivo CSV formatado.
    """
    colunas = ["Temporada", "Clube_ID", "Tipo", "Player", "Origem_Destino", "Valor"]
    df = pd.DataFrame(dados, columns=colunas)

    if df.empty:
        print("[ERRO] Nenhuma transferência encontrada!")
        return

    # Ordenação por temporada e jogador
    df.sort_values(by=["Season", "Player"], inplace=True)

    df.to_csv(ARQUIVO_TRANSFERENCIAS_RAW, sep=';', index=False, encoding='utf-8')
    print(f"[INFO] Dados salvos em {ARQUIVO_TRANSFERENCIAS_RAW}")

# Execução do script
if __name__ == "__main__":
    dados = coletar_dados()
    salvar_dados(dados)
