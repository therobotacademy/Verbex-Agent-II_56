# Tutorial 06 · Casos de error del pipeline

¿Qué pasa cuando algo sale mal? Aquí provocas errores controlados y observas cómo el pipeline los maneja — sin que el sistema se rompa irrecuperablemente.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~15 min | **Ninguna** (experimentos A–D) / `ANTHROPIC_API_KEY` (E) | `run_t06.py` |

---

## Taxonomía de errores del pipeline

```
Error de negocio       → estado=ERROR en el dict po (alertas[], no excepción)
Error técnico parser   → ValueError con prefijo JSON_PARSE_ERROR:
Error técnico red/API  → anthropic.APIError, propagada hasta main.py
Error I/O CSV          → OSError, capturado en observability
Error notificación     → SMTPException / TelegramError, no afecta CSV
```

Los errores de negocio **no son excepciones** — son datos. Los errores técnicos sí son excepciones y se registran en `data/Errores.csv` vía `observability.registrar_excepcion()`.

---

## Experimento A · Error de negocio: PN desconocido

```python
import sys
sys.path.insert(0, '.')
import rules

po = {
    "numero_pedido": "PO-ERR-001",
    "cliente": {"codigo_erp": "STRA-001"},
    "lineas": [{"linea_id": 1,
                "part_number_cliente": "XX-INVENTADO-999",
                "cantidad": 5, "unidad": "EA",
                "fecha_entrega_requerida": "2026-12-01",
                "requiere_coc": False, "requiere_easa_form1": False}],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.97, "alertas": [], "aog": False,
}

out = rules.aplicar_reglas(po)
print("estado      :", out["estado_normalizacion"])   # ERROR
print("alertas     :", out["alertas"])
print("¿excepción? : No — el error está en el dict, no en Python")
```

**Qué observar:** `estado=ERROR` es un valor en el dict. El código que llama a `rules.aplicar_reglas()` no necesita un `try/except` para este caso. El error está modelado como dato.

---

## Experimento B · Error técnico: JSON malformado del LLM

```python
import sys
sys.path.insert(0, '.')
from verbex.llm import _parsear_respuesta

# Simula lo que devolvería un LLM con fallo de generación
respuestas_malas = [
    '{"numero_pedido": "PO-X", "lineas": [ROTO',           # JSON inválido
    '',                                                       # respuesta vacía
    'Lo siento, no puedo procesar esta solicitud.',          # texto plano (no JSON)
]

for resp in respuestas_malas:
    try:
        po = _parsear_respuesta(resp)
        print(f"  OK: {po.get('estado_normalizacion')}")
    except ValueError as e:
        print(f"  ValueError: {str(e)[:80]}")
```

**Salida esperada:**
```
  ValueError: JSON_PARSE_ERROR: Expecting value: line 1 column 38 (char 37)
  ValueError: JSON_PARSE_ERROR: ...
  ValueError: JSON_PARSE_ERROR: ...
```

El prefijo `JSON_PARSE_ERROR:` permite distinguir estos errores de otros `ValueError` en los logs.

---

## Experimento C · Error técnico: `observability` en acción

```python
import sys
sys.path.insert(0, '.')
from verbex import observability
import traceback

observability.setup_logging()

# Simular un error técnico y registrarlo
try:
    raise ConnectionError("Timeout conectando a Anthropic API")
except ConnectionError as e:
    observability.registrar_excepcion(e, origen="tutorial_06_exp_c")
    print("Excepción registrada en data/Errores.csv")

# Ver la última fila de Errores.csv
import csv
with open("data/Errores.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
if rows:
    last = rows[-1]
    print(f"Timestamp : {last.get('timestamp')}")
    print(f"Origen    : {last.get('origen')}")
    print(f"Tipo      : {last.get('tipo_error')}")
    print(f"Mensaje   : {str(last.get('error_raw', ''))[:60]}")
```

**Qué observar:** `observability.registrar_excepcion()` escribe en `data/Errores.csv` **sin relanzar la excepción**. El pipeline puede decidir si continuar o abortar — la decisión está en `main.py`, no en `observability`.

---

## Experimento D · El pipeline completo con error de negocio

Traza el ciclo de vida completo de una PO con PN desconocido:

```python
import sys
sys.path.insert(0, '.')
from verbex import persistence
import rules

# 1. Simular output del LLM (con PN cliente fuera de EQUIVALENCIAS)
po_post_llm = {
    "numero_pedido": "PO-ERR-002",
    "cliente": {"codigo_erp": "STRA-001", "nombre": "Stratos Systems"},
    "lineas": [{"linea_id": 1,
                "part_number_cliente": "ST9-INVENTADO-XXX",
                "part_number_proveedor": None,   # guardia 4 ya actuó
                "cantidad": 3, "unidad": "EA",
                "fecha_entrega_requerida": "2026-09-01",
                "requiere_coc": False, "requiere_easa_form1": False}],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.65, "alertas": ["PN cliente ST9-INVENTADO-XXX no encontrado"],
    "aog": False,
}

# 2. Aplicar reglas (R04 detectará PN desconocido → ERROR)
po = rules.aplicar_reglas(po_post_llm)
print("Post-reglas:")
print(f"  estado  : {po['estado_normalizacion']}")
print(f"  alertas : {po['alertas']}")

# 3. Anti-duplicado (no es duplicado porque nunca estuvo en COMPLETO)
es_dup = persistence.es_duplicado(po["numero_pedido"])
print(f"\nEs duplicado: {es_dup}")  # False

# 4. Persistir (se escribe aunque sea ERROR — queda en el registro)
# persistence.append_pedido(po)  # descomenta si quieres escribir
print("\nConclusión: la PO en ERROR se registra en CSV para auditoría")
print("Puede reprocesarse cuando se corrija el PN del cliente")
```

---

## Experimento E · Error real de API (necesita API key y red)

```python
import os
from dotenv import load_dotenv
load_dotenv()

import anthropic

# Llamar con modelo inexistente para provocar error controlado
client = anthropic.Anthropic()
try:
    resp = client.messages.create(
        model="modelo-que-no-existe",
        max_tokens=10,
        messages=[{"role": "user", "content": "test"}]
    )
except anthropic.BadRequestError as e:
    print("BadRequestError:", str(e)[:100])
except anthropic.NotFoundError as e:
    print("NotFoundError:", str(e)[:100])
except Exception as e:
    print(f"{type(e).__name__}: {str(e)[:100]}")
```

**Qué observar:** los errores de la API de Anthropic son excepciones Python estándar del SDK — no dicts. Se propagan hasta `main.py`, que los captura en el bloque `try/except` general y los registra con `observability.registrar_excepcion()`.

---

## Lo que acabas de aprender

- Los errores de **negocio** (PN inválido, cliente desconocido) son **datos** en el dict `po`, no excepciones.
- Los errores **técnicos** (JSON roto, red caída) son **excepciones** Python, registradas en `Errores.csv`.
- `observability.registrar_excepcion()` escribe el error sin relanzarlo — el pipeline decide si abortar.
- Una PO en `ERROR` sí se escribe en CSV (para auditoría) y **no** es duplicado — puede reprocesarse.

---

## Siguiente tutorial

→ **[07 · AOG: prioridad máxima end-to-end](07-aog-maxima-prioridad.md)** — traza una PO de emergencia desde el texto libre hasta el CSV y la notificación.
