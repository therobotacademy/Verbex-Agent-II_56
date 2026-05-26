# Tutorial 10 · Bot Telegram en vivo

Levanta el bot y envía una PO real desde tu móvil. El ciclo completo: texto en Telegram → LLM → reglas → CSV → respuesta en Telegram.

| Tiempo | Credenciales | Dependencias |
|--------|-------------|--------------|
| ~15 min | `ANTHROPIC_API_KEY` + `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID_*` | Bot de Telegram creado con @BotFather |

---

## Prerrequisitos

### 1. Bot de Telegram (si no tienes uno)

1. Abre Telegram y busca **@BotFather**.
2. Envía `/newbot` y sigue las instrucciones.
3. Copia el **Bot Token** (formato: `1234567890:ABCdef...`).
4. Habla con tu bot (envía cualquier mensaje) para que el chat exista.
5. Para obtener tu `CHAT_ID`, visita:  
   `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`  
   Busca el campo `"chat": {"id": ...}` en el primer mensaje.

### 2. Configurar `.env`

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxx
TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
TELEGRAM_CHAT_ID_PRODUCCION=<tu_chat_id>
TELEGRAM_CHAT_ID_CALIDAD=<tu_chat_id>   # puede ser el mismo para pruebas
```

---

## Paso 1 · Verificar la conexión Telegram

Antes de levantar el bot, comprueba que el token funciona:

```python
# run_t10_check.py
from dotenv import load_dotenv
load_dotenv()
import os
import urllib.request, json

token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not token:
    print("ERROR: TELEGRAM_BOT_TOKEN no está en .env")
else:
    url = f"https://api.telegram.org/bot{token}/getMe"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())
    print(f"Bot conectado: @{data['result']['username']}")
    print(f"Nombre      : {data['result']['first_name']}")
```

```bash
python run_t10_check.py
```

**Salida esperada:**
```
Bot conectado: @VerbexAgentBot
Nombre      : VERBEX Agent
```

---

## Paso 2 · Levantar el bot

```bash
python telegram_bot.py
```

**Salida esperada:**
```
INFO  · Bot iniciado — esperando mensajes...
```

El proceso se queda en espera (polling). Déjalo correr en la terminal.

---

## Paso 3 · Enviar una PO desde Telegram

Abre Telegram y envía este texto a tu bot:

```
Purchase Order PO-T10-001. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 3 EA, Need Date: 30/09/2026.
Ref: ST-900 program. CoC required.
```

### Respuesta esperada del bot

El bot responderá con un resumen del resultado:

```
✅ PO procesada: PO-T10-001
Estado   : COMPLETO
Prioridad: NORMAL
Confianza: 0.97
Alertas  : ninguna
```

En la terminal verás los logs:
```
INFO  · LLM: PO-T10-001 estado=COMPLETO confianza=0.97
INFO  · Reglas: estado=COMPLETO prioridad=NORMAL alertas=0
INFO  · CSV: PO-T10-001 escrita en Pedidos.csv
INFO  · Telegram producción: enviado
```

---

## Paso 4 · Probar los casos del curso

Envía estas variaciones una a una y observa la respuesta:

**Caso AOG:**
```
URGENT AOG — Aircraft on Ground.
PO-T10-AOG. Kairos Aerospace.
Part: HX7-FUS-PNL-331, Qty: 1 EA, Required immediately.
EASA Form 1 required.
```
→ Espera: `prioridad=AOG`, canal de calidad también notificado (EASA).

**Caso PN desconocido:**
```
PO-T10-ERR. Stratos.
Part: ST9-UNKNOWN-999, Qty: 5 EA, Need Date: 01/12/2026.
```
→ Espera: `estado=ERROR`, alerta sobre PN no reconocido.

**Caso no-PO:**
```
Hola, ¿tenéis disponibilidad para el próximo martes?
```
→ Espera: `estado=ERROR`, mensaje indicando que no es una Purchase Order.

**Caso duplicado** (reenvía la primera PO `PO-T10-001`):
```
Purchase Order PO-T10-001. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 3 EA, Need Date: 30/09/2026.
```
→ Espera: mensaje de duplicado, sin escribir en CSV.

---

## Paso 5 · Verificar el CSV tras los envíos

Con el bot aún corriendo (o después de pararlo), verifica el CSV:

```python
# run_t10_verify.py
import csv

print("── Pedidos.csv (últimas 5 filas) ───────────")
with open("data/Pedidos.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for row in rows[-5:]:
    print(f"  {row['numero_pedido']:25s} "
          f"estado={row['estado_normalizacion']:10s} "
          f"prioridad={row['prioridad_calculada']:12s} "
          f"confianza={row['confianza']}")
```

---

## Detener el bot

`Ctrl+C` en la terminal donde corre `telegram_bot.py`.

---

## Arquitectura de `telegram_bot.py`

```python
# telegram_bot.py — estructura simplificada
async def handle_message(update, context):
    texto = update.message.text
    resultado = main.process(texto)    # ← todo el pipeline
    await update.message.reply_text(formatear(resultado))

# El handler llama a main.process() que ya conoces de los tutoriales anteriores.
# telegram_bot.py solo hace de adaptador de entrada/salida.
```

El bot es un **adaptador**: recibe el texto de Telegram, llama al pipeline que ya conoces, y devuelve el resumen. No contiene lógica de negocio.

---

## Lo que acabas de aprender

- El bot de Telegram es un **adaptador de interfaz** — delega todo a `main.process()`.
- El pipeline es el mismo que en Tutorial 01, solo que el trigger es Telegram en lugar de un script Python.
- Los 4 casos del curso (PO válida, AOG, PN desconocido, no-PO) funcionan igual desde Telegram que desde el script.
- El CSV se escribe independientemente de si la notificación Telegram llega al destinatario.

---

## Felicidades — has completado todos los tutoriales

| Tutorial | Concepto clave |
|----------|---------------|
| 01 | Pipeline end-to-end: texto → CSV |
| 02 | Reglas puras: dict → dict sin red |
| 03 | LLM: texto → JSON, confianza, guardias |
| 04 | Tests como especificación ejecutable |
| 05 | R09: anti-duplicado fuera de rules.py |
| 06 | Taxonomía de errores: negocio vs técnico |
| 07 | AOG: señal semántica → dato estructurado |
| 08 | CSV: la memoria del sistema |
| 09 | Parser anti-alucinación: 4 guardias |
| 10 | Bot Telegram: adaptador de interfaz |
