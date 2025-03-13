import pandas as pd
import numpy as np

# Caminho dos arquivos
ARQUIVO_ENTRADA = 'data/raw/transferencias.csv'
ARQUIVO_CLUBES = 'data/processed/clubes.csv'
ARQUIVO_SAIDA = 'data/processed/transferencias_tratadas.csv'

# Carregar os dados
transferencias = pd.read_csv(ARQUIVO_ENTRADA, sep=';')
clubes = pd.read_csv(ARQUIVO_CLUBES, sep=';')

# Remover duplicatas
transferencias.drop_duplicates(inplace=True)

# Substituir valores não definidos por NaN
transferencias.replace({'-': np.nan, '?': np.nan}, inplace=True)

# Criar coluna "Tipo de Transação"
def definir_tipo_transacao(tipo, valor):
    palavras_emprestimo = ["loan transfer", "End of loan", "Loan fee"]
    if any(palavra in str(tipo) for palavra in palavras_emprestimo) or "Loan fee" in str(valor):
        return "Empréstimo"
    return "Definitivo"

transferencias['Tipo de Transação'] = transferencias.apply(lambda row: definir_tipo_transacao(row['Tipo'], row['Valor']), axis=1)

# Converter valores monetários
def converter_valor(valor):
    if pd.isna(valor) or "End of loan" in str(valor) or "loan transfer" in str(valor):
        return np.nan
    valor = valor.replace('€', '').replace('m', '000000').replace('k', '000')
    valor = valor.replace('Loan fee:', '').strip()
    try:
        return float(valor)
    except ValueError:
        return np.nan

transferencias['Valor'] = transferencias['Valor'].astype(str).apply(converter_valor)

# Filtrar apenas as temporadas de 2015 até o ano atual
ano_atual = pd.to_datetime('today').year
ano_limite = 2015

def extrair_ano(temporada):
    if isinstance(temporada, str):
        if '/' in temporada:  # Temporadas no formato "xx/yy"
            ano = int("20" + temporada.split('/')[0]) if int(temporada.split('/')[0]) >= 15 else int("19" + temporada.split('/')[0])
            return ano
        elif temporada.isdigit():  # Anos completos antes de 1930
            return int(temporada)
    return None

transferencias['Ano Inicial'] = transferencias['Temporada'].apply(extrair_ano)
transferencias = transferencias[(transferencias['Ano Inicial'] >= ano_limite) & (transferencias['Ano Inicial'] <= ano_atual)]
transferencias.drop(columns=['Ano Inicial'], inplace=True)

# Substituir a coluna "Clube" pelo nome oficial
clubes_dict = clubes.set_index('Nome Transfermarkt')['Nome Oficial'].to_dict()
transferencias['Clube'] = transferencias['Clube'].map(clubes_dict)

# Ordenar os dados por temporada e tipo
transferencias.sort_values(by=['Temporada', 'Tipo'], ascending=[False, True], inplace=True)

# Salvar os dados tratados
transferencias.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8')

print(f"[INFO] Tratamento finalizado! Dados salvos em {ARQUIVO_SAIDA}")
