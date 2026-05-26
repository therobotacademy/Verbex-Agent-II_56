"""VERBEX · II-6 · Dashboard MVP (versión Python / CSV).

Streamlit read-only que muestra el estado del agente normalizador leyendo los
mismos CSV que escribe `verbex/persistence.py` (data/Pedidos.csv, Lineas.csv,
Errores.csv). No usa Google Sheets ni Service Account: los datos son locales.

Es el equivalente del dashboard de Sheets del track n8n — misma información, sin
credenciales. La persistencia ya vive en el repo Python, así que el dashboard
solo tiene que leer ficheros.

Uso:
    streamlit run app.py
    # → http://localhost:8501

Requiere:
    - pip install -r requirements.txt
    - data/*.csv poblados por el agente (o los de muestra del repo)
    - opcional: CSV_DATA_DIR en .env para apuntar a otra carpeta de datos
"""

import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

# Carpeta de datos: misma convención que verbex/persistence.py.
_DEFAULT_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR = Path(os.environ.get("CSV_DATA_DIR", _DEFAULT_DIR))

st.set_page_config(
    page_title="VERBEX · MVP Dashboard",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=60, show_spinner="Leyendo CSV…")
def load_csv(nombre: str) -> pd.DataFrame:
    """Lee data/<nombre>.csv como DataFrame. Vacío si no existe todavía."""
    path = DATA_DIR / nombre
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


# --- Header --------------------------------------------------------------------------------------

st.markdown(
    """
    <div style="background:#1E3A5F;padding:18px 24px;border-radius:8px;margin-bottom:24px;">
      <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#FF8C3B;letter-spacing:.18em;text-transform:uppercase;">VERBEX COMPOSITES · MVP Dashboard · Python</span>
      <h1 style="font-family:'Syne',sans-serif;color:#fff;font-size:28px;margin:6px 0 0;letter-spacing:-.02em;">
        Normalizador de Purchase Orders <span style="color:#FF8C3B;">— estado en vivo</span>
      </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Carga de datos ------------------------------------------------------------------------------

df_pedidos = load_csv("Pedidos.csv")
df_lineas = load_csv("Lineas.csv")
df_errores = load_csv("Errores.csv")

if df_pedidos.empty:
    st.warning(
        f"Sin datos en `Pedidos.csv` (carpeta `{DATA_DIR}`). "
        "¿El agente ha procesado alguna PO todavía? Ejecuta `python main.py` o el bot."
    )
    st.stop()

# Tipado y enriquecimiento
df_pedidos["timestamp"] = pd.to_datetime(df_pedidos["timestamp"], errors="coerce")
df_pedidos["confianza"] = pd.to_numeric(df_pedidos["confianza"], errors="coerce")
df_pedidos["aog"] = df_pedidos["aog"].astype(str).str.lower().isin(["true", "1", "yes"])
df_pedidos["duplicado"] = (
    df_pedidos["duplicado"].astype(str).str.lower().isin(["true", "1", "yes"])
)
df_pedidos = df_pedidos.sort_values("timestamp", ascending=False)

if not df_lineas.empty:
    df_lineas["timestamp"] = pd.to_datetime(df_lineas["timestamp"], errors="coerce")
    df_lineas["cantidad"] = pd.to_numeric(df_lineas["cantidad"], errors="coerce")

if not df_errores.empty:
    df_errores["timestamp"] = pd.to_datetime(df_errores["timestamp"], errors="coerce")
    df_errores = df_errores.sort_values("timestamp", ascending=False)

# --- Sidebar filtros -----------------------------------------------------------------------------

st.sidebar.markdown("### Filtros")

programas_disponibles = sorted({p for p in df_lineas.get("programa", []) if p}) if not df_lineas.empty else []
programa_sel = st.sidebar.multiselect("Programa", programas_disponibles, default=programas_disponibles)

estados_disponibles = sorted(df_pedidos["estado_normalizacion"].dropna().unique())
estado_sel = st.sidebar.multiselect("Estado", estados_disponibles, default=estados_disponibles)

prioridades_disponibles = sorted(df_pedidos["prioridad_calculada"].dropna().unique())
prioridad_sel = st.sidebar.multiselect("Prioridad", prioridades_disponibles, default=prioridades_disponibles)

solo_aog = st.sidebar.checkbox("Solo AOG", value=False)
solo_hoy = st.sidebar.checkbox("Solo POs de hoy", value=False)

st.sidebar.divider()
st.sidebar.caption(
    f"Carpeta de datos:\n`{DATA_DIR}`\n\n"
    f"Última carga: {datetime.now().strftime('%H:%M:%S')}"
)

# --- Aplicar filtros ----------------------------------------------------------------------------

df_filt = df_pedidos.copy()
if estado_sel:
    df_filt = df_filt[df_filt["estado_normalizacion"].isin(estado_sel)]
if prioridad_sel:
    df_filt = df_filt[df_filt["prioridad_calculada"].isin(prioridad_sel)]
if solo_aog:
    df_filt = df_filt[df_filt["aog"]]
if solo_hoy:
    hoy = pd.Timestamp(date.today())
    df_filt = df_filt[df_filt["timestamp"] >= hoy]

if programa_sel and not df_lineas.empty:
    pos_con_programa = df_lineas[df_lineas["programa"].isin(programa_sel)]["numero_pedido"].unique()
    df_filt = df_filt[df_filt["numero_pedido"].isin(pos_con_programa)]

# --- KPIs ---------------------------------------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

n_pos = len(df_filt)
hoy = pd.Timestamp(date.today())
n_pos_hoy = len(df_filt[df_filt["timestamp"] >= hoy])
n_aog = int(df_filt["aog"].sum())
n_completos = (df_filt["estado_normalizacion"] == "COMPLETO").sum()
tasa_exito = (n_completos / n_pos * 100) if n_pos > 0 else 0
n_errores_recientes = (
    len(df_errores[df_errores["timestamp"] >= hoy - timedelta(days=7)])
    if not df_errores.empty
    else 0
)

col1.metric("POs totales", n_pos)
col2.metric("POs hoy", n_pos_hoy)
col3.metric("AOGs activos", n_aog, help="POs con aog=true en el filtro actual")
col4.metric("Tasa de éxito", f"{tasa_exito:.0f}%", help="% de POs en estado COMPLETO")
col5.metric("Errores 7d", n_errores_recientes, help="Errores técnicos en los últimos 7 días")

st.divider()

# --- Pestañas -----------------------------------------------------------------------------------

tab_pedidos, tab_top, tab_errores = st.tabs(["📋 Últimas POs", "📊 Top clientes & productos", "⚠ Errores recientes"])

with tab_pedidos:
    st.markdown(f"### Últimas {min(50, len(df_filt))} POs")
    if df_filt.empty:
        st.info("Sin POs que coincidan con los filtros.")
    else:
        cols_show = [
            "timestamp", "numero_pedido", "cliente_nombre", "codigo_erp",
            "estado_normalizacion", "prioridad_calculada", "confianza",
            "total_lineas", "duplicado", "aog",
        ]
        cols_show = [c for c in cols_show if c in df_filt.columns]
        st.dataframe(
            df_filt[cols_show].head(50),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### Detalle de una PO")
        po_select = st.selectbox(
            "Selecciona PO para ver líneas:",
            df_filt["numero_pedido"].head(50).tolist(),
        )
        if po_select and not df_lineas.empty:
            df_l = df_lineas[df_lineas["numero_pedido"] == po_select]
            if df_l.empty:
                st.caption("Sin líneas registradas para esta PO.")
            else:
                cols_l = [
                    "linea_id", "part_number_cliente", "part_number_proveedor",
                    "descripcion", "cantidad", "unidad",
                    "fecha_entrega_requerida", "programa",
                    "prioridad", "doc_requerida",
                ]
                cols_l = [c for c in cols_l if c in df_l.columns]
                st.dataframe(df_l[cols_l], use_container_width=True, hide_index=True)

with tab_top:
    if df_filt.empty:
        st.info("Sin datos.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Top 5 clientes (por # POs)")
            top_clientes = (
                df_filt.groupby(["codigo_erp", "cliente_nombre"], dropna=False)
                .size()
                .reset_index(name="POs")
                .sort_values("POs", ascending=False)
                .head(5)
            )
            st.dataframe(top_clientes, use_container_width=True, hide_index=True)

        with c2:
            st.markdown("#### Top 5 productos (por cantidad total)")
            if df_lineas.empty:
                st.caption("Sin líneas.")
            else:
                df_l_filt = df_lineas[df_lineas["numero_pedido"].isin(df_filt["numero_pedido"])]
                top_prod = (
                    df_l_filt.groupby("part_number_proveedor", dropna=False)["cantidad"]
                    .sum()
                    .reset_index()
                    .sort_values("cantidad", ascending=False)
                    .head(5)
                )
                st.dataframe(top_prod, use_container_width=True, hide_index=True)

with tab_errores:
    if df_errores.empty:
        st.success("Sin errores registrados. ✓")
    else:
        st.markdown(f"### {len(df_errores)} errores totales")
        cols_e = ["timestamp", "numero_pedido", "tipo_error", "origen", "error_raw"]
        cols_e = [c for c in cols_e if c in df_errores.columns]
        st.dataframe(df_errores[cols_e].head(20), use_container_width=True, hide_index=True)

# --- Footer -------------------------------------------------------------------------------------

st.divider()
st.caption(
    "VERBEX COMPOSITES · MVP Dashboard · Read-only · "
    "Datos refrescados cada 60s desde CSV locales (data/) · "
    "Confirmación de pedidos automatizada vía Telegram (II-4)"
)
