# Memory — Qué recuerda el agente VERBEX entre ejecuciones

> En n8n la "memoria" del agente eran las hojas de Google Sheets: cada PO procesada quedaba
> registrada y el nodo de lookup (R09) la consultaba para detectar duplicados. En el repo
> Python esa memoria son ficheros CSV locales. Este `MEMORY.md` es el **índice** de esa
> memoria: documenta *qué* se recuerda, *dónde* vive y *para qué* se usa. No es la base de
> datos en sí — es el mapa de la memoria del agente.

---

## 1. Pedidos procesados — `data/Pedidos.csv`

- **Qué guarda:** una fila por cada PO normalizada (15 columnas: timestamp, numero_pedido, cliente, estado, prioridad, confianza, aog, totales, flags y resúmenes).
- **Para qué se usa:** detección anti-spam / anti-duplicado (regla **R09**). Antes de registrar una PO nueva, el agente busca en este fichero si ya existe el mismo `numero_pedido` con `estado_normalizacion = COMPLETO`. Si existe, marca la PO como duplicada y no reprocesa.
- **Quién lo escribe:** `verbex/persistence.py · append_pedido()`.
- **Quién lo lee:** `verbex/persistence.py · buscar_po()` (= nodo R09 lookup de n8n).
- **Equivalente n8n:** hoja `Pedidos` del Google Sheet `VERBEX-Pedidos`.

## 2. Líneas de pedido — `data/Lineas.csv`

- **Qué guarda:** una fila por cada línea de cada PO (14 columnas: PN cliente/proveedor, cantidad, unidad, fecha, programa, prioridad, certificaciones, doc_requerida).
- **Para qué se usa:** trazabilidad y registro detallado. No se consulta para anti-spam (eso es a nivel de PO).
- **Quién lo escribe:** `verbex/persistence.py · append_lineas()`.
- **Equivalente n8n:** hoja `Lineas` del Google Sheet.

## 3. Catálogo de clientes y PN — **embebido en `SKILL.md`**

- **Qué guarda:** la tabla nombre→codigo_erp, las equivalencias PN cliente→PN proveedor y el catálogo de certificaciones (CoC / EASA Form 1).
- **Para qué se usa:** el LLM la consulta al extraer; las reglas `rules.py` la reusan para validar (R04, R07).
- **Por qué vive en SKILL y no en CSV:** es conocimiento **estable** del dominio (cambia raras veces), no estado operativo. Por eso se versiona con el prompt, no con los datos.
- **Equivalente n8n:** hoja `Clientes` + las constantes hardcoded en los nodos Code.

---

## Regla de diseño: estado vs. conocimiento

| Tipo                                                     | Dónde vive      | Ejemplo                                     |
| -------------------------------------------------------- | ---------------- | ------------------------------------------- |
| **Estado operativo** (cambia en cada ejecución)   | CSV en `data/` | POs procesadas, líneas                     |
| **Conocimiento de dominio** (estable)              | `SKILL.md`     | equivalencias PN, catálogo certificaciones |
| **Identidad y reglas del agente** (casi inmutable) | `PERSONA.md`   | "nunca invento Part Numbers"                |

Esta separación es la misma que ya viste en n8n: los datos en Sheets, el conocimiento en el prompt, la identidad en el system message.
