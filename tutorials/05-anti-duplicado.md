# Tutorial 05 · Anti-duplicado: R09 y el CSV

R09 es la única "regla" del pipeline que no es una función pura — vive en `verbex/persistence.py` y lee el CSV. Aquí entenderás por qué y cómo se comporta.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~10 min | **Ninguna** | `verbex/persistence.py` |

---

## Por qué R09 no está en `rules.py`

```python
# rules.py — solo funciones puras (dict → dict)
# R09 requiere leer data/Pedidos.csv → efecto secundario → no puede ir aquí

# verbex/persistence.py — aquí vive es_duplicado()
def es_duplicado(numero_pedido: str) -> bool:
    # abre Pedidos.csv, busca el numero_pedido, devuelve True/False
```

El principio E5 exige que `rules.py` sea completamente puro. R09 rompe esa pureza al necesitar acceso al sistema de ficheros. Por eso vive en `persistence.py` y `main.py` lo llama antes de las reglas.

---

## Flujo en `main.py`

```
main.process(texto_po)
    │
    ├─ llm.normalizar()          ← LLM extrae dict
    ├─ rules.aplicar_reglas()    ← R01–R08 (puras)
    │
    ├─ persistence.es_duplicado(numero_pedido)
    │       ↓ True → return (no CSV, no notificaciones)
    │       ↓ False → continuar
    │
    ├─ persistence.append_pedido()  ← escribe CSV
    └─ notify.*()                   ← Telegram + email
```

**Orden crítico:** el CSV se escribe **antes** del fan-out de notificaciones. Si Telegram falla, la PO ya está registrada. El fallo es de notificación, no de persistencia.

---

## Experimento A · Inspeccionar `es_duplicado` directamente

Guarda como `run_t05a.py`:

```python
import sys
sys.path.insert(0, '.')
from verbex import persistence

# PO que sabemos que ya existe en Pedidos.csv (viene en los datos de muestra)
pn = "PO-2025-STRA-0847"
print(f"¿Es duplicado '{pn}'?  →  {persistence.es_duplicado(pn)}")

# PO inventada que no existe
pn2 = "PO-2099-TEST-NEVER"
print(f"¿Es duplicado '{pn2}'?  →  {persistence.es_duplicado(pn2)}")
```

**Salida esperada:**
```
¿Es duplicado 'PO-2025-STRA-0847'?  →  True
¿Es duplicado 'PO-2099-TEST-NEVER'?  →  False
```

---

## Experimento B · ¿Qué cuenta como duplicado?

Lee el código de `es_duplicado` en `verbex/persistence.py`:

```python
def es_duplicado(numero_pedido: str) -> bool:
    if not os.path.exists(RUTA_PEDIDOS):
        return False
    with open(RUTA_PEDIDOS, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row["numero_pedido"] == numero_pedido
                    and row["estado_normalizacion"] == "COMPLETO"):
                return True
    return False
```

**Condición exacta:** mismo `numero_pedido` **Y** `estado_normalizacion=COMPLETO`.

Implicación: si una PO procesó con `ERROR` (PN desconocido), **no se considera duplicado**. El operador puede reenviarla una vez corregida y el pipeline la reprocesará.

Guarda como `run_t05b.py`:

```python
import sys, csv
sys.path.insert(0, '.')
from verbex import persistence

# Ver qué POs en el CSV son COMPLETO vs ERROR/PARCIAL
with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Total POs en CSV: {len(rows)}")
for row in rows:
    print(f"  {row['numero_pedido']:30s}  estado={row['estado_normalizacion']}")

# Probar la lógica de duplicado directamente
print()
for row in rows:
    pn = row["numero_pedido"]
    print(f"  es_duplicado('{pn}') = {persistence.es_duplicado(pn)}")
```

---

## Experimento C · Simular el pipeline con duplicado

Guarda como `run_t05c.py`:

```python
import sys
sys.path.insert(0, '.')
from verbex import persistence
import rules

# Construir una PO ya procesada
po = {
    "numero_pedido": "PO-2025-STRA-0847",
    "cliente": {"codigo_erp": "STRA-001"},
    "lineas": [{"linea_id": 1, "part_number_cliente": "ST9-HTP-RIB-047",
                "cantidad": 12, "unidad": "EA",
                "fecha_entrega_requerida": "2025-09-15",
                "requiere_coc": True, "requiere_easa_form1": False}],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.97, "alertas": [], "aog": False,
}

po = rules.aplicar_reglas(po)

# Simular la lógica de main.py
if persistence.es_duplicado(po["numero_pedido"]):
    print(f"⚠ Duplicado: {po['numero_pedido']} — pipeline detenido")
else:
    print(f"✓ Nueva PO: {po['numero_pedido']} — continuaría al CSV")
```

**Salida esperada:**
```
⚠ Duplicado: PO-2025-STRA-0847 — pipeline detenido
```

---

## Experimento D · Ver `append_pedido` en acción (sin escribir realmente)

Revisa en `verbex/persistence.py` qué columnas escribe `append_pedido`:

```python
# COLS_PEDIDOS en persistence.py
COLS_PEDIDOS = [
    "numero_pedido", "cliente_codigo_erp", "cliente_nombre",
    "estado_normalizacion", "prioridad_calculada", "confianza",
    "aog", "alertas", "cliente_no_registrado", "total_lineas",
    "lineas_error", "lineas_ok", "timestamp", "modelo_llm", "version_rules"
]
```

15 columnas. La PO normalizada (`dict`) se transforma a fila CSV mediante un mapping explícito — ningún campo del LLM va directamente al CSV sin pasar por la lista de columnas. Eso previene que campos inesperados del LLM contaminen el CSV.

---

## Lo que acabas de aprender

- R09 no existe en `rules.py` por diseño — requiere I/O, viola la pureza.
- `es_duplicado` comprueba `numero_pedido + estado=COMPLETO`. Una PO en ERROR puede reprocesarse.
- El CSV se escribe antes del fan-out: la persistencia es atómica respecto a las notificaciones.
- `COLS_PEDIDOS` es la lista explícita de qué va al CSV — sin campos inesperados.

---

## Siguiente tutorial

→ **[06 · Casos de error del pipeline](06-casos-de-error.md)** — qué pasa cuando el LLM devuelve basura, la red cae o el CSV está corrupto.
