import streamlit as st
import pandas as pd
import time

# Configuración de la página
# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦", layout="centered")

# --- CSS PERSONALIZADO: ESTILO MINIMALISTA Y LLAMATIVO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    :root {
        --primary-color: #6C63FF; /* Un morado vibrante pero elegante */
        --background-color: #F8F9FA;
        --card-bg: #FFFFFF;
        --text-color: #2D3436;
        --subtext-color: #636E72;
    }

    /* Reset global */
    .stApp {
        background-color: var(--background-color);
        font-family: 'Inter', sans-serif;
    }

    /* Ocultar elementos de Streamlit por defecto */
    #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px;
    }

    /* Título Principal */
    h1 {
        font-weight: 800 !important;
        color: var(--text-color) !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        text-align: center;
        color: var(--subtext-color);
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }

    /* Input de Chat Estilizado */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        border: 2px solid transparent !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease;
        background-color: var(--card-bg) !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 8px 25px rgba(108, 99, 255, 0.15) !important;
        transform: translateY(-2px);
    }
    
    [data-testid="stChatInput"] input {
        color: var(--text-color) !important;
    }

    /* Burbujas de Chat */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    }

    /* Burbuja del Usuario */
    [data-testid="chatAvatarIcon-user"] {
        background-color: var(--primary-color) !important;
    }
    div[data-testid="stChatMessage"]:nth-child(even) [data-testid="stMarkdownContainer"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    div[data-testid="stChatMessage"]:nth-child(even) [data-testid="stMarkdownContainer"] p {
        color: white !important;
    }

    /* Burbuja del Asistente */
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #00B894 !important; /* Verde menta para el bot */
    }
    div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stMarkdownContainer"] {
        background-color: var(--card-bg) !important;
        border: 1px solid #EFEFEF !important;
        color: var(--text-color) !important;
    }

    /* Tarjeta de Estado (Custom HTML) */
    .status-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border-left: 5px solid var(--primary-color);
        margin-top: 1rem;
    }
    .status-title {
        color: var(--subtext-color);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .client-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 1rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .status-success { background: #E6FFFA; color: #00B894; }
    .status-process { background: #E3F2FD; color: #0984E3; }
    .status-error { background: #FFEBEE; color: #D63031; }

    </style>
""", unsafe_allow_html=True)

st.title("📦 Rastreo de Envíos")
st.markdown('<p class="subtitle">Ingresa tu número de pedido para consultar el estado en tiempo real.</p>', unsafe_allow_html=True)

# --- 1. CONEXIÓN A LOS DATOS ---
@st.cache_data(ttl=60)
def cargar_datos():
    # TU LINK DE GOOGLE SHEETS
    url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5z9zHagRYwvPxMcQK_prKnH6p4v-rCPpNksjzxeiBFt2tCY0ZeKoOLYUQXrccDyNNuTRQj5Di2jvX/pub?gid=0&single=true&output=csv"
    
    try:
        df = pd.read_csv(url_csv, dtype=str)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

# --- 2. INTERFAZ DE CHAT ---

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_order" not in st.session_state:
    st.session_state.last_order = None

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_html"):
            st.markdown(message["content"], unsafe_allow_html=True)
        else:
            st.markdown(message["content"])
# --- 3. LÓGICA DEL BOT ---

if prompt := st.chat_input("Ej: PED-12345"):
    
    # Mensaje usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta bot
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Consultando...*")
        time.sleep(0.6) 
        
        prompt_lower = prompt.lower()
        
        # 1. DETECCIÓN DE INTENCIÓN: CUSTODIA
        if "custodia" in prompt_lower:
            if st.session_state.last_order:
                lo = st.session_state.last_order
                if "custodia" in str(lo['estado']).lower():
                    resp = f"Confirmado, **{lo['cliente']}**. Tu pedido **{lo['pedido']}** se encuentra actualmente en **Custodia**."
                else:
                    resp = f"No, el pedido **{lo['pedido']}** no está en custodia. Su estado actual es: **{lo['estado']}**."
            else:
                resp = "Para confirmarte si un pedido está en custodia, por favor indícame primero el número de pedido."
            
            message_placeholder.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp, "is_html": False})

        # 2. BÚSQUEDA SMART (SI NO SE MANEJÓ POR KEYWORD O SI PARECE TENER UN ID)
        else:
            if not df.empty and 'pedido' in df.columns:
                lista_pedidos_reales = df['pedido'].astype(str).tolist()
                pedido_encontrado_id = None
                
                palabras_usuario = prompt.split()
                for palabra in palabras_usuario:
                    palabra_limpia = palabra.strip(".,;?!¡¿'\"")
                    match = next((x for x in lista_pedidos_reales if str(x).lower() == palabra_limpia.lower()), None)
                    if match:
                        pedido_encontrado_id = match
                        break 

                clave_busqueda = pedido_encontrado_id if pedido_encontrado_id else prompt.strip()
                resultado = df[df['pedido'] == clave_busqueda]
                
                if not resultado.empty:
                    estado = resultado.iloc[0]['estado']
                    cliente = resultado.iloc[0]['cliente']
                    
                    # Guardar en contexto
                    st.session_state.last_order = {
                        "pedido": clave_busqueda,
                        "cliente": cliente,
                        "estado": estado
                    }
                    
                    badge_class = "status-process"
                    if "entregado" in str(estado).lower(): badge_class = "status-success"
                    elif "cancelado" in str(estado).lower() or "error" in str(estado).lower(): badge_class = "status-error"
                    elif "custodia" in str(estado).lower(): badge_class = "status-process" # Podríamos usar otro color si existiera

                    respuesta_html = f"""
                    <div class="status-card">
                        <div class="status-title">Detalles del Pedido</div>
                        <div class="client-name">{cliente}</div>
                        <div>
                            Estado: <span class="status-badge {badge_class}">{estado}</span>
                        </div>
                    </div>
                    """
                    message_placeholder.markdown(respuesta_html, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_html, "is_html": True})
                
                else:
                    respuesta_texto = f"🔍 No pudimos identificar un pedido válido en: \"**{prompt}**\"."
                    message_placeholder.markdown(respuesta_texto)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_texto, "is_html": False})
            else:
                 respuesta_texto = "⚠️ El sistema no está disponible."
                 message_placeholder.markdown(respuesta_texto)
                 st.session_state.messages.append({"role": "assistant", "content": respuesta_texto, "is_html": False})