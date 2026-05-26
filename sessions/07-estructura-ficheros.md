# Notas de presentador — Slide 07: Estructura de ficheros

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 1.1 main.py como orquestador puro — los cuatro módulos y sus fronteras semánticas
> - § 1.3 Archivos de configuración — PERSONA.md, SKILL.md, CSV y .env como dependencias de lectura en runtime
> - § 2.1 Los cinco pasos de main.py — los TODOs numerados de `main.py` y su correspondencia con los nodos del workflow

**Slide:** CÓDIGO · II-5 — "Estructura de ficheros"  
**Duración estimada:** 6 min

---

## Qué decir

"Cuatro bloques en el slide. Solo dos los vais a tocar hoy: `rules.py` y `main.py`. Los otros dos — `pytest` y `telegram_bot.py` — ya están dados."

---

## rules.py — "5 funciones puras"

"Abrid `rules.py` ahora. Veréis las cinco firmas con `pass`. El orden en el que aparecen en el fichero es el orden en el que se aplican:"

```
R04+R08  →  R07  →  R01+R02  →  R05+R06  →  R03
```

"¿Por qué este orden y no otro? Primero validamos las líneas (R04, R08): si un PN no existe o la cantidad es cero, ya tenemos un ERROR y no merece la pena calcular prioridades. Luego el cliente (R07): si no está en el ERP, degradamos a PARCIAL antes de calcular docs requeridas. Después prioridad (R01, R02): necesitamos saber si es AOG antes de decidir qué notificamos. Docs (R05, R06) al final porque dependen de los campos de cada línea, no del estado global. Y confianza (R03) al final del todo: es un post-proceso que puede degradar el estado calculado."

"El orden importa. No es arbitrario."

---

## main.py — "El orquestador"

"En el esqueleto, `main.py` tiene TODOs numerados. Esos números corresponden exactamente a los nodos del grafo del workflow de II-4. Si tenéis el workflow abierto en otra pestaña, podéis hacer la correspondencia uno a uno."

"La estructura es simple: `llm.normalizar()` → `rules.aplicar_reglas()` → `persistence.es_duplicado()` → fan-out condicional. No hay magia. Es el grafo escrito como código imperativo."

---

## pytest — "El Gate"

"No lo tocáis, pero lo corréis constantemente. Abrid una terminal y dejad esto corriendo:"

```bash
pytest tests/ -v
```

"Cada vez que guardéis `rules.py`, corred el comando. El número de `passed` es vuestro progreso."

---

## telegram_bot.py — "Ya dado"

"Este fichero no lo tocáis en II-5. Está completo. Cuando queráis probarlo con Telegram real, hacéis `python telegram_bot.py` y el bot empieza a escuchar. Para II-5, `main.py` tiene un bloque `__main__` que os permite probarlo sin bot."

---

## Acción concreta para el grupo

"Antes de seguir: abrid `rules.py` en vuestro editor. Identificad las cinco firmas. Localizad `aplicar_reglas()` al final del fichero. Esa función es la que orquesta el orden. Tenéis 2 minutos."

---

## Transición

→ Ahora la tabla completa de reglas: qué hace cada función, qué decide y qué test la verifica.
