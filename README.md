terminal -> for 1st and second demo

-> python3 app.py


* **`google-genai`**: Official Google SDK to connect to and generate content from Gemini AI models.
* **`gradio`**: Build and serve the web user interface (chat window, dropdowns, and layouts).
* **`gradio-client`**: Required backend utility for handling Gradio API routing and UI event streams.
* **`pydantic==2.10.6`**: Prevents schema generation crashes (`TypeError: argument of type 'bool' is not iterable`) between Gradio and Pydantic.
* **`python-dotenv`**: Loads secret variables (like `GEMINI_API_KEY`) securely from a local `.env` file into Python.
* **`markdown`**: Converts AI Markdown responses (bullet points, bold text) into clean HTML for custom visual display.
