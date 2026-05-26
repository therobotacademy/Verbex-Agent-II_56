# Tutoriales de familiarización — VERBEX Agent Python

Secuencia de tutoriales de acceso rápido al código del agente VERBEX.  
Cada tutorial es independiente y se completa en 10–20 minutos.  
El orden propuesto va de zero-code a full-code: puedes empezar sin haber leído nada.

---

## Prerrequisitos comunes

```bash
pip install -r requirements.txt
cp .env.example .env          # editar con tus credenciales
```

Cada tutorial indica qué credenciales necesita para ejecutarse.

---

## Lista de tutoriales

| # | Fichero | Título | Tiempo | Credenciales mínimas |
|---|---------|--------|--------|----------------------|
| 01 | [01-smoke-test-end-to-end.md](01-smoke-test-end-to-end.md) | Smoke test end-to-end | 10 min | Solo `ANTHROPIC_API_KEY` |
| 02 | [02-reglas-en-el-shell.md](02-reglas-en-el-shell.md) | Reglas sin red: el shell interactivo | 10 min | Ninguna |
| 03 | [03-llm-directamente.md](03-llm-directamente.md) | El LLM en acción: texto → JSON | 15 min | `ANTHROPIC_API_KEY` |
| 04 | [04-tests-rojo-verde.md](04-tests-rojo-verde.md) | Tests: de rojo a verde | 20 min | Ninguna |
| 05 | [05-anti-duplicado.md](05-anti-duplicado.md) | Anti-duplicado R09 | 10 min | `ANTHROPIC_API_KEY` |
| 06 | [06-casos-de-error.md](06-casos-de-error.md) | Casos de error: PN, cantidad, texto | 15 min | `ANTHROPIC_API_KEY` |
| 07 | [07-aog-maxima-prioridad.md](07-aog-maxima-prioridad.md) | AOG: máxima prioridad | 10 min | `ANTHROPIC_API_KEY` |
| 08 | [08-leer-los-csv.md](08-leer-los-csv.md) | Leer los CSV de salida | 10 min | Ninguna |
| 09 | [09-parser-anti-alucinacion.md](09-parser-anti-alucinacion.md) | El parser anti-alucinación | 15 min | `ANTHROPIC_API_KEY` |
| 10 | [10-bot-telegram-en-vivo.md](10-bot-telegram-en-vivo.md) | Bot Telegram en vivo | 15 min | `ANTHROPIC_API_KEY` + `TELEGRAM_*` |

---

## Descripción de cada tutorial

### 01 · Smoke test end-to-end
Primera toma de contacto sin haber estudiado el código. En dos fases: primero se ejecuta la capa cognitiva (LLM) y las reglas en una sola línea de Python; después, el pipeline completo `main.py`. Al terminar tendrás una PO procesada en los CSV. Solo necesitas `ANTHROPIC_API_KEY`.

### 02 · Reglas sin red: el shell interactivo
Las reglas de `rules.py` son funciones puras — reciben un diccionario, devuelven un diccionario, sin red, sin credenciales. Este tutorial juega con ellas desde el REPL de Python: cambias valores, ves cómo cambia el resultado. Ideal para entender R01–R09 antes de implementarlas.

### 03 · El LLM en acción: texto → JSON
Llama a `llm.normalizar()` directamente con distintos textos de PO y observa la respuesta raw de Claude: PN traducidos, fechas normalizadas, confianza calculada. También provoca al parser anti-alucinación con un PN inventado y verás cómo lo anula.

### 04 · Tests: de rojo a verde
El ciclo completo de II-5 en miniatura: `pytest` arranca en rojo (8 tests fallando), implementas las cinco funciones de `rules.py` una a una, y el contador verde sube. Cada función tiene pistas en el test correspondiente. El tutorial te guía test a test.

### 05 · Anti-duplicado R09
Envías la misma PO dos veces a través de `main.py`. La primera vez se procesa y queda en CSV. La segunda, `persistence.es_duplicado()` devuelve `True`, el pipeline se corta y el operador recibe una alerta. Ves exactamente el punto de corte y la fila en CSV que lo activa.

### 06 · Casos de error
Tres entradas que activan error-paths distintos: un PN de cliente fuera del catálogo (R04 → ERROR), una cantidad cero (R08 → ERROR) y un texto que no es una PO (LLM → `no_pedido`, reglas no se ejecutan). Cada caso muestra qué campo cambia y qué alerta se genera.

### 07 · AOG: máxima prioridad
Envías una PO con la palabra "AOG" en el texto. El LLM detecta `aog=True`, R01 eleva la PO a prioridad AOG y cada línea individual hereda esa prioridad. Ves en el CSV el campo `prioridad_calculada=AOG` y entiendes por qué el fan-out de notificaciones es distinto.

### 08 · Leer los CSV de salida
Sin ejecutar código nuevo: abre `data/Pedidos.csv` y `data/Lineas.csv` con un editor o con Python/pandas y lee las columnas fila a fila. El tutorial explica qué significa cada columna, cómo se relacionan las dos tablas (clave `numero_pedido`) y dónde vive la información de certificación.

### 09 · El parser anti-alucinación
Centra el foco en `verbex/llm.py`: las cuatro guardias de `_parsear_respuesta()`. Llamas a `llm.normalizar()` con POs deliberadamente ambiguas (PN de proveedor inventado, texto a medio escribir, mensaje no en inglés ni en español) y observas qué guardia actúa en cada caso y qué deja en `alertas[]`.

### 10 · Bot Telegram en vivo
Levanta el bot con `python telegram_bot.py` y envía POs reales desde tu móvil. El tutorial guía la configuración mínima de Telegram (crear bot con BotFather, obtener chat_id, completar `.env`) y propone tres mensajes de prueba: PO estándar, AOG, y texto no-PO.

---

## Orden recomendado

```
Sin credenciales:    02 → 08 → 04
Solo ANTHROPIC_KEY:  01 → 03 → 05 → 06 → 07 → 09
Credenciales completas: 10
```

El tutorial 04 (tests rojo→verde) es el núcleo de II-5: hazlo antes de la sesión práctica.
