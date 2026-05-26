# Tutorial 02 · Reglas sin red: el shell interactivo

Juega con las funciones de `rules.py` desde el REPL de Python. Sin API key, sin Telegram, sin CSV — las reglas son funciones puras que reciben un `dict` y devuelven un `dict`.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~10 min | **Ninguna** | `run_t02.py` |

---

## Por qué esto es posible

```python
# rules.py — firma de cualquier regla
def r04_r08_validar_lineas(po: dict) -> dict:
    # recibe dict, devuelve dict, sin efectos secundarios
```

Las reglas no llaman al LLM, no leen CSV, no envían mensajes. Puedes pasarles cualquier dict fabricado a mano y ver el resultado en milisegundos. Eso es el principio E5 en la práctica.

---

## Setup (30 s)

```bash
python -c "import rules; print('OK')"   # no necesita .env
```

---

## Experimento 1 · R04+R08: validaciones de línea

Guarda como `run_t02.py` y ejecuta con `python run_t02.py`:

```python
import rules

# PO base válida (punto de partida de todos los experimentos)
def po_base():
    return {
        "numero_pedido": "PO-T",
        "cliente": {"codigo_erp": "STRA-001"},
        "lineas": [{
            "linea_id": 1,
            "part_number_cliente": "ST9-HTP-RIB-047",
            "cantidad": 5, "unidad": "EA",
            "fecha_entrega_requerida": "2026-12-01",
            "requiere_coc": False, "requiere_easa_form1": False,
        }],
        "estado_normalizacion": "COMPLETO",
        "confianza": 0.97, "alertas": [], "aog": False,
    }

# --- R04: PN desconocido ---
po = po_base()
po["lineas"][0]["part_number_cliente"] = "ST9-UNKNOWN-999"
out = rules.r04_r08_validar_lineas(po)
print("R04 — PN desconocido")
print("  estado :", out["estado_normalizacion"])   # ERROR
print("  alertas:", out["alertas"])

print()

# --- R08: cantidad 0 ---
po = po_base()
po["lineas"][0]["cantidad"] = 0
out = rules.r04_r08_validar_lineas(po)
print("R08 — cantidad 0")
print("  estado :", out["estado_normalizacion"])   # ERROR
print("  alertas:", out["alertas"])

print()

# --- R08: unidad inválida ---
po = po_base()
po["lineas"][0]["unidad"] = "PZ"
out = rules.r04_r08_validar_lineas(po)
print("R08 — unidad inválida")
print("  estado :", out["estado_normalizacion"])   # ERROR
print("  alertas:", out["alertas"])
```

---

## Experimento 2 · R07: cliente no registrado

```python
# Añade al final de run_t02.py:

po = po_base()
po["cliente"]["codigo_erp"] = "CLIENTE-NUEVO"  # no está en CLIENTES_VALIDOS
out = rules.r07_validar_cliente(po)
print("\nR07 — cliente no registrado")
print("  estado              :", out["estado_normalizacion"])   # PARCIAL
print("  cliente_no_registrado:", out.get("cliente_no_registrado"))  # True
print("  alertas             :", out["alertas"])
```

---

## Experimento 3 · R01+R02: prioridad

```python
import datetime as dt

# R01 — AOG
po = po_base()
po["aog"] = True
out = rules.r01_r02_prioridad(po)
print("\nR01 — AOG")
print("  prioridad_calculada:", out["prioridad_calculada"])           # AOG
print("  prioridad línea 1  :", out["lineas"][0]["prioridad"])        # AOG

# R02 — fecha urgente (3 días)
po = po_base()
po["lineas"][0]["fecha_entrega_requerida"] = (
    dt.date.today() + dt.timedelta(days=3)
).isoformat()
out = rules.r01_r02_prioridad(po)
print("\nR02 — fecha a 3 días")
print("  prioridad_calculada:", out["prioridad_calculada"])           # PRIORITARIO

# R02 — fecha lejana (no urgente)
po = po_base()
po["lineas"][0]["fecha_entrega_requerida"] = "2027-01-01"
out = rules.r01_r02_prioridad(po)
print("\nR02 — fecha lejana")
print("  prioridad_calculada:", out["prioridad_calculada"])           # NORMAL
```

---

## Experimento 4 · R05+R06: doc_requerida

```python
# Solo CoC
po = po_base()
po["lineas"][0]["requiere_coc"] = True
out = rules.r05_r06_doc_requerida(po)
print("\nR05 — solo CoC")
print("  doc_requerida:", out["lineas"][0].get("doc_requerida"))  # ['CoC']

# CoC + EASA Form 1
po = po_base()
po["lineas"][0]["requiere_coc"] = True
po["lineas"][0]["requiere_easa_form1"] = True
out = rules.r05_r06_doc_requerida(po)
print("\nR05+R06 — CoC + EASA")
print("  doc_requerida:", out["lineas"][0].get("doc_requerida"))  # ['CoC', 'EASA Form 1']

# Ninguno
po = po_base()
out = rules.r05_r06_doc_requerida(po)
print("\nNinguno requerido")
print("  doc_requerida:", out["lineas"][0].get("doc_requerida"))  # None
```

---

## Experimento 5 · R03: confianza baja

```python
# Confianza 0.60 — degrada COMPLETO a PARCIAL
po = po_base()
po["confianza"] = 0.60
out = rules.r03_confianza(po)
print("\nR03 — confianza 0.60")
print("  estado :", out["estado_normalizacion"])  # PARCIAL
print("  alertas:", out["alertas"])

# Confianza 0.85 — no degrada
po = po_base()
po["confianza"] = 0.85
out = rules.r03_confianza(po)
print("\nR03 — confianza 0.85")
print("  estado :", out["estado_normalizacion"])  # COMPLETO (sin cambio)
```

---

## Experimento 6 · El orden importa: aplicar_reglas()

```python
# ¿Qué pasa si confianza=0.60 Y aog=True?
po = po_base()
po["confianza"] = 0.60
po["aog"] = True
out = rules.aplicar_reglas(po)
print("\naog=True + confianza=0.60")
print("  estado    :", out["estado_normalizacion"])  # PARCIAL (R03 lo degradó)
print("  prioridad :", out["prioridad_calculada"])   # AOG (R01 lo elevó)
# Las reglas no se contradicen: estado y prioridad son dimensiones independientes
```

---

## Lo que acabas de aprender

- Cada función recibe un dict y devuelve un dict. **Nunca modifica la entrada original** (`copy.deepcopy` interno).
- El orden en `aplicar_reglas()` importa: R04+R08 va primero porque si hay ERROR, las reglas siguientes siguen corriendo pero sobre datos ya marcados.
- `estado` y `prioridad` son **dimensiones independientes**: una PO puede ser AOG (máxima prioridad) y aun así tener confianza baja (PARCIAL).

---

## Siguiente tutorial

→ **[03 · El LLM en acción](03-llm-directamente.md)** — ahora que entiendes qué hacen las reglas, observa qué les llega desde el LLM.  
→ **[04 · Tests: de rojo a verde](04-tests-rojo-verde.md)** — usa los mismos dicts fabricados para escribir tus propios tests.
