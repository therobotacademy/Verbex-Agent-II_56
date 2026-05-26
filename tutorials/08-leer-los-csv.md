# Tutorial 08 · Leer los CSV: entender la persistencia

Inspecciona los tres CSV del sistema — `Pedidos.csv`, `Lineas.csv`, `Errores.csv` — desde Python puro. Sin API key, sin red. Los CSV son la fuente de verdad del sistema.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~10 min | **Ninguna** | `run_t08.py` |

---

## Los tres CSV del sistema

```
data/
├── Pedidos.csv    ← una fila por PO (15 columnas)
├── Lineas.csv     ← una fila por línea de PO (14 columnas)
└── Errores.csv    ← una fila por excepción técnica (6 columnas)
```

Los CSV son la "memoria" del sistema en el entorno del curso. En producción equivalen a tablas de base de datos. `persistence.py` es la única capa que los lee y escribe.

---

## Experimento A · Estructura de `Pedidos.csv`

Guarda como `run_t08a.py`:

```python
import csv, json

print("── PEDIDOS.CSV ──────────────────────────────────────────")
with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(f"Columnas ({len(reader.fieldnames)}): {reader.fieldnames}")
    rows = list(reader)

print(f"\nTotal POs: {len(rows)}")
print()

for row in rows:
    print(f"  numero_pedido   : {row['numero_pedido']}")
    print(f"  estado          : {row['estado_normalizacion']}")
    print(f"  prioridad       : {row['prioridad_calculada']}")
    print(f"  confianza       : {row['confianza']}")
    print(f"  aog             : {row['aog']}")
    print(f"  alertas         : {row['alertas'][:60] if row['alertas'] else '[]'}")
    print(f"  timestamp       : {row['timestamp']}")
    print()
```

**Qué observar:**
- 15 columnas: identificación de PO + estado/prioridad/confianza + flags (aog, cliente_no_registrado, duplicado) + estadísticas (total_lineas, alertas_count) + metadatos (timestamp, texto_original, alertas_resumen).
- `alertas_resumen` resume las alertas en texto legible; `alertas_count` es el número entero de alertas.
- `texto_original` preserva el texto bruto de la PO recibida — permite reprocesamientos y auditoría.

---

## Experimento B · Estructura de `Lineas.csv`

```python
import csv

print("── LINEAS.CSV ───────────────────────────────────────────")
with open("data/Lineas.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(f"Columnas ({len(reader.fieldnames)}): {reader.fieldnames}")
    rows = list(reader)

print(f"\nTotal líneas: {len(rows)}")
print()

# Agrupar por PO
from collections import defaultdict
por_po = defaultdict(list)
for row in rows:
    por_po[row["numero_pedido"]].append(row)

for po_num, lineas in por_po.items():
    print(f"  PO: {po_num}  ({len(lineas)} líneas)")
    for linea in lineas:
        print(f"    L{linea['linea_id']}: {linea['part_number_cliente']} → "
              f"{linea['part_number_proveedor']}  "
              f"qty={linea['cantidad']} {linea['unidad']}  "
              f"doc={linea.get('doc_requerida', '—')}")
```

**Qué observar:**
- Cada línea de PO es una fila en `Lineas.csv` (1 PO con 3 líneas = 3 filas).
- La join entre POs y Lineas es `numero_pedido` — igual que en SQL.
- `part_number_cliente` → `part_number_proveedor` — la traducción del LLM queda persistida.
- `doc_requerida` está aquí (no solo en el dict en memoria) — el CSV captura el resultado de R05+R06.

---

## Experimento C · Estructura de `Errores.csv`

```python
import csv

print("── ERRORES.CSV ──────────────────────────────────────────")
with open("data/Errores.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(f"Columnas ({len(reader.fieldnames)}): {reader.fieldnames}")
    rows = list(reader)

print(f"\nTotal errores: {len(rows)}")
for row in rows:
    print(f"  [{row['timestamp']}] {row['origen']:20s} "
          f"{row['tipo_excepcion']:20s} {row['mensaje'][:50]}")
```

**Qué observar:**
- 6 columnas: timestamp, origen (módulo/función), tipo_excepcion, mensaje, numero_pedido, traceback.
- Solo errores **técnicos** van aquí — los errores de negocio (PN desconocido, cliente no registrado) van a `alertas[]` en el dict, no a `Errores.csv`.
- Si el CSV está vacío, el pipeline no ha tenido errores técnicos. Buena señal.

---

## Experimento D · Análisis básico: estadísticas de los CSV

```python
import csv
from collections import Counter

# Pedidos por estado
with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    pedidos = list(csv.DictReader(f))

estados = Counter(r["estado_normalizacion"] for r in pedidos)
prioridades = Counter(r["prioridad_calculada"] for r in pedidos)
print("Estados:")
for k, v in estados.most_common():
    print(f"  {k:10s}: {v}")

print("\nPrioridades:")
for k, v in prioridades.most_common():
    print(f"  {k:12s}: {v}")

# Confianza promedio de las COMPLETO
completos = [float(r["confianza"]) for r in pedidos
             if r["estado_normalizacion"] == "COMPLETO"]
if completos:
    print(f"\nConfianza media (COMPLETO): {sum(completos)/len(completos):.3f}")

# Lineas por PO
with open("data/Lineas.csv", newline="", encoding="utf-8") as f:
    lineas = list(csv.DictReader(f))

from collections import defaultdict
lineas_por_po = defaultdict(int)
for l in lineas:
    lineas_por_po[l["numero_pedido"]] += 1
print(f"\nLineas por PO: min={min(lineas_por_po.values())}, "
      f"max={max(lineas_por_po.values())}, "
      f"media={sum(lineas_por_po.values())/len(lineas_por_po):.1f}")
```

**Qué observar:** este análisis ad-hoc es el precursor del dashboard Streamlit (II-6). La diferencia es que el dashboard lo actualiza automáticamente; aquí tú escribes la query Python.

---

## Experimento E · Unir Pedidos y Lineas (join manual)

```python
import csv

with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    pedidos = {r["numero_pedido"]: r for r in csv.DictReader(f)}

with open("data/Lineas.csv", newline="", encoding="utf-8") as f:
    lineas = list(csv.DictReader(f))

print("── Vista unificada (Pedido + Líneas) ────────────────")
for linea in lineas:
    po = pedidos.get(linea["numero_pedido"], {})
    print(f"PO: {linea['numero_pedido']:30s} "
          f"estado={po.get('estado_normalizacion', '?'):10s} "
          f"L{linea['linea_id']}: {linea['part_number_cliente']:20s} "
          f"qty={linea['cantidad']:4s} {linea['unidad']}")
```

---

## Lo que acabas de aprender

- `Pedidos.csv` (15 cols) + `Lineas.csv` (14 cols) + `Errores.csv` (6 cols) son la memoria del sistema.
- Los errores de negocio van a `alertas[]` en el dict → `Pedidos.csv`. Los técnicos van a `Errores.csv`.
- `persistence.py` es la única capa que toca los CSV — nunca desde `rules.py` o `llm.py`.
- Los joins entre CSVs usan `numero_pedido` como clave, igual que en SQL relacional.

---

## Siguiente tutorial

→ **[09 · Parser anti-alucinación: las 4 guardias](09-parser-anti-alucinacion.md)** — disecciona `_parsear_respuesta()` guardia a guardia.  
→ **[10 · Bot Telegram en vivo](10-bot-telegram-en-vivo.md)** — levanta el bot y envía una PO desde tu móvil.
