# PrevisaoTempoGUI

Pipeline ETL e dashboard em Streamlit para coletar, tratar e visualizar dados meteorologicos da API OpenWeather.

## Visao Geral

O projeto conecta uma API externa, transforma dados climaticos em datasets tabulares e apresenta as informacoes em uma interface web interativa. Ele demonstra uma rotina completa de dados: ingestao, tratamento, persistencia local e visualizacao.

## Resultado

- Coleta de clima atual e previsao usando OpenWeather.
- Conversao de timestamps e padronizacao de campos.
- Persistencia em CSV para analise historica.
- Dashboard Streamlit com filtros e visualizacoes.
- Base pronta para evoluir para agendamento, banco de dados ou deploy.

## Arquitetura

```text
OpenWeather API -> etl_openweather.py -> CSV tratado -> app_streamlit.py -> Dashboard
```

## Stack

- Python
- Requests
- Pandas
- Streamlit
- Matplotlib
- python-dotenv
- API REST
- ETL

## Estrutura

```text
PrevisaoTempoGUI/
├── README.md
├── previsaotempogui/
│   ├── app_streamlit.py
│   ├── etl_openweather.py
│   ├── requirements.txt
│   ├── data/
│   └── figures/
└── .gitignore
```

## Como Executar

1. Clone o repositorio.
2. Crie um arquivo `.env` com sua chave da OpenWeather.
3. Instale as dependencias.
4. Execute o ETL.
5. Abra o dashboard Streamlit.

```bash
cd previsaotempogui
pip install -r requirements.txt
python etl_openweather.py --city "Sao Paulo, BR" --mode all
streamlit run app_streamlit.py
```

Exemplo de `.env`:

```env
OWM_API_KEY=sua_chave_aqui
LOCAL_TZ=America/Sao_Paulo
```

## Observacoes

- Nao commitar `.env`, tokens ou chaves de API.
- A pasta `venv/` deve ficar fora do repositorio.
- Arquivos gerados em `data/` e `figures/` podem ser mantidos fora do Git ou versionados apenas como amostras pequenas.

## Proximos Passos

- Remover `venv/` do historico atual do repositorio.
- Adicionar prints do dashboard no README.
- Criar agendamento do ETL.
- Salvar dados em banco relacional ou data warehouse.
- Publicar uma versao demonstrativa do dashboard.
