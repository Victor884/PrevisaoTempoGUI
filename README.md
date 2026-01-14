# 🌤️ PrevisaoTempoGUI

Um aplicativo moderno para consultar dados meteorológicos em tempo real usando a API OpenWeather com uma interface web interativa construída com Streamlit.

## 📋 Sobre o Projeto

PrevisaoTempoGUI é uma solução completa para obtenção e visualização de dados climáticos. O projeto é composto por:

- **ETL (Extract, Transform, Load)**: Pipeline robusto que coleta dados da API OpenWeather One Call API
- **Dashboard Interativo**: Interface web desenvolvida com Streamlit para visualização de dados climáticos
- **Armazenamento de Dados**: Persistência em CSV para consultas históricas

## ✨ Funcionalidades

### 🔄 ETL - Coleta de Dados
- Busca dados de clima atual (Current Weather)
- Coleta previsões por hora (One Call Hourly)
- Coleta previsões em 5 dias (One Call Daily)
- Tratamento robusto de erros e retry automático
- Suporte a múltiplas cidades
- Conversão automática de timezones

### 📊 Dashboard Streamlit
- **Aba Atual**: Visualização da leitura meteorológica mais recente
- **Aba Previsão 5 dias**: 
  - Gráfico de linha com evolução da temperatura
  - Gráfico de barras com precipitação
  - Tabela completa com todos os dados
- Filtro dinâmico por cidade
- Interface responsiva

## 🚀 Começando

### Pré-requisitos
- Python 3.8+
- Chave API do OpenWeather (obtenha em https://openweathermap.org/api)

### Instalação Rápida

1. Clone o repositório:
```bash
git clone https://github.com/Victor884/PrevisaoTempoGUI.git
cd PrevisaoTempoGUI
```

2. Configure as variáveis de ambiente (crie um `.env` na raiz do projeto):
```env
OWM_API_KEY=sua_chave_aqui
LOCAL_TZ=America/Sao_Paulo
```

3. Instale as dependências:
```bash
cd previsaotempogui
pip install -r requirements.txt
```

### ⚡ Como Executar o Projeto

#### **Opção 1: Dashboard Apenas (Recomendado)**
Se você já tem dados salvos em `data/weather_current.csv` e `data/weather_forecast.csv`:

```bash
cd previsaotempogui
streamlit run app_streamlit.py
```
O dashboard abrirá automaticamente em `http://localhost:8501`

#### **Opção 2: Coletar Dados + Dashboard**

1. Executar o ETL para coletar dados:
```bash
cd previsaotempogui
python etl_openweather.py --city "São Paulo, BR" --mode all
```

2. Iniciar o Dashboard:
```bash
streamlit run app_streamlit.py
```

#### **Opção 3: Coletar dados de múltiplas cidades**

```bash
cd previsaotempogui

# São Paulo
python etl_openweather.py --city "São Paulo, BR" --mode all

# Rio de Janeiro
python etl_openweather.py --city "Rio de Janeiro, BR" --mode all

# Belo Horizonte
python etl_openweather.py --city "Belo Horizonte, BR" --mode all

# Brasília
python etl_openweather.py --city "Brasília, BR" --mode all

# Salvador
python etl_openweather.py --city "Salvador, BR" --mode all

# Iniciar dashboard
streamlit run app_streamlit.py
```

### 📋 Uso do ETL

#### Comandos disponíveis:
```bash
# Coletar dados da cidade especificada
python etl_openweather.py --city "São Paulo, BR"

# Coletar todas as fontes de dados (current, hourly, daily)
python etl_openweather.py --city "São Paulo, BR" --mode all

# Ver ajuda
python etl_openweather.py --help
```

**Saída do ETL:**
- `data/weather_current.csv` - Dados de clima atual
- `data/weather_forecast.csv` - Previsão horária
- `figures/` - Gráficos gerados

## 📁 Estrutura do Projeto

```
PrevisaoTempoGUI/
├── README.md                          # Este arquivo
├── previsaotempogui/
│   ├── app_streamlit.py              # Dashboard web Streamlit
│   ├── etl_openweather.py            # Pipeline ETL
│   ├── requirements.txt              # Dependências Python
│   ├── data/
│   │   ├── weather_current.csv       # Dados de clima atual
│   │   └── weather_forecast.csv      # Previsão 5 dias
│   └── figures/                      # Gráficos gerados
└── .env                              # Variáveis de ambiente (não commitado)
```

## 📦 Dependências

- **requests**: Requisições HTTP para APIs
- **pandas**: Manipulação e análise de dados
- **matplotlib**: Geração de gráficos
- **streamlit**: Framework web para o dashboard
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `OWM_API_KEY` | Chave da API OpenWeather | - |
| `LOCAL_TZ` | Timezone local | `America/Sao_Paulo` |

## 📊 Dados Coletados

### Dados de Clima Atual
- Temperatura, sensação térmica, umidade
- Pressão, orvalho, cobertura de nuvens
- Índice UV, visibilidade
- Velocidade e direção do vento
- Precipitação, neve
- Descrição do clima com ícone

### Previsão (Horária e Diária)
- Todos os campos acima
- Probabilidade de precipitação
- Timestamps UTC e local
- Coordenadas geográficas (lat, lon)

## 🛠️ Desenvolvimento

### Adicionar Nova Cidade

```bash
python etl_openweather.py --city "Rio de Janeiro, BR" --mode all
```

### Estender o ETL

Edite [etl_openweather.py](previsaotempogui/etl_openweather.py) para:
- Adicionar novas fontes de dados
- Modificar transformações
- Alterar formato de saída

### Customizar o Dashboard

Edite [app_streamlit.py](previsaotempogui/app_streamlit.py) para:
- Adicionar novas visualizações
- Implementar filtros avançados
- Criar novos gráficos

## 📝 Notas Importantes

- **API Limits**: Verificar limites de requisições do plano OpenWeather
- **Chave API**: Manter a chave em variáveis de ambiente, nunca commitar no repositório
- **Timezones**: O projeto usa `zoneinfo` para conversão de horários
- **Cache**: Dados são sobrescritos a cada execução do ETL

## 📄 Licença

Este projeto está disponível sob licença MIT.

## 👤 Autor

Victor884

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

---

**Última atualização**: Janeiro 2026
