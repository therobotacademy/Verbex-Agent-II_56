# Notas de presentador — Slide 05: Tests como especificación

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 1.1 main.py como orquestador puro — "tests/test_rules.py puede ejecutarse sin red, sin credenciales y sin el LLM"
> - § 3.3 El principio E5 en acción — por qué las funciones puras hacen posible 0 llamadas de red en los tests
> - § 7.3 Checklist pre-II5 — los 8 tests en verde como criterio de entrada a la sesión

**Slide:** MARCO TEÓRICO · SESIÓN 5 · C — "Tests como especificación"  
**Duración estimada:** 5 min

---

## Qué decir

"Los 8 tests de `test_rules.py` no son una verificación añadida al final. Son la especificación del sistema, escrita en código ejecutable."

"Pensadlo así: en la sesión de n8n validasteis 8 casos en el nodo Code — un AOG, una fecha urgente, un PN desconocido, una cantidad inválida… Esos casos no vivían en ningún documento. Vivían en vuestra cabeza y en el workflow. Ahora viven en `test_rules.py`, y se pueden ejecutar en cualquier momento, en cualquier máquina, sin red."

---

## Recorrer el diagrama

**ROJO (punto de partida):** "`pytest tests/ -v` ahora mismo devuelve 8 FAILED. Las firmas de las funciones existen en `rules.py` pero el cuerpo es `pass`. Los tests fallan porque las funciones no hacen nada todavía. Eso es correcto — es el punto de partida."

**Vosotros implementáis `rules.py`:** "Función a función. Cada vez que completéis una función, corréis `pytest` y veis cuántos tests pasan. El número verde sube."

**VERDE (objetivo):** "Cuando el contador dice `8 passed`, habéis terminado II-5. Ese es el gate."

---

## El dato de los 0 llamadas de red

"Fijáos en el número de la izquierda: 0 llamadas de red en los tests. Esto es consecuencia directa del principio E5. Las reglas son funciones puras, así que los tests no necesitan la API key de Anthropic, no necesitan Telegram, no necesitan CSV en disco. Corren solos."

"Implicación práctica: un compañero puede clonar el repo sin ninguna credencial y correr `pytest`. Si los tests pasan, las reglas son correctas. Si fallan, sabe exactamente qué función y qué caso."

---

## Énfasis

- TDD invertido: aquí los tests ya están escritos, vosotros escribís la implementación que los hace pasar. Es una forma de onboarding — los tests os dicen qué tiene que hacer cada función antes de que la escribáis.
- "La especificación no es solo un documento, es un script ejecutable" — frase del slide para retener.

---

## Transición

→ Teoría terminada. Ahora veamos cómo esa teoría se materializa en la arquitectura del repositorio.
