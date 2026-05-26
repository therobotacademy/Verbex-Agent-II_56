# Log de ejecución — Tutorial 01: Smoke test end-to-end

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.x · Anthropic API activa  
**Resultado global:** ✅ Tutorial funcional con dos correcciones aplicadas al código y al tutorial

---

## Paso 0 · Verificación de prerrequisitos

```
python -c "from anthropic import Anthropic; print('OK')"
→ OK
```

✅ `anthropic` instalado y operativo.

---

## Fase 1 · LLM + reglas

### Incidencia 1 — `load_dotenv()` no se llama automáticamente

**Síntoma:** al ejecutar el script de Fase 1 sin `load_dotenv()` explícito, el proceso falla con:

```
KeyError: 'ANTHROPIC_API_KEY'
```

**Causa raíz:** `verbex/llm.py` accede a `os.environ["ANTHROPIC_API_KEY"]` directamente. Ningún módulo del core llama `load_dotenv()`. Solo `telegram_bot.py` lo hace en su función `run()`. Por tanto, cualquier script que importe `llm` directamente (sin pasar por el bot) debe cargar el `.env` manualmente.

**Corrección aplicada:**
1. Se añadió `from dotenv import load_dotenv; load_dotenv()` al bloque `if __name__ == "__main__"` de `main.py`.
2. Se actualizó el script de Fase 1 del tutorial para incluir `load_dotenv()` como primera línea.

**Impacto en alumnos:** sin esta corrección, el tutorial falla en la primera llamada al LLM con un error críptico (`KeyError`) que no orienta hacia la solución.

---

### Salida real de Fase 1 (PO estándar Stratos)

**Entrada:**
```
Purchase Order PO-2025-STRA-0847. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.
Ref: ST-900 program. CoC required.
```

**JSON devuelto por el LLM:**
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
      "precio_unitario": null,
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

**Observaciones sobre la salida del LLM:**
- `tier: "TIER_1"` — campo extra que Claude añade y que no estaba en el schema esperado. No rompe nada (las reglas ignoran campos desconocidos), pero es un ejemplo de por qué el parser anti-alucinación existe.
- `descripcion: "Costilla composite HTP sección delantera"` — Claude infiere la descripción desde el catálogo embebido en `SKILL.md`. Correcto.
- `fecha_entrega_requerida: "2025-09-15"` — normalización correcta de `15/09/2025` a ISO 8601.
- `part_number_proveedor: "VBX-COMP-4471-B"` — traducción correcta desde la tabla de equivalencias de `SKILL.md`.
- `confianza: 0.97` — PO estructurada y clara. Coherente con el rango 0.95–1.00 descrito en `SKILL.md`.

**Tras `rules.aplicar_reglas()`:**
```
estado      : COMPLETO
prioridad   : NORMAL
confianza   : 0.97
alertas     : []
doc linea 1 : ['CoC']
```

✅ Coincide exactamente con la salida esperada del tutorial.  
R05 añadió `"CoC"` a `doc_requerida` porque `requiere_coc=True`. El resto de reglas (R01–R04, R06–R08) no dispararon ningún cambio.

---

## Variaciones

### Variación 1 — PN desconocido

**Entrada:** `Part: ST9-UNKNOWN-999`

**Salida:**
```
estado      : ERROR
alertas     : ['PN cliente ST9-UNKNOWN-999 no encontrado en tabla de equivalencias',
               'R04: PN cliente desconocido: ST9-UNKNOWN-999 (línea 1)']
pn_proveedor: None
```

✅ Dos alertas: una del parser anti-alucinación de `llm.py` (guardia 4, whitelist) y otra de R04 en `rules.py`. El alumno verá que el fallo se detecta en **dos capas independientes**, lo que es un buen ejemplo de defensa en profundidad.

> **Nota pedagógica:** la doble alerta puede confundir. Aclarar: el parser anula el PN proveedor (lo pone a `None`) y R04 detecta que el PN cliente no está en `EQUIVALENCIAS`. Son dos comprobaciones distintas sobre dos campos distintos.

---

### Variación 2 — AOG

**Entrada:** `URGENT AOG -- Aircraft on Ground. [...] HX7-FUS-PNL-331 [...] EASA Form 1 required.`

**Salida:**
```
estado      : COMPLETO
prioridad   : AOG
aog         : True
alertas     : ['AOG detectado - Aircraft on Ground - verificar stock inmediatamente']
doc linea 1 : ['CoC', 'EASA Form 1']
prio linea 1: AOG
```

✅ R01 propagó `AOG` tanto a `prioridad_calculada` como a `prioridad` de cada línea. R05+R06 construyeron `doc_requerida = ["CoC", "EASA Form 1"]`.

> **Nota pedagógica:** el alumno puede observar que la alerta la genera el **LLM** (la incluye en el JSON), y R01 actúa sobre el campo `aog=True` que el LLM detectó. Esta es la materialización del principio E5: el LLM detecta la señal semántica "AOG", las reglas actúan sobre el dato estructurado.

---

### Variación 3 — Texto que no es una PO

**Entrada:** `"Hola, teneis disponibilidad para una reunion el proximo martes?"`

**Salida:**
```
estado (post-LLM)  : ERROR
alertas (post-LLM) : ['LLM clasificó como no_pedido: Consulta sobre disponibilidad
                       para reunión - no es una Purchase Order']
estado (post-reglas): ERROR
lineas             : []
```

✅ El LLM devolvió `{"error": "no_pedido", ...}`, el parser lo normalizó a `estado=ERROR`, y `rules.aplicar_reglas()` no cambió nada (no hay líneas que validar).

> **Nota pedagógica:** `rules.aplicar_reglas()` se ejecuta igualmente sobre el dict, pero como `lineas=[]` ninguna regla dispara efectos. El estado ERROR se conserva. Esto muestra que la arquitectura es robusta: el código no hace `if estado == ERROR: skip rules` — simplemente las reglas no encuentran nada que hacer.

---

## Latencias medidas

| Paso | Tiempo |
|------|--------|
| `llm.normalizar()` (llamada a Claude API) | **3,33 s** |
| `rules.aplicar_reglas()` (9 reglas, puras) | **0,1 ms** |

**Ratio: el LLM es ~33.000 veces más lento que las reglas.**

> **Nota pedagógica:** este dato ilustra de forma muy concreta por qué el principio E5 importa. Si R02 (calcular si la fecha está a ≤7 días) se delegara al LLM en lugar de ser una expresión Python, cada PO tardaría varios segundos más y costaría tokens adicionales. Las reglas deterministas son instantáneas y gratuitas.

---

## Fase 2 · Pipeline completo via `main.py`

### Incidencia 2 — PO demo ya presente en CSV (duplicado esperado)

La PO demo `PO-2025-STRA-0847` viene incluida en `data/Pedidos.csv` como dato de muestra del repo. Al ejecutar `python main.py`:

```
INFO  · LLM: PO-2025-STRA-0847 estado=COMPLETO confianza=0.97
INFO  · Reglas: estado=COMPLETO prioridad=NORMAL alertas=0
WARNING · Duplicado: PO-2025-STRA-0847 — no se reenvía
```

R09 activó el anti-duplicado correctamente: la PO no se reescribió en CSV ni se notificó.

**Corrección aplicada en el tutorial:** se añadió una nota explicando este comportamiento y sugiriendo usar un número de pedido distinto (`PO-2025-STRA-SMOKE-01`) para ver el flujo no-duplicado completo.

---

### Pipeline con PO nueva (PO-2025-STRA-SMOKE-01)

Se ejecutó `main.process()` con una PO de número único:

```
INFO  · LLM: PO-2025-STRA-SMOKE-01 estado=COMPLETO confianza=0.97
INFO  · Reglas: estado=COMPLETO prioridad=NORMAL alertas=0
ERROR · SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted...')
```

**Qué ocurrió:**
1. ✅ LLM procesó correctamente (estado=COMPLETO, confianza=0.97)
2. ✅ Reglas aplicadas (prioridad=NORMAL, 0 alertas)
3. ✅ R09: no duplicado — flujo continúa
4. ✅ **CSV escrito antes del fallo** — la PO quedó registrada en `data/Pedidos.csv` y `data/Lineas.csv`
5. ❌ Email falló por credenciales SMTP de prueba — error esperado en este entorno

**Verificación CSV post-ejecución:**
```
Pedidos.csv última fila:
  numero_pedido        : PO-2025-STRA-SMOKE-01
  estado_normalizacion : COMPLETO
  prioridad_calculada  : NORMAL
  confianza            : 0.97
  timestamp            : 2026-05-26T17:46:55.737358

Lineas.csv última fila:
  numero_pedido        : PO-2025-STRA-SMOKE-01
  part_number_cliente  : ST9-HTP-RIB-047
  part_number_proveedor: VBX-COMP-4471-B
  cantidad             : 3 EA
  doc_requerida        : CoC
```

✅ La persistencia funciona correctamente y es **anterior al fan-out de notificaciones** — dato importante sobre el orden de operaciones en `main.py`.

---

## Incidencia 3 — Heredoc `<<'EOF'` no funciona en Windows PowerShell/cmd

El tutorial usa sintaxis `python - <<'EOF'` válida en bash/zsh pero no en PowerShell ni cmd.

**Corrección aplicada en el tutorial:** se añadió una nota al inicio del bloque de Fase 1 indicando que en Windows PowerShell/cmd hay que guardar el contenido en un fichero `.py` y ejecutarlo con `python run_fase1.py`.

---

## Correcciones aplicadas al código y al tutorial

| # | Tipo | Fichero | Descripción |
|---|------|---------|-------------|
| 1 | Bug fix | `main.py` | Añadido `load_dotenv()` en `__main__` |
| 2 | Nota | `01-smoke-test-end-to-end.md` | Advertencia sobre PO demo = duplicado |
| 3 | Fix | `01-smoke-test-end-to-end.md` | Añadido `load_dotenv()` en script Fase 1 |
| 4 | Nota | `01-smoke-test-end-to-end.md` | Advertencia sobre heredoc en Windows |

---

## Resumen de validación

| Sección | Estado | Comentario |
|---------|--------|-----------|
| Prerrequisitos | ✅ | `anthropic` instalado, `.env` presente |
| Fase 1 — LLM + reglas | ✅ | Salida coincide con la esperada (tras fix load_dotenv) |
| Variación 1 — PN desconocido | ✅ | ERROR + doble alerta (parser + R04) |
| Variación 2 — AOG | ✅ | AOG propagado a PO y líneas, doc_requerida correcta |
| Variación 3 — no-PO | ✅ | ERROR sin ejecutar reglas de negocio |
| Latencias | ✅ | LLM 3,33 s · reglas 0,1 ms (ratio ×33.000) |
| Fase 2 — main.py | ✅ | Pipeline escribe CSV correctamente; SMTP falla (esperado) |
| CSV resultante | ✅ | Pedidos.csv + Lineas.csv escritos con datos correctos |
