import os
import json
from dotenv import load_dotenv
from google import genai

# 1. Load secret key from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# PART 1: Database Retrieval Function
# ==========================================
def get_ward_data_from_db(ward_id: int):
    """
    Simulates fetching raw disaster data from your project's database.
    """
    mock_database = {
        4: {
            "ward_name": "Ward No. 4, Kavre",
            "landslide_risk_score": 88.5,
            "flood_risk_score": 25.0,
            "soil_type": "Clay",
            "slope_degree": 38,
            "recent_incidents": "1 minor landslide reported near main market road."
        },
        5: {
            "ward_name": "Ward No. 5, Kavre",
            "landslide_risk_score": 12.0,
            "flood_risk_score": 85.0,
            "soil_type": "Sandy",
            "slope_degree": 6,
            "recent_incidents": "River water overflowing near local bridge."
        }
    }
    return mock_database.get(ward_id, None)

# ==========================================
# PART 2: The AI Agent Function
# ==========================================
def disaster_ai_agent(user_query: str, ward_id: int) -> str:
    """
    Fetches raw data from the DB function, passes it to Gemini, 
    and returns a human-friendly response.
    """
    raw_data = get_ward_data_from_db(ward_id)
    
    if not raw_data:
        return f"Sorry, I couldn't find any records for Ward {ward_id} in the database."

    full_prompt = f"""
    You are an AI Disaster Assistance Agent for local authorities and citizens in Nepal.
    Your task is to convert raw database metrics into clear, empathetic, and actionable 
    natural language alerts. Use formatting like bold text and bullet points.

    User Query: "{user_query}"

    Database Record Loaded:
    {json.dumps(raw_data, indent=2)}

    Please answer the user query based strictly on the loaded database record above.
    """

    try:
        response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=full_prompt,
)
        # Extract only text parts to eliminate warnings
        text_parts= [
            part.text for part in response.candidates[0].content.parts
            if hasattr(part, 'text') and part.text is not None
        ]
        return "".join(text_parts)

    except Exception as e:
        return f"Error communicating with AI model: {str(e)}"

# ==========================================
# PART 3: Execution / Testing
# ==========================================
# ==========================================
# PART 3: Interactive Terminal Chat
# ==========================================
if __name__ == "__main__":
    print("=============================================")
    print("   🇳🇵 Nepal Disaster AI Agent Terminal Chat   ")
    print("=============================================")
    print("Type 'exit' or 'quit' anytime to stop the program.\n")

    while True:
        # 1. Ask user for the Ward Number
        ward_input = input("Enter Ward Number (e.g., 4 or 5): ").strip()
        
        # Check if user wants to exit
        if ward_input.lower() in ['exit', 'quit']:
            print("Shutting down AI Agent. Stay safe!")
            break

        # Validate that the ward input is a number
        if not ward_input.isdigit():
            print("❌ Please enter a valid number for the ward ID!\n")
            continue

        ward_id = int(ward_input)

        # 2. Ask user for their specific question
        user_query = input(f"Ask your question about Ward {ward_id}: ").strip()
        
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down AI Agent. Stay safe!")
            break

        if not user_query:
            print("❌ Question cannot be empty!\n")
            continue

        # 3. Call the AI agent and display the response
        print("\n⏳ Fetching database metrics and generating response...\n")
        answer = disaster_ai_agent(user_query=user_query, ward_id=ward_id)
        
        print("---------------------------------------------")
        print(answer)
        print("---------------------------------------------\n")