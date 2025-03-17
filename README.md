# Football Science

Aplicação de técnicas de Machine Learning para prever o sucesso futuro dos clubes, levando em conta gastos, dívidas e estatísticas de jogadores. Este projeto abrange todo o ciclo de Ciência de Dados – da coleta à avaliação –, utilizando bibliotecas avançadas para extrair insights acionáveis.

## Funcionalidades

- **Coleta e Limpeza de Dados:** Extração de dados de diversas fontes e aplicação de um rigoroso processo de limpeza para garantir qualidade.
- **Modelagem Preditiva:** Implementação de múltiplos algoritmos (scikit-learn, TensorFlow, Keras, XGBoost, LightGBM, CatBoost) para prever o desempenho dos clubes.
- **Avaliação e Validação:** Comparação crítica dos modelos utilizando métricas robustas, assegurando a confiabilidade dos resultados.
- **Visualização e Relatórios:** Criação de gráficos e dashboards que facilitam a interpretação e a tomada de decisão com base nos dados.

## Tecnologias Utilizadas

- **Linguagem:** Python
- **Machine Learning:** scikit-learn, TensorFlow, Keras, XGBoost, LightGBM, CatBoost
- **Manipulação de Dados:** Pandas, NumPy
- **Visualização:** Matplotlib, Seaborn

## Estrutura do Projeto

```
footballscience/
│
├── data/            # Dados brutos e processados
├── notebooks/       # Notebooks de análise, experimentos e visualizações
├── src/             # Código-fonte dos modelos, pipelines e scripts auxiliares
├── tests/           # Arquivos de testes
└── README.md        # Este arquivo
```

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/renanmrbraga/footballscience.git
   ```
2. **Entre no diretório do projeto:**
   ```bash
   cd footballscience
   ```
3. **Crie e ative um ambiente virtual (recomendado):**
   - Linux/macOS:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

## Uso

- **Execução Completa do Pipeline:**
  ```bash
  python src/main.py
  ```
- **Análises Específicas:**
  Explore os notebooks na pasta `notebooks` para testar etapas individuais ou para aprofundar a análise dos dados.

## Contribuição

Se quiser contribuir para este projeto, siga os passos:
1. **Fork** o repositório
2. Crie uma **branch** para sua funcionalidade (`git checkout -b minha-feature`)
3. Commit suas mudanças (`git commit -m 'Adicionando nova feature'`)
4. Faça **push** para a branch (`git push origin minha-feature`)
5. Abra um **Pull Request**

## Licença

Este projeto está licenciado sob a Licença MIT – consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
