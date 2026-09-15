import os
import json
import time
import gradio as gr
from dotenv import load_dotenv
from google import genai
import gradio as gr

# Load secret API key from environment
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. Flexible Dynamic Database Schema
# ==========================================

def get_ward_data_from_db(ward_id: int):
    """
    Returns a rich, nested dictionary containing risk scores, 
    safe zones, open infrastructure, medical aid, and disaster protocols.
    """
    mock_database = {
        4: {
            "ward_info": {
                "ward_name": "Ward No. 4, Kavre",
                "location_type": "Hilly terrain / Steep slopes",
                "emergency_helpline": "+977-11-440123"
            },
            "risk_metrics": {
                "landslide_risk_score": 88.5,
                "flood_risk_score": 25.0,
                "soil_type": "Clay",
                "slope_degree": 38,
                "safe_buffer_distance_meters": 150,
                "active_hazards": "Active slope displacement and minor mudslides near main market road."
            },
            "safe_zones_and_shelters": [
                {
                    "name": "Kavre Ward 4 Secondary School Compound",
                    "capacity": "250 people",
                    "status": "OPEN",
                    "elevation": "High / Stable ground",
                    "distance_from_market": "600 meters north"
                },
                {
                    "name": "Mahadevsthan Community Hall",
                    "capacity": "100 people",
                    "status": "OPEN",
                    "elevation": "High",
                    "distance_from_market": "1.2 km east"
                }
            ],
            "critical_services": {
                "medical_aid": "Ward Health Post (Open 24/7 with first aid supplies)",
                "open_roads": "Upper ridge road is OPEN. Main market road is CLOSED due to debris.",
                "relief_distribution": "Food and clean water packets available at Ward Office.",
                "power_grid_status": "Partial blackout in low-lying zones."
            },
            "safety_protocols": [
                "Move away from steep slopes immediately if continuous rainfall occurs.",
                "Do not attempt to clear landslip debris manually without local authorities.",
                "Keep emergency bags packed with essential medication and documents."
            ]
        },
        5: {
            "ward_info": {
                "ward_name": "Ward No. 5, Kavre",
                "location_type": "River basin / Valley floor",
                "emergency_helpline": "+977-11-440555"
            },
            "risk_metrics": {
                "landslide_risk_score": 12.0,
                "flood_risk_score": 85.0,
                "soil_type": "Sandy alluvial",
                "slope_degree": 6,
                "safe_buffer_distance_meters": 200,
                "active_hazards": "River bank overflowing near the central bridge; high water velocity."
            },
            "safe_zones_and_shelters": [
                {
                    "name": "Ward 5 Community Health Post (Upper Elevation)",
                    "capacity": "300 people",
                    "status": "OPEN",
                    "elevation": "High ground above flood line",
                    "distance_from_river": "450 meters uphill"
                },
                {
                    "name": "Shree Ganesh Primary School Ground",
                    "capacity": "150 people",
                    "status": "OPEN",
                    "elevation": "Moderate high ground",
                    "distance_from_river": "800 meters west"
                }
            ],
            "critical_services": {
                "medical_aid": "Red Cross Emergency Tent setup near Ganesh School.",
                "open_roads": "Bridge crossing is CLOSED. North bypass highway is OPEN for vehicles.",
                "relief_distribution": "Dry rations and water purification tablets at Health Post.",
                "power_grid_status": "Main power cut off near riverbank for safety precautions."
            },
            "safety_protocols": [
                "Maintain at least a 200-meter distance from the riverbank.",
                "Do not cross flooded bridges on foot or motorbikes.",
                "Boil water before drinking to avoid waterborne contamination."
            ]
        }
    }
    return mock_database.get(ward_id, None)


# ==========================================
# 2. Resilient API Execution Engine
# ==========================================
def safe_generate_content(prompt: str):
    """
    Queries Google API for currently supported models, filters for text generation models,
    and executes requests with fallback retries.
    """
    valid_models = []
    
    try:
        # Dynamically pull models available on your API key
        for m in client.models.list():
            model_id = m.name.replace("models/", "") if hasattr(m, "name") else str(m)
            # Match flash/pro generation models and filter out image/audio/embedding tools
            if any(k in model_id for k in ["flash", "pro"]) and not any(x in model_id for x in ["image", "tts", "embedding", "realtime"]):
                valid_models.append(model_id)
        
        # Sort so newer models like gemini-2.5 run first
        valid_models.sort(reverse=True)
    except Exception as e:
        print(f"Failed to fetch model list: {e}")

    # Fallback list if the API list call returned empty or failed
    if not valid_models:
        valid_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']

    # Try each model
    for model_name in valid_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and hasattr(response, 'text') and response.text:
                    print(f"✅ Success using model: {model_name}")
                    return response.text
            except Exception as e:
                print(f"[{model_name}] Attempt {attempt+1} failed: {str(e)}")
                time.sleep(1)

    return "⚠️ All API model attempts failed. Please check your API key or network connection."


# ==========================================
# 3. Dynamic Response Logic
# ==========================================
def respond_to_user(message, history, ward_id, language):
    if not message.strip():
        return "Please enter a valid query."

    raw_data = get_ward_data_from_db(int(ward_id))
    if not raw_data:
        return f"No database records available for Ward {ward_id}."

    system_instructions = f"""
    You are a proactive Emergency Response AI Agent for local authorities and residents in Nepal.
    
    CORE OPERATIONAL DIRECTIVES:
    1. Language Output: Translate and answer ENTIRELY in {language}. 
       Do not append English labels in parentheses if non-English is selected.
    2. Proactive Emergency Assistance:
       - Directly answer the user's explicit question first.
       - Highlight key hazards and exact safe distances (`safe_buffer_distance_meters`).
       - Provide relevant shelter, road status, or medical info based on context.
       - End with immediate safety steps and local emergency contact info (`emergency_helpline`).
    3. Format & Visuals:
       - Use clean formatting with bold titles and bullet points for immediate readability.
       - If user asks for "short" or "quick", limit output to 3 concise bullet points.
    """

    full_prompt = f"""
    {system_instructions}

    User Question: "{message}"

    Comprehensive Ward Real-Time Data Record:
    {json.dumps(raw_data, indent=2)}
    """

    return safe_generate_content(full_prompt)


# ==========================================
# 4. Custom Visual Styling
# ==========================================
custom_css = """
.gradio-container { max-width: 950px !important; margin: 0 auto !important; }
#custom_chatbot { height: 530px !important; overflow-y: auto !important; }
"""

# ==========================================
# 5. UI Layout Interface
# ==========================================
with gr.Blocks(css=custom_css, title="Nepal Disaster AI Assistant") as demo:
    gr.Markdown("# 🇳🇵 Localized Emergency AI Response Agent")
    gr.Markdown("Real-time disaster risk queries, buffer zones, open roads, and emergency shelters for local wards in Nepal.")
    
    with gr.Row():
        ward_dropdown = gr.Dropdown(
            choices=[4, 5], 
            value=5, 
            label="📍 Target Ward"
        )
        lang_dropdown = gr.Dropdown(
            choices=["English", "Nepali (नेपाली)", "Hindi (हिंदी)", "Chinese (中文)"], 
            value="English", 
            label="🌐 Response Language"
        )

    chatbot = gr.Chatbot(elem_id="custom_chatbot", show_copy_button=True)

    chat_interface = gr.ChatInterface(
        fn=respond_to_user,
        additional_inputs=[ward_dropdown, lang_dropdown],
        chatbot=chatbot
    )

if __name__ == "__main__":
    demo.launch(share=True)