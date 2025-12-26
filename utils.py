import pandas as pd
import streamlit as st

@st.cache_data(ttl=60)
def cargar_datos():
    url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5z9zHagRYwvPxMcQK_prKnH6p4v-rCPpNksjzxeiBFt2tCY0ZeKoOLYUQXrccDyNNuTRQj5Di2jvX/pub?gid=0&single=true&output=csv"
    try:
        df = pd.read_csv(url_csv, dtype=str)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        return pd.DataFrame()

def buscar_pedido(prompt, df):
    if df.empty or 'pedido' not in df.columns:
        return None
    
    lista_pedidos_reales = df['pedido'].astype(str).tolist()
    palabras = prompt.split()
    
    for p in palabras:
        p_limpia = p.strip(".,;?!¡¿'\"")
        match = next((x for x in lista_pedidos_reales if str(x).lower() == p_limpia.lower()), None)
        if match:
            return df[df['pedido'] == match].iloc[0]
    
    return None

def render_status_card(row, title="Estado del Envío"):
    cliente = row['cliente']
    estado = row['estado']
    pedido = row['pedido']
    
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
    
    if config["prog"] == 0 and st_lower != "cancelado":
        for key, val in status_map.items():
            if key in st_lower:
                config = val
                break

    html = f"""<div class="status-card">
<div class="status-title">{title}</div>
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
Pedido: <b>{pedido}</b> • 
<span class="status-badge {config['class']}">{config['icon']} {estado}</span>
</div>
</div>"""
    return html
