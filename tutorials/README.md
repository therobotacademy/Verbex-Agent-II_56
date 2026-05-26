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

## II-5 · Implementación y Pruebas

> **Objetivo de sesión:** `rules.py` + `main.py` implementados · `pytest 8/8` verde · pipeline end-to-end funcional.  
> **Gate:** `pytest tests/ -v` → 8 passed.

| # | Fichero | Título | Tiempo | Credenciales | Concepto clave |
|---|---------|--------|--------|--------------|----------------|
| 01 | [01-smoke-test-end-to-end.md](01-smoke-test-end-to-end.md) | Smoke test end-to-end | 10 min | `ANTHROPIC_API_KEY` | Pipeline completo de un vistazo |
| 02 | [02-reglas-en-el-shell.md](02-reglas-en-el-shell.md) | Reglas sin red: el shell interactivo | 10 min | Ninguna | Funciones puras · principio E5 |
| 03 | [03-llm-directamente.md](03-llm-directamente.md) | El LLM en acción: texto → JSON | 15 min | `ANTHROPIC_API_KEY` | Capa cognitiva · confianza · parser |
| 04 | [04-tests-rojo-verde.md](04-tests-rojo-verde.md) | Tests: de rojo a verde | 20 min | Ninguna | Tests como especificación · Gate II-5 |
| 05 | [05-anti-duplicado.md](05-anti-duplicado.md) | Anti-duplicado: R09 y el CSV | 10 min | Ninguna | R09 fuera de rules.py · pureza |
| 06 | [06-casos-de-error.md](06-casos-de-error.md) | Casos de error del pipeline | 15 min | Ninguna | Taxonomía de fallos · negocio vs técnico |
| 07 | [07-aog-maxima-prioridad.md](07-aog-maxima-prioridad.md) | AOG: prioridad máxima end-to-end | 15 min | `ANTHROPIC_API_KEY` | Señal semántica → dato estructurado |
| 09 | [09-parser-anti-alucinacion.md](09-parser-anti-alucinacion.md) | Parser anti-alucinación: las 4 guardias | 15 min | Ninguna | Guardia 1–4 · taxonomía de alertas |

---

## II-6 · Operación y Despliegue

> **Objetivo de sesión:** dashboard en `localhost:8501` · `start_verbex.bat` arranca bot + dashboard · gobernanza AS9100.  
> **Gate:** `pytest 8/8` verde + dashboard activo + deploy con doble clic.

| # | Fichero | Título | Tiempo | Credenciales | Concepto clave |
|---|---------|--------|--------|--------------|----------------|
| 08 | [08-leer-los-csv.md](08-leer-los-csv.md) | Leer los CSV: entender la persistencia | 10 min | Ninguna | Memoria del sistema · observabilidad |
| 10 | [10-bot-telegram-en-vivo.md](10-bot-telegram-en-vivo.md) | Bot Telegram en vivo | 15 min | `ANTHROPIC_API_KEY` + `TELEGRAM_*` | Adaptador de interfaz · sistema operable |

---

## Descripción de cada tutorial

### II-5 · Implementación y Pruebas

#### 01 · Smoke test end-to-end
Primera toma de contacto sin haber estudiado el código. En dos fases: primero la capa cognitiva (LLM) y las reglas; después el pipeline completo `main.py`. Al terminar tendrás una PO procesada en los CSV. Solo necesitas `ANTHROPIC_API_KEY`. _(Slide 6 — El pipeline en código)_

#### 02 · Reglas sin red: el shell interactivo
Las reglas de `rules.py` son funciones puras — reciben un dict, devuelven un dict, sin red, sin credenciales. Este tutorial juega con ellas desde el REPL: cambias valores, ves cómo cambia el resultado. Ideal para entender R01–R09 antes de implementarlas. _(Slide 8 — R01–R09 como funciones)_

#### 03 · El LLM en acción: texto → JSON
Llama a `llm.normalizar()` directamente con distintos textos de PO y observa la respuesta raw de Claude: PNs traducidos, fechas normalizadas, confianza calculada. También provoca al parser anti-alucinación con un PN inventado. _(Slide 6 — Capa cognitiva)_

#### 04 · Tests: de rojo a verde
El Gate de II-5 en miniatura: `pytest` arranca con 8 tests, lees cada test como especificación y entiendes qué función de `rules.py` implementa cada requisito de negocio. 0 llamadas de red en los tests. _(Slide 5 — Tests como especificación)_

#### 05 · Anti-duplicado: R09 y el CSV
Explora por qué R09 no vive en `rules.py` sino en `persistence.py`: requiere I/O. `es_duplicado()` comprueba `numero_pedido + estado=COMPLETO` — una PO en ERROR puede reprocesarse. _(Slide 7 — Estructura de ficheros)_

#### 06 · Casos de error del pipeline
Taxonomía de fallos (slide 4) aplicada al código: errores de negocio como datos (`estado=ERROR + alertas[]`) frente a errores técnicos como excepciones (`ValueError`, `ConnectionError` → `Errores.csv`). _(Slide 4 — Taxonomía de fallos)_

#### 07 · AOG: prioridad máxima end-to-end
El LLM detecta la señal semántica "AOG" y devuelve `aog=True`. R01 actúa sobre el booleano y eleva la prioridad. Separación E5 perfecta: el LLM no decide la prioridad; la regla no interpreta texto. _(Slide 8 — R01–R09 como funciones)_

#### 09 · Parser anti-alucinación: las 4 guardias
Disecciona `_parsear_respuesta()` guardia a guardia: strip de fences, JSON inválido, no_pedido, PN inventado. Aprende la taxonomía de prefijos de alerta: sin prefijo (LLM), `PARSER:` (parser), `R0X:` (reglas). _(Slide 6 — Capa cognitiva)_

---

### II-6 · Operación y Despliegue

#### 08 · Leer los CSV: entender la persistencia
Sin ejecutar código nuevo: inspecciona `Pedidos.csv`, `Lineas.csv` y `Errores.csv` desde Python. Entiende las 15 + 14 + 6 columnas, la join por `numero_pedido` y la diferencia entre errores de negocio (Pedidos.csv) y técnicos (Errores.csv). Precursor directo del dashboard Streamlit. _(Slide 10 — Los tres pilares de observabilidad)_

#### 10 · Bot Telegram en vivo
Levanta el bot con `python telegram_bot.py` y envía POs reales desde tu móvil. El tutorial guía la configuración mínima de Telegram y propone cuatro mensajes de prueba: PO estándar, AOG, PN desconocido y texto no-PO. El bot es un adaptador: delega todo a `main.process()`. _(Slide 11 — Deploy)_

---

## Orden recomendado

```
II-5 sin credenciales:    02 → 05 → 06 → 04
II-5 con ANTHROPIC_KEY:   01 → 03 → 07 → 09
────────────── Gate II-5: pytest 8/8 verde ──────────────
II-6 sin credenciales:    08
II-6 completo:            10
────────────── Gate II-6: dashboard + bot live ──────────
```

El tutorial **04** (tests rojo→verde) es el núcleo de II-5 — el Gate no pasa sin él.  
El tutorial **08** (leer CSV) es el puente entre II-5 y II-6: de datos de prueba a observabilidad operacional.

---

## Anexo · Clasificación por sesión y slide

| # | Tutorial | Sesión | Slide de referencia |
|---|----------|--------|---------------------|
| 01 | Smoke test end-to-end | **II-5** | Slide 6 — El pipeline en código |
| 02 | Reglas sin red | **II-5** | Slide 8 — R01–R09 como funciones |
| 03 | El LLM en acción | **II-5** | Slide 6 — Capa cognitiva |
| 04 | Tests: de rojo a verde | **II-5** | Slide 5 — Tests como especificación · **Gate** |
| 05 | Anti-duplicado R09 | **II-5** | Slide 7 — Estructura de ficheros |
| 06 | Casos de error | **II-5** | Slide 4 — Taxonomía de fallos |
| 07 | AOG: prioridad máxima | **II-5** | Slide 8 — R01–R09 como funciones |
| 08 | Leer los CSV | **II-6** | Slide 10 — Los tres pilares de observabilidad |
| 09 | Parser anti-alucinación | **II-5** | Slide 6 — Capa cognitiva |
| 10 | Bot Telegram en vivo | **II-6** | Slide 11 — Deploy |

El tutorial **08** actúa de puente: cierra II-5 (datos de prueba) y abre II-6 (observabilidad operacional).
