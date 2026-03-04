import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ---------------------------------------------------------------------------
# CONFIG & STYLE
# ---------------------------------------------------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("OPENAI_API_KEY", "") 
BOT_NAME = "Bot Vascote"
BOT_AVATAR = "🧑"
USER_AVATAR = "👨🏻"

st.set_page_config(page_title=f"{BOT_NAME}", page_icon="🤖", layout="centered")

# --- CSS MODERNO COM FOCO NO INPUT EM AZUL ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #0b0e14;
        color: #e0e0e0;
    }

    /* Header Styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 15px;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0b0e14; }
    ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 10px; }

    /* Tags/Labels */
    .stSlider label, .stSelectbox label {
        color: #9ca3af !important;
        font-weight: 600;
    }

    /* --- O AJUSTE QUE PEDISTE: Trocar o vermelho pelo azul no foco do input --- */
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PERSONALITY & CORE
# ---------------------------------------------------------------------------
def load_personality(path: str = "my_data.txt") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError: return ""

PERSONALITY_DATA = load_personality()
SYSTEM_PROMPT = f"Tu és o Bot Vascote, o gémeo digital do Vasco. Fala de forma informal, com calão português (mano, ya, fds, foleiro). Sê sarcástico e engraçado. {PERSONALITY_DATA}"

genai.configure(api_key=GOOGLE_API_KEY)

@st.cache_resource
def get_available_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except: return ["gemini-1.5-flash", "gemini-pro"]

available_models = get_available_models()

# ---------------------------------------------------------------------------
# UI ELEMENTS
# ---------------------------------------------------------------------------
st.markdown('<h1 class="main-title">Bot Vascote.exe</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280;'>O teu bro digital pronto para ajudar</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Painel de Controlo")
    model_choice = st.selectbox("Cérebro", available_models, index=0)
    temperature = st.slider("Nível de Estupidez", 0.0, 1.5, 0.9, 0.1)
    st.divider()
    if st.button("Limpar Memória", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# CHAT ENGINE
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = BOT_AVATAR if msg["role"] == "assistant" else USER_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Manda vir, mano..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        try:
            model = genai.GenerativeModel(model_name=model_choice, system_instruction=SYSTEM_PROMPT)
            chat = model.start_chat(history=[])
            
            response_placeholder = st.empty()
            full_response = ""
            
            response = chat.send_message(prompt, stream=True, 
                                         generation_config=genai.types.GenerationConfig(temperature=temperature))

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"💀 Deu raia: `{e}`")