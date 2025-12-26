import streamlit as st
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Asistente de Pedidos", page_icon="📦")
# --- OCULTAR MARCA DE AGUA Y MENÚ ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.title("📦 Rastreo de Envíos")
st.markdown("Escribe tu número de pedido para saber dónde está.")

# --- 1. CONEXIÓN A LOS DATOS ---
# Usamos caché para no leer el excel en cada click, pero que se actualice cada 60 segs
@st.cache_data(ttl=60)
def cargar_datos():
    # PEGA AQUÍ TU LINK DE GOOGLE SHEETS (El que termina en .csv)
    # Ejemplo ficticio:
    url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5z9zHagRYwvPxMcQK_prKnH6p4v-rCPpNksjzxeiBFt2tCY0ZeKoOLYUQXrccDyNNuTRQj5Di2jvX/pub?gid=0&single=true&output=csv"
    
    try:
        # dtype=str es VITAL para que no se borren los ceros a la izquierda (ej: 00123)
        df = pd.read_csv(url_csv, dtype=str)
        # Limpiamos espacios en los nombres de las columnas por si acaso
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

# --- 2. INTERFAZ DE CHAT ---

# Inicializar historial de chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de bienvenida del bot
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy el asistente virtual. Por favor, indícame tu número de pedido."})

# Mostrar mensajes anteriores del historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. LÓGICA DEL BOT ---

# Input del usuario (la cajita de escribir)
if prompt := st.chat_input("Escribe tu número de pedido aquí..."):
    
    # 1. Mostrar lo que el usuario escribió
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Pensar/Buscar (Simulación de "escribiendo...")
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Buscando...")
        time.sleep(0.5) # Pequeña pausa para efecto visual
        
        # Lógica de búsqueda
        # Asumimos que la columna en el excel se llama 'pedido'
        pedido_buscado = prompt.strip()
        
        # Filtramos el dataframe
        resultado = df[df['pedido'] == pedido_buscado]
        
        if not resultado.empty:
            estado = resultado.iloc[0]['estado']
            cliente = resultado.iloc[0]['cliente'] # Opcional
            respuesta = f"Hola **{cliente}**, hemos encontrado tu pedido. \n\n El estado actual es: **{estado}**."
        else:
            respuesta = f"Lo siento, no encuentro el pedido **{pedido_buscado}**. Por favor verifica el número."
            
        message_placeholder.markdown(respuesta)
    
    # 3. Guardar respuesta en historial
    st.session_state.messages.append({"role": "assistant", "content": respuesta})