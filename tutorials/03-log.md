# Log de ejecución — Tutorial 03: El LLM en acción

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.x · claude-sonnet-4-20250514  
**Resultado global:** ✅ Tutorial funcional sin correcciones al código. Una observación pedagógica relevante en Experimento D.

---

## Experimento A · ¿Qué recibe Claude?

```
System prompt: 13.796 caracteres, 404 líneas

Primeras 5 líneas:
  # Soul — Normalizador de Purchase Orders VERBEX COMPOSITES

  Soy el agente de normalización de Purchase Orders (POs) de **VERBEX COMPOSITES S.L.**,
  empresa fabricante de componentes en composite para la industria aeronáutica, ubicada
  en Sevilla. Mi rol es Tier 2 en la cadena de suministro...

Mensaje de usuario:
  role   : user
  content: Texto de la PO a normalizar:
           Purchase Order PO-TEST. Stratos Systems. Part: ST9-HTP-RIB-047, 5 EA.
```

**Observaciones:**

- **13.796 caracteres** es el coste fijo de cada llamada: `PERSONA.md` + `SKILL.md` se envían enteros en cada `normalizar()`. No hay "memoria" entre llamadas.
- El prefijo del mensaje de usuario (`"Texto de la PO a normalizar:\n\n"`) es literalmente la única instrucción adicional al texto de la PO. Todo el resto de contexto viene del system prompt.
- Las 404 líneas del system prompt incluyen las tablas de equivalencias PN cliente→proveedor y el catálogo de 16 PNs válidos. Eso es lo que permite al LLM hacer la traducción sin inventar.

> **Nota pedagógica:** en n8n, este system prompt vivía dentro del nodo Claude API como texto plano no versionado. Aquí vive en `PERSONA.md` + `SKILL.md` — dos ficheros con historial `git diff`. Si el comportamiento del modelo cambia, sabes exactamente qué línea cambió.

---

## Experimento B · Confianza: cómo varía con la calidad del input

| Caso | Estado | Confianza | Latencia | Observación |
|------|--------|-----------|----------|-------------|
| PO clara y estructurada | COMPLETO | **0.98** | 4.29 s | Todo extraído perfectamente |
| PO en prosa, sin estructura | PARCIAL | **0.75** | 5.03 s | Fecha y PO# ambiguos |
| PO incompleta — cliente/fecha ambiguos | PARCIAL | **0.65** | 4.16 s | Cliente=None, fecha=None |

### Caso 1 — PO clara (confianza 0.98)

```
estado    : COMPLETO
confianza : 0.98
PN cliente: ST9-HTP-RIB-047  →  VBX-COMP-4471-B
fecha     : 2026-06-30
cliente   : STRA-001
alertas   : []
```

Fecha `30/06/2026` → `2026-06-30` (ISO 8601). PN traducido correctamente. Confianza máxima para PO bien formada.

### Caso 2 — PO en prosa (confianza 0.75)

```
estado    : PARCIAL
confianza : 0.75
PN cliente: HX7-FUS-PNL-331  →  VBX-COMP-3301-A
fecha     : None
cliente   : KAIRO-001
alertas   : ["Fecha de entrega ambigua: 'antes de julio' - requiere confirmación específica",
             'Número de PO no especificado - generado automáticamente']
```

**Observaciones:**
- El LLM extrajo `HX7-FUS-PNL-331` y `VBX-COMP-3301-A` del texto en prosa `"panel HX7-FUS-PNL-331"`. La tabla de equivalencias en `SKILL.md` funciona con texto no estructurado.
- `"antes de julio"` no es una fecha ISO → `fecha=None` + alerta descriptiva. Correcto.
- El LLM generó un número de PO interno porque el texto no incluía uno. Estado PARCIAL por esto.
- Confianza 0.75: coherente con el rango 0.60–0.80 descrito en `SKILL.md` para POs con campos faltantes.

> **Nota pedagógica:** este caso ilustra la diferencia entre `llm.py` y `rules.py`. El LLM sabe que "antes de julio" es ambiguo y lo dice en `alertas`. R02 (fecha ≤7 días → PRIORITARIO) recibirá `fecha=None` y no disparará — comportamiento correcto: no inferir prioridad de datos ausentes.

### Caso 3 — PO incompleta (confianza 0.65)

```
estado    : PARCIAL
confianza : 0.65
PN cliente: ST9-LE-PNL-550  →  VBX-COMP-5501-A
fecha     : None
cliente   : None
alertas   : ['Número de pedido no identificado',
             'Cliente no identificado',
             'Fecha de entrega no especificada']
```

**Observaciones:**
- `"El programa es el de siempre"` → el LLM no asume qué programa es (correcto: sigue regla absoluta #1, no infiere).
- `cliente=None` a pesar de que el PN (`ST9-LE-PNL-550`) sugiere Stratos: el LLM no infiere el cliente desde el PN, sino desde el texto. Correcto.
- Confianza 0.65: en el límite entre "PN desconocido" y "varios campos faltantes". R03 degradará COMPLETO→PARCIAL si el LLM hubiera devuelto COMPLETO, pero aquí ya viene PARCIAL del propio LLM.

---

## Experimento C · Las 4 guardias del parser (sin API)

Todas las guardias funcionaron exactamente como el tutorial describe. **0 llamadas de API.**

### Guardia 1 — Strip de fences markdown
```
Input : ```json\n{"numero_pedido":"PO-X", ...}\n```
Output: estado=COMPLETO — fences eliminados correctamente
```
✅ El JSON dentro de las fences se parsea sin error.

### Guardia 2 — JSON malformado
```
Input : '{"numero_pedido": "PO-X", "lineas": [ROTO'
Output: ValueError: JSON_PARSE_ERROR: Expecting value: line 1 column 38 (char 37)
```
✅ `ValueError` con prefijo `JSON_PARSE_ERROR:` — capturado limpiamente. El mensaje incluye posición del error.

> **Nota pedagógica:** este `ValueError` se propaga hasta `main.py`, que lo captura en el bloque `try/except` de `__main__` y lo registra vía `observability.registrar_excepcion()`. Ese es el camino completo de un fallo técnico: LLM devuelve basura → parser lanza → orquestador captura → `Errores.csv` registra.

### Guardia 3 — no_pedido
```
Input : {"error": "no_pedido", "mensaje": "Consulta de disponibilidad, no es una PO"}
Output:
  estado_normalizacion: ERROR
  alertas             : ['LLM clasificó como no_pedido: Consulta de disponibilidad, no es una PO']
  lineas              : []
  confianza           : 0
```
✅ La normalización a `estado=ERROR` con `confianza=0` y `lineas=[]` es correcta. `rules.aplicar_reglas()` recibirá `lineas=[]` y no disparará ninguna regla de negocio.

### Guardia 4 — PN proveedor inventado
```
Input : part_number_proveedor = "VBX-COMP-9999-Z"  (no está en PNS_VALIDOS)
Output:
  PN proveedor tras parser: None
  alertas: ['PARSER: PN proveedor inventado por el LLM línea 1: VBX-COMP-9999-Z']
```
✅ El PN se anula y el prefijo `PARSER:` en la alerta distingue este fallo (del parser) de los fallos de negocio (de las reglas R01–R09).

---

## Experimento D · PN inventado end-to-end (via API)

**Entrada:** `ST9-HTP-RIB-999` (PN cliente plausible pero fuera de la tabla de SKILL.md)

```
PN cliente  : ST9-HTP-RIB-999
PN proveedor: None  ← guardia no necesitó actuar
alertas     : ['PN cliente ST9-HTP-RIB-999 no encontrado en tabla de equivalencias']
confianza   : 0.65
estado      : PARCIAL
```

**Observación importante:** la guardia 4 **no disparó**. El LLM devolvió `null` directamente para `part_number_proveedor`, y la alerta la generó el propio LLM — no el parser.

**Por qué:** `PERSONA.md` incluye la regla absoluta #2: *"Nunca inventa Part Numbers; si no reconoce el PN, lo devuelve tal cual + baja confianza"*. Claude siguió esa instrucción y fue honesto sobre su ignorancia.

**Consecuencia:** la guardia 4 es un **safety net** para cuando el LLM no sigue sus instrucciones, no para el caso normal. En producción, si el modelo mejora o el system prompt cambia, la guardia 4 es la última línea de defensa.

> **Nota pedagógica para el tutorial:** este resultado es más sofisticado de lo que el alumno espera. Conviene señalar explícitamente: el LLM puede comportarse bien (devolver null + alerta) O mal (inventar un PN). La guardia 4 protege del segundo caso. Que en este test el LLM se comporte bien es una buena noticia, no un fallo del tutorial.

**Verificación:** si las reglas (`rules.py`) procesan esta PO, R04 marcará `estado=ERROR` porque `ST9-HTP-RIB-999` no está en `EQUIVALENCIAS`. La cadena de protección funciona:

```
LLM no sabe el PN proveedor → devuelve null → guardia 4 (si hubiera inventado)
→ R04 detecta PN cliente desconocido → estado=ERROR + alerta
```

---

## Datos de latencia (Experimento B)

| Caso | Latencia API |
|------|-------------|
| PO clara (1 línea, datos completos) | 4.29 s |
| PO prosa (1 línea, 2 ambigüedades) | 5.03 s |
| PO incompleta (1 línea, 3 campos faltantes) | 4.16 s |

Las diferencias son pequeñas y no sistemáticas — la latencia depende más de la carga del servidor Anthropic que de la complejidad del input.

---

## Correcciones aplicadas

Ninguna corrección al código ni al tutorial fue necesaria en este experimento. El tutorial funciona tal como está escrito.

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| A — System prompt y messages | ✅ | 13.796 chars, 404 líneas |
| B — Tres niveles de confianza | ✅ | 0.98 / 0.75 / 0.65 como esperado |
| C — Guardia 1 (fences) | ✅ | Strip correcto |
| C — Guardia 2 (JSON malformado) | ✅ | ValueError con posición del error |
| C — Guardia 3 (no_pedido) | ✅ | ERROR + lineas=[] + confianza=0 |
| C — Guardia 4 (PN inventado, mock) | ✅ | PN→None + alerta PARSER: |
| D — Guardia 4 end-to-end (API) | ✅ | LLM fue honesto; guardia no necesitó actuar |
