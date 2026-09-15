import os
import json
import time
from dotenv import load_dotenv
from google import genai
from database import get_ward_data_from_db

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def safe_generate_content(prompt: str) -> str:
    valid_models = []
    try:
        for m in client.models.list():
            model_id = m.name.replace("models/", "") if hasattr(m, "name") else str(m)
            if any(k in model_id for k in ["flash", "pro"]) and not any(x in model_id for x in ["image", "tts", "embedding", "realtime"]):
                valid_models.append(model_id)
        valid_models.sort(reverse=True)
    except Exception as e:
        print(f"Model listing warning: {e}")

    if not valid_models:
        valid_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']

    for model_name in valid_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                time.sleep(1)

    return "⚠️ Service is currently under heavy load. Please retry in a few seconds."


def process_disaster_query(user_message: str, ward_id: int, language: str) -> str:
    if not user_message.strip():
        return "Please ask a valid question."

    raw_data = get_ward_data_from_db(int(ward_id))
    if not raw_data:
        return f"No records found for Ward {ward_id}."

    system_instructions = f"""
    You are PRAVAH, an emergency response AI agent for local wards in Nepal.

    RESPONSE FORMATTING RULES:
    1. Language: Always respond in {language}.
    2. Adaptive Layout:
       - Greetings / Conversational: 1–2 friendly sentences.
       - Direct Confirmation (e.g., "yes", "yes i need", "show routes"): Immediately provide the actionable information using 2–4 clean bullet points.
       - Critical Hazard / High Risk: State the risk in 1 sentence, followed by bulleted action steps or safe locations.
    3. Scannability: Use **bolding** for key locations, status (e.g., **OPEN**, **CLOSED**), and phone numbers so users can read it instantly during emergencies.
    4. Proactive Next Steps: If you haven't yet provided complete assistance, end with 1 relevant follow-up question. If the user says "thank you" or "no", politely close the chat.
    """

    full_prompt = f"""
    {system_instructions}

    User Message: "{user_message}"

    Ward Data Context:
    {json.dumps(raw_data, indent=2)}
    """

    return safe_generate_content(full_prompt)