import gradio as gr
from ai_engine import process_conversational_query

custom_css = """
/* Fullscreen zero-margin reset */
body, .gradio-container {
    background-color: #0F172A !important;
    color: #F8FAFC !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100vw !important;
}

/* Floating orange toggle button */
#toggle_btn_overlay {
    position: absolute !important;
    top: 12px !important;
    left: 12px !important;
    z-index: 99999 !important;
    background-color: #EA580C !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    cursor: pointer !important;
    width: auto !important;
}

/* Map area */
#map_placeholder {
    background: #1E293B;
    border: 1px solid #334155;
    height: 98vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748B;
    font-size: 16px;
}

/* Sidebar styling */
#chat_panel {
    background: #111827 !important;
    border-left: 1px solid #1F2937 !important;
    padding: 10px !important;
    height: 98vh !important;
}

/* Header & Compact Language Dropdown FIX */
.chat-header-row {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 5px !important;
    margin-bottom: 8px !important;
}

.chat-header-title {
    font-size: 13px !important;
    font-weight: 700 !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

/* Kills Gradio wrapper wasted space for dropdown */
/* Real-world compact rectangle dropdown fix */
.lang-dropdown-wrapper {
    width: 55px !important;
    min-width: 55px !important;
    max-width: 55px !important;
    margin: 0 !important;
    padding: 0 !important;
    flex-grow: 0 !important;
}

.lang-dropdown-wrapper .form, 
.lang-dropdown-wrapper .block,
.lang-dropdown-wrapper .wrap {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    min-height: unset !important;
}

.lang-dropdown-wrapper select {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    color: #9CA3AF !important;
    padding: 2px 4px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    height: 24px !important;
    min-height: 24px !important;
    width: 100% !important;
    cursor: pointer !important;
}

/* Compact Typography */
.gradio-container .message {
    font-size: 12px !important;
    line-height: 1.35 !important;
    padding: 6px 10px !important;
}

/* Pill Input Bar Fix */
.pill-input-box textarea {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 18px !important;
    color: #F3F4F6 !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
}

.send-btn-circle {
    background-color: #2563EB !important;
    color: white !important;
    border-radius: 50% !important;
    min-width: 32px !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    border: none !important;
}
"""

def toggle_sidebar(visible_state):
    # Toggles visibility boolean cleanly
    return gr.update(visible=not visible_state), not visible_state

def respond(message, history, language):
    if not message or not message.strip():
        return "", history
    bot_message = process_conversational_query(message, history, language)
    history.append((message, bot_message))
    return "", history

with gr.Blocks(css=custom_css, title="Pravah AI Risk Intelligence") as demo:
    # State tracking sidebar state (Starts Hidden = False)
    sidebar_visible = gr.State(False)

    # Absolute Top-Left Floating Toggle Button
    toggle_btn = gr.Button("🟠 Pravah AI", elem_id="toggle_btn_overlay")

    with gr.Row(equal_height=True):
        # Map Column (100% width by default when sidebar is hidden)
        with gr.Column(scale=5, min_width=200) as map_column:
            gr.HTML('<div id="map_placeholder">📍 Interactive Map (Full View Area)</div>')

        # Sidebar Chat Panel (Hidden by default)
        with gr.Column(scale=1, min_width=240, visible=False, elem_id="chat_panel") as chat_column:
            
            # Header Row
            with gr.Row(elem_classes=["chat-header-row"]):
                lang = gr.Dropdown(
                    choices=["ENGLISH", "NEPALI", "HINDI", "CHINESE"],
                    value="EN",
                    show_label=False,
                    container=False,
                    elem_classes=["lang-dropdown-wrapper"]
                )
            
            chatbot = gr.Chatbot(height=520, show_label=False)

            # Clean Input Bar
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask weather or risk...",
                    show_label=False,
                    container=False,
                    scale=5,
                    elem_classes=["pill-input-box"]
                )
                send = gr.Button("⬆", elem_classes=["send-btn-circle"], scale=0)

            send.click(respond, inputs=[msg, chatbot, lang], outputs=[msg, chatbot])
            msg.submit(respond, inputs=[msg, chatbot, lang], outputs=[msg, chatbot])

    # Dynamic Toggle Handler
    toggle_btn.click(
        fn=toggle_sidebar,
        inputs=[sidebar_visible],
        outputs=[chat_column, sidebar_visible]
    )

if __name__ == "__main__":
    demo.launch(share=True)