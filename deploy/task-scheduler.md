# Task Scheduler · Arranque automático del MVP (Python) en Windows

Configura Windows Task Scheduler para que el MVP arranque automáticamente al iniciar sesión. El agente queda operativo sin que nadie tenga que abrir nada manualmente cada mañana.

A diferencia del track n8n (3 procesos), aquí solo hay **2 procesos Python**: el bot de Telegram y el dashboard. No hace falta n8n ni Service Account de Google.

---

## Pre-requisitos

- ✅ `start_verbex.bat` probado manualmente (doble clic) y los 2 procesos arrancan.
- ✅ Python 3.10+ en PATH (`python --version`).
- ✅ Dependencias instaladas: `pip install -r requirements.txt` (raíz) y `pip install -r dashboard/requirements.txt`.
- ✅ `.env` con `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS` (y SMTP si activas email).

> Si usas un entorno virtual (`venv`), edita la línea `set "PY=python"` de `start_verbex.bat` para que apunte a `\.venv\Scripts\python.exe`.

---

## Paso 1 · Abrir Task Scheduler

1. Pulsa **Windows + R** → escribe `taskschd.msc` → Enter.
2. Panel izquierdo: **Task Scheduler Library**.

---

## Paso 2 · Crear nueva tarea

**Action** → **Create Task...** (NO "Create Basic Task" — la versión avanzada da más control).

### Pestaña **General**

- **Name:** `VERBEX MVP arranque`
- **Description:** `Lanza el bot de Telegram + el dashboard Streamlit tras login.`
- **Run only when user is logged on** ✓ (imprescindible: los procesos abren ventanas)
- **Configure for:** Windows 10/11

### Pestaña **Triggers** → **New...**

- **Begin the task:** *At log on*
- **Specific user:** tu usuario Windows
- **Delay task for:** `30 seconds`
- **Enabled** ✓

### Pestaña **Actions** → **New...**

- **Action:** *Start a program*
- **Program/script:** `C:\verbex\verbex-agent\deploy\start_verbex.bat`
  > Sustituye por la ruta absoluta real en tu PC.
- **Start in (optional):** `C:\verbex\verbex-agent\deploy`

### Pestaña **Conditions**

- **Start the task only if the computer is on AC power** ⬜ (desmarcar para portátiles)
- **Stop if the computer switches to battery power** ⬜

### Pestaña **Settings**

- **Allow task to be run on demand** ✓
- **If the task fails, restart every:** `1 minute` · max **3** intentos
- **If the running task does not end when requested, force it to stop** ✓
- **If the task is already running:** *Do not start a new instance*

Click **OK**.

---

## Paso 3 · Probar la tarea

1. Click derecho en `VERBEX MVP arranque` → **Run**.
2. Deberían abrirse 2 ventanas cmd.exe (Bot, Dashboard).
3. Abrir [http://localhost:8501](http://localhost:8501) y comprobar el dashboard.
4. Enviar un mensaje al bot de Telegram y verificar que responde.

---

## Paso 4 · Probar tras login

1. Cerrar sesión Windows (`Win + L` o **Sign out**).
2. Volver a iniciar sesión.
3. Esperar 30 segundos: las 2 ventanas deberían abrirse solas.

---

## Cómo PARAR el agente

Opción A · cerrar las 2 ventanas cmd.exe individualmente.

Opción B · script `stop_verbex.bat` (opcional):

```batch
@echo off
taskkill /F /FI "WINDOWTITLE eq VERBEX Bot*"
taskkill /F /FI "WINDOWTITLE eq VERBEX Dashboard*"
echo VERBEX MVP detenido.
pause
```

---

## Troubleshooting

### "El bat se ejecuta pero las ventanas se cierran inmediatamente"

Causa habitual: `PATH` distinto entre Task Scheduler y tu cmd interactivo (no encuentra `python`). Solución: en `start_verbex.bat`, pon la ruta absoluta del intérprete en `set "PY=..."` (p.ej. `C:\Users\<USUARIO>\AppData\Local\Programs\Python\Python313\python.exe` o el de tu venv).

### "El dashboard arranca pero dice 'Sin datos en Pedidos.csv'"

Es normal si el agente aún no ha procesado ninguna PO. Envía una PO al bot, o copia los CSV de muestra a `data/`. El dashboard refresca cada 60 s.

### "ModuleNotFoundError: streamlit / anthropic"

Las dependencias no están en el entorno que usa el `.bat`. Instala con el mismo intérprete que apunta `PY`: `<PY> -m pip install -r requirements.txt -r dashboard/requirements.txt`.

### "Task Scheduler dice 'Task succeeded' pero nada se ve"

Marca **Run only when user is logged on**. Sin esto, los procesos arrancan en una sesión invisible y no verás las ventanas.

---

*COIIAOC · Parte 2 · Fork Python · Despliegue Windows (2 procesos)*
