import requests
import pandas as pd

# URL base da OpenLigaDB para obter a classificação de um campeonato específico
BASE_URL = "https://www.openligadb.de/api/get/standings/2023/1"  # 2023 é o ano da temporada e 1 é o ID da liga do Campeonato Brasileiro

def get_standings():
    """Obtém a classificação do Campeonato Brasileiro para a temporada de 2023."""
    response = requests.get(BASE_URL)
    
    if response.status_code == 200:
        data = response.json()
        
        # Estruturando os dados
        teams_data = []
        for team in data:
            teams_data.append({
                "Posição": team["StandingNumber"],
                "Time": team["Team"]["TeamName"],
                "Pontos": team["Points"],
                "Jogos": team["MatchesPlayed"],
                "Vitórias": team["Wins"],
                "Empates": team["Draws"],
                "Derrotas": team["Losses"],
                "Gols Pró": team["GoalsFor"],
                "Gols Contra": team["GoalsAgainst"],
                "Saldo de Gols": team["GoalDifference"],
                "Ano": 2023  # Adiciona a coluna Ano
            })
        
        return pd.DataFrame(teams_data)
    else:
        print(f"[ERRO] Falha ao acessar {BASE_URL} - Status: {response.status_code}")
        return None

def save_standings_to_csv(df):
    """Salva todos os dados coletados em um único arquivo CSV."""
    file_path = "data/raw/classificacao_brasileirao_2023_openligadb.csv"
    df.to_csv(file_path, sep=';', index=False, encoding='utf-8')
    print(f"[INFO] Dados salvos em {file_path}")

# Coleta a classificação para 2023 diretamente
print(f"Coletando dados para a temporada 2023...")
df = get_standings()
if df is not None:
    save_standings_to_csv(df)
else:
    print("[INFO] Nenhum dado foi coletado para a temporada 2023.")
