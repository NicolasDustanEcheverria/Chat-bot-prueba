import pandas as pd
import streamlit as st
import textwrap

@st.cache_data(ttl=60)
def cargar_datos():
    url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5z9zHagRYwvPxMcQK_prKnH6p4v-rCPpNksjzxeiBFt2tCY0ZeKoOLYUQXrccDyNNuTRQj5Di2jvX/pub?gid=0&single=true&output=csv"
    try:
        df = pd.read_csv(url_csv, dtype=str)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        return pd.DataFrame()

import re
from difflib import get_close_matches

def buscar_pedido(prompt, df):
    if df.empty or 'pedido' not in df.columns:
        return None, None  # Retorna tupla (Row, Razon)

    # 0. Normalización básica
    prompt_norm = prompt.strip()
    lista_pedidos = df['pedido'].astype(str).tolist()
    lista_clientes = df['cliente'].astype(str).tolist() if 'cliente' in df.columns else []

    # ESTRATEGIA 1: Búsqueda exacta o Regex de números en el prompt
    # Busca cualquier secuencia de números o alfanuméricos que se parezca a un pedido
    # Aceptamos pedidos que sean solo números o letras-números
    match_directo = None
    
    # Intento 1: Coincidencia exacta de palabra
    words = prompt_norm.split()
    for w in words:
        clean_w = w.strip(".,;?!¡¿'\"").lower()
        # Buscar en la lista de pedidos (normalizada)
        for idx, pedido_real in enumerate(lista_pedidos):
            if str(pedido_real).strip().lower() == clean_w:
                return df.iloc[idx], "Exact Match"

    # Intento 2: Búsqueda difusa en Pedidos (Typos)
    # Usamos difflib para ver si alguna palabra se parece mucho a un pedido real
    for w in words:
        clean_w = w.strip(".,;?!¡¿'\"")
        matches = get_close_matches(clean_w, [str(p) for p in lista_pedidos], n=1, cutoff=0.85)
        if matches:
            best_match = matches[0]
            row = df[df['pedido'].astype(str) == best_match].iloc[0]
            return row, f"Fuzzy Match Pedido ({best_match})"

    # ESTRATEGIA 2: Búsqueda por Nombre de Cliente (Fuzzy parcial)
    # Si el usuario dice "pedido de Nicolas", buscamos "Nicolas" en la columna clientes
    # Esto es más complejo porque el nombre puede ser multi-palabra.
    # Vamos a buscar si el prompt contiene subcadenas que coincidan con clientes.
    
    # Ordenamos clientes por longitud (descendente) para matchear nombres largos primero
    unique_clients = list(set([str(c) for c in lista_clientes if str(c).lower() != 'nan']))
    # Un filtro simple: si alguna parte del prompt está en el nombre del cliente
    
    prompt_lower = prompt_norm.lower()
    
    best_client_match = None
    highest_score = 0
    
    for client in unique_clients:
        client_clean = client.strip().lower()
        if not client_clean: continue
        
        # 1. Chequeo directo: si el nombre del cliente está en el prompt
        if client_clean in prompt_lower:
             # Prioridad absoluta si está contenido
             row = df[df['cliente'].astype(str) == client].iloc[0]
             return row, f"Match Cliente ({client})"
             
        # 2. Fuzzy match de palabras clave del cliente
        # Si cliente es "Nicolas Dustan", y prompt es "nicolas", match.
        client_parts = client_clean.split()
        for part in client_parts:
            if len(part) > 3 and part in prompt_lower:
                # Coincidencia parcial fuerte
                row = df[df['cliente'].astype(str) == client].iloc[0]
                return row, f"Match Cliente Parcial ({client})"

    return None, None

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

    # Detectar fecha y custodia
    custodia_val = str(row.get('custodia', 'No')).strip().lower()
    es_custodia = "SÍ" if custodia_val == "si" else "NO"
    
    # Buscar la columna de fecha (la que no sea de las conocidas)
    known_cols = ['pedido', 'cliente', 'estado', 'custodia']
    fecha_entrega = "Pendiente"
    for col in row.index:
        if col.lower() not in known_cols:
            # Asumimos que la columna sobrante es la fecha
            val_fecha = str(row[col])
            if val_fecha and val_fecha.lower() != "nan":
                fecha_entrega = val_fecha
            break

    html = f"""
<div class="status-card">
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
<div style="margin-top: 1rem; background-color: #f8f9fa; padding: 10px; border-radius: 8px; font-size: 0.95rem; color: #333;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>📅 <b>Entrega:</b> {fecha_entrega}</span>
        <span>🔒 <b>Custodia:</b> <strong>{es_custodia}</strong></span>
    </div>
</div>
<div style="margin-top: 1rem;">
Pedido: <b>{pedido}</b> • 
<span class="status-badge {config['class']}">{config['icon']} {estado}</span>
</div>
</div>
"""
    return html
