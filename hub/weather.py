#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
from .config import load_config
from .ui import Colors as C, loading

def geocode_city(city_name):
    clean_name = (city_name or "").strip()
    if not clean_name:
        return None
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(clean_name)}&count=1&language=en&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "hub-cli/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results")
            if results and len(results) > 0:
                loc = results[0]
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                name = f"{loc.get('name')}, {loc.get('country_code', '').upper()}"
                return (lat, lon, name)
    except Exception:
        pass
    return None

def fetch_weather(city=None):
    cfg = load_config()
    target_city = city or cfg.get("weather", {}).get("default_city")
    if not target_city:
        print(f"{C.RED}[ERROR]{C.RESET} No city provided and no 'default_city' configured.")
        return

    coords = geocode_city(target_city)
    if not coords:
        print(f"{C.RED}[ERROR]{C.RESET} Location not found for: '{target_city}'")
        return

    lat, lon, label = coords
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m&forecast_days=1"
    req = urllib.request.Request(url, headers={"User-Agent": "hub-cli/1.0"})
    
    with loading(f"Fetching forecast for {label}..."):
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current", {})
                temp = current.get("temperature_2m")
                app_temp = current.get("apparent_temperature")
                humidity = current.get("relative_humidity_2m")
                wind = current.get("wind_speed_10m")
                precip = current.get("precipitation")

                print(f"\n{C.BOLD}--- WEATHER: {label.upper()} ---{C.RESET}")
                print(f"Temperature:      {C.CYAN}{temp}°C{C.RESET} (Feels like: {app_temp}°C)")
                print(f"Relative Humidity: {humidity}%")
                print(f"Wind Speed:        {wind} km/h")
                print(f"Precipitation:     {precip} mm\n")
        except Exception as e:
            print(f"{C.RED}[ERROR]{C.RESET} Could not retrieve weather data: {e}")
