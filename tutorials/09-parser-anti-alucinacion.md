# Tutorial 09 · Parser anti-alucinación: las 4 guardias

`_parsear_respuesta()` en `verbex/llm.py` es la frontera entre el LLM no-determinista y el código Python determinista. Aquí diseccionas cada guardia y entiendes qué fallo previene.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~15 min | **Ninguna** | `run_t09.py` |

---

## Las 4 guardias en orden de ejecución

```python
def _parsear_respuesta(raw: str) -> dict:
    # Guardia 1 — Strip fences markdown
    # Guardia 2 — Parsear JSON
    # Guardia 3 — Detectar no_pedido
    # Guardia 4 — Anular PNs inventados
    return po
```

Cada guardia es independiente. Si Guardia 1 falla, la excepción se propaga antes de llegar a Guardia 2.

---

## Guardia 1 · Strip de fences markdown

**Problema que resuelve:** Claude a veces envuelve el JSON en \`\`\`json ... \`\`\` aunque se le pida JSON puro. El parser elimina esas marcas antes de intentar parsear.

```python
import sys
sys.path.insert(0, '.')
from verbex.llm import _parsear_respuesta

# JSON válido envuelto en fences
json_con_fences = '''```json
{"numero_pedido":"PO-G1",
 "cliente":{"nombre":"Test","codigo_erp":"STRA-001"},
 "lineas":[{"linea_id":1,"part_number_cliente":"ST9-HTP-RIB-047",
 "part_number_proveedor":"VBX-COMP-4471-B","cantidad":1,"unidad":"EA",
 "fecha_entrega_requerida":"2026-12-01","requiere_coc":false,"requiere_easa_form1":false}],
 "estado_normalizacion":"COMPLETO","confianza":0.9,"alertas":[],"aog":false}
```'''

po = _parsear_respuesta(json_con_fences)
print("Guardia 1 — fences eliminados")
print(f"  estado : {po['estado_normalizacion']}")
print(f"  PN     : {po['lineas'][0]['part_number_cliente']}")
```

**Implementación en `llm.py`:**
```python
# Strip triple-backtick fences
if raw.strip().startswith("```"):
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
```

---

## Guardia 2 · JSON malformado

**Problema que resuelve:** si el LLM trunca la respuesta (por max_tokens), el JSON puede quedar incompleto. El parseo falla con un `ValueError` informativo.

```python
casos_rotos = [
    ('JSON truncado',      '{"numero_pedido": "PO-X", "lineas": [ROTO'),
    ('Respuesta vacía',    ''),
    ('Solo texto',         'No puedo procesar esto como PO.'),
    ('JSON roto al final', '{"numero_pedido":"PO-X","estado":"COMPLETO"'),
]

print("Guardia 2 — JSON malformado")
for nombre, raw in casos_rotos:
    try:
        po = _parsear_respuesta(raw)
        print(f"  {nombre:25s}: OK (inesperado)")
    except ValueError as e:
        print(f"  {nombre:25s}: ValueError — {str(e)[:60]}")
```

**Qué observar:** todos lanzan `ValueError` con prefijo `JSON_PARSE_ERROR:`. El prefijo permite en los logs distinguir "el LLM devolvió basura" de otros `ValueError` del código Python.

---

## Guardia 3 · Respuesta `no_pedido`

**Problema que resuelve:** el LLM puede recibir texto que no es una PO (consulta de disponibilidad, email de marketing, etc.). En ese caso devuelve `{"error": "no_pedido", "mensaje": "..."}` en lugar de un dict de PO. El parser lo convierte en un dict de PO con `estado=ERROR`.

```python
import json

# El LLM devuelve este JSON cuando el texto no es una PO
no_po_cases = [
    '{"error": "no_pedido", "mensaje": "Consulta de disponibilidad, no PO"}',
    '{"error": "no_pedido", "mensaje": "Mensaje de marketing, no es pedido"}',
]

print("Guardia 3 — no_pedido")
for raw in no_po_cases:
    po = _parsear_respuesta(raw)
    print(f"  estado              : {po['estado_normalizacion']}")
    print(f"  alertas             : {po['alertas']}")
    print(f"  lineas              : {po['lineas']}")
    print(f"  confianza           : {po['confianza']}")
    print()
```

**Salida esperada:**
```
estado              : ERROR
alertas             : ['LLM clasificó como no_pedido: Consulta de disponibilidad, no PO']
lineas              : []
confianza           : 0
```

**Por qué `confianza=0` y `lineas=[]`:** una PO clasificada como no-pedido no tiene líneas que procesar ni confianza que asignar. `rules.aplicar_reglas()` recibirá `lineas=[]` y no disparará ninguna regla.

---

## Guardia 4 · PN proveedor inventado

**Problema que resuelve:** el LLM podría inventar un PN proveedor plausible (ej: `VBX-COMP-9999-Z`) si el PN cliente no está en su tabla de equivalencias. La guardia 4 comprueba cada `part_number_proveedor` contra `PNS_VALIDOS` y lo anula si no está.

```python
import json

# JSON con un PN proveedor inventado
pn_inventado = json.dumps({
    "numero_pedido": "PO-G4",
    "cliente": {"nombre": "Test", "codigo_erp": "STRA-001"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "ST9-HTP-RIB-047",
        "part_number_proveedor": "VBX-COMP-9999-Z",  # ← NO en PNS_VALIDOS
        "cantidad": 1, "unidad": "EA",
        "fecha_entrega_requerida": "2026-12-01",
        "requiere_coc": False, "requiere_easa_form1": False
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.85, "alertas": [], "aog": False
})

print("Guardia 4 — PN inventado")
po = _parsear_respuesta(pn_inventado)
print(f"  PN proveedor : {po['lineas'][0]['part_number_proveedor']}")  # None
print(f"  alertas      : {po['alertas']}")  # PARSER: PN proveedor inventado

# Con PN proveedor válido (no actúa la guardia)
pn_valido = json.dumps({
    "numero_pedido": "PO-G4b",
    "cliente": {"nombre": "Test", "codigo_erp": "STRA-001"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "ST9-HTP-RIB-047",
        "part_number_proveedor": "VBX-COMP-4471-B",  # ← SÍ en PNS_VALIDOS
        "cantidad": 1, "unidad": "EA",
        "fecha_entrega_requerida": "2026-12-01",
        "requiere_coc": False, "requiere_easa_form1": False
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.97, "alertas": [], "aog": False
})

po2 = _parsear_respuesta(pn_valido)
print(f"\n  PN proveedor (válido): {po2['lineas'][0]['part_number_proveedor']}")  # VBX-COMP-4471-B
print(f"  alertas              : {po2['alertas']}")  # []
```

**Qué distingue la alerta de Guardia 4:** el prefijo `PARSER:` en el mensaje. Esto diferencia "el parser anuló un PN" (problema del LLM) de "el PN cliente no está en EQUIVALENCIAS" (problema de los datos de entrada).

---

## Experimento final · Las 4 guardias en cascada

¿Qué pasa si una respuesta activa varias guardias?

```python
import json

# Respuesta con fences Y PN inventado
complejo = '''```json
{"numero_pedido":"PO-COMPLEX",
 "cliente":{"nombre":"Test","codigo_erp":"STRA-001"},
 "lineas":[{"linea_id":1,
   "part_number_cliente":"ST9-HTP-RIB-047",
   "part_number_proveedor":"VBX-INVENTED-0001",
   "cantidad":1,"unidad":"EA",
   "fecha_entrega_requerida":"2026-12-01",
   "requiere_coc":false,"requiere_easa_form1":false}],
 "estado_normalizacion":"COMPLETO","confianza":0.9,"alertas":[],"aog":false}
```'''

po = _parsear_respuesta(complejo)
print("Guardia 1+4 en cascada")
print(f"  estado     : {po['estado_normalizacion']}")  # COMPLETO (G1 limpió fences)
print(f"  PN         : {po['lineas'][0]['part_number_proveedor']}")  # None (G4 anuló PN)
print(f"  alertas    : {po['alertas']}")  # PARSER: PN proveedor inventado
```

**Observación:** G1 (strip fences) actúa antes del parseo; G4 (PN whitelist) actúa después. El resultado es correcto aunque se activaron dos guardias.

---

## Lo que acabas de aprender

| Guardia | Input que activa | Output | Tipo resultado |
|---------|-----------------|--------|----------------|
| 1 — Strip fences | JSON dentro de \`\`\`json...\`\`\` | JSON limpio | Transformación |
| 2 — JSON inválido | Cualquier no-JSON | `ValueError` | Excepción |
| 3 — no_pedido | `{"error": "no_pedido", ...}` | `estado=ERROR, lineas=[]` | Normalización |
| 4 — PN inventado | PN proveedor fuera de whitelist | `PN=None + alerta PARSER:` | Anulación |

---

## Siguiente tutorial

→ **[10 · Bot Telegram en vivo](10-bot-telegram-en-vivo.md)** — conecta el bot y envía una PO real desde tu móvil.
