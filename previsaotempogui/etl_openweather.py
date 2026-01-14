
# etl_openweather.py
import os
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
import zoneinfo

import requests
import pandas as pd
import matplotlib.pyplot as plt

# Carrega variáveis do .env automaticamente
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

API_KEY = os.getenv("OWM_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"
BASE_URL_ONECALL = "https://api.openweathermap.org/data/3.0"
TZ_NAME = os.getenv("LOCAL_TZ", "America/Sao_Paulo")
TIMEZONE_LOCAL = zoneinfo.ZoneInfo(TZ_NAME)

def _fetch_json(endpoint: str, params: dict, retries: int = 3, backoff: float = 1.5, base_url: str = None):
    if base_url is None:
        base_url = BASE_URL
    url = f"{base_url}/{endpoint}"
    params = params.copy()
    params["appid"] = API_KEY
    params.setdefault("units", "metric")
    params.setdefault("lang", "pt_br")

    last_err = None
    for i in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                last_err = Exception(f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            last_err = e
        time.sleep(backoff * (i + 1))
    raise last_err

def _get_lat_lon(city_query: str) -> tuple:
    """Converte nome da cidade em coordenadas (lat, lon)"""
    try:
        # Tenta usar Geocoding API
        data = _fetch_json("geo/1.0/direct", {"q": city_query, "limit": 1})
        if not data:
            raise ValueError(f"Cidade não encontrada: {city_query}")
        city_data = data[0]
        return city_data["lat"], city_data["lon"], city_data.get("name"), city_data.get("country")
    except Exception as e:
        print(f"  ⚠ Geocoding API indisponível: {e}")
        print(f"  ℹ Usando busca por nome de cidade direto")
        # Fallback: retorna None para lat/lon, será usada busca por nome
        return None, None, city_query, None

def _to_local_ts(ts_utc: int) -> str:
    dt_utc = datetime.fromtimestamp(ts_utc, tz=timezone.utc)
    dt_local = dt_utc.astimezone(TIMEZONE_LOCAL)
    return dt_local.strftime("%Y-%m-%d %H:%M:%S")

def _normalize_weather_dict(weather_list: list) -> dict:
    """Extrai primeira entrada da lista weather"""
    if not weather_list:
        return {"id": None, "main": None, "description": None, "icon": None}
    w = weather_list[0]
    return {
        "weather_id": w.get("id"),
        "weather_main": w.get("main"),
        "weather_description": w.get("description"),
        "weather_icon": w.get("icon")
    }

def normalize_onecall_current(json_obj: dict, city_name: str, city_country: str) -> dict:
    """Normaliza dados current da One Call API"""
    current = json_obj.get("current", {}) or {}
    weather_info = _normalize_weather_dict(current.get("weather", []))
    rain = current.get("rain", {}) or {}
    snow = current.get("snow", {}) or {}

    ts_utc = current.get("dt")
    return {
        "fonte": "onecall_current",
        "cidade": city_name,
        "pais": city_country,
        "lat": json_obj.get("lat"),
        "lon": json_obj.get("lon"),
        "timezone": json_obj.get("timezone"),
        "timestamp_utc": datetime.fromtimestamp(ts_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if ts_utc else None,
        "timestamp_local": _to_local_ts(ts_utc) if ts_utc else None,
        "sunrise_utc": datetime.fromtimestamp(current.get("sunrise"), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if current.get("sunrise") else None,
        "sunset_utc": datetime.fromtimestamp(current.get("sunset"), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if current.get("sunset") else None,
        "temp_c": current.get("temp"),
        "sensacao_c": current.get("feels_like"),
        "umidade_pct": current.get("humidity"),
        "pressao_hpa": current.get("pressure"),
        "orvalho_c": current.get("dew_point"),
        "nuvens_pct": current.get("clouds"),
        "uvi": current.get("uvi"),
        "visibilidade_m": current.get("visibility"),
        "vento_ms": current.get("wind_speed"),
        "vento_dir_graus": current.get("wind_deg"),
        "rajada_vento_ms": current.get("wind_gust"),
        "chuva_1h_mm": rain.get("1h"),
        "neve_1h_mm": snow.get("1h"),
        "weather_id": weather_info["weather_id"],
        "weather_main": weather_info["weather_main"],
        "weather_description": weather_info["weather_description"],
        "weather_icon": weather_info["weather_icon"],
    }

def normalize_onecall_hourly(json_obj: dict, city_name: str, city_country: str) -> list:
    """Normaliza dados hourly da One Call API"""
    items = []
    for entry in json_obj.get("hourly", []):
        weather_info = _normalize_weather_dict(entry.get("weather", []))
        rain = entry.get("rain", {}) or {}
        snow = entry.get("snow", {}) or {}

        ts_utc = entry.get("dt")
        items.append({
            "fonte": "onecall_hourly",
            "cidade": city_name,
            "pais": city_country,
            "lat": json_obj.get("lat"),
            "lon": json_obj.get("lon"),
            "timezone": json_obj.get("timezone"),
            "timestamp_utc": datetime.fromtimestamp(ts_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if ts_utc else None,
            "timestamp_local": _to_local_ts(ts_utc) if ts_utc else None,
            "temp_c": entry.get("temp"),
            "sensacao_c": entry.get("feels_like"),
            "umidade_pct": entry.get("humidity"),
            "pressao_hpa": entry.get("pressure"),
            "orvalho_c": entry.get("dew_point"),
            "nuvens_pct": entry.get("clouds"),
            "uvi": entry.get("uvi"),
            "visibilidade_m": entry.get("visibility"),
            "vento_ms": entry.get("wind_speed"),
            "vento_dir_graus": entry.get("wind_deg"),
            "rajada_vento_ms": entry.get("wind_gust"),
            "prob_precipitacao": entry.get("pop"),
            "chuva_1h_mm": rain.get("1h"),
            "neve_1h_mm": snow.get("1h"),
            "weather_id": weather_info["weather_id"],
            "weather_main": weather_info["weather_main"],
            "weather_description": weather_info["weather_description"],
            "weather_icon": weather_info["weather_icon"],
        })
    return items

def normalize_onecall_daily(json_obj: dict, city_name: str, city_country: str) -> list:
    """Normaliza dados daily da One Call API"""
    items = []
    for entry in json_obj.get("daily", []):
        weather_info = _normalize_weather_dict(entry.get("weather", []))
        temp = entry.get("temp", {}) or {}
        feels_like = entry.get("feels_like", {}) or {}
        rain = entry.get("rain", {}) or {}
        snow = entry.get("snow", {}) or {}

        ts_utc = entry.get("dt")
        items.append({
            "fonte": "onecall_daily",
            "cidade": city_name,
            "pais": city_country,
            "lat": json_obj.get("lat"),
            "lon": json_obj.get("lon"),
            "timezone": json_obj.get("timezone"),
            "timestamp_utc": datetime.fromtimestamp(ts_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if ts_utc else None,
            "timestamp_local": _to_local_ts(ts_utc) if ts_utc else None,
            "sunrise_utc": datetime.fromtimestamp(entry.get("sunrise"), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if entry.get("sunrise") else None,
            "sunset_utc": datetime.fromtimestamp(entry.get("sunset"), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if entry.get("sunset") else None,
            "moonrise_utc": datetime.fromtimestamp(entry.get("moonrise"), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if entry.get("moonrise") else None,
            "moonset_utc": datetime.fromtimestamp(entry.get("moonset"), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if entry.get("moonset") else None,
            "moon_phase": entry.get("moon_phase"),
            "summary": entry.get("summary"),
            "temp_manha_c": temp.get("morn"),
            "temp_dia_c": temp.get("day"),
            "temp_tarde_c": temp.get("eve"),
            "temp_noite_c": temp.get("night"),
            "temp_min_c": temp.get("min"),
            "temp_max_c": temp.get("max"),
            "sensacao_manha_c": feels_like.get("morn"),
            "sensacao_dia_c": feels_like.get("day"),
            "sensacao_tarde_c": feels_like.get("eve"),
            "sensacao_noite_c": feels_like.get("night"),
            "umidade_pct": entry.get("humidity"),
            "pressao_hpa": entry.get("pressure"),
            "orvalho_c": entry.get("dew_point"),
            "nuvens_pct": entry.get("clouds"),
            "uvi_max": entry.get("uvi"),
            "vento_ms": entry.get("wind_speed"),
            "vento_dir_graus": entry.get("wind_deg"),
            "rajada_vento_ms": entry.get("wind_gust"),
            "prob_precipitacao": entry.get("pop"),
            "chuva_mm": entry.get("rain"),
            "neve_mm": entry.get("snow"),
            "weather_id": weather_info["weather_id"],
            "weather_main": weather_info["weather_main"],
            "weather_description": weather_info["weather_description"],
            "weather_icon": weather_info["weather_icon"],
        })
    return items

def fetch_onecall(city_query: str) -> tuple:
    """Busca dados completos da One Call API v3.0"""
    lat, lon, city_name, city_country = _get_lat_lon(city_query)
    
    if lat is None or lon is None:
        raise ValueError(f"Não foi possível obter coordenadas para: {city_query}. Use formato: 'Cidade, País'")
    
    print(f"  ℹ Coordenadas: lat={lat}, lon={lon}")
    
    data = _fetch_json(
        "onecall",
        {"lat": lat, "lon": lon, "exclude": "minutely,alerts"},
        base_url=BASE_URL_ONECALL
    )
    
    current_df = pd.DataFrame([normalize_onecall_current(data, city_name, city_country)])
    hourly_df = pd.DataFrame(normalize_onecall_hourly(data, city_name, city_country))
    daily_df = pd.DataFrame(normalize_onecall_daily(data, city_name, city_country))
    
    return current_df, hourly_df, daily_df

def fetch_current_weather(city_query: str) -> pd.DataFrame:
    """Busca clima atual usando o endpoint /weather"""
    lat, lon, city_name, city_country = _get_lat_lon(city_query)
    
    # Se temos coordenadas, usa lat/lon; senão usa busca por nome
    if lat is not None and lon is not None:
        print(f"  ℹ Usando coordenadas: lat={lat}, lon={lon}")
        params = {"lat": lat, "lon": lon}
    else:
        print(f"  ℹ Usando busca por nome: {city_query}")
        params = {"q": city_query}
    
    data = _fetch_json("weather", params)
    
    # Normaliza os dados
    main = data.get("main", {}) or {}
    wind = data.get("wind", {}) or {}
    clouds = data.get("clouds", {}) or {}
    weather = (data.get("weather") or [{}])[0]
    rain = data.get("rain", {}) or {}
    snow = data.get("snow", {}) or {}
    sys = data.get("sys", {}) or {}
    
    ts_utc = data.get("dt")
    row = {
        "cidade": data.get("name"),
        "pais": sys.get("country"),
        "lat": data.get("coord", {}).get("lat"),
        "lon": data.get("coord", {}).get("lon"),
        "timestamp_utc": datetime.fromtimestamp(ts_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if ts_utc else None,
        "timestamp_local": _to_local_ts(ts_utc) if ts_utc else None,
        "temp_c": main.get("temp"),
        "sensacao_c": main.get("feels_like"),
        "temp_min_c": main.get("temp_min"),
        "temp_max_c": main.get("temp_max"),
        "umidade_pct": main.get("humidity"),
        "pressao_hpa": main.get("pressure"),
        "nuvens_pct": clouds.get("all"),
        "vento_ms": wind.get("speed"),
        "vento_dir_graus": wind.get("deg"),
        "rajada_vento_ms": wind.get("gust"),
        "visibilidade_m": data.get("visibility"),
        "chuva_1h_mm": rain.get("1h"),
        "neve_1h_mm": snow.get("1h"),
        "weather_id": weather.get("id"),
        "weather_main": weather.get("main"),
        "weather_description": weather.get("description"),
        "weather_icon": weather.get("icon"),
    }
    
    return pd.DataFrame([row])

def save_csv(df: pd.DataFrame, path: Path, mode: str = "append"):
    """Salva DataFrame em CSV com modo append ou replace"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "replace" or not path.exists():
        df.to_csv(path, index=False)
    else:
        existing = pd.read_csv(path)
        combined = pd.concat([existing, df], ignore_index=True)
        # Remove duplicatas se tiver coluna timestamp_utc
        if "timestamp_utc" in combined.columns:
            combined = combined.drop_duplicates(subset=["timestamp_utc"], keep="last")
        combined.to_csv(path, index=False)

def plot_forecast(df_forecast: pd.DataFrame, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = df_forecast.copy()
    df["ts"] = pd.to_datetime(df["timestamp_local"])
    df = df.sort_values("ts")

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.plot(df["ts"], df["temp_c"], color="#1f77b4", marker="o", label="Temperatura (°C)")
    ax1.set_xlabel("Tempo (local)")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.grid(True, which="both", ls="--", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.bar(df["ts"], df["chuva_mm"].fillna(0), width=0.08, alpha=0.3, color="#2ca02c", label="Chuva (mm/3h)")
    ax2.set_ylabel("Chuva (mm/3h)")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title(f"Previsão de Temperatura e Chuva - {df['cidade'].iloc[0]}")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)

def main():
    parser = argparse.ArgumentParser(description="ETL OpenWeatherMap - Current Weather & Forecast")
    parser.add_argument("--city", type=str, default="São Paulo, BR", help="Cidade (ex.: 'São Paulo, BR')")
    parser.add_argument("--data_dir", type=str, default="data", help="Pasta para CSVs")
    parser.add_argument("--fig_dir", type=str, default="figures", help="Pasta para gráficos")
    parser.add_argument("--mode", type=str, default="current", choices=["current", "onecall", "all"], 
                       help="Modo: current (API /weather), onecall (One Call API), all (ambos)")
    args = parser.parse_args()

    if not API_KEY:
        raise RuntimeError("OWM_API_KEY não encontrado. Defina no .env ou ambiente.")

    data_dir = Path(args.data_dir)
    fig_dir = Path(args.fig_dir)

    try:
        # Buscar Current Weather
        if args.mode in ["current", "all"]:
            print(f"[INFO] Buscando clima atual para {args.city}...")
            df_current = fetch_current_weather(args.city)
            save_csv(df_current, data_dir / "weather_current.csv", mode="append")
            print(f"  ✓ Current: {len(df_current)} linha(s) salva(s) em weather_current.csv")

        # Buscar One Call API
        if args.mode in ["onecall", "all"]:
            print(f"[INFO] Buscando dados completos (One Call API) para {args.city}...")
            df_current, df_hourly, df_daily = fetch_onecall(args.city)
            
            save_csv(df_current, data_dir / "weather_onecall_current.csv", mode="append")
            print(f"  ✓ Current: {len(df_current)} linha(s)")
            
            save_csv(df_hourly, data_dir / "weather_onecall_hourly.csv", mode="replace")
            print(f"  ✓ Hourly: {len(df_hourly)} linha(s)")
            
            save_csv(df_daily, data_dir / "weather_onecall_daily.csv", mode="replace")
            print(f"  ✓ Daily: {len(df_daily)} linha(s)")
            
            print(f"[INFO] Gerando gráficos...")
            plot_forecast(df_hourly, fig_dir / "temp_forecast_hourly.png")
            print(f"  ✓ Gráfico horário salvo")
            
            plot_forecast(df_daily, fig_dir / "temp_forecast_daily.png")
            print(f"  ✓ Gráfico diário salvo")
        
        print("[OK] ETL concluído com sucesso!")
        
    except Exception as e:
        print(f"[ERRO] {e}", file=__import__("sys").stderr)
        raise

if __name__ == "__main__":
    main()
