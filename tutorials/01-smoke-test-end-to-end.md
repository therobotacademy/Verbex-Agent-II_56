# Tutorial 01 · Smoke test end-to-end

**Primera toma de contacto.** No necesitas haber leído el código.  
Al terminar habrás procesado una Purchase Order real con Claude y verás el resultado en los CSV.

| Tiempo | Credenciales | Conocimiento previo |
|--------|-------------|---------------------|
| ~10 min | Solo `ANTHROPIC_API_KEY` | Ninguno |

---

## Qué vas a ver

Una PO en texto libre entra al sistema → Claude la convierte a JSON estructurado → las reglas de negocio la validan y calculan prioridad → el resultado queda registrado en `data/Pedidos.csv` y `data/Lineas.csv`.

```
"Purchase Order PO-2025-STRA-0847…"
        ↓
  llm.normalizar()   ← Claude convierte el texto a JSON
        ↓
  rules.aplicar_reglas()  ← 9 reglas deterministas
        ↓
  data/Pedidos.csv   ← la PO queda registrada
  data/Lineas.csv    ← cada línea queda registrada
```

---

## Paso 0 · Prerrequisitos (2 min)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear fichero de configuración
cp .env.example .env
```

Abre `.env` y pon tu API key de Anthropic:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

El resto de variables (`TELEGRAM_*`, `SMTP_*`) las puedes dejar vacías por ahora.

**Verificación:**
```bash
python -c "from anthropic import Anthropic; print('OK')"
```

---

## Fase 1 · LLM + reglas (sin persistencia ni notificaciones)

Esta fase no requiere Telegram ni email. Solo la API de Anthropic.

Copia y pega este bloque en tu terminal (**Git Bash / macOS / Linux**):

> **Windows PowerShell / cmd:** guarda el contenido del bloque en un fichero `run_fase1.py` y ejecútalo con `python run_fase1.py`.

```bash
python - <<'EOF'
import json
from dotenv import load_dotenv
load_dotenv()                  # carga .env antes de cualquier import que lea credenciales
from verbex import llm, observability
import rules

observability.setup_logging()

TEXTO_PO = (
    "Purchase Order PO-2025-STRA-0847. Stratos Systems.\n"
    "Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.\n"
    "Ref: ST-900 program. CoC required."
)

print("\n── Texto original ──────────────────────────────")
print(TEXTO_PO)

print("\n── Tras el LLM (claude-sonnet) ─────────────────")
po = llm.normalizar(TEXTO_PO)
print(json.dumps(po, indent=2, ensure_ascii=False))

print("\n── Tras las reglas R01–R09 ─────────────────────")
po = rules.aplicar_reglas(po)
print(f"  estado      : {po['estado_normalizacion']}")
print(f"  prioridad   : {po['prioridad_calculada']}")
print(f"  confianza   : {po['confianza']}")
print(f"  alertas     : {po['alertas']}")
print(f"  doc línea 1 : {po['lineas'][0].get('doc_requerida')}")
EOF
```

### Salida esperada

```
── Texto original ──────────────────────────────
Purchase Order PO-2025-STRA-0847. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.
Ref: ST-900 program. CoC required.

── Tras el LLM (claude-sonnet) ─────────────────
{
  "numero_pedido": "PO-2025-STRA-0847",
  "cliente": {
    "nombre": "Stratos Systems",
    "codigo_erp": "STRA-001"
  },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "ST9-HTP-RIB-047",
      "part_number_proveedor": "VBX-COMP-4471-B",
      "cantidad": 12,
      "unidad": "EA",
      "fecha_entrega_requerida": "2025-09-15",
      "requiere_coc": true,
      "requiere_easa_form1": false
    }
  ],
  "estado_normalizacion": "COMPLETO",
  "confianza": 0.97,
  "aog": false,
  "alertas": []
}

── Tras las reglas R01–R09 ─────────────────────
  estado      : COMPLETO
  prioridad   : NORMAL
  confianza   : 0.97
  alertas     : []
  doc línea 1 : ['CoC']
```

**Qué acaba de ocurrir:**
- Claude recibió texto libre y devolvió JSON estructurado.
- El PN del cliente `ST9-HTP-RIB-047` fue mapeado al PN de proveedor `VBX-COMP-4471-B` (tabla en `SKILL.md`).
- La fecha `15/09/2025` fue normalizada a `2025-09-15` (ISO 8601).
- R05 añadió `"CoC"` a `doc_requerida` porque `requiere_coc=True`.
- La PO quedó como COMPLETO, NORMAL, confianza 0.97.

---

## Fase 2 · Pipeline completo con main.py

```bash
python main.py
```

> **Nota:** La PO demo (`PO-2025-STRA-0847`) ya viene incluida en `data/Pedidos.csv` como dato de muestra. La primera vez que ejecutes `main.py` verás el mensaje **"Duplicado"** — R09 la detecta y detiene el pipeline. Usa un número de pedido distinto (como `PO-2025-STRA-SMOKE-01`) para ver el flujo completo.

> **Notificaciones:** Si Telegram o SMTP no están configurados, el pipeline falla en el fan-out *después* de escribir en CSV. La PO quedará registrada igualmente. Esto es un fallo técnico de notificación, no un error de procesamiento.

### ¿Qué pasa internamente?

`main.py` ejecuta exactamente lo que viste en Fase 1, más:

1. Comprueba si la PO ya existe en `data/Pedidos.csv` (R09 anti-duplicado).
2. Si no es duplicado, escribe la PO en `data/Pedidos.csv` y las líneas en `data/Lineas.csv`.
3. Envía notificación a Telegram calidad (porque hay CoC requerido).
4. Envía email de confirmación al cliente.

### Ver el resultado en los CSV

Abre los CSV con cualquier editor o desde Python:

```bash
python - <<'EOF'
import csv, sys

print("\n── data/Pedidos.csv (últimas 2 filas) ──────────")
with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
for row in rows[-2:]:
    print(f"  {row['numero_pedido']} | {row['estado_normalizacion']} | {row['prioridad_calculada']} | confianza={row['confianza']}")

print("\n── data/Lineas.csv (últimas 2 filas) ───────────")
with open("data/Lineas.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
for row in rows[-2:]:
    print(f"  {row['numero_pedido']} | {row['part_number_cliente']} → {row['part_number_proveedor']} | {row['doc_requerida']}")
EOF
```

---

## Envía tu propia PO

Cambia el texto de la PO en Fase 1 y observa cómo cambia el resultado.  
Prueba estas variaciones:

**Variación 1 — PN desconocido:**
```
Purchase Order PO-TEST-001. Stratos Systems.
Part: ST9-UNKNOWN-999, Qty: 5 EA, Need Date: 20/12/2025.
```
→ Espera: `estado=ERROR`, alerta sobre PN no reconocido.

**Variación 2 — Urgente (AOG):**
```
URGENT AOG — Aircraft on Ground.
Purchase Order PO-AOG-TEST. Kairos Aerospace.
Part: HX7-FUS-PNL-331, Qty: 2 EA, Required immediately.
EASA Form 1 required.
```
→ Espera: `aog=True`, `prioridad=AOG`, `doc_requerida=["EASA Form 1"]`.

**Variación 3 — Texto que no es una PO:**
```
Hola, ¿tenéis disponibilidad para una reunión el próximo martes?
```
→ Espera: `estado=ERROR`, `alertas` con mensaje `no_pedido`.

---

## Qué acabas de aprender

| Concepto | Dónde lo has visto |
|----------|--------------------|
| El LLM convierte texto libre a JSON | `llm.normalizar()` en Fase 1 |
| Las reglas son funciones puras (sin red) | `rules.aplicar_reglas()` en Fase 1 |
| El pipeline completo lo orquesta `main.py` | Fase 2 |
| El resultado persiste en CSV | `data/Pedidos.csv` + `data/Lineas.csv` |
| Los errores quedan en alertas[], no en excepciones | Variación 1 |

---

## Siguiente tutorial

→ **[02 · Reglas sin red: el shell interactivo](02-reglas-en-el-shell.md)** — juega con las funciones de `rules.py` una a una en el REPL de Python, sin necesitar API key ni credenciales. El tutorial más rápido para entender qué decide cada regla.
