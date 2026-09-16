import math
import requests

def fetch_srtm_elevation_and_slope(lat: float, lon: float):
    try:
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
        res = requests.get(url, timeout=3).json()
        elev = res.get("elevation", [1350.0])[0]

        url_off = f"https://api.open-meteo.com/v1/elevation?latitude={lat+0.003}&longitude={lon+0.003}"
        res_off = requests.get(url_off, timeout=3).json()
        elev_off = res_off.get("elevation", [1350.0])[0]

        slope_deg = round(math.degrees(math.atan(abs(elev - elev_off) / 400.0)), 1)
        return float(elev), min(max(slope_deg, 2.0), 65.0)
    except Exception:
        return 1350.0, 15.0

def fetch_soilgrids_composition(lat: float, lon: float):
    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=clay&depth=0-5cm&value=mean"
        res = requests.get(url, timeout=4).json()
        layers = res.get("properties", {}).get("layers", [])
        if layers:
            clay_g_kg = layers[0]["depths"][0]["values"]["mean"]
            return round(clay_g_kg / 10.0, 1) if clay_g_kg else 35.0
        return 35.0
    except Exception:
        return 35.0

def fetch_live_weather(lat: float, lon: float):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=rain_sum&timezone=Asia%2FKathmandu"
        res = requests.get(url, timeout=3).json()
        rain = res.get("daily", {}).get("rain_sum", [0.0])[0] or 0.0
        return round(float(rain), 1)
    except Exception:
        return 10.0

def get_live_telemetry_payload(lat: float, lon: float):
    elev, slope = fetch_srtm_elevation_and_slope(lat, lon)
    clay_pct = fetch_soilgrids_composition(lat, lon)
    rain_24h = fetch_live_weather(lat, lon)

    landslide_risk = round(min(((slope / 45.0) * 45) + ((clay_pct / 50.0) * 20) + ((rain_24h / 60.0) * 35), 99.0), 1)
    flash_flood_risk = round(min(((rain_24h / 40.0) * 75) + ((1.0 - min(slope / 30.0, 1.0)) * 25), 99.0), 1)

    return {
        "elevation_m": elev,
        "slope_deg": slope,
        "soil_clay_pct": clay_pct,
        "rain_24h_mm": rain_24h,
        "landslide_risk_pct": landslide_risk,
        "flash_flood_risk_pct": flash_flood_risk,
        "max_risk_pct": max(landslide_risk, flash_flood_risk)
    }