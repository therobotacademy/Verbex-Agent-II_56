# Tutorial 11 · Dashboard de observabilidad con Streamlit

Levanta el dashboard y observa el estado del agente en vivo. Sin credenciales, sin API key — solo los CSV que el pipeline ya ha escrito.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~10 min | **Ninguna** | `dashboard/app.py` |

---

## Qué vas a ver

```
data/Pedidos.csv  ─┐
data/Lineas.csv   ─┼─▶  streamlit run dashboard/app.py  ─▶  localhost:8501
data/Errores.csv  ─┘
         ↑
   refresco automático cada 60 s
```

El dashboard es **read-only**: lee los mismos CSV que escribe `verbex/persistence.py`. Ningún dato cambia por abrir el dashboard. Es el equivalente del panel de Sheets del track n8n — misma información, sin credenciales de Google.

---

## Paso 1 · Arrancar el dashboard

```bash
streamlit run dashboard/app.py
```

Streamlit abre automáticamente `http://localhost:8501` en el navegador. Si no lo abre, ve manualmente a esa URL.

**Salida esperada en la terminal:**

```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

> **Windows PowerShell:** si `streamlit` no se reconoce, ejecuta  
> `python -m streamlit run dashboard/app.py`

---

## Experimento A · Los 5 KPIs

La fila superior muestra cinco métricas calculadas sobre los CSV actuales:

| KPI | Qué mide | Dónde vive en el CSV |
|-----|----------|----------------------|
| POs totales | Filas en `Pedidos.csv` tras filtros | `len(df_filt)` |
| POs hoy | POs con `timestamp >= hoy` | `timestamp` |
| AOGs activos | POs con `aog=true` en el filtro | columna `aog` |
| Tasa de éxito | % de POs en estado `COMPLETO` | `estado_normalizacion` |
| Errores 7d | Filas en `Errores.csv` con `timestamp >= hoy-7d` | `Errores.csv.timestamp` |

**Qué observar:** estos KPIs cambian en tiempo real (≤60 s de latencia) cada vez que el bot procesa una PO nueva.

---

## Experimento B · La pestaña "Últimas POs"

1. En la tabla principal aparecen las últimas 50 POs, ordenadas por `timestamp` descendente.
2. Usa el selector de la barra lateral para filtrar por **Estado** (`COMPLETO` / `PARCIAL` / `ERROR`).
3. Activa **Solo AOG** para ver únicamente POs de emergencia.
4. En el desplegable **"Selecciona PO para ver líneas"** elige cualquier PO — aparecen sus líneas con `part_number_proveedor`, `doc_requerida`, `prioridad` por línea.

**Qué observar:** la columna `doc_requerida` es el resultado de R05+R06. La columna `prioridad` por línea es el resultado de R01. Ambas viven en `Lineas.csv`, no se calculan en el dashboard.

---

## Experimento C · Refresco automático en acción

Mientras el dashboard está abierto, procesa una PO nueva desde otra terminal:

```python
# run_t11c.py — procesar una PO nueva sin Telegram ni email
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from verbex import llm, persistence
import rules

TEXTO = (
    "Purchase Order PO-T11-001. Stratos Systems.\n"
    "Part: ST9-HTP-RIB-047, Qty: 2 EA, Need Date: 31/12/2026.\n"
    "CoC required."
)

po = llm.normalizar(TEXTO)
po = rules.aplicar_reglas(po)

if not persistence.es_duplicado(po["numero_pedido"]):
    persistence.append_pedido(po, TEXTO)
    persistence.append_lineas(po)
    print(f"PO escrita: {po['numero_pedido']} — estado={po['estado_normalizacion']}")
else:
    print("Duplicado — no escrita")
```

```bash
python run_t11c.py
```

Espera ≤60 segundos y observa cómo **el KPI "POs totales" sube en 1** y la PO `PO-T11-001` aparece en la tabla sin recargar el navegador.

**Mecanismo:** `@st.cache_data(ttl=60)` en `dashboard/app.py:44` invalida la caché cada 60 segundos y relee los CSV. No hay websocket — es poll-basado.

---

## Experimento D · La pestaña "Errores recientes"

Si el pipeline ha tenido errores técnicos (SMTP, timeout de red, JSON roto), aparecen aquí ordenados por `timestamp`.

Para generar un error de prueba sin romper nada:

```python
# run_t11d.py
import sys
sys.path.insert(0, '.')
from verbex import observability
observability.setup_logging()
observability.registrar_excepcion(
    ValueError("Error de prueba — tutorial 11"),
    origen="tutorial_11_exp_d"
)
print("Error escrito en Errores.csv")
```

Después de ejecutarlo, ve a la pestaña **"⚠ Errores recientes"** en el dashboard — el error aparece (en ≤60 s) con timestamp, origen `tutorial_11_exp_d` y mensaje.

**Qué observar:** los errores de negocio (PN desconocido, cliente no registrado) **no aparecen aquí** — están en `Pedidos.csv` como `estado=ERROR`. Solo los fallos técnicos del pipeline van a `Errores.csv`.

---

## Experimento E · Los filtros de la barra lateral

| Filtro | Efecto |
|--------|--------|
| Programa | Filtra por `programa` de las líneas (join con Lineas.csv) |
| Estado | `COMPLETO` / `PARCIAL` / `ERROR` |
| Prioridad | `NORMAL` / `PRIORITARIO` / `AOG` |
| Solo AOG | Muestra únicamente POs con `aog=True` |
| Solo POs de hoy | `timestamp >= hoy 00:00` |

Todos los filtros afectan tanto a la tabla como a los KPIs. La tasa de éxito, por ejemplo, se calcula sobre las POs filtradas — si filtras solo `COMPLETO`, la tasa sube al 100%.

---

## Detener el dashboard

`Ctrl+C` en la terminal donde corre `streamlit run`.

---

## Arquitectura del dashboard

```python
# dashboard/app.py — estructura

@st.cache_data(ttl=60)          # relee CSV cada 60 s
def load_csv(nombre): ...

df_pedidos = load_csv("Pedidos.csv")   # ← los mismos ficheros que escribe persistence.py
df_lineas  = load_csv("Lineas.csv")
df_errores = load_csv("Errores.csv")

# KPIs + filtros sidebar + 3 pestañas
```

El dashboard no escribe nada — es **estrictamente read-only**. `persistence.py` es la única capa que toca los CSV.

---

## Lo que acabas de aprender

- El dashboard es la materialización del pilar **métricas** de observabilidad (slide 10): agrega sobre los CSV sin requerir una base de datos ni credenciales externas.
- El refresco de 60 s es suficiente para la demo en clase; en producción podría bajarse a 15–30 s sin impacto de rendimiento significativo.
- La distinción clave: errores de **negocio** → `Pedidos.csv` (estado=ERROR); errores **técnicos** → `Errores.csv`. El dashboard los separa en pestañas distintas.

---

## Siguiente tutorial

Este es el último tutorial de la secuencia. Consulta el **[README](README.md)** para el orden recomendado completo.

→ **[10 · Bot Telegram en vivo](10-bot-telegram-en-vivo.md)** — si aún no has levantado el bot, hazlo ahora que ya tienes el dashboard para ver las POs en tiempo real.
