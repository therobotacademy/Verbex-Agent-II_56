# Notas de presentador — Slide 06: El pipeline en código

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 2. Flujo de control completo — process() — diagrama D2, el grafo del workflow n8n como llamadas secuenciales en Python
> - § 2.1 Los cinco pasos de main.py — los cinco pasos exactos del orquestador con su equivalencia a nodos n8n
> - § 1. El repositorio en una imagen — arquitectura modular — los tres números del slide (5 ficheros, 3 capas) explicados en el diagrama D1

**Slide:** ARQUITECTURA · II-5 — "El pipeline en código"  
**Duración estimada:** 5 min

---

## Qué decir

"Mirad el diagrama. ¿Veis algo familiar?"

Señalar los bloques de izquierda a derecha:

`texto libre (Telegram)` → `llm.normalizar` → `rules.aplicar_reglas` → `es_duplicado` → `CSV + notify`

"Es exactamente el grafo del workflow de n8n, pero escrito como llamadas de función en Python. El webhook de Telegram se convierte en `telegram_bot.py`. El nodo LLM se convierte en `llm.normalizar()`. Los nodos Code se convierten en `rules.aplicar_reglas()`. Los splits y branches se convierten en `if/elif` en `main.py`."

---

## Los tres números del slide

**5 ficheros de texto + paquete `verbex/`** — "El agente completo, incluyendo prompts, lógica, orquestador y trigger, son cinco ficheros Markdown y Python más el paquete. Caben en la cabeza."

**3 capas** — "Cognitiva (LLM), lógica (reglas), efectos (CSV + notificación). Esta separación en tres capas es la que hace el sistema mantenible. Cuando algo falla, sabéis en qué capa buscar."

**~150 líneas de Python** — "El orquestador `main.py` completo, sin los módulos de soporte, son menos de 150 líneas. No es magia — es una función `process()` con cuatro pasos. El workflow de n8n tenía más XML que esto."

---

## Énfasis

- `main.py` **es el grafo del workflow en código**: las conexiones de n8n se vuelven llamadas secuenciales y condicionales. Esta frase del slide es la clave para que el alumno que viene de n8n entienda qué tiene que escribir.
- Si alguien pregunta "¿por qué no usar FastAPI o algún framework?": la respuesta es que no hace falta. El trigger es Telegram, no HTTP externo. Long-polling + stdlib es suficiente para este MVP.

---

## Transición

→ Vamos al detalle de cada fichero que vais a tocar hoy.
