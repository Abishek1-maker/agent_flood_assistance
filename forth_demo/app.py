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
    background: #F8FAFC;
    border: 1px solid #334155;
    height: 98vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748B;
    font-size: 16px;
}

/* Fixed-width sidebar styling */
#chat_panel {
    background: #111827 !important;
    border-left: 1px solid #1F2937 !important;
    padding: 10px !important;
    height: 98vh !important;
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    flex-grow: 0 !important;
}

/* Header row - alignment to the right */
.chat-header-row,
.chat-header-row .block,
.chat-header-row .form {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 0 8px 0 !important;
    display: flex !important;
    justify-content: flex-end !important;
}

.chat-header-title {
    font-size: 13px !important;
    font-weight: 700 !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

/* 1. Sets outer container to white and shrinks width */
.lang-dropdown-wrapper,
.lang-dropdown-wrapper .block {
    background: #FFFFFF !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-left: auto !important;
    width: fit-content !important;
    min-width: unset !important;
    border-radius: 8px !important;
}

/* 2. Sets all internal wrappers to white */
.lang-dropdown-wrapper div,
.lang-dropdown-wrapper .form,
.lang-dropdown-wrapper .wrap,
.lang-dropdown-wrapper .secondary-wrap {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: fit-content !important;
    min-width: unset !important;
}
/* Compact white EN badge */
.lang-dropdown-wrapper select,
.lang-dropdown-wrapper input {
    background-color: #6e86cf !important;
    border: 1px solid transparent !important;
    color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    padding: 2px 6px !important;
    border-radius: 6px !important;
    height: 26px !important;
    width: 55px !important;
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
    return gr.update(visible=not visible_state), not visible_state

def respond(message, history, language):
    if not message or not message.strip():
        return "", history
    bot_message = process_conversational_query(message, history, language)
    history.append((message, bot_message))
    return "", history

with gr.Blocks(css=custom_css, title="Pravah AI Risk Intelligence") as demo:
    sidebar_visible = gr.State(False)

    toggle_btn = gr.Button("🟠 Pravah AI", elem_id="toggle_btn_overlay")

    with gr.Row(equal_height=True):
        with gr.Column(scale=5, min_width=200) as map_column:
            gr.HTML('<div id="map_placeholder">📍 Interactive Map (Full View Area)</div>')

        with gr.Column(scale=0, min_width=240, visible=False, elem_id="chat_panel") as chat_column:
            
            # Header Row without default grey container
            with gr.Row(elem_classes=["chat-header-row"], container=False):
                lang = gr.Dropdown(
                    choices=["EN", "NE", "HI", "ZH"],
                    value="EN",
                    show_label=False,
                    container=False,
                    scale=0,
                    elem_classes=["lang-dropdown-wrapper"]
                )
            
            chatbot = gr.Chatbot(height=520, show_label=False)

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

    toggle_btn.click(
        fn=toggle_sidebar,
        inputs=[sidebar_visible],
        outputs=[chat_column, sidebar_visible]
    )

if __name__ == "__main__":
    demo.launch(share=True)