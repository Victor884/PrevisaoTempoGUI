
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Clima – OpenWeather ETL", layout="wide")
st.title("Dashboard de Clima (OpenWeather)")

data_dir = Path("data")
cur_path = data_dir / "weather_current.csv"
for_path = data_dir / "weather_forecast.csv"

cidade = st.text_input("Cidade (ex.: Brasília, BR)", value="Brasília, BR")
tabs = st.tabs(["Atual", "Previsão 5 dias"])

with tabs[0]:
    if cur_path.exists():
        df_cur = pd.read_csv(cur_path)
        df_cur = df_cur[df_cur["cidade"] == cidade] if cidade else df_cur
        st.subheader("Leitura atual (última linha)")
        if len(df_cur) > 0:
            st.write(df_cur.sort_values("timestamp_utc").tail(1))
        else:
            st.info("Sem dados para a cidade informada.")
    else:
        st.warning("Arquivo weather_current.csv não encontrado. Rode o ETL primeiro.")

with tabs[1]:
    if for_path.exists():
        df_for = pd.read_csv(for_path)
        df_for = df_for[df_for["cidade"] == cidade] if cidade else df_for
        if len(df_for) > 0:
            df_for["ts"] = pd.to_datetime(df_for["timestamp_local"])
            st.subheader("Temperatura (°C)")
            st.line_chart(df_for.set_index("ts")["temp_c"])

            st.subheader("Chuva (mm/3h)")
            st.bar_chart(df_for.set_index("ts")["chuva_mm"].fillna(0))

            st.subheader("Tabela completa")
            st.dataframe(df_for)
        else:
            st.info("Sem dados para a cidade informada.")
    else:
        st.warning("Arquivo weather_forecast.csv não encontrado. Rode o ETL primeiro.")
