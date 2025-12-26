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
        position: relative;
        overflow: hidden;
    }
    
    /* Progress Bar / Stepper */
    .progress-container {
        margin: 2rem 0 1rem 0;
        position: relative;
        width: 100%;
        height: 6px;
        background: #F1F2F6;
        border-radius: 10px;
    }
    .progress-bar {
        height: 100%;
        background: var(--primary-color);
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }
    .truck-icon {
        position: absolute;
        top: -25px;
        right: -15px;
        font-size: 24px;
        transition: all 1s ease-in-out;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .stages {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        font-size: 0.7rem;
        color: var(--subtext-color);
        text-transform: uppercase;
        font-weight: 600;
    }
    .stage-item { flex: 1; text-align: center; position: relative; }
    .stage-item:first-child { text-align: left; }
    .stage-item:last-child { text-align: right; }

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
        padding: 0.4rem 0.8rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.8rem;
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
                
                # Re-usamos la lógica de visualización para consistencia
                status_map = {
                    "pendiente de pago": {"prog": 10, "class": "status-process", "icon": "💰"},
                    "en proceso": {"prog": 40, "class": "status-process", "icon": "⚙️"},
                    "enviado": {"prog": 75, "class": "status-process", "icon": "🚛"},
                    "entregado": {"prog": 100, "class": "status-success", "icon": "✅"},
                    "custodia": {"prog": 60, "class": "status-process", "icon": "📦"},
                    "cancelado": {"prog": 0, "class": "status-error", "icon": "❌"}
                }
                st_lower = str(lo['estado']).lower()
                config = status_map.get(st_lower, {"prog": 0, "class": "status-process", "icon": "🚛"})
                if config["prog"] == 0 and st_lower != "cancelado":
                    for key, val in status_map.items():
                        if key in st_lower:
                            config = val
                            break

                respuesta_html = f"""
                <div class="status-card">
                    <div class="status-title">Consulta de Custodia</div>
                    <div class="client-name">{lo['cliente']}</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {config['prog']}%;">
                            <div class="truck-icon" style="left: calc({config['prog']}% - 20px);">🚛</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem;">
                        El pedido <b>{lo['pedido']}</b> {"SÍ" if "custodia" in st_lower else "NO"} está en custodia.<br>
                        Estado actual: <span class="status-badge {config['class']}">{config['icon']} {lo['estado']}</span>
                    </div>
                </div>
                """
                message_placeholder.markdown(respuesta_html, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_html, "is_html": True})
            else:
                resp = "🕵️ Para decirte si un pedido está en custodia, primero dime el número de pedido."
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
                    
                    # --- CÁLCULO DE PROGRESO ---
                    status_map = {
                        "pendiente de pago": {"prog": 10, "class": "status-process", "icon": "💰"},
                        "en proceso": {"prog": 40, "class": "status-process", "icon": "⚙️"},
                        "enviado": {"prog": 75, "class": "status-process", "icon": "🚛"},
                        "entregado": {"prog": 100, "class": "status-success", "icon": "✅"},
                        "custodia": {"prog": 60, "class": "status-process", "icon": "📦"},
                        "cancelado": {"prog": 0, "class": "status-error", "icon": "❌"}
                    }
                    
                    st_lower = str(estado).lower()
                    config = status_map.get(st_lower, {"prog": 0, "class": "status-process", "icon": "🚛"})
                    
                    # Si no está en el mapa, intentamos búsqueda parcial
                    if config["prog"] == 0 and st_lower != "cancelado":
                        for key, val in status_map.items():
                            if key in st_lower:
                                config = val
                                break

                    # Guardar en contexto
                    st.session_state.last_order = {
                        "pedido": clave_busqueda,
                        "cliente": cliente,
                        "estado": estado
                    }
                    
                    # Generar HTML Card con Progress Bar
                    respuesta_html = f"""
                    <div class="status-card">
                        <div class="status-title">Estado del Envío</div>
                        <div class="client-name">{cliente}</div>
                        
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {config['prog']}%;">
                                <div class="truck-icon" style="left: calc({config['prog']}% - 20px);">🚛</div>
                            </div>
                        </div>
                        <div class="stages">
                            <div class="stage-item">Pago</div>
                            <div class="stage-item">Proceso</div>
                            <div class="stage-item">En Camino</div>
                            <div class="stage-item">Entregado</div>
                        </div>

                        <div style="margin-top: 1.5rem;">
                            Pedido: <b>{clave_busqueda}</b> • 
                            <span class="status-badge {config['class']}">{config['icon']} {estado}</span>
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