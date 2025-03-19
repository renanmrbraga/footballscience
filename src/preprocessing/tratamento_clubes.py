import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())

# Configuração dos arquivos
ARQUIVO_CLUBES_RAW = os.getenv("ARQUIVO_CLUBES_RAW")
ARQUIVO_CLUBES_PROCESSED = os.getenv("ARQUIVO_CLUBES_PROCESSED")
ARQUIVO_TRANSFERENCIAS_PROCESSED = os.getenv("ARQUIVO_TRANSFERENCIAS_PROCESSED")
ARQUIVO_BRASILEIRAO_PROCESSED = os.getenv("ARQUIVO_BRASILEIRAO_PROCESSED")
COLUNA_NOME_OFICIAL = os.getenv("COLUNA_NOME_OFICIAL")

# Carregar datasets
df_clubes = pd.read_csv(ARQUIVO_CLUBES_RAW, sep=";", encoding="utf-8")
df_transferencias = pd.read_csv(ARQUIVO_TRANSFERENCIAS_PROCESSED, sep=";", encoding="utf-8")
df_brasileirao = pd.read_csv(ARQUIVO_BRASILEIRAO_PROCESSED, sep=";", encoding="utf-8")

# Adicionar novas colunas
estatisticas = []

for idx, clube in df_clubes.iterrows():
    nome_oficial = clube[COLUNA_NOME_OFICIAL]

    # Dados do Brasileirão
    participacoes = df_brasileirao[df_brasileirao["Clube"].str.contains(nome_oficial, na=False)]
    qtd_participacoes = participacoes.shape[0]

    posicoes_count = participacoes["Posição"].value_counts().to_dict()

    rebaixamentos = participacoes[participacoes["Posição"] >= 17].shape[0]

    # Métricas históricas
    media_pontos = participacoes["Pontos"].mean() if qtd_participacoes > 0 else 0
    aproveitamento = (participacoes["Pontos"].sum() / (participacoes["Jogos"].sum() * 3) * 100
                      if participacoes["Jogos"].sum() > 0 else 0)

    ultimo_ano_serie_a = participacoes["Ano"].max() if qtd_participacoes > 0 else None

    recentes = participacoes.sort_values(by="Ano", ascending=False).head(3)
    media_recente = recentes["Pontos"].mean() if len(recentes) > 0 else 0
    posicao_media_recente = recentes["Posição"].mean() if len(recentes) > 0 else None

    # Dados financeiros
    id_clube = clube["ID"]
    transferencias_clube = df_transferencias[df_transferencias["Clube_ID"] == id_clube]

    compras = transferencias_clube[transferencias_clube["Tipo"] == "Chegada"]["Valor"].sum()
    vendas = transferencias_clube[transferencias_clube["Tipo"] == "Saída"]["Valor"].sum()
    saldo_transferencias = vendas - compras

    # Participações internacionais (top 12 colocados)
    internacionais = participacoes[participacoes["Posição"] <= 12].shape[0]

    estatisticas.append({
        "ID": id_clube,
        "Nome Oficial": nome_oficial,
        "UF": clube["UF"],  # Coluna UF incluída na 3ª posição
        "Participacoes_SerieA": qtd_participacoes,
        "Rebaixamentos": rebaixamentos,
        "Media_Pontos": round(media_pontos, 2),
        "Aproveitamento(%)": round(aproveitamento, 2),
        "Ultimo_Ano_SerieA": ultimo_ano_serie_a,
        "Media_Pontos_Ult3anos": round(media_recente, 2),
        "Posicao_Media_Ult3anos": round(posicao_media_recente, 2) if posicao_media_recente is not None else None,
        "Compras_Total_R$": round(compras, 2),
        "Vendas_Total_R$": round(vendas, 2),
        "Saldo_Transferencias_R$": round(saldo_transferencias, 2),
        "Participacoes_Internacionais": internacionais,
        **{f"Pos_{pos}": posicoes_count.get(pos, 0) for pos in range(1, 21)}
    })

# DataFrame final enriquecido
df_clubes_final = pd.DataFrame(estatisticas)

# Salvar CSV tratado
df_clubes_final.to_csv(ARQUIVO_CLUBES_PROCESSED, sep=";", index=False, encoding="utf-8-sig")

print(f"[INFO] CSV enriquecido e salvo em {ARQUIVO_CLUBES_PROCESSED}")
