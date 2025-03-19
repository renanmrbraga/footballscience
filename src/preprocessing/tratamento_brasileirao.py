import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de ambiente
load_dotenv(find_dotenv())

# Configuração dos arquivos
ARQUIVO_BRASILEIRAO_RAW = os.getenv("ARQUIVO_BRASILEIRAO_RAW")      # CSV de entrada
ARQUIVO_BRASILEIRAO_PROCESSED = os.getenv("ARQUIVO_BRASILEIRAO_PROCESSED")  # CSV de saída

# Carregar o CSV com o separador correto
df = pd.read_csv(ARQUIVO_BRASILEIRAO_RAW, sep=";", encoding="utf-8")

# Remover "(C)" do nome dos clubes
df["Equipevde"] = df["Equipevde"].str.replace(r"\(C\)", "", regex=True).str.strip()

# Tratamento das colunas numéricas:
# Para a coluna SG, removemos espaços, substituímos o traço especial por traço normal e removemos o sinal "+"
df["SG"] = df["SG"].astype(str).str.strip()\
    .str.replace("−", "-", regex=False)\
    .str.replace("+", "", regex=False)

# Lista das colunas que devem ser convertidas para inteiro
cols_to_convert = ["Pos", "Pts", "J", "V", "E", "D", "GP", "GC", "SG", "Ano"]

# Converter as colunas para int (valores não convertíveis virão como 0)
for col in cols_to_convert:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# Renomear as colunas conforme o padrão desejado
df.rename(columns={
    "Pos": "Posição",
    "Equipevde": "Clube",
    "Pts": "Pontos",
    "J": "Jogos",
    "V": "Vitórias",
    "E": "Empates",
    "D": "Derrotas",
    "GP": "GP",
    "GC": "GC",
    "SG": "SG",
    "Ano": "Ano"
}, inplace=True)

# Adicionar a coluna "ID" como a primeira coluna (sequencial, iniciando em 1)
df.insert(0, "ID", range(1, len(df) + 1))

# Verificar o resultado
print(df.info())
print(df.head())

# Salvar o CSV tratado
df.to_csv(ARQUIVO_BRASILEIRAO_PROCESSED, sep=";", index=False, encoding="utf-8")
print(f"[INFO] Dados corrigidos e salvos em {ARQUIVO_BRASILEIRAO_PROCESSED}")
