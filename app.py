import streamlit as st
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Asistente de Pedidos", page_icon="📦")

# --- CSS AGRESIVO PARA LIMPIEZA TOTAL ---
hide_st_style = """
            <style>
            /* Ocultar menú de hamburguesa, footer y cabecera decorativa */
            #MainMenu {visibility: hidden; display: none;}
            footer {visibility: hidden; display: none;}
            header {visibility: hidden; display: none;}
            
            /* Ocultar la barra superior de colores de Streamlit */
            div[data-testid="stDecoration"] {
                visibility: hidden;
                display: none;
            }

            /* Eliminar el espacio en blanco gigante de arriba */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 0rem !important;
            }
            
            /* (Opcional) Ocultar botón de 'Deploy' si apareciera */
            .stDeployButton {
                display:none;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("📦 Rastreo de Envíos")
st.markdown("Escribe tu número de pedido para saber dónde está.")

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
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy el asistente virtual. Por favor, indícame tu número de pedido."})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. LÓGICA DEL BOT ---

if prompt := st.chat_input("Escribe tu número de pedido aquí..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Buscando...")
        time.sleep(0.5) 
        
        pedido_buscado = prompt.strip()
        
        # Validación simple para evitar errores si el df está vacío
        if not df.empty and 'pedido' in df.columns:
            resultado = df[df['pedido'] == pedido_buscado]
            
            if not resultado.empty:
                estado = resultado.iloc[0]['estado']
                cliente = resultado.iloc[0]['cliente']
                respuesta = f"Hola **{cliente}**, hemos encontrado tu pedido. \n\n El estado actual es: **{estado}**."
            else:
                respuesta = f"Lo siento, no encuentro el pedido **{pedido_buscado}**. Por favor verifica el número."
        else:
             respuesta = "Lo siento, estamos actualizando la base de datos. Intenta en un momento."

        message_placeholder.markdown(respuesta)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})