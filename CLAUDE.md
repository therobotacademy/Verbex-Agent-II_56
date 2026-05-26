# CLAUDE.md — Agente VERBEX (implementación Python)

Instrucciones de proyecto para Claude Code (y para cualquiera que trabaje en este repo).
Este es el equivalente Python del workflow n8n `workflow_II4-csv.json` de la sesión II-4.

## Qué es este proyecto

Agente de normalización de Purchase Orders de **VERBEX COMPOSITES S.L.** (Tier 2 aeronáutico).
Recibe una PO en texto libre por Telegram, la normaliza con Claude, aplica reglas de negocio
deterministas y enruta el resultado a CSV, Telegram (producción/calidad) y email.

Pipeline: `texto → LLM → reglas R01–R09 → {CSV, Telegram, email}`.

## Stack

- Python 3.10+
- `anthropic` — cliente de la API de Claude
- `python-telegram-bot` — recepción de mensajes (trigger)
- `python-dotenv` — credenciales desde `.env`
- `pytest` — tests de las reglas

## Estructura

```
verbex-agent/
├── PERSONA.md          system prompt (= SOUL_verbex.md de n8n) — NO editar sin motivo
├── SKILL.md            instrucciones + few-shots (= SKILL_verbex.md) — NO editar sin motivo
├── MEMORY.md           índice de qué recuerda el agente y dónde
├── rules.py            R01–R09 como funciones puras  ← AQUÍ se implementa en II-5
├── main.py             orquestador (= grafo del workflow)  ← AQUÍ se implementa en II-5
├── telegram_bot.py     handler que recibe mensajes y llama a main.process()
├── verbex/
│   ├── llm.py          llamada a Claude con PERSONA + SKILL (anti-alucinación)
│   ├── persistence.py  lectura/escritura CSV (= nodos Sheets de n8n)
│   ├── notify.py       envío Telegram y email (= nodos Telegram/Email)
│   └── observability.py logging + registro de errores (= Error Trigger de n8n)  ← II-6
├── data/
│   ├── Pedidos.csv     memoria de POs (anti-duplicado R09)
│   ├── Lineas.csv      registro de líneas
│   └── Errores.csv     fallos técnicos del pipeline (alimenta el dashboard)  ← II-6
├── dashboard/app.py    Streamlit read-only sobre los CSV (localhost:8501)  ← II-6
├── deploy/             start_verbex.bat + task-scheduler.md + README_deploy.md  ← II-6
├── proyecto-alumno/    brief + checklist del proyecto del alumno  ← II-6
├── tests/test_rules.py 8 casos = los 8 casos de prueba de n8n
├── .env.example        plantilla de credenciales
└── requirements.txt
```

## Cómo correr

```bash
pip install -r requirements.txt
cp .env.example .env          # rellenar ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, ...
pytest tests/ -v              # las reglas deben pasar (en el starter kit empiezan en rojo)
python telegram_bot.py        # levanta el bot
```

## Convenciones

- **No reescribir `PERSONA.md` ni `SKILL.md`.** Son el mismo prompt validado en II-2/II-3.
  Si el comportamiento del LLM debe cambiar, se edita el prompt, nunca `rules.py`.
- **El LLM extrae, las reglas deciden.** `rules.py` nunca llama al LLM; `verbex/llm.py` nunca
  aplica lógica de negocio. Esta separación (principio E5) es deliberada — no la rompas.
- **`rules.py` son funciones puras:** reciben un dict `po`, devuelven un dict `po` modificado,
  sin efectos secundarios (no escriben CSV, no envían mensajes). Eso las hace testeables.
- **Los efectos (CSV, Telegram, email) viven en `verbex/`** y los orquesta `main.py`.

## Estado del starter kit (II-4 → II-5)

- ✅ Completo y funcional: `PERSONA.md`, `SKILL.md`, `MEMORY.md`, `verbex/llm.py`,
  `verbex/persistence.py`, `verbex/notify.py`, `telegram_bot.py`, datos CSV.
- 🔧 Esqueleto a implementar en II-5: `rules.py` (firmas con `pass`) y `main.py` (orquestador
  con TODOs). Cuando `rules.py` esté implementado, `pytest tests/` pasa de rojo a verde.
