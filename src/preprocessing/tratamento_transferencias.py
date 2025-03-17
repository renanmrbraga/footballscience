import pandas as pd
import os
import re
from dotenv import load_dotenv  # Carregamento de variáveis de ambiente

# Obtém o diretório do env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório do script atual
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")  # Caminho para o .env

# Carrega o .env do caminho correto
load_dotenv(ENV_PATH)

# 🔹 Configuração dos arquivos
ARQUIVO_TRANSFERENCIAS_RAW = os.getenv("ARQUIVO_TRANSFERENCIAS_RAW")  # CSV com as transferências extraídas
ARQUIVO_TRANSFERENCIAS_PROCESSED = os.getenv("ARQUIVO_TRANSFERENCIAS_PROCESSED")  # Caminho de saída do CSV tratado

# 🔹 Verificação se os arquivos foram carregados corretamente
if not ARQUIVO_TRANSFERENCIAS_RAW or not ARQUIVO_TRANSFERENCIAS_PROCESSED:
    raise ValueError("[ERRO] Um ou mais caminhos de arquivo não foram carregados corretamente. Verifique o .env.")

# 🔹 Carregar os dados de transferências
df_transferencias = pd.read_csv(ARQUIVO_TRANSFERENCIAS_RAW, sep=';', dtype=str)

# 🔹 Identificar se a transferência foi um empréstimo
df_transferencias["Empréstimo"] = df_transferencias["Transfer Sum"].apply(
    lambda x: "Sim" if "loan" in str(x).lower() or "end of loan" in str(x).lower() else "Não"
)

# 🔹 Função para limpar e converter valores corretamente para float
def limpar_valor(transfer_sum):
    if pd.isna(transfer_sum) or transfer_sum.strip() == "-" or transfer_sum.lower() in ["unknown", "end of loan"]:
        return 0.0  # Se não houver valor, define como 0.0

    # Extrai apenas números e abreviações (m para milhões, k para milhares)
    match = re.match(r"€?([\d,.]+)([mk]?)", transfer_sum.lower().replace(",", "."))
    if match:
        valor, multiplicador = match.groups()
        try:
            valor_float = float(valor)  # Converte a parte numérica para float

            # Ajusta o valor conforme o multiplicador (milhões ou milhares)
            if multiplicador == "m":
                return valor_float * 1_000_000
            elif multiplicador == "k":
                return valor_float * 1_000
            else:
                return valor_float  # Valor normal sem multiplicador
        except ValueError:
            return 0.0  # Caso não consiga converter

    return 0.0  # Se não conseguiu processar corretamente

# 🔹 Aplicar a conversão correta dos valores
df_transferencias["Valor"] = df_transferencias["Transfer Sum"].apply(limpar_valor)

# 🔹 Função para converter a temporada (ex: "14/15" → 2015, "15/16" → 2016)
def converter_temporada(temporada):
    match = re.match(r"(\d{2})/(\d{2})", str(temporada))
    if match:
        _, ano_final = match.groups()
        return int(f"20{ano_final}")  # Pega o segundo ano como referência (ex: "15" → 2015)
    return None  # Retorna None se o formato estiver incorreto

# 🔹 Aplicar a conversão de temporada
df_transferencias["Ano"] = df_transferencias["Temporada"].apply(converter_temporada)

# 🔹 Criar DataFrame com as colunas desejadas
df_tratado = df_transferencias[["Clube_ID", "Tipo", "Origem_Destino", "Valor", "Empréstimo", "Ano"]].copy()

# 🔹 Criar a coluna de ID sequencial (começando em 1)
df_tratado.insert(0, "ID", range(1, len(df_tratado) + 1))

# 🔹 Salvar o CSV tratado com valores corretamente formatados
df_tratado.to_csv(ARQUIVO_TRANSFERENCIAS_PROCESSED, sep=";", index=False, encoding="utf-8-sig", float_format="%.2f")

print(f"[INFO] Transferências tratadas salvas em {ARQUIVO_TRANSFERENCIAS_PROCESSED}")
