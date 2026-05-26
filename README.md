# VERBEX Agent — implementación Python

Starter kit de la sesión **II-5**. Es el mismo agente que construiste en n8n durante
II-4 (`workflow_II4-csv.json`), reescrito como repositorio Python. **Misma lógica,
distinto contenedor.**

## El mapa: de n8n a este repo

| En n8n (II-4)                  | Aquí                          | Estado                                |
| ------------------------------ | ------------------------------ | ------------------------------------- |
| System prompt del nodo Claude  | `PERSONA.md`                 | ✅ dado (idéntico a SOUL)            |
| Instrucciones + few-shots      | `SKILL.md`                   | ✅ dado (idéntico a SKILL)           |
| Hojas Sheets / CSV             | `data/*.csv` + `MEMORY.md` | ✅ dado                               |
| Nodo Claude API + Validar JSON | `verbex/llm.py`              | ✅ dado                               |
| Nodos Google Sheets            | `verbex/persistence.py`      | ✅ dado                               |
| Nodos Telegram + Email         | `verbex/notify.py`           | ✅ dado                               |
| Manual Trigger / webhook       | `telegram_bot.py`            | ✅ dado                               |
| Nodos Code R01–R09            | `rules.py`                   | 🔧**tú lo implementas (II-5)** |
| Conexiones del workflow        | `main.py`                    | 🔧**tú lo implementas (II-5)** |

## Puesta en marcha

```bash
pip install -r requirements.txt
cp .env.example .env        # rellena tus credenciales
pytest tests/ -v            # 8 tests en ROJO: rules.py está sin implementar
```

## Tu trabajo en II-5

1. Implementa las funciones de `rules.py` (cada una equivale a un nodo Code de n8n).
   Cuando termines, `pytest tests/ -v` pasa a **verde** (8/8) — ese es tu Gate.
2. Completa el orquestador `main.py` (los `TODO` numerados siguen el grafo del workflow).
3. Arranca el bot: `python telegram_bot.py` y envíale una PO por Telegram.

NOTA: Los scripts ` main.py` y `rules.py` incompletos están en  `./py-blank`. Para hacer el ejercicio debes sustituir los originales completos (localizados en el directorio raíz) por ellos

## Tu trabajo en II-6 — operar el agente

Una vez el agente procesa POs, lo conviertes en un sistema **operable**:

1. **Observabilidad** — el agente ya registra eventos en `logs/verbex.log` y los fallos
   técnicos en `data/Errores.csv` (vía `verbex/observability.py`). Es el equivalente
   del *Error Trigger Workflow* de n8n, en ~30 líneas de la stdlib.
2. **Dashboard** — `python -m streamlit run dashboard/app.py` levanta un panel read-only
   (`http://localhost:8501`) que lee los CSV de `data/`. KPIs, filtros, últimas POs y errores.
3. **Deploy** — `deploy/start_verbex.bat` arranca bot + dashboard con doble clic;
   `deploy/task-scheduler.md` lo automatiza al iniciar sesión en Windows.
4. **Proyecto propio** — `proyecto-alumno/` contiene el brief para adaptar este patrón
   a otro dominio (tu entrega del curso).

## Principio E5 (no lo rompas)

> El LLM extrae, las reglas deciden.

`rules.py` nunca llama al LLM. `verbex/llm.py` nunca aplica lógica de negocio. Esa
separación es la misma que viste en n8n (nodo Claude separado de los nodos Code) y es
lo que hace que las reglas sean testeables sin red.
