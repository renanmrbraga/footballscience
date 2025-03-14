# Informações do sistema
APP_NAME="API FUTEBOL BRASILEIRO"

# Tipo de Ambientes: ['local', 'development', 'staging', 'production']
APP_ENV=production

# Hash app key (Importante para a segurança do Laravel)
APP_KEY=

# Debug (Permanecer *false* enquanto *production* para evitar exposição de erros)
APP_DEBUG=false

# Adicionar URL do próprio sistema (Default: "http://127.0.0.1:8000")
APP_URL="http://127.0.0.1:8000"

# URL do site referência de dados
URL_SITE_BRASILEIRAO="https://www.terra.com.br/esportes/futebol/brasileiro-serie-a/tabela/"
URL_JOGOS_BRASILEIRAO="https://p1.trrsf.com/api/musa-soccer/ms-standings-games-light?idChampionship=1376&idPhase=&language=pt-BR&country=BR&nav=N&timezone=BR"
URL_DETALHES_JOGOS_BRASILEIRAO="https://www.terra.com.br/esportes/futebol/brasileiro-serie-a/ao-vivo"
URL_JSON_ESTATISTICA_JOGO="https://p1.trrsf.com/api/musa-api/matches-get?lang=pt-BR&type=json&full=true&id="

# Níveis de Log
LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

# Conexão Banco de Dados (PRODUÇÃO) - Mantém comentado caso precise no futuro
# DB_CONNECTION=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_DATABASE="api-futebol"
# DB_USERNAME=
# DB_PASSWORD=

# Conexão Banco de Dados (DESENVOLVIMENTO)
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=footballscience
DB_USERNAME=renanmrbraga
DB_PASSWORD=fuz886062***

# Serviço do E-mail (Configurar o de sua preferência)
MAIL_MAILER=smtp
MAIL_HOST=mailhog
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS=null
MAIL_FROM_NAME="${APP_NAME}"

