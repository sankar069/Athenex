import streamlit as st
import requests

st.set_page_config(page_title="Athenex | Tech & Gym Chatbot", layout="centered")
st.title("🏛️ Athenex – Your Tech + Gym AI Assistant")

# Get token from Streamlit Secrets
HF_TOKEN = st.secrets["hf_token"]

# Model selector
MODEL_OPTIONS = {
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.2",
    "Zephyr 7B Beta": "HuggingFaceH4/zephyr-7b-beta",
    "OpenChat 3.5": "openchat/openchat-3.5-1210",
    "Phi-2": "microsoft/phi-2",
    "TinyLlama Chat": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "Nous Hermes 2 Mistral": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO"
}

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Greek_Temple.svg/2560px-Greek_Temple.svg.png", width=120)
    st.header("⚙️ Athenex Settings")
    selected_model_name = st.selectbox("🧠 Choose an AI Model", list(MODEL_OPTIONS.keys()))
    selected_domain = st.radio("🎯 Domain Focus", ["Tech", "Gym"], horizontal=True)

model_id = MODEL_OPTIONS[selected_model_name]

# Create system prompt for Athenex
system_prompt = f"""
You are Athenex, a luxurious, articulate, and expert-level AI assistant. You specialize in {selected_domain} topics.

If the user asks about:
- **Tech**: Provide deep, accurate, and modern answers about AI, coding, programming, gadgets, etc.
- **Gym**: Give expert fitness advice, routines, supplements, nutrition tips, recovery guidance, etc.

Be concise, empowering, and intelligent. Do not hallucinate answers. Speak in an elegant and slightly futuristic tone.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Display past chat
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
user_input = st.chat_input("💬 Ask Athenex anything about Tech or Gym...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    payload = {
        "inputs": {
            "past_user_inputs": [m["content"] for m in st.session_state.messages if m["role"] == "user"],
            "generated_responses": [m["content"] for m in st.session_state.messages if m["role"] == "assistant"],
            "text": user_input
        }
    }

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        output = response.json()

        if isinstance(output, dict) and "generated_text" in output:
            reply = output["generated_text"]
        elif isinstance(output, list) and "generated_text" in output[0]:
            reply = output[0]["generated_text"]
        else:
            reply = "⚠️ Athenex couldn't generate a proper response. Try another query."

    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})