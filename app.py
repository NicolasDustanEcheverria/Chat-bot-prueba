import streamlit as st
import time
from utils import cargar_datos, buscar_pedido, render_status_card

# --- CONFIGURACIÓN ---
# Actualización de UI: Mostrar fecha y custodia
st.set_page_config(page_title="Rastreo de Pedidos", page_icon="📦", layout="centered")

# --- CARGAR CSS ---
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- CABECERA ---
st.title("📦 Rastreo de Envíos")
st.markdown('<p class="subtitle">Ingresa tu número de pedido para consultar el estado en tiempo real.</p>', unsafe_allow_html=True)

# --- DATA ---
df = cargar_datos()

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_order" not in st.session_state:
    st.session_state.last_order = None

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- LÓGICA ---
if prompt := st.chat_input("Ej: PED-12345"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-message-content">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Consultando...*")
        time.sleep(0.6)
        
        prompt_lower = prompt.lower()
        
        # 1. Caso: Consulta de Custodia
        if "custodia" in prompt_lower:
            if st.session_state.last_order is not None:
                row = st.session_state.last_order
                respuesta_html = render_status_card(row, title="Consulta de Custodia")
                # Personalizar un poco el texto bajo la tarjeta
                # Verificamos la columna 'custodia' directamente
                val_custodia = str(row.get('custodia', '')).strip().lower()
                esta_en_custodia = "SÍ" if val_custodia == "si" else "NO"
                info_extra = f'<div class="info-box" style="margin-top: 10px;">ℹ️ El pedido <b>{row["pedido"]}</b> {esta_en_custodia} está en custodia.</div>'
                full_html = respuesta_html + info_extra
                
                message_placeholder.markdown(full_html, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_html})
            else:
                resp = "🕵️ Para confirmarte si un pedido está en custodia, primero dime el número de pedido."
                message_placeholder.markdown(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})

        # 2. Caso: Búsqueda Normal/Smart
        else:
            row, reason = buscar_pedido(prompt, df)
            
            if row is not None:
                st.session_state.last_order = row
                
                # Mensaje contextual si fue por nombre de cliente
                intro_msg = ""
                if "Cliente" in reason:
                    cliente_detectado = row['cliente']
                    intro_msg = f"🧠 *Entendí que buscas el pedido de:* **{cliente_detectado}**<br>"
                elif "Fuzzy" in reason:
                    pedido_detectado = row['pedido']
                    intro_msg = f"🧠 *Quizás quisiste decir el pedido:* **{pedido_detectado}**<br>"
                
                respuesta_html = render_status_card(row)
                full_resp = intro_msg + respuesta_html
                
                message_placeholder.markdown(full_resp, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_resp})
            else:
                resp = f"🔍 No pudimos identificar un pedido ni un cliente en: \"**{prompt}**\"."
                message_placeholder.markdown(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})

# --- FOOTER ---
st.markdown("""
    <div style="position: fixed; bottom: 10px; width: 100%; text-align: center; color: #888; font-size: 0.8rem;">
        Powered by AI 🤖 | v2.0 Premium
    </div>
""", unsafe_allow_html=True)