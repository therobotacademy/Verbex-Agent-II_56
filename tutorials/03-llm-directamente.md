# Tutorial 03 · El LLM en acción: texto → JSON

Llama a `llm.normalizar()` directamente y observa cómo Claude convierte texto libre en JSON estructurado. Verás cómo varía la confianza con la calidad del input y cómo el parser anti-alucinación intercepta PNs inventados — sin tocar `rules.py`.

| Tiempo | Credenciales | Fichero de apoyo |
|--------|-------------|-----------------|
| ~15 min | `ANTHROPIC_API_KEY` | `run_t03.py` (ver abajo) |

---

## Arquitectura de la capa cognitiva

```
texto libre
    │
    ▼
cargar_system_prompt()   ← PERSONA.md + SKILL.md concatenados
    │
    ▼
build_messages()         ← envuelve el texto en {"role": "user", ...}
    │
    ▼
client.messages.create() ← llamada a la API de Anthropic
    │
    ▼
_parsear_respuesta()     ← 4 guardias anti-alucinación
    │
    ▼
dict po                  ← lo que recibe rules.py
```

El principio E5 empieza exactamente aquí: lo que sale de `_parsear_respuesta()` es un dict limpio. A partir de ese punto, todo es Python determinista.

---

## Experimento A · ¿Qué recibe Claude?

Antes de hacer llamadas, observa qué se le envía exactamente al modelo.

Guarda como `run_t03a.py` y ejecuta con `python run_t03a.py`:

```python
from dotenv import load_dotenv
load_dotenv()
from verbex import llm

# A1: el system prompt (PERSONA.md + SKILL.md concatenados)
sp = llm.cargar_system_prompt()
print(f"System prompt: {len(sp)} caracteres, {len(sp.splitlines())} líneas")
print("──── Primeras 5 líneas ────")
for line in sp.splitlines()[:5]:
    print(" ", line)

# A2: el mensaje de usuario que recibe Claude
msgs = llm.build_messages("Purchase Order PO-TEST. Stratos Systems. Part: ST9-HTP-RIB-047, 5 EA.")
print("\n──── Mensaje de usuario ────")
print(f"  role   : {msgs[0]['role']}")
print(f"  content: {msgs[0]['content'][:120]}…")
```

**Qué observar:**
- El system prompt tiene cientos de líneas — es `PERSONA.md` + `SKILL.md` completos.
- Claude no "recuerda" entre llamadas: cada `normalizar()` envía el system prompt entero desde cero.
- El mensaje de usuario es solo el texto de la PO envuelto en el prefijo `"Texto de la PO a normalizar:"`.

---

## Experimento B · Confianza: cómo varía con la calidad del input

Tres POs con distintos niveles de completitud. Guarda como `run_t03b.py`:

```python
import json
from dotenv import load_dotenv
load_dotenv()
from verbex import llm

casos = [
    ("PO clara y estructurada",
     "Purchase Order PO-2026-STRA-1001. Stratos Systems (STRA-001).\n"
     "Part: ST9-HTP-RIB-047, Qty: 8 EA, Need Date: 30/06/2026.\n"
     "ST900 program. CoC required."),

    ("PO en prosa, sin estructura formal",
     "Hola, somos Kairos y necesitamos 3 unidades del panel HX7-FUS-PNL-331 "
     "para el proyecto HX7. Lo antes posible, preferiblemente antes de julio. "
     "Necesitaremos EASA Form 1."),

    ("PO incompleta — cliente y fecha ambiguos",
     "Necesitamos 5 unidades del parte ST9-LE-PNL-550. "
     "El programa es el de siempre. Sin fecha concreta."),
]

for titulo, texto in casos:
    po = llm.normalizar(texto)
    estado = po.get("estado_normalizacion")
    conf   = po.get("confianza")
    pn_c   = po["lineas"][0].get("part_number_cliente") if po.get("lineas") else "—"
    pn_p   = po["lineas"][0].get("part_number_proveedor") if po.get("lineas") else "—"
    fecha  = po["lineas"][0].get("fecha_entrega_requerida") if po.get("lineas") else "—"
    print(f"\n{'─'*50}")
    print(f"  {titulo}")
    print(f"  estado    : {estado}  |  confianza: {conf}")
    print(f"  PN cliente: {pn_c}  →  PN proveedor: {pn_p}")
    print(f"  fecha     : {fecha}")
    print(f"  alertas   : {po.get('alertas')}")
```

**Qué observar:**
- La confianza baja cuando faltan datos estructurales (fechas, PN explícito, cliente identificado).
- Claude infiere el PN proveedor desde la tabla embebida en `SKILL.md` incluso con texto en prosa.
- `fecha_entrega_requerida` puede ser `null` si el texto no da una fecha concreta.

---

## Experimento C · Las 4 guardias del parser (sin API)

Estas pruebas llaman a `_parsear_respuesta()` directamente con strings fabricados. **No consumen API key.**

Guarda como `run_t03c.py`:

```python
import json
from verbex.llm import _parsear_respuesta

print("══ GUARDIA 1: strip de fences markdown ══════════")
json_con_fences = '''```json
{"numero_pedido":"PO-X","cliente":{"nombre":"Test","codigo_erp":"STRA-001"},
 "lineas":[{"linea_id":1,"part_number_cliente":"ST9-HTP-RIB-047",
 "part_number_proveedor":"VBX-COMP-4471-B","cantidad":1,"unidad":"EA",
 "fecha_entrega_requerida":"2026-12-01","requiere_coc":false,"requiere_easa_form1":false}],
 "estado_normalizacion":"COMPLETO","confianza":0.9,"alertas":[],"aog":false}
```'''
po = _parsear_respuesta(json_con_fences)
print("  Resultado:", po["estado_normalizacion"], "— fences eliminados correctamente")

print("\n══ GUARDIA 2: JSON malformado ════════════════════")
try:
    _parsear_respuesta('{"numero_pedido": "PO-X", "lineas": [ROTO')
except ValueError as e:
    print("  ValueError capturado:", str(e)[:60])

print("\n══ GUARDIA 3: respuesta no_pedido ════════════════")
no_po = '{"error": "no_pedido", "mensaje": "Consulta de disponibilidad, no es una PO"}'
po = _parsear_respuesta(no_po)
print("  estado_normalizacion:", po["estado_normalizacion"])
print("  alertas             :", po["alertas"])

print("\n══ GUARDIA 4: PN proveedor inventado ════════════")
pn_inventado = json.dumps({
    "numero_pedido": "PO-X",
    "cliente": {"nombre": "Test", "codigo_erp": "STRA-001"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "ST9-HTP-RIB-047",
        "part_number_proveedor": "VBX-COMP-9999-Z",   # ← NO está en PNS_VALIDOS
        "cantidad": 1, "unidad": "EA",
        "fecha_entrega_requerida": "2026-12-01",
        "requiere_coc": False, "requiere_easa_form1": False
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.85, "alertas": [], "aog": False
})
po = _parsear_respuesta(pn_inventado)
print("  PN proveedor tras parser:", po["lineas"][0]["part_number_proveedor"])
print("  alertas                 :", po["alertas"])
```

**Qué observar:**
- Guardia 1: el JSON es válido aunque venga envuelto en \`\`\`json.
- Guardia 2: `ValueError` con prefijo `JSON_PARSE_ERROR:` — propagable y logueable.
- Guardia 3: un JSON válido pero con `"error": "no_pedido"` produce `estado=ERROR` y `lineas=[]`.
- Guardia 4: `VBX-COMP-9999-Z` no está en `PNS_VALIDOS` → se pone a `None` y aparece en `alertas`.

---

## Experimento D · Guardia 4 end-to-end: PN inventado por el LLM

Envía una PO con un PN de cliente que NO existe en la tabla de equivalencias. El LLM intentará inferir el PN proveedor y la guardia 4 lo anulará si se inventa uno.

Guarda como `run_t03d.py`:

```python
import json
from dotenv import load_dotenv
load_dotenv()
from verbex import llm

# PN cliente real en formato plausible pero FUERA de la tabla de SKILL.md
texto = (
    "Purchase Order PO-2026-FAKE-001. Stratos Systems.\n"
    "Part: ST9-HTP-RIB-999, Qty: 4 EA, Need Date: 01/09/2026.\n"
    "ST900 program. CoC required."
)

po = llm.normalizar(texto)
linea = po["lineas"][0] if po.get("lineas") else {}

print("PN cliente  :", linea.get("part_number_cliente"))
print("PN proveedor:", linea.get("part_number_proveedor"),
      " ← None si la guardia actuó")
print("alertas     :", po.get("alertas"))
print("confianza   :", po.get("confianza"))
print("estado      :", po.get("estado_normalizacion"))
```

**Dos escenarios posibles:**
- Si Claude **no inventa** el PN proveedor → devuelve `null`. Guardia 4 no necesita actuar (el LLM siguió las instrucciones de `PERSONA.md`).
- Si Claude **inventa** un PN → la guardia 4 lo detecta (no está en `PNS_VALIDOS`), lo pone a `null` y añade alerta con prefijo `PARSER:`.

En ambos casos, `rules.py` (R04) marcará estado `ERROR` porque el PN cliente no existe en `EQUIVALENCIAS`.

---

## Lo que distingue esta capa de `rules.py`

| `verbex/llm.py` | `rules.py` |
|-----------------|------------|
| Recibe texto libre (cualquier formato) | Recibe dict estructurado |
| Produce JSON (estructura variable) | Produce dict enriquecido |
| Puede variar entre llamadas (temperatura 0.1) | Siempre determinista |
| Necesita API key y red | No necesita nada externo |
| ~3 s de latencia | ~0.1 ms de latencia |
| El parser valida la estructura | Las reglas validan el negocio |

---

## Siguiente tutorial

→ **[04 · Tests: de rojo a verde](04-tests-rojo-verde.md)** — ahora que entiendes qué produce `llm.py`, implementa las cinco funciones de `rules.py` guiado por los 8 tests. Sin API key, sin red.
