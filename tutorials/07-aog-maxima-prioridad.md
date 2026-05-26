# Tutorial 07 · AOG: prioridad máxima end-to-end

AOG (Aircraft on Ground) es el nivel de urgencia más alto de la industria aeronáutica. Traza cómo el sistema detecta la señal semántica "AOG" y la convierte en datos estructurados que fluyen hasta el fan-out de notificaciones.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~15 min | `ANTHROPIC_API_KEY` | `run_t07.py` |

---

## Arquitectura AOG en el pipeline

```
"URGENT AOG — Aircraft on Ground..."  ← texto libre
        ↓
    llm.normalizar()         → aog=True   (LLM detecta la señal semántica)
        ↓
    rules.r01_r02_prioridad()→ prioridad=AOG  (regla actúa sobre el dato)
        ↓
    persistence.append_pedido() → escrito en CSV con prioridad=AOG
        ↓
    notify.enviar_telegram_produccion()  → canal de producción URGENTE
    notify.enviar_telegram_calidad()     → canal de calidad (si hay CoC/EASA)
    notify.enviar_email()                → email de confirmación
```

**División E5:** el LLM detecta "AOG" como señal semántica. La regla R01 actúa sobre `aog=True` como dato booleano. El LLM nunca decide la prioridad; la regla nunca interpreta texto.

---

## Experimento A · AOG sin API: solo las reglas

```python
import sys
sys.path.insert(0, '.')
import rules

po = {
    "numero_pedido": "PO-AOG-TEST-001",
    "cliente": {"codigo_erp": "KAIRO-001"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "HX7-FUS-PNL-331",
        "cantidad": 2, "unidad": "EA",
        "fecha_entrega_requerida": "2026-06-01",
        "requiere_coc": True, "requiere_easa_form1": True,
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.97,
    "alertas": ["AOG detectado - Aircraft on Ground - verificar stock inmediatamente"],
    "aog": True,   # ← el LLM detectó la señal y puso True
}

out = rules.aplicar_reglas(po)

print("estado         :", out["estado_normalizacion"])
print("prioridad_PO   :", out["prioridad_calculada"])
print("prioridad_linea:", out["lineas"][0]["prioridad"])
print("doc_requerida  :", out["lineas"][0].get("doc_requerida"))
print("alertas        :", out["alertas"])
```

**Salida esperada:**
```
estado         : COMPLETO
prioridad_PO   : AOG
prioridad_linea: AOG
doc_requerida  : ['CoC', 'EASA Form 1']
alertas        : ['AOG detectado - Aircraft on Ground - verificar stock inmediatamente']
```

**Qué observar:**
- `prioridad_calculada=AOG` y `lineas[0]["prioridad"]=AOG` — R01 propaga AOG a nivel de PO y de cada línea.
- `doc_requerida=['CoC', 'EASA Form 1']` — R05+R06 independientes de la prioridad.
- La alerta viene del LLM (sin prefijo `R0X:`). R01 no añade alerta propia cuando detecta AOG — la señal semántica ya la documentó el LLM.

---

## Experimento B · AOG end-to-end con LLM (necesita API key)

Guarda como `run_t07b.py`:

```python
import json
from dotenv import load_dotenv
load_dotenv()
from verbex import llm
import rules

TEXTO_AOG = (
    "URGENT AOG — Aircraft on Ground.\n"
    "Purchase Order PO-AOG-2026-001. Kairos Aerospace.\n"
    "Part: HX7-FUS-PNL-331, Qty: 2 EA, Required immediately.\n"
    "EASA Form 1 required. CoC required."
)

print("── Texto original ──────────────────────────")
print(TEXTO_AOG)

print("\n── Tras el LLM ─────────────────────────────")
po = llm.normalizar(TEXTO_AOG)
print(f"  aog         : {po.get('aog')}")
print(f"  estado      : {po.get('estado_normalizacion')}")
print(f"  confianza   : {po.get('confianza')}")
print(f"  alertas LLM : {po.get('alertas')}")

print("\n── Tras las reglas ──────────────────────────")
po = rules.aplicar_reglas(po)
print(f"  prioridad_PO   : {po.get('prioridad_calculada')}")
print(f"  prioridad_linea: {po['lineas'][0].get('prioridad') if po.get('lineas') else '—'}")
print(f"  doc_requerida  : {po['lineas'][0].get('doc_requerida') if po.get('lineas') else '—'}")
print(f"  alertas final  : {po.get('alertas')}")
```

**Qué observar:**
- El LLM extrae `aog=True` del texto "URGENT AOG". Esto es comprensión semántica — ninguna regla podría hacer esto desde texto libre.
- R01 recibe `aog=True` y pone `prioridad=AOG`. Lógica determinista, sin ambigüedad.
- El fan-out (Telegram, email) recibirá `prioridad=AOG` y puede priorizar la notificación.

---

## Experimento C · Comparar AOG vs PRIORITARIO vs NORMAL

```python
import sys, datetime as dt
sys.path.insert(0, '.')
import rules

def po_con(aog, fecha_delta_dias):
    return {
        "numero_pedido": "PO-COMP",
        "cliente": {"codigo_erp": "STRA-001"},
        "lineas": [{"linea_id": 1, "part_number_cliente": "ST9-HTP-RIB-047",
                    "cantidad": 1, "unidad": "EA",
                    "fecha_entrega_requerida": (
                        dt.date.today() + dt.timedelta(days=fecha_delta_dias)
                    ).isoformat(),
                    "requiere_coc": False, "requiere_easa_form1": False}],
        "estado_normalizacion": "COMPLETO",
        "confianza": 0.97, "alertas": [], "aog": aog,
    }

casos = [
    ("AOG",        True,  30),   # aog=True anula la fecha
    ("PRIORITARIO",False,  3),   # fecha en 3 días
    ("NORMAL",     False, 90),   # fecha en 90 días
]

print(f"{'Caso':15s}  {'prioridad_calculada':20s}")
print("-" * 40)
for nombre, aog, dias in casos:
    po = rules.aplicar_reglas(po_con(aog, dias))
    print(f"{nombre:15s}  {po['prioridad_calculada']:20s}")
```

**Salida esperada:**
```
Caso             prioridad_calculada 
----------------------------------------
AOG              AOG                 
PRIORITARIO      PRIORITARIO         
NORMAL           NORMAL              
```

**R01 tiene precedencia sobre R02:** si `aog=True`, la prioridad es AOG independientemente de la fecha.

---

## Experimento D · Verificar en el CSV

Después del Experimento B (si ejecutaste con API real y un número de PO único), verifica que la PO AOG quedó registrada:

```python
import csv

with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

aog_rows = [r for r in rows if r.get("aog", "").lower() in ("true", "1")]
print(f"POs con aog=True en CSV: {len(aog_rows)}")
for r in aog_rows:
    print(f"  {r['numero_pedido']:30s}  prioridad={r['prioridad_calculada']}")
```

---

## Lo que acabas de aprender

- **AOG es señal semántica → dato estructurado:** el LLM detecta "AOG" en texto libre y lo convierte en `aog=True`. R01 actúa sobre el booleano. Separación E5 perfecta.
- **R01 > R02:** AOG tiene precedencia sobre la prioridad por fecha.
- **Propagación doble:** `prioridad_calculada` (PO) y `lineas[i]["prioridad"]` (cada línea).
- **Fan-out aware:** el sistema de notificaciones recibe el dict con `prioridad=AOG` y puede usar ese campo para urgenciar la entrega.

---

## Siguiente tutorial

→ **[08 · Leer los CSV: entender la persistencia](08-leer-los-csv.md)** — inspecciona `Pedidos.csv`, `Lineas.csv` y `Errores.csv` desde Python para entender qué se persiste y qué no.
