
import pandas as pd
import streamlit as st
from pathlib import Path
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Clima – OpenWeather ETL", layout="wide")

# Customização de cores e layout
st.markdown("""
    <style>
        .metric-card {
            background-color: #0E1117;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #1f77b4;
        }
        .header {
            color: #00D9FF;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌤️ Dashboard de Clima (OpenWeather)")
st.markdown("Visualize dados meteorológicos em tempo real de múltiplos estados brasileiros")

data_dir = Path("data")
cur_path = data_dir / "weather_current.csv"
for_path = data_dir / "weather_forecast.csv"

# Carregar dados
if cur_path.exists():
    df_cur = pd.read_csv(cur_path)
    cidades_disponiveis = df_cur["cidade"].unique().tolist()
else:
    cidades_disponiveis = []
    df_cur = pd.DataFrame()

# Sidebar para filtros
with st.sidebar:
    st.header("⚙️ Filtros")
    if len(cidades_disponiveis) > 0:
        cidade_selecionada = st.selectbox(
            "Selecione uma cidade",
            cidades_disponiveis,
            index=0
        )
    else:
        cidade_selecionada = None
        st.warning("Nenhuma cidade disponível nos dados")

# Tabs principais
tabs = st.tabs(["🗺️ Mapa", "🌡️ Clima Atual", "📊 Previsão 5 Dias", "📋 Dados Brutos"])

# TAB 1: MAPA
with tabs[0]:
    st.subheader("Mapa de Cidades Monitoradas")
    
    if not df_cur.empty:
        # Criar mapa com Folium
        m = folium.Map(
            location=[-10, -55],
            zoom_start=4,
            tiles="OpenStreetMap"
        )
        
        # Adicionar markers para cada cidade
        for idx, row in df_cur.drop_duplicates(subset=['cidade']).iterrows():
            temp = row['temp_c']
            descricao = row['weather_description']
            cidade = row['cidade']
            
            # Cor do marker baseado na temperatura
            if temp > 30:
                color = 'red'
            elif temp > 25:
                color = 'orange'
            elif temp > 20:
                color = 'yellow'
            else:
                color = 'blue'
            
            popup_text = f"""
            <b>{cidade}</b><br>
            🌡️ Temp: {temp:.1f}°C<br>
            💨 Vento: {row['vento_ms']:.1f} m/s<br>
            💧 Umidade: {row['umidade_pct']}%<br>
            ☁️ {descricao}
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=popup_text,
                icon=folium.Icon(color=color, icon='cloud'),
                tooltip=f"{cidade}: {temp:.1f}°C"
            ).add_to(m)
        
        st_folium(m, width=1200, height=600)
    else:
        st.warning("Nenhum dado disponível para exibir no mapa")

# TAB 2: CLIMA ATUAL
with tabs[1]:
    if not df_cur.empty and cidade_selecionada:
        df_filtrado = df_cur[df_cur["cidade"] == cidade_selecionada]
        if len(df_filtrado) > 0:
            # Pegar o registro mais recente
            dados_atuais = df_filtrado.sort_values("timestamp_utc").iloc[-1]
            
            st.subheader(f"🌍 {dados_atuais['cidade']}")
            
            # Métricas principais em colunas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🌡️ Temperatura",
                    value=f"{dados_atuais['temp_c']:.1f}°C",
                    delta=f"Sensação: {dados_atuais['sensacao_c']:.1f}°C"
                )
            
            with col2:
                st.metric(
                    label="💧 Umidade",
                    value=f"{dados_atuais['umidade_pct']:.0f}%"
                )
            
            with col3:
                st.metric(
                    label="💨 Vento",
                    value=f"{dados_atuais['vento_ms']:.1f} m/s",
                    delta=f"Dir: {dados_atuais['vento_dir_graus']:.0f}°"
                )
            
            with col4:
                st.metric(
                    label="🔽 Pressão",
                    value=f"{dados_atuais['pressao_hpa']:.0f} hPa"
                )
            
            # Informações detalhadas
            col_esq, col_dir = st.columns(2)
            
            with col_esq:
                st.markdown("### 📈 Detalhes Adicionais")
                st.write(f"""
                - **Nuvens**: {dados_atuais['nuvens_pct']:.0f}%
                - **Orvalho**: {dados_atuais.get('orvalho_c', 'N/A')}°C
                - **Visibilidade**: {dados_atuais['visibilidade_m']:.0f}m
                - **Índice UV**: {dados_atuais.get('uvi', 'N/A')}
                """)
            
            with col_dir:
                st.markdown("### 🌦️ Condição do Tempo")
                st.write(f"""
                - **Tipo**: {dados_atuais['weather_main']}
                - **Descrição**: {dados_atuais['weather_description'].title()}
                - **Atualizado em**: {dados_atuais['timestamp_local']}
                """)
            
            # Histórico de temperaturas da cidade
            st.markdown("### 📊 Histórico de Leituras")
            df_historico = df_filtrado.sort_values("timestamp_utc")[['timestamp_local', 'temp_c', 'umidade_pct']].tail(10)
            st.dataframe(df_historico, width="stretch")
        else:
            st.info(f"Nenhum dado disponível para {cidade_selecionada}")
    elif not df_cur.empty:
        st.info("Selecione uma cidade no sidebar para visualizar dados")
    else:
        st.warning("Arquivo weather_current.csv não encontrado. Rode o ETL primeiro.")

# TAB 3: PREVISÃO 5 DIAS
with tabs[2]:
    if for_path.exists() and not df_cur.empty and cidade_selecionada:
        df_for = pd.read_csv(for_path)
        df_for_filtrado = df_for[df_for["cidade"] == cidade_selecionada].copy()
        
        if len(df_for_filtrado) > 0:
            df_for_filtrado.loc[:, "ts"] = pd.to_datetime(df_for_filtrado["timestamp_local"])
            df_for_filtrado = df_for_filtrado.sort_values("ts")
            
            st.subheader(f"📅 Previsão 5 Dias - {cidade_selecionada}")
            
            # Gráfico de Temperatura
            st.markdown("#### 🌡️ Evolução da Temperatura")
            temp_chart = df_for_filtrado.set_index("ts")[["temp_c", "sensacao_c"]]
            st.line_chart(temp_chart, width="stretch")
            
            # Gráfico de Precipitação
            st.markdown("#### 🌧️ Precipitação (mm/hora)")
            precip_chart = df_for_filtrado.set_index("ts")[["chuva_1h_mm"]].fillna(0)
            precip_chart.columns = ["Chuva (mm)"]
            st.bar_chart(precip_chart, width="stretch")
            
            # Gráfico de Umidade
            st.markdown("#### 💧 Umidade Relativa")
            umidade_chart = df_for_filtrado.set_index("ts")[["umidade_pct"]]
            umidade_chart.columns = ["Umidade (%)"]
            st.line_chart(umidade_chart, width="stretch")
            
            # Tabela detalhada
            st.markdown("#### 📋 Dados Detalhados da Previsão")
            colunas_exibicao = ["timestamp_local", "temp_c", "sensacao_c", "umidade_pct", 
                               "pressao_hpa", "nuvens_pct", "vento_ms", "chuva_1h_mm", "weather_description"]
            colunas_existentes = [col for col in colunas_exibicao if col in df_for_filtrado.columns]
            st.dataframe(df_for_filtrado[colunas_existentes].tail(24), width="stretch")
        else:
            st.info(f"Nenhuma previsão disponível para {cidade_selecionada}")
    elif for_path.exists() and not df_cur.empty:
        st.info("Selecione uma cidade no sidebar para visualizar previsão")
    else:
        st.warning("Arquivo weather_forecast.csv não encontrado. Rode o ETL primeiro.")

# TAB 4: DADOS BRUTOS
with tabs[3]:
    st.subheader("📊 Dados Brutos")
    
    col_atual, col_prev = st.columns(2)
    
    with col_atual:
        st.markdown("### Clima Atual")
        if not df_cur.empty:
            st.dataframe(df_cur, width="stretch")
        else:
            st.warning("Sem dados disponíveis")
    
    with col_prev:
        st.markdown("### Previsão")
        if for_path.exists():
            df_for = pd.read_csv(for_path)
            st.dataframe(df_for, width="stretch")
        else:
            st.warning("Sem dados disponíveis")
