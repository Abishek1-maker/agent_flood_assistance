# knowledge_base.py
import requests
import re

COVERED_BOUNDS = {
    "kailali": {
        "region_name": "Kailali District",
        "bounds": {"min_lat": 28.3, "max_lat": 29.1, "min_lon": 80.4, "max_lon": 81.4},
        "rivers": ["Mohana River", "Karnali River", "Pathariya River", "Sharda River"],
        "roads_bridges": ["East-West Highway (H01)", "Dhangadhi-Attariya Road", "Karnali Bridge (Chisapani)"]
    },
    "kathmandu": {
        "region_name": "Kathmandu District",
        "bounds": {"min_lat": 27.55, "max_lat": 27.85, "min_lon": 85.15, "max_lon": 85.55},
        "rivers": ["Bagmati River", "Bishnumati River", "Dhobi Khola", "Hanumante River", "Manohara River", "Tukucha Khola"],
        "roads_bridges": ["Ring Road", "Araniko Highway", "Balkhu Bridge", "Thapathali Bridge", "Koteshwor Underpass", "Maitighar Mandala"]
    },
    "bhotekoshi": {
        "region_name": "Bhotekoshi Area (Sindhupalchok)",
        "bounds": {"min_lat": 27.70, "max_lat": 28.05, "min_lon": 85.75, "max_lon": 86.10},
        "rivers": ["Bhote Koshi River", "Sun Koshi River", "Chaku Khola"],
        "roads_bridges": ["Araniko Highway (H03)", "Mitteri Bridge (Tatopani)", "Larcha Dry Port Bridge"]
    }
}

def geocode_place_name(place_query: str):
    stop_words = r'\b(my|friend|sansar|also|live|lives|living|stay|stays|there|here|in|at|near|around|is|are|there|any|prolem|problem|risk|condition|how|going|of|right|now|what|status|\?|,|\.)\b'
    clean_query = re.sub(stop_words, ' ', place_query, flags=re.I)
    clean_query = ' '.join(clean_query.split())

    search_candidates = [clean_query, clean_query.replace("-", " "), place_query]
    headers = {"User-Agent": "PravahDisasterAI/2.0"}

    for q in search_candidates:
        if not q or len(q.strip()) < 3:
            continue
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": f"{q}, Nepal", "format": "json", "limit": 1}
            response = requests.get(url, headers=headers, params=params, timeout=4)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "lat": float(data[0]["lat"]),
                        "lon": float(data[0]["lon"]),
                        "display_name": data[0]["display_name"]
                    }
        except Exception as e:
            print(f"Geocoding Error: {e}")
    return None

def resolve_location_context(user_query: str, chat_history: list = None) -> dict:
    text_lower = user_query.lower()

    for region_key, region_info in COVERED_BOUNDS.items():
        if region_key in text_lower or region_info["region_name"].lower() in text_lower:
            lat = (region_info["bounds"]["min_lat"] + region_info["bounds"]["max_lat"]) / 2
            lon = (region_info["bounds"]["min_lon"] + region_info["bounds"]["max_lon"]) / 2
            return {
                "status": "found",
                "region_key": region_key,
                "place_name": region_info["region_name"],
                "lat": lat,
                "lon": lon,
                "region_info": region_info
            }

    geo_res = geocode_place_name(user_query)
    if geo_res:
        lat, lon = geo_res["lat"], geo_res["lon"]
        for region_key, region_info in COVERED_BOUNDS.items():
            b = region_info["bounds"]
            if b["min_lat"] <= lat <= b["max_lat"] and b["min_lon"] <= lon <= b["max_lon"]:
                return {
                    "status": "found",
                    "region_key": region_key,
                    "place_name": geo_res["display_name"].split(",")[0],
                    "full_address": geo_res["display_name"],
                    "lat": lat,
                    "lon": lon,
                    "region_info": region_info
                }

    if "kathmandu" in text_lower or "ktm" in text_lower or "valley" in text_lower:
        return {
            "status": "found",
            "region_key": "kathmandu",
            "place_name": "Kathmandu Area",
            "lat": 27.7172,
            "lon": 85.3240,
            "region_info": COVERED_BOUNDS["kathmandu"]
        }

    return {"status": "not_covered"}