import os
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

custom_css = """
#modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 15, 15, 0.6);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}

#modal-card {
    background: var(--background-fill-primary);
    border: 1px solid var(--border-color-primary);
    border-radius: 12px;
    padding: 32px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    margin: auto;
}

#chat-wrapper {
    max-width: 850px !important;
    margin: 20px auto !important;
    height: 90vh !important;
    border: none !important;
}

#input-row {
    align-items: flex-end;
    background: var(--background-fill-secondary);
    border-radius: 16px;
    padding: 8px;
    margin-top: 10px;
}
"""

def initialize_session(gemini, pinecone, github, owner, repo):
    if not all([gemini, pinecone, github, owner, repo]):
        gr.Warning("All fields are required to initialize the workspace.")
        return gr.update(visible=True), gemini, pinecone, github

    try:
        headers = {
            "x-gemini-key": gemini,
            "x-pinecone-key": pinecone,
            "x-github-token": github
        }
        payload = {"owner": owner, "repo": repo}

        # FIX: Enable stream=True so the generator endpoint doesn't lock your client
        response = requests.post(
            f"{API_BASE_URL}/index_repository/", 
            json=payload, 
            headers=headers, 
            stream=True
        )
        response.raise_for_status()

        # Iterate through the backend yield events to let the process complete
        for line in response.iter_lines():
            if line:
                print(f"[Backend Log]: {line.decode('utf-8')}")

        # Now the modal hides cleanly because the stream has wrapped up!
        return gr.update(visible=False), gemini, pinecone, github

    except Exception as e:
        gr.Warning(f"Connection failed: {str(e)}")
        return gr.update(visible=True), "", "", ""

def chat_with_codebase(user_message, chat_history, gemini, pinecone, github):
    if chat_history is None:
        chat_history = []

    try:
        headers = {
            "x-gemini-key": gemini,
            "x-pinecone-key": pinecone,
            "x-github-token": github
        }
        payload = {"question": user_message}

        response = requests.post(f"{API_BASE_URL}/ask/", json=payload, headers=headers)
        response.raise_for_status()

        ai_response = response.json().get("response", "No response received.")

        # FIX: Append as modern message dicts instead of a tuple
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": ai_response})
        return "", chat_history

    except Exception as e:
        # FIX: Error message handling in the new schema format
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": f"**Error:** {str(e)}"})
        return "", chat_history

# 'base' string key handles the clean, non-distracting minimalist interface natively
with gr.Blocks(theme="base", css=custom_css, title="Code RAG") as app:

    state_gemini = gr.State("")
    state_pinecone = gr.State("")
    state_github = gr.State("")

    with gr.Column(elem_id="modal-overlay", visible=True) as auth_modal:
        with gr.Column(elem_id="modal-card"):
            gr.Markdown("## Initialize Workspace")

            with gr.Group():
                gemini_input = gr.Textbox(label="Gemini API Key", type="password")
                pinecone_input = gr.Textbox(label="Pinecone API Key", type="password")
                github_input = gr.Textbox(label="GitHub PAT", type="password")

            with gr.Row():
                owner_input = gr.Textbox(label="Owner", placeholder="octocat")
                repo_input = gr.Textbox(label="Repository", placeholder="hello-world")

            connect_btn = gr.Button("Connect Engine", variant="primary")

    with gr.Column(elem_id="chat-wrapper"):
        # FIXED: Removed 'type' and 'show_copy_button' for legacy-compatible runtime
        chatbot = gr.Chatbot(
            height=700,
            show_label=False
        )

        with gr.Row(elem_id="input-row"):
            msg_input = gr.Textbox(
                scale=8,
                show_label=False,
                placeholder="Ask about the codebase...",
                container=False,
                lines=1,
                max_lines=10
            )
            submit_btn = gr.Button("Send", scale=1, variant="secondary")


    connect_btn.click(
        fn=initialize_session,
        inputs=[gemini_input, pinecone_input, github_input, owner_input, repo_input],
        outputs=[auth_modal, state_gemini, state_pinecone, state_github]
    )

    msg_input.submit(
        fn=chat_with_codebase,
        inputs=[msg_input, chatbot, state_gemini, state_pinecone, state_github],
        outputs=[msg_input, chatbot]
    )

    submit_btn.click(
        fn=chat_with_codebase,
        inputs=[msg_input, chatbot, state_gemini, state_pinecone, state_github],
        outputs=[msg_input, chatbot]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)


