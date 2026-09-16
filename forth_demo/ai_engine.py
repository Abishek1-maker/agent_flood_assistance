import os
import json
import time
from dotenv import load_dotenv
from google import genai
from knowledge_base import resolve_location_context
from telemetry_engine import get_live_telemetry_payload

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def safe_generate_content(prompt: str) -> str:
    # Use reliable production models in order
    valid_models = ['gemini-3.6-flash', 'gemini-3.1-pro-preview', 'gemini-1.5-flash']
    for model_name in valid_models:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text
        except Exception as err:
            print(f"Model {model_name} failed: {err}")
            time.sleep(0.5)
            
    return "I am currently syncing real-time weather streams. Please ask your question once more!"

def process_conversational_query(user_message: str, chat_history: list, language: str = "English") -> str:
    if not user_message.strip():
        return "Please enter a valid question."

    loc_res = resolve_location_context(user_message, chat_history)

    if loc_res["status"] == "not_covered":
        uncovered_msg = {
            "Nepali (नेपाली)": "मलाई हाल यस क्षेत्रको लागि विस्तृत विवरण प्राप्त भएको छैन। मेरो वर्तमान कभरेज **कैलाली**, **काठमाडौं**, र **भोटेकोशी** क्षेत्रमा सीमित छ।",
            "Hindi (हिंदी)": "मेरे पास वर्तमान में इस स्थान के लिए विस्तृत डेटा नहीं है। मेरी वर्तमान लाइव कवरेज **कैलाली**, **काठमांडू**, और **भोटेकोशी** तक सीमित है।",
            "Chinese (中文)": "我目前没有该位置的详细数据。我目前的实时数据覆盖范围为 **凯拉利**, **加德满都** 和 **波特科西**。",
            "English": "I don't currently have detailed live telemetry coverage for this exact place. My detailed coverage extends across **Kailali**, **Kathmandu**, and **Bhotekoshi**."
        }
        return uncovered_msg.get(language, uncovered_msg["English"])

    lat, lon = loc_res["lat"], loc_res["lon"]
    place_name = loc_res["place_name"]
    region_info = loc_res["region_info"]
    telemetry = get_live_telemetry_payload(lat, lon)

    prompt = f"""
    You are PRAVAH, an intelligent disaster AI assistant in Nepal.

    STRICT LANGUAGE REQUIREMENT:
    - You MUST answer completely in: {language}.

    RESPONSE RULES:
    1. Direct & natural answer.
    2. Place queried: {place_name} ({region_info['region_name']})
    3. Live Risk Metrics: {json.dumps(telemetry)}

    Condition Handling:
    - If max_risk_pct < 35%: State clearly that conditions around {place_name} are normal and safe right now 🟢.
    - If max_risk_pct >= 35%: Warn about potential flood/landslide risk near nearby rivers.

    User Question: "{user_message}"
    """

    return safe_generate_content(prompt)