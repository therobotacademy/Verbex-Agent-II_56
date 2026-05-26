# Tutorial de operación — Agente VERBEX

> Sesión II-4/II-5 · COIIAOC Parte 2 — Automatización de Procesos con Agentes Inteligentes

Este tutorial recorre el agente de principio a fin ejecutando comandos reales.
Cada paso muestra la salida esperada y explica qué parte del código la produce
y cómo se corresponde con el workflow n8n que ya conoces.

**Requisito previo:** haber copiado `.env.example` a `.env` y completado al menos
`ANTHROPIC_API_KEY` y `TELEGRAM_BOT_TOKEN`.

```bash
cp .env.example .env   # luego edita .env con tus credenciales
pip install -r requirements.txt
```

---

## Paso 1 — Verifica que el entorno funciona

```bash
python -c "from anthropic import Anthropic; from dotenv import load_dotenv; load_dotenv(); print('OK')"
```

Salida esperada: `OK`. Si aparece `ModuleNotFoundError`, ejecuta `pip install -r requirements.txt`.

---

## Paso 2 — Corre los tests (gate de corrección)

```bash
pytest tests/ -v
```

Salida esperada:

```
tests/test_rules.py::test_caso_estandar             PASSED   [12%]
tests/test_rules.py::test_r01_aog                   PASSED   [25%]
tests/test_rules.py::test_r02_fecha_urgente         PASSED   [37%]
tests/test_rules.py::test_r03_confianza_baja        PASSED   [50%]
tests/test_rules.py::test_r04_pn_desconocido        PASSED   [62%]
tests/test_rules.py::test_r05_r06_doc_requerida     PASSED   [75%]
tests/test_rules.py::test_r07_cliente_no_registrado PASSED   [87%]
tests/test_rules.py::test_r08_cantidad_invalida     PASSED   [100%]

8 passed in 0.03s
```

**¿Qué prueba cada test?**

| Test | Regla | Lo que comprueba |
|---|---|---|
| `test_caso_estandar` | — | PO válida en todo → COMPLETO · NORMAL |
| `test_r01_aog` | R01 | `aog=True` eleva a AOG todas las líneas |
| `test_r02_fecha_urgente` | R02 | Fecha a 3 días → PRIORITARIO |
| `test_r03_confianza_baja` | R03 | Confianza 0.60 degrada COMPLETO → PARCIAL |
| `test_r04_pn_desconocido` | R04 | PN fuera de tabla → ERROR |
| `test_r05_r06_doc_requerida` | R05+R06 | CoC + EASA Form 1 → `doc_requerida` correcto |
| `test_r07_cliente_no_registrado` | R07 | `codigo_erp=null` → `cliente_no_registrado` + PARCIAL |
| `test_r08_cantidad_invalida` | R08 | `cantidad=0` → ERROR |

> **Conexión n8n:** cada test reproduce exactamente uno de los 8 casos del panel de
> prueba que validaste en el nodo Code de n8n. La lógica es la misma; cambia el contenedor.

---

## Paso 3 — Juega con una regla sola (shell interactivo)

Abre Python y experimenta con `rules.py` directamente.
Las reglas son funciones puras: entran un dict, salen un dict, sin red ni ficheros.

```python
import rules

# PO mínima para probar R03 (confianza baja)
po = {
    "numero_pedido": "PO-TEST-001",
    "cliente": {"nombre": "Stratos Systems", "codigo_erp": "STRA-001", "tier": "TIER_1"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "ST9-HTP-RIB-047",
        "cantidad": 5,
        "unidad": "EA",
        "fecha_entrega_requerida": "2026-12-01",
        "requiere_coc": False,
        "requiere_easa_form1": False,
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.55,   # <-- baja a propósito
    "alertas": [],
    "aog": False,
}

resultado = rules.aplicar_reglas(po)

print(resultado["estado_normalizacion"])   # PARCIAL
print(resultado["alertas"])               # ['R03: confianza baja (0.55 < 0.80)']
```

Ahora prueba R01 cambiando una sola línea:

```python
po["aog"] = True
po["confianza"] = 0.95
resultado = rules.aplicar_reglas(po)

print(resultado["prioridad_calculada"])                        # AOG
print([l["prioridad"] for l in resultado["lineas"]])          # ['AOG']
```

> **Clave de diseño:** las reglas nunca llaman al LLM y nunca escriben en disco.
> Eso es el **principio E5** del curso: el LLM extrae, las reglas deciden, los
> módulos de `verbex/` actúan. Tres capas separadas = tres responsabilidades únicas.

---

## Paso 4 — Ve cómo el LLM extrae una PO de texto libre

Este paso requiere `ANTHROPIC_API_KEY` en `.env`.

```python
import os
from dotenv import load_dotenv
load_dotenv()

from verbex import llm

texto = """
Purchase Order PO-2025-STRA-0847. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.
Ref: ST-900 program. CoC required.
"""

po = llm.normalizar(texto)

import json
print(json.dumps(po, indent=2, ensure_ascii=False))
```

Salida real del agente:

```json
{
  "numero_pedido": "PO-2025-STRA-0847",
  "cliente": {
    "nombre": "Stratos Systems",
    "tier": "TIER_1",
    "codigo_erp": "STRA-001"
  },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "ST9-HTP-RIB-047",
      "part_number_proveedor": "VBX-COMP-4471-B",
      "descripcion": "Costilla composite HTP sección delantera",
      "cantidad": 12,
      "unidad": "EA",
      "fecha_entrega_requerida": "2025-09-15",
      "programa": "ST900",
      "prioridad": "NORMAL",
      "requiere_coc": true,
      "requiere_easa_form1": false
    }
  ],
  "estado_normalizacion": "COMPLETO",
  "confianza": 0.97,
  "alertas": [],
  "aog": false
}
```

Observa:
- `"15/09/2025"` → `"2025-09-15"`: el LLM normaliza la fecha al formato ISO.
- `"ST9-HTP-RIB-047"` → `"VBX-COMP-4471-B"`: el LLM mapea el PN del cliente al PN interno
  usando la tabla de equivalencias de `SKILL.md`.
- `prioridad: "NORMAL"` por defecto: el LLM **no calcula prioridad**. Eso lo hará R01/R02.
- El parser `_parsear_respuesta()` en `verbex/llm.py` verifica que `VBX-COMP-4471-B`
  esté en `PNS_VALIDOS`. Si el LLM alucinara un PN inventado, lo anularía y añadiría
  una alerta `PARSER:`.

> **Conexión n8n:** este paso equivale exactamente a los tres nodos
> "Construir body API" → "Cognitivo · Llamada Claude API" → "Validar JSON LLM".
> El código en `verbex/llm.py` hace lo mismo, cargando el mismo `PERSONA.md` + `SKILL.md`.

---

## Paso 5 — Pipeline completo: LLM → reglas → CSV

```python
import os
from dotenv import load_dotenv
load_dotenv()

from verbex import llm, persistence
import rules, json

texto = """
Purchase Order PO-2025-STRA-0848. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 6 EA, Need Date: 20/12/2025.
Ref: ST-900 program. CoC required.
"""

# 1. Capa cognitiva
po = llm.normalizar(texto)
print("Tras LLM:", po["estado_normalizacion"], "confianza=", po["confianza"])

# 2. Reglas deterministas
po = rules.aplicar_reglas(po)
print("Tras reglas:", po["estado_normalizacion"], "prioridad=", po["prioridad_calculada"])
print("doc_requerida línea 1:", po["lineas"][0].get("doc_requerida"))

# 3. Anti-duplicado R09
po["duplicado"] = persistence.es_duplicado(po["numero_pedido"])
print("¿Duplicado?", po["duplicado"])

# 4. Guardar en CSV si no es duplicado
if not po["duplicado"]:
    persistence.append_pedido(po, texto)
    persistence.append_lineas(po)
    print("Guardado en data/Pedidos.csv y data/Lineas.csv")
```

Salida esperada:

```
Tras LLM: COMPLETO confianza= 0.97
Tras reglas: COMPLETO prioridad= NORMAL
doc_requerida línea 1: ['CoC']
¿Duplicado? False
Guardado en data/Pedidos.csv y data/Lineas.csv
```

La regla R05 construyó `doc_requerida = ["CoC"]` porque `requiere_coc=True`.
La prioridad es NORMAL porque la fecha de entrega está a más de 7 días y `aog=False`.

---

## Paso 6 — Anti-duplicado: envía la misma PO dos veces

Vuelve a ejecutar el bloque del Paso 5 con exactamente el mismo `texto` (misma PO).
En la segunda ejecución:

```python
po["duplicado"] = persistence.es_duplicado("PO-2025-STRA-0848")
print("¿Duplicado?", po["duplicado"])   # True
```

Salida:

```
¿Duplicado? True
```

Cuando `es_duplicado` devuelve `True`, el orquestador `main.process()` llama a
`notify.telegram_operador_duplicado(po)` y detiene el pipeline ahí.
La PO no se vuelve a guardar ni se notifica a producción o calidad.

> **Conexión n8n:** esto es el nodo "R09 · Buscar PO en CSV" + el nodo "Evaluar duplicado"
> + el branch de la condición IF que iba al nodo "Telegram · Operador (duplicado)".

---

## Paso 7 — Casos de error: qué pasa cuando la PO es mala

### 7a. PN de cliente desconocido (R04)

```python
import rules

po = {
    "numero_pedido": "PO-ERR-001",
    "cliente": {"nombre": "Stratos Systems", "codigo_erp": "STRA-001", "tier": "TIER_1"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "ST9-HTP-RIB-999",   # no existe en EQUIVALENCIAS
        "cantidad": 5, "unidad": "EA",
        "fecha_entrega_requerida": "2026-12-01",
        "requiere_coc": False, "requiere_easa_form1": False,
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.90,
    "alertas": [], "aog": False,
}

out = rules.aplicar_reglas(po)
print(out["estado_normalizacion"])   # ERROR
print(out["alertas"])               # ['R04: PN cliente desconocido: ST9-HTP-RIB-999 (línea 1)']
```

### 7b. Cantidad inválida (R08)

```python
po["lineas"][0]["part_number_cliente"] = "ST9-HTP-RIB-047"   # PN válido ahora
po["lineas"][0]["cantidad"] = 0                               # cantidad inválida

out = rules.aplicar_reglas(po)
print(out["estado_normalizacion"])   # ERROR
print(out["alertas"])               # ['R08: cantidad inválida: 0 (línea 1)']
```

### 7c. Texto que no es una PO

```python
import os
from dotenv import load_dotenv
load_dotenv()
from verbex import llm

out = llm.normalizar("Hola, ¿cuándo abrís mañana?")
print(out["estado_normalizacion"])   # ERROR
print(out["alertas"])               # ['LLM clasificó como no_pedido: ...']
```

El LLM responde `{ "error": "no_pedido", "mensaje": "..." }` y el parser
`_parsear_respuesta()` lo convierte en `estado_normalizacion = "ERROR"` con la alerta.
Las reglas no se ejecutan sobre texto que no es una PO.

---

## Paso 8 — Prueba AOG: máxima prioridad

```python
import os
from dotenv import load_dotenv
load_dotenv()
from verbex import llm
import rules

texto_aog = """
URGENT AOG — Aircraft on Ground.
PO: AOG-2025-HELI-0012. Client: Helion Aircraft.
Part HX7-ELV-220 · qty 2 EA · need ASAP · EASA Form 1 required.
"""

po = llm.normalizar(texto_aog)
print("LLM detectó AOG:", po.get("aog"))        # True

po = rules.aplicar_reglas(po)
print("Prioridad:", po["prioridad_calculada"])                      # AOG
print("Líneas:", [l["prioridad"] for l in po["lineas"]])           # ['AOG']
print("Doc requerida:", po["lineas"][0].get("doc_requerida"))      # ['EASA Form 1']
```

La palabra "AOG" en el texto activa `aog=True` en el LLM (regla absoluta definida en
`PERSONA.md`). R01 hereda ese flag y eleva toda la PO y cada línea a prioridad AOG.
En producción esto dispararía `notify.telegram_produccion_aog()`: el equipo recibe
alerta inmediata en Telegram con el mensaje "🚨 AOG · VERBEX".

---

## Paso 9 — Levanta el bot Telegram

```bash
python telegram_bot.py
```

Salida en consola:

```
VERBEX bot escuchando… (Ctrl+C para parar)
```

El bot entra en bucle de `getUpdates` (long-polling a 30 s) y espera mensajes.

**Envía esta PO desde Telegram** al chat del bot:

```
Purchase Order PO-2025-STRA-0848. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 6 EA, Need Date: 20/12/2025.
Ref: ST-900 program. CoC required.
```

El bot responde en segundos en el mismo chat:

```
✅ PO procesada
Número: PO-2025-STRA-0848
Estado: COMPLETO · Prioridad: NORMAL
Líneas: 1
```

Y en el chat de calidad llega automáticamente:

```
📋 Documentación requerida · VERBEX

PO: PO-2025-STRA-0848
Cliente: Stratos Systems

Líneas con certificación:
· VBX-COMP-4471-B → CoC

Preparar documentación antes de envío.
```

**Prueba de duplicado:** envía exactamente la misma PO una segunda vez.
El bot responde al chat de producción:

```
⚠ VERBEX · PO duplicada

PO: PO-2025-STRA-0848
Cliente: Stratos Systems

No se reenvía notificación.
```

**Prueba de texto no-PO:** envía `"Hola, ¿qué tal?"`.
El bot responde en el chat del remitente:

```
❌ Error procesando la PO: SCHEMA_ERROR: lineas[] vacío
```

---

## Paso 10 — Observa los CSV resultantes

Después de varias pruebas, abre los ficheros de datos:

```bash
# Windows
type data\Pedidos.csv

# macOS / Linux
cat data/Pedidos.csv
```

Cada fila es una PO procesada. Las columnas relevantes:

| Campo | Qué muestra |
|---|---|
| `estado_normalizacion` | COMPLETO / PARCIAL / ERROR |
| `prioridad_calculada` | NORMAL / PRIORITARIO / AOG |
| `confianza` | Score 0–1 asignado por el LLM |
| `alertas_count` | Cuántas alertas generaron las reglas |
| `duplicado` | True si fue bloqueada como duplicada |
| `texto_original` | El texto libre que llegó por Telegram |

`data/Lineas.csv` tiene una fila por cada línea de cada PO, con los Part Numbers
ya traducidos y la lista `doc_requerida` aplanada a texto (`"CoC"`, `"CoC, EASA Form 1"`…).

> Estos CSV son el equivalente exacto de las hojas `Pedidos` y `Lineas` de Google Sheets
> que usaba el workflow n8n. El schema de columnas es idéntico para que los datos
> sean intercambiables entre las dos implementaciones.

---

## Mapa completo del código

```
texto de Telegram
      │
      ▼
telegram_bot.py            ← trigger (= nodo "Manual Trigger" de n8n)
  └─ _handle()
      │
      ▼
main.process()             ← grafo del workflow (nodos conectados en secuencia)
  │
  ├─ verbex/llm.normalizar()             ← nodos "Construir body" + "Claude API" + "Validar JSON"
  │     └─ PERSONA.md + SKILL.md         ← system prompt (= SOUL_verbex + SKILL_verbex en n8n)
  │
  ├─ rules.aplicar_reglas()              ← nodos Code R04+R08, R07, R01+R02, R05+R06, R03
  │     R04+R08 → validar PN y cantidad
  │     R07     → validar cliente ERP
  │     R01+R02 → calcular prioridad
  │     R05+R06 → construir doc_requerida
  │     R03     → umbral de confianza
  │
  ├─ persistence.es_duplicado()          ← nodo "R09 · Buscar PO en CSV"
  │
  ├─ [if duplicado] notify.telegram_operador_duplicado()
  │
  └─ [si no duplicado]
        ├─ persistence.append_pedido()       ← nodo "CSV · Append Pedidos"
        ├─ persistence.append_lineas()       ← nodo "CSV · Append Lineas"
        ├─ notify.telegram_produccion_*()    ← nodo Switch + "Telegram Producción"
        ├─ notify.telegram_calidad()         ← nodo Filter + "Telegram Calidad"
        └─ notify.email_enviar()             ← nodos "Render email" + "Email · Enviar"
```

---

## Preguntas frecuentes

**¿Por qué las reglas son funciones puras sin efectos secundarios?**
Para que sean testeables con `pytest` sin red ni credenciales. Un test de `rules.py` pasa
igual en tu portátil que en un servidor de CI. Los efectos (CSV, Telegram, email) son
difíciles de testear aislados, así que viven en `verbex/` y se prueban manualmente o con mocks.

**¿Por qué el LLM no calcula la prioridad?**
Porque el LLM puede alucinar. Una función Python que hace
`(fecha - date.today()).days <= 7` nunca se equivoca. Es el **principio E5** del curso:
usas el LLM para lo que hace bien (extraer estructura de lenguaje natural) y el código
determinista para lo que tiene que ser exacto.

**¿Qué ocurre si el email SMTP falla?**
La excepción sube hasta `telegram_bot._handle()`, que la captura y responde al chat
con `❌ Error procesando la PO: <mensaje>`. La PO **sí fue guardada en CSV** y las
notificaciones de Telegram **sí se enviaron**. Solo falla la confirmación email al cliente.
Para activarlo, reemplaza las credenciales SMTP en `.env` con una App Password real de Gmail.

**¿Puedo cambiar el comportamiento del LLM sin tocar `rules.py`?**
Sí. Edita `PERSONA.md` o `SKILL.md`. Son los mismos ficheros que en n8n llamabas
`SOUL_verbex.md` y `SKILL_verbex.md`. El código los carga en tiempo de ejecución;
no necesitas reiniciar el bot si solo cambias los prompts.

**¿Cómo sé qué parte del código ejecutó cada mensaje?**
Añade `print()` al inicio de cada función en `verbex/llm.py`, `rules.py` y `verbex/notify.py`
mientras practicas. En producción, se sustituirían por llamadas al módulo `logging` de la
librería estándar — eso queda para II-5.
