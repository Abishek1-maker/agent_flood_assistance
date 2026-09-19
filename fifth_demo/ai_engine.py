# ==============================================================================
# PRAVAH AI - CORE INTELLIGENCE ENGINE
# File: ai_engine.py
# Description: Handles Gemini LLM calls, intelligent response formatting, 
#              and language enforcement.
# ==============================================================================

import os
import json
import time
from dotenv import load_dotenv
from google import genai

# Custom Risk Data & Spatial Engines
from knowledge_base import resolve_location_context
from telemetry_engine import get_live_telemetry_payload

# Load environment variables from .env
load_dotenv()

# Initialize Gemini Client with API Key
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ==============================================================================
# 1. MULTI-LANGUAGE QUOTA FALLBACK DICTIONARY
# ==============================================================================

QUOTA_ERROR_MESSAGES = {
    "Nepali": "⚠️ API कोटा सीमा समाप्त भयो। कृपया १ मिनेट पर्खनुहोस् र पुन: प्रयास गर्नुहोस्।",
    "Hindi": "⚠️ API कोटा सीमा समाप्त हो गई है। कृपया 1 मिनट प्रतीक्षा करें और पुनः प्रयास करें।",
    "Chinese": "⚠️ 已达到 API 配额限制。请等待 1 分钟后再试。",
    "English": "⚠️ API Quota Limit Reached: Free tier limit exceeded. Please wait 1 minute and try again."
}


# ==============================================================================
# 2. SAFE GENERATION PIPELINE
# ==============================================================================
# Load multiple API keys into a list
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2")
]
# Filter out any empty keys
API_KEYS = [k for k in API_KEYS if k]

def safe_generate_content(prompt: str, language: str = "English") -> str:
    """Attempts generation using valid models and rotates API keys on quota exhaustion."""
    if not API_KEYS:
        print("[AI Engine Error] No valid GEMINI_API_KEY found in environment variables.")
        return "System Config Error: GEMINI_API_KEY is missing from environment variables."

    # Use the current valid flash model for your API tier
    valid_models = ['gemini-3.6-flash']

    # Try every key in our key rotation pool
    for key_index, api_key in enumerate(API_KEYS):
        client = genai.Client(api_key=api_key)
        
        for model_name in valid_models:
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=model_name, 
                        contents=prompt
                    )
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except Exception as err:
                    err_str = str(err)
                    print(f"[AI Engine Error] Key #{key_index + 1} | Attempt {attempt + 1} failed: {err_str}")
                    
                    # If 429 / Resource Exhausted, wait 1.5 seconds for per-second rate limits to reset
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        print(f"[AI Engine Warning] Key #{key_index + 1} rate limited. Retrying in 1.5s...")
                        time.sleep(1.5)
                    else:
                        time.sleep(0.5)

    # If all keys and attempts fail, return localized quota fallback message
    return QUOTA_ERROR_MESSAGES.get(language, QUOTA_ERROR_MESSAGES["English"])

# ==============================================================================
# 3. MAIN CONVERSATIONAL AGENT ROUTER
# ==============================================================================

def process_conversational_query(user_message: str, chat_history: list, language: str = "English") -> str:
    if not user_message or not user_message.strip():
        return "Please enter a valid question."

    # 1. Limit memory to the last 4 exchanges (8 messages total)
    recent_history = chat_history[-4:] if chat_history else []

    # 2. Format history into a string for Gemini
    formatted_history = ""
    for item in recent_history:
        if isinstance(item, list) and len(item) == 2:
            formatted_history += f"User: {item[0]}\nAI: {item[1]}\n"

    # 3. Resolve location context using both current message and past history
    loc_res = resolve_location_context(user_message, recent_history)
    

    if loc_res.get("status") == "not_covered":
        uncovered_msg = {
            "Nepali": "मलाई हाल यस क्षेत्रको लागि विस्तृत विवरण प्राप्त भएको छैन। मेरो वर्तमान कभरेज **कैलाली**, **काठमाडौं**, र **भोटेकोशी** क्षेत्रमा सीमित छ।",
            "Hindi": "मेरे पास वर्तमान में इस स्थान के लिए विस्तृत डेटा नहीं है। मेरी वर्तमान लाइव कवरेज **कैलाली**, **काठमांडू**, और **भोटेकोशी** तक सीमित है।",
            "Chinese": "我目前没有该位置的详细数据。我目前的实时数据覆盖范围为 **凯拉利**, **加德满都** 和 **波特科西**。",
            "English": "I don't currently have detailed live telemetry coverage for this exact place. My detailed coverage extends across **Kailali**, **Kathmandu**, and **Bhotekoshi**."
        }
        return uncovered_msg.get(language, uncovered_msg["English"])

    lat, lon = loc_res["lat"], loc_res["lon"]
    place_name = loc_res["place_name"]
    region_info = loc_res["region_info"]
    telemetry = get_live_telemetry_payload(lat, lon)

    # 4. Inject history string into system prompt
    prompt = f"""
    You are PRAVAH, an intelligent disaster risk AI assistant operating in Nepal.

    STRICT LANGUAGE REQUIREMENT:
    - You MUST reply completely in this language: {language}.

    RECENT CONVERSATION HISTORY:
    {formatted_history if formatted_history else "No previous conversation."}

    CURRENT CONTEXT:
    - Queried Location: {place_name} ({region_info['region_name']})
    - Live Telemetry Metrics: {json.dumps(telemetry)}

    INSTRUCTIONS:
    - Use RECENT CONVERSATION HISTORY to understand follow-up questions (e.g., if user says "what about there?", "tell me details").
    - If user asks simple questions, reply in 1-2 concise sentences.
    - If user asks for details/data/breakdown, output each metric with `<br>• ` on a new line.

    Current User Question: "{user_message}"
    
    """


    return safe_generate_content(prompt, language)