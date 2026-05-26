# Dry Run · Sesiones II-5 y II-6 — VERBEX COMPOSITES

**Curso:** COIIAOC · Parte 2 · Fork Python  
**Repo:** `verbex-agent-56-github`  
**Fecha de preparación:** 2026-05-26  
**Sesiones cubiertas:** II-5 (implementar + probar) y II-6 (operar + desplegar)

---

## 1. Contexto del arco del curso

| Sesión | Contenido | Producto |
|--------|-----------|----------|
| II-1 | Prompt engineering: PERSONA + SKILL | `PERSONA.md`, `SKILL.md` |
| II-2 | Parser anti-alucinación, few-shots | `verbex/llm.py` finalizado |
| II-3 | Reglas deterministas en n8n Code node | 8 casos de prueba validados |
| II-4 | Workflow completo n8n con CSV/Telegram/email | `workflow_II4-csv.json` |
| **II-5** | **Reescritura Python: rules.py + main.py** | **`pytest` pasa de rojo a verde** |
| **II-6** | **Observabilidad + dashboard + deploy** | **Sistema operable en Windows** |

**Idea clave de la sesión:** el workflow que construiste en n8n ya es un agente; Python lo hace operable. Misma lógica, distinto contenedor.

---

## 2. Estructura del repositorio

```
verbex-agent-56-github/
├── PERSONA.md          system prompt — identidad del agente (no editar)
├── SKILL.md            instrucciones + few-shots + tablas de referencia (no editar)
├── MEMORY.md           índice de persistencia del agente
├── rules.py            R01–R09 como funciones puras      ← lo implementa el alumno (II-5)
├── main.py             orquestador del pipeline          ← lo implementa el alumno (II-5)
├── telegram_bot.py     trigger Telegram (completo en starter kit)
├── verbex/
│   ├── llm.py          capa cognitiva: texto → JSON (completo)
│   ├── persistence.py  leer/escribir CSV (completo)
│   ├── notify.py       Telegram × 4 + email (completo)
│   └── observability.py logging + Errores.csv (completo)
├── data/
│   ├── Pedidos.csv     memoria de POs (anti-duplicado R09)
│   ├── Lineas.csv      registro de líneas por PN
│   └── Errores.csv     fallos técnicos del pipeline
├── dashboard/app.py    Streamlit read-only sobre los CSV (II-6)
├── deploy/             start_verbex.bat + task-scheduler.md (II-6)
├── tests/test_rules.py 8 casos de prueba (rojo → verde en II-5)
├── II-56/              material de la sesión (slides PDF + guía HTML)
├── proyecto-alumno/    brief + rúbrica del proyecto entregable
├── py-blank/           plantilla vacía para el proyecto del alumno
└── docs/               diagramas SVG de arquitectura
```

### Mapa n8n → Python

| n8n | Python |
|-----|--------|
| SOUL_verbex.md (system prompt) | `PERSONA.md` |
| SKILL_verbex.md (instrucciones) | `SKILL.md` |
| Nodo LLM (Claude) | `verbex/llm.py · normalizar()` |
| Nodos Code (R01–R09) | `rules.py · aplicar_reglas()` |
| Nodos Google Sheets | `verbex/persistence.py` |
| Nodos Telegram / Email | `verbex/notify.py` |
| Error Trigger Workflow | `verbex/observability.py` |
| Grafo de conexiones | `main.py · process()` |
| Webhook trigger | `telegram_bot.py` |

---

## 3. Estado del starter kit al inicio de II-5

### Completo y funcional (no tocar)
- `PERSONA.md`, `SKILL.md`, `MEMORY.md`
- `verbex/llm.py`, `persistence.py`, `notify.py`, `observability.py`
- `telegram_bot.py`
- `data/Pedidos.csv`, `data/Lineas.csv` (con 5 POs y 7 líneas de ejemplo)
- `tests/test_rules.py` (8 tests en ROJO porque `rules.py` tiene `pass`)

### A implementar en II-5 (objetivo del alumno)
- `rules.py` — 5 funciones puras + orquestador
- `main.py` — orquestador completo del pipeline

### A instalar/configurar en II-6
- `dashboard/app.py` — levantar Streamlit
- `deploy/start_verbex.bat` — arrancar 2 procesos
- Windows Task Scheduler — automatizar arranque

---

## 4. Principio rector: E5

> **El LLM extrae, las reglas deciden.**

| Capa | Fichero | Hace |
|------|---------|------|
| Cognitiva | `verbex/llm.py` | Texto libre → JSON estructurado |
| Lógica | `rules.py` | Valida, calcula, decide (puro, sin red) |
| Persistencia | `verbex/persistence.py` | Lee/escribe CSV |
| Notificación | `verbex/notify.py` | Telegram + email |
| Orquestación | `main.py` | Encadena todas las capas |

**Lo que E5 prohíbe expresamente:**
- `rules.py` nunca llama al LLM
- `verbex/llm.py` nunca aplica lógica de negocio
- `rules.py` nunca escribe CSV ni envía mensajes

Esta separación es lo que hace las reglas **testeables sin red ni credenciales**.

---

## 5. Las reglas R01–R09 en detalle

### Firma de todas las funciones

```python
def r_XX_nombre(po: dict) -> dict:
    # recibe PO, devuelve PO modificada
    # sin efectos secundarios
```

### Tablas de referencia en rules.py

```python
EQUIVALENCIAS = {
    "ST9-HTP-RIB-047": "VBX-COMP-4471-B",  # Costilla HTP delantera, ST900
    "ST9-HTP-RIB-048": "VBX-COMP-4472-C",
    "HX7-FUS-PNL-331": "VBX-COMP-3301-A",  # Panel fuselaje central, HX7
    "HX7-FUS-PNL-332": "VBX-COMP-3302-A",
    "HX7-BHD-332":     "VBX-COMP-3303-B",  # Mamparo presurización, HX7
    "ST9-LE-PNL-550":  "VBX-COMP-5501-A",  # Borde de ataque ala, ST900
    "HX7-ELV-220":     "VBX-COMP-2201-C",  # Timón profundidad, RT55
}
CLIENTES_VALIDOS = {"STRA-001", "KAIRO-001", "KAIRO-002", "HELI-001", "VECT-001"}
UNIDADES_VALIDAS = {"EA", "KG", "ML", "M2"}
```

### Orden de aplicación (crítico)

```
R04+R08 (validar líneas) → R07 (cliente ERP) → R01+R02 (prioridad) → R05+R06 (doc) → R03 (confianza)
```

### Lógica de cada regla

| Regla(s) | Condición | Acción |
|----------|-----------|--------|
| R04 | PN cliente NO en EQUIVALENCIAS | alerta + estado → ERROR |
| R08 | cantidad ≤ 0 o unidad inválida | alerta + estado → ERROR |
| R07 | codigo_erp NO en CLIENTES_VALIDOS | `cliente_no_registrado=True`; si estado=COMPLETO → PARCIAL |
| R01 | `aog=True` | `prioridad_calculada="AOG"`; cada línea `prioridad="AOG"` |
| R02 | `fecha_entrega_requerida` en 0–7 días | línea `prioridad="PRIORITARIO"`; global sube si era NORMAL |
| R05 | `requiere_coc=True` | `doc_requerida` incluye `"CoC"` |
| R06 | `requiere_easa_form1=True` | `doc_requerida` incluye `"EASA Form 1"` |
| R03 | `confianza < 0.80` y estado=COMPLETO | degrada a PARCIAL + alerta |
| R09 | `numero_pedido` ya existe en Pedidos.csv | `duplicado=True` (evaluado en `main.py`, no en reglas) |

### Función orquestadora

```python
def aplicar_reglas(po: dict) -> dict:
    po = copy.deepcopy(po)      # nunca muta la entrada
    po = r04_r08_validar_lineas(po)
    po = r07_validar_cliente(po)
    po = r01_r02_prioridad(po)
    po = r05_r06_doc_requerida(po)
    po = r03_confianza(po)
    return po
```

---

## 6. El orquestador main.py

```python
def process(texto_po: str) -> dict:
    # 1. Capa cognitiva
    po = llm.normalizar(texto_po)

    # 2. Reglas deterministas (R01–R08)
    po = rules.aplicar_reglas(po)

    # 3. R09 anti-duplicado
    po["duplicado"] = persistence.es_duplicado(po["numero_pedido"])

    # 4. Rama duplicado
    if po.get("duplicado"):
        notify.telegram_operador_duplicado(po)
        return po

    # 5. Fan-out (no duplicado)
    persistence.append_pedido(po, texto_po)
    persistence.append_lineas(po)

    if po["prioridad_calculada"] == "AOG":
        notify.telegram_produccion_aog(po)
    elif po["prioridad_calculada"] == "PRIORITARIO":
        notify.telegram_produccion_prioritario(po)

    if any(l.get("requiere_coc") or l.get("requiere_easa_form1") for l in po["lineas"]):
        notify.telegram_calidad(po)

    notify.email_enviar(po)
    return po
```

---

## 7. Los 8 tests (tests/test_rules.py)

Cada test reproduce uno de los 8 casos de prueba validados en el nodo Code de n8n.

| Test | Entrada | Regla ejercida | Resultado esperado |
|------|---------|----------------|-------------------|
| `test_caso_estandar` | PO válida, PN conocido, confianza 0.97 | — | COMPLETO, NORMAL |
| `test_r01_aog` | `aog=True` | R01 | prioridad=AOG; cada línea AOG |
| `test_r02_fecha_urgente` | fecha en 3 días | R02 | prioridad=PRIORITARIO |
| `test_r03_confianza_baja` | confianza=0.60 | R03 | degrada a PARCIAL |
| `test_r04_pn_desconocido` | PN fuera de tabla | R04 | estado=ERROR, alerta |
| `test_r05_r06_doc_requerida` | CoC+EASA ambos True | R05+R06 | doc_requerida=["CoC","EASA Form 1"] |
| `test_r07_cliente_no_registrado` | `codigo_erp=None` | R07 | PARCIAL, `cliente_no_registrado=True` |
| `test_r08_cantidad_invalida` | cantidad=0 | R08 | estado=ERROR, alerta |

**Gate de corrección:** `pytest tests/ -v` debe terminar con `8 passed`.

---

## 8. Guía paso a paso (M3 — sesión)

### II-5

**Paso 1 — Prepara el entorno**
```bash
cp .env.example .env        # editar: ANTHROPIC_API_KEY + TELEGRAM_BOT_TOKEN
pip install -r requirements.txt
python -c "from anthropic import Anthropic; print('OK')"
```

**Paso 2 — Corre los tests (parten en rojo)**
```bash
pytest tests/ -v
# objetivo: 8 passed in 0.03s
```

**Paso 3 — Implementa las reglas**  
Implementa las 5 funciones en `rules.py` + `aplicar_reglas()`. Corre `pytest` tras cada función.

**Paso 4 — Juega con una regla en el shell (sin red)**
```python
import rules
po = {"numero_pedido":"PO-T","cliente":{"codigo_erp":"STRA-001"},
      "lineas":[{"linea_id":1,"part_number_cliente":"ST9-HTP-RIB-047",
      "cantidad":5,"unidad":"EA","fecha_entrega_requerida":"2026-12-01"}],
      "estado_normalizacion":"COMPLETO","confianza":0.55,"alertas":[],"aog":False}
print(rules.aplicar_reglas(po)["estado_normalizacion"])   # → PARCIAL (R03)
```

**Paso 5 — Llama al LLM directamente** (requiere API key)
```python
from verbex import llm
po = llm.normalizar("Purchase Order PO-2025-STRA-0847. Stratos Systems.\n"
                    "Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025. CoC required.")
# confianza 0.97; PN → VBX-COMP-4471-B; fecha → 2025-09-15
```

**Paso 6 — Completa main.py**  
Encadena `llm.normalizar → rules.aplicar_reglas → es_duplicado → [CSV + notify]`.

**Paso 7 — Prueba anti-duplicado**  
Envía la misma PO dos veces: la segunda activa la alerta de duplicado y corta el pipeline.

**Paso 8 — Casos de error**

| Entrada | Regla | Resultado |
|---------|-------|-----------|
| PN cliente desconocido | R04 | ERROR + alerta |
| cantidad = 0 | R08 | ERROR + alerta |
| cliente no en ERP | R07 | PARCIAL + flag |
| confianza < 0.80 | R03 | PARCIAL |
| texto que no es una PO | LLM | ERROR (reglas no se ejecutan) |

**Paso 9 — Levanta el bot y prueba AOG**
```bash
python telegram_bot.py
# VERBEX bot escuchando… (Ctrl+C para parar)
```
Envía una PO con "AOG" → LLM marca `aog=True` → R01 eleva a AOG → producción recibe alerta.

---

### II-6

**Paso 10 — Observabilidad** (ya implementada en starter kit)

| Pilar | Qué responde | Dónde |
|-------|-------------|-------|
| Logs | qué pasó y cuándo | `logs/verbex.log` |
| Métricas | con qué frecuencia | KPIs del dashboard |
| Trazas | por qué falló | `error_raw` en `Errores.csv` |

**Paso 11 — Dashboard Streamlit**
```bash
pip install -r dashboard/requirements.txt
python -m streamlit run dashboard/app.py
# → http://localhost:8501
```
5 KPIs: POs totales · hoy · AOGs · tasa de éxito · errores 7d.  
Filtros: programa / estado / prioridad.  
Pestañas: últimas POs con líneas detalladas + pestaña de errores.

**Paso 12 — Deploy (2 procesos, doble clic)**
```
deploy/start_verbex.bat  →  proceso 1: telegram_bot.py
                         →  proceso 2: streamlit dashboard/app.py
```
`deploy/task-scheduler.md`: automatizar arranque al iniciar sesión en Windows Task Scheduler.

---

## 9. Módulos core ya implementados

### verbex/llm.py

- Modelo: `claude-sonnet-4-20250514`, `MAX_TOKENS=1500`, `TEMPERATURE=0.1`
- Carga `PERSONA.md + SKILL.md` como system prompt
- **Parser anti-alucinación:** anula cualquier `part_number_proveedor` no en la tabla de 16 PNs válidos; si el LLM lo inventa, lo deja en `null` y añade alerta

### verbex/persistence.py

- `buscar_po(numero_pedido)` — R09 lookup en Pedidos.csv
- `es_duplicado(numero_pedido)` — True si ya existe un COMPLETO
- `append_pedido(po, texto_original)` — escribe fila en Pedidos.csv
- `append_lineas(po)` — escribe una fila por línea en Lineas.csv
- `append_error(...)` — registra fallo técnico en Errores.csv

### verbex/notify.py

- `telegram_operador_duplicado(po)` — ⚠ aviso al operador
- `telegram_produccion_aog(po)` — 🚨 AOG urgente
- `telegram_produccion_prioritario(po)` — ⚠ PO PRIORITARIA
- `telegram_calidad(po)` — 📋 documentación requerida
- `email_enviar(po)` — email HTML branded VERBEX vía SMTP

### verbex/observability.py

- `setup_logging()` — configura logger "verbex" (fichero + consola, idempotente)
- `registrar_excepcion(exc, origen, numero_pedido, texto_original)` — loggea + persiste en Errores.csv

---

## 10. Datos de ejemplo incluidos

### data/Pedidos.csv (5 POs)

| numero_pedido | cliente | estado | prioridad | aog |
|--------------|---------|--------|-----------|-----|
| PO-2025-STRA-0847 | Stratos Systems | COMPLETO | NORMAL | False |
| PO-2026-STRA-0901 | Stratos Systems | COMPLETO | NORMAL | False |
| PO-2026-KAI-0055-AOG | Kairos Aerospace | COMPLETO | AOG | True |
| PO-2026-VECT-0012 | (cliente desconocido) | ERROR | — | False |
| PO-2026-STRA-E2E-143002 | Stratos Systems | COMPLETO | NORMAL | False |

### data/Lineas.csv (7 líneas)

Incluye mappings `ST9-HTP-RIB-047 → VBX-COMP-4471-B`, `HX7-FUS-PNL-331 → VBX-COMP-3301-A`, AOG con 2 líneas, y 1 línea con PN desconocido.

---

## 11. Configuración (.env)

```env
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID_PRODUCCION=-100111...
TELEGRAM_CHAT_ID_CALIDAD=-100222...
TELEGRAM_ALLOWED_CHAT_IDS=           # vacío = todos; o lista separada por comas
SMTP_FROM=pedidos@verbex.example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=pedidos@verbex.example
SMTP_PASSWORD=app-password-google
CSV_DATA_DIR=                         # opcional; default: ./data/
```

---

## 12. Proyecto del alumno (II-6)

### Objetivo

Adaptar el patrón VERBEX a otro dominio (mantener arquitectura, cambiar problema).

### Dominios sugeridos

- A) Mantenimiento programado (preventive maintenance)
- B) Gestión de no conformidades (NCR)
- C) Control de stock crítico (kanban-style)
- D) Dominio propio

### Entregables mínimos

1. `catalogo.csv` (≥10 ítems)
2. `actores.csv` (≥3 roles)
3. Schema JSON documentado
4. `PERSONA.md` con ≥5 reglas absolutas
5. `SKILL.md` con ≥3 few-shots distintos
6. `rules.py` con ≥3 funciones puras (nombres R01/R02/…)
7. `tests/test_rules.py` con ≥3 tests verdes (sin red, sin API keys)
8. `main.py` con encadenamiento + anti-duplicado + routing condicional
9. `README.md`

### Rúbrica (criterios obligatorios 90%)

| Bloque | Peso | Criterio clave |
|--------|------|----------------|
| Schema JSON | 15% | tipos documentados, capa cognitiva vs determinista |
| Tablas | 10% | catálogo ≥10, actores ≥3, cabeceras consistentes |
| PERSONA | 10% | ≥5 reglas absolutas, manejo no-pertinente |
| SKILL | 10% | pasos de extracción, tablas embebidas, ≥3 few-shots |
| rules.py | 20% | ≥3 funciones puras, orquestador, sin efectos |
| tests | 15% | ≥3 verde, al menos uno rechazado, sin red |
| main.py | 10% | anti-duplicado, routing condicional |
| README | 10% | dominio, capas con I/O, cómo correr |

### Antipatrones penalizadores

| Antipatrón | Penalización |
|-----------|-------------|
| LLM calcula valores (fechas, cantidades) | -15% |
| Sin parser anti-alucinación | -10% |
| rules.py con efectos secundarios | -10% |
| Sin tests | -15% |
| Sin diferenciación capa cognitiva/lógica | -15% |
| README pobre | -20% |

---

## 13. Prompts del sistema (PERSONA.md)

### Reglas absolutas del agente

1. **Nunca calcula** fechas, días ni cantidades — solo extrae literal del texto
2. **Nunca inventa** Part Numbers — si no reconoce el PN, lo devuelve tal cual + confianza baja
3. **AOG** es máxima prioridad detectable (busca "AOG", "Aircraft on Ground", "inmovilizado")
4. **Amendment** → referencia PO original en `alertas[]`
5. **Solo devuelve JSON** — sin markdown, sin explicaciones
6. El idioma de los campos extraídos = idioma del documento (no traduce)
7. **No calcula prioridad ni doc_requerida** — eso lo hacen R01–R09

### Si el texto no es una PO

```json
{"error": "no_pedido", "mensaje": "El texto no contiene una orden de compra reconocible."}
```

---

## 14. Schema JSON de salida del LLM

```json
{
  "numero_pedido": "PO-2025-STRA-0847",
  "cliente": {
    "nombre": "Stratos Systems",
    "codigo_erp": "STRA-001"
  },
  "fecha_recepcion": "2025-09-01",
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "ST9-HTP-RIB-047",
      "part_number_proveedor": "VBX-COMP-4471-B",
      "descripcion": "Costilla HTP delantera",
      "cantidad": 12,
      "unidad": "EA",
      "fecha_entrega_requerida": "2025-09-15",
      "programa": "ST900",
      "requiere_coc": true,
      "requiere_easa_form1": false,
      "doc_requerida": [],
      "prioridad": "NORMAL"
    }
  ],
  "estado_normalizacion": "COMPLETO",
  "prioridad_calculada": "NORMAL",
  "confianza": 0.97,
  "aog": false,
  "alertas": [],
  "duplicado": false,
  "cliente_no_registrado": false
}
```

**Estados:** `COMPLETO` | `PARCIAL` | `ERROR`  
**Prioridades:** `AOG` | `PRIORITARIO` | `NORMAL`  
**Confianza:** 0.95–1.0=estructurado | 0.80–0.95=libre estándar | 0.60–0.80=PN desconocido | <0.60=varios campos faltantes

---

## 15. Coste estimado en producción

- Claude API: ~20 €/mes (volumen normal)
- Telegram bot: gratuito
- SMTP (Gmail): gratuito
- Persistencia (CSV local): gratuita
- Dashboard (Streamlit local): gratuito
- **Total: ~20 €/mes**

---

## 16. Checklist de verificación (dry run)

### Pre-sesión

- [ ] Repo clonado y tests corriendo (`pytest tests/ -v` → 8 ROJO esperado)
- [ ] `.env` configurado con `ANTHROPIC_API_KEY`
- [ ] `python -c "from anthropic import Anthropic; print('OK')"` pasa
- [ ] `python -c "import rules; print('OK')"` pasa (aunque tests fallen)

### Durante II-5

- [ ] `rules.py`: `r04_r08_validar_lineas` → 2 tests pasan
- [ ] `rules.py`: `r07_validar_cliente` → 1 test más pasa
- [ ] `rules.py`: `r01_r02_prioridad` → 2 tests más pasan
- [ ] `rules.py`: `r05_r06_doc_requerida` → 1 test más pasa
- [ ] `rules.py`: `r03_confianza` → último test pasa
- [ ] `pytest tests/ -v` → **8 passed** ✅
- [ ] `main.py`: pipeline completo funciona con PO demo
- [ ] Anti-duplicado: segunda PO idéntica → alerta, no doble escritura

### Durante II-6

- [ ] `python -m streamlit run dashboard/app.py` abre http://localhost:8501
- [ ] Dashboard muestra las 5 POs de ejemplo
- [ ] `start_verbex.bat` lanza 2 ventanas (bot + dashboard)
- [ ] `logs/verbex.log` tiene entradas tras procesar una PO

---

*Documento generado para dry run de sesión — 2026-05-26*
