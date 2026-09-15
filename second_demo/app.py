import gradio as gr
from ai_engine import process_disaster_query
import markdown

# ==========================================
# 1. Custom Dark Theme CSS (PRAVAH Layout)
# ==========================================
custom_css = """
/* App Canvas */
body, .gradio-container {
    background-color: #121212 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #E0E0E0 !important;
}

/* Main Container Shell */
#pravah_shell {
    max-width: 700px !important;
    margin: 10px auto !important;
    background: #181818 !important;
    border-radius: 16px !important;
    border: 1px solid #282828 !important;
    padding: 20px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
}

/* Custom Dropdowns */
.dark-dropdown {
    background: #222222 !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
}
.dark-dropdown * {
    background: #222222 !important;
    color: #FFFFFF !important;
}

/* Chat History Display Area */
#chat_viewport {
    height: 460px !important;
    overflow-y: auto !important;
    padding-right: 8px !important;
    margin-bottom: 12px !important;
}

/* Chat Message Card Styling */
.msg-row {
    display: flex;
    margin-bottom: 20px;
    align-items: flex-start;
}
.msg-row.user {
    justify-content: flex-end;
}
.msg-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background-color: #2F5241;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: bold;
    margin-right: 10px;
    flex-shrink: 0;
}
.msg-content-block {
    max-width: 85%;
}
.msg-author {
    font-size: 11px;
    color: #888888;
    margin-bottom: 4px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.msg-row.user .msg-author {
    text-align: right;
}
.msg-text {
    font-size: 14px;
    line-height: 1.5;
    color: #E2E8F0;
}
.msg-row.user .msg-text {
    color: #94A3B8;
}

/* Bottom Input Card */
#input_card {
    border: 1px solid #2E3E33 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    background: #1C241F !important;
}
#input_card textarea {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
}
#send_btn {
    background-color: #2F5241 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 18px !important;
    min-width: 42px !important;
    height: 42px !important;
    cursor: pointer !important;
}
"""

# Initial greeting state
DEFAULT_CHAT_HISTORY = [
    {
        "role": "assistant",
        "content": "Hi, I'm PRAVAH. Ask me about the weather, air quality, travel conditions, or local environmental risk."
    }
]

# ==========================================
# 2. HTML Chat Renderer
# ==========================================
def render_chat_html(history):
    html = '<div id="chat_viewport">'
    for msg in history:
        # Convert markdown (bold, lists) to standard HTML
        formatted_content = markdown.markdown(msg["content"])

        if msg["role"] == "user":
            html += f'''
            <div class="msg-row user">
                <div class="msg-content-block">
                    <div class="msg-author">You</div>
                    <div class="msg-text">{formatted_content}</div>
                </div>
            </div>
            '''
        else:
            html += f'''
            <div class="msg-row bot">
                <div class="msg-avatar">🌐</div>
                <div class="msg-content-block">
                    <div class="msg-author">PRAVAH</div>
                    <div class="msg-text">{formatted_content}</div>
                </div>
            </div>
            '''
    html += '</div>'
    return html

# ==========================================
# 3. Interactive Handlers
# ==========================================
def handle_user_message(user_text, history_state, ward_id, language):
    if not user_text.strip():
        return "", history_state, render_chat_html(history_state)
    
    # Append user question
    updated_history = history_state + [{"role": "user", "content": user_text}]
    
    # Process AI query
    bot_reply = process_disaster_query(user_text, ward_id, language)
    updated_history.append({"role": "assistant", "content": bot_reply})
    
    return "", updated_history, render_chat_html(updated_history)


# ==========================================
# 4. Gradio UI Layout
# ==========================================
with gr.Blocks(css=custom_css, title="PRAVAH AI") as demo:
    history_state = gr.State(DEFAULT_CHAT_HISTORY)

    with gr.Column(elem_id="pravah_shell"):
        
        # Top Weather Status Pill
        gr.HTML("""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#1C2E24; padding:8px 14px; border-radius:8px; font-size:12px; color:#A7F3D0; font-weight:500; margin-bottom:14px; border:1px solid #234734;">
                <span>Rain likely · Kathmandu</span>
                <span>💨 4 km/h</span>
            </div>
        """)

        # Target Ward & Language Selectors
        with gr.Row():
            ward_dropdown = gr.Dropdown(
                choices=[4, 5], value=5, label="📍 Target Ward", elem_classes=["dark-dropdown"]
            )
            lang_dropdown = gr.Dropdown(
    choices=["English", "Nepali (नेपाली)", "Hindi (हिंदी)", "Chinese (中文)"], 
    value="English", 
    label="🌐 Language", 
    elem_classes=["dark-dropdown"]
)
 

        # Dynamic Chat Viewport
        chat_display = gr.HTML(value=render_chat_html(DEFAULT_CHAT_HISTORY))

        # Bottom Dock Container
        with gr.Column(elem_id="input_card"):
            user_input = gr.Textbox(
                placeholder="Ask PRAVAH anything...",
                show_label=False,
                container=False,
                lines=2
            )
            with gr.Row():
                mic_btn = gr.Button("🎙️", variant="tool", scale=1)
                gr.Markdown("<div style='flex-grow:1; text-align:center; font-size:11px; color:#6B7280; margin-top:8px;'>Type or speak your question</div>")
                send_btn = gr.Button("➔", elem_id="send_btn", scale=1)

        # Event Listeners
        send_btn.click(
            handle_user_message,
            inputs=[user_input, history_state, ward_dropdown, lang_dropdown],
            outputs=[user_input, history_state, chat_display]
        )
        
        user_input.submit(
            handle_user_message,
            inputs=[user_input, history_state, ward_dropdown, lang_dropdown],
            outputs=[user_input, history_state, chat_display]
        )

if __name__ == "__main__":
    demo.launch(share=True)