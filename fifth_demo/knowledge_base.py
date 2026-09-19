# ==============================================================================
# PRAVAH AI - INTERACTIVE MAPPING KNOWLEDGE BASE
# File: knowledge_base.py
# Description: Defines spatial bounding boxes, critical rivers, highways, 
#              pronoun context resolution, and OpenStreetMap geocoding logic.
# ==============================================================================

import requests
import re

# ==============================================================================
# 1. BOUNDING BOXES & GEOSPATIAL BOUNDARIES
# ==============================================================================

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

PRONOUNS_AND_GENERIC_WORDS = ["there", "it", "here", "this place", "that place", "the area"]
GREETINGS = ["hello", "hi", "hey", "namaste", "good morning", "good evening"]


# ==============================================================================
# 2. NOMINATIM GEOCODING ENGINE
# ==============================================================================

def geocode_place_name(place_query: str):
    """Strips filler words and resolves latitude/longitude via OpenStreetMap API."""
    stop_words = r'\b(my|live|lives|living|stay|stays|there|here|in|at|near|around|is|are|any|problem|risk|condition|how|going|of|right|now|what|status|\?|,|\.)\b'
    clean_query = re.sub(stop_words, ' ', place_query, flags=re.IGNORECASE)
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
            print(f"[Knowledge Base Error] Geocoding request failed: {e}")
            
    return None


# ==============================================================================
# 3. COMBINED SPATIAL & CONTEXT RESOLUTION ENGINE
# ==============================================================================

def resolve_location_context(user_message: str, chat_history: list = None) -> dict:
    """Combines boundary checks, chat history pronouns, greetings filter, and live geocoding."""
    msg_lower = user_message.strip().lower()

    # Step 0: Catch simple greetings and skip geocoding
    if msg_lower in GREETINGS:
        return {"status": "greeting"}

    # Step 1: Check direct boundary keywords in current message
    for region_key, region_info in COVERED_BOUNDS.items():
        if region_key in msg_lower or region_info["region_name"].lower() in msg_lower:
            lat = (region_info["bounds"]["min_lat"] + region_info["bounds"]["max_lat"]) / 2
            lon = (region_info["bounds"]["min_lon"] + region_info["bounds"]["max_lon"]) / 2
            return {
                "status": "covered",
                "place_name": region_info["region_name"],
                "lat": lat,
                "lon": lon,
                "region_info": region_info
            }

    # Step 2: Dynamic Geocoding via OpenStreetMap
    geo_res = geocode_place_name(user_message)
    if geo_res:
        lat, lon = geo_res["lat"], geo_res["lon"]
        for region_key, region_info in COVERED_BOUNDS.items():
            b = region_info["bounds"]
            if b["min_lat"] <= lat <= b["max_lat"] and b["min_lon"] <= lon <= b["max_lon"]:
                return {
                    "status": "covered",
                    "place_name": geo_res["display_name"].split(",")[0],
                    "lat": lat,
                    "lon": lon,
                    "region_info": region_info
                }

    # Step 3: Handle Pronouns ("there", "it", "here", "this place", etc.) using Chat Memory
    contains_pronoun = any(word in msg_lower for word in PRONOUNS_AND_GENERIC_WORDS)
    if contains_pronoun or chat_history:
        for turn in reversed(chat_history or []):
            past_text = " ".join(turn).lower() if isinstance(turn, list) else str(turn).lower()
            
            for region_key, region_info in COVERED_BOUNDS.items():
                if region_key in past_text or region_info["region_name"].lower() in past_text:
                    lat = (region_info["bounds"]["min_lat"] + region_info["bounds"]["max_lat"]) / 2
                    lon = (region_info["bounds"]["min_lon"] + region_info["bounds"]["max_lon"]) / 2
                    return {
                        "status": "covered",
                        "place_name": region_info["region_name"],
                        "lat": lat,
                        "lon": lon,
                        "region_info": region_info
                    }

    # Step 4: Fallback for unmapped locations
    return {"status": "not_covered"}