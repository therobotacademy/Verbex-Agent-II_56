# Notas de presentador — Slide 15: Cierre

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 7.2 Por qué la modularización no puede esperar más — la frase "Lo modular se opera; lo monolítico se rehace" es la tesis del slide de cierre
> - § 6.2 Criterio Gate F4 — los cuatro criterios binarios del gate son la operacionalización de "¿tienes un sistema?"
> - § 0. Introducción — Cómo leer este documento — el documento completo es la lectura post-sesión recomendada para consolidar lo visto

**Slide:** CIERRE · SESIÓN 5 — "¿Tienes un agente o un sistema operable?"  
**Duración estimada:** 3 min

---

## Qué decir

"Esta es la pregunta del curso. No '¿funciona?', sino '¿es operable?'."

"Un agente que funciona en demo tiene: un script que procesa texto, quizás una respuesta en Telegram, quizás algo escrito en un fichero. Funciona. Pero si falla a las 2 de la mañana, nadie lo sabe. Si alguien lo reinicia, pierde el contexto. Si lo auditáis, no hay rastro."

"Un sistema operable tiene: tests que verifican las reglas de forma automática, logs que registran cada evento, un dashboard que muestra el estado en tiempo real, y un deploy que arranca sin intervención manual. Y cuando falla, lo dice."

---

## La frase del slide

**"Con tests, observabilidad y deploy: un SISTEMA."**

"Eso es lo que habéis construido hoy. No un prototipo, no un script — un sistema."

---

## Cierre de sesión

"Dos cosas para llevaros:"

1. **El patrón** — `texto → LLM → reglas → notificación + registro` — se transfiere a cualquier dominio. Lo vais a usar en vuestro proyecto.
2. **La pregunta** — antes de llamar 'terminado' a cualquier sistema que construyáis, preguntaos: ¿se observa, se recupera de fallos, deja rastro? Si no, todavía no es operable.

"Nos vemos en la sesión 6. CrewAI — varios agentes colaborando. La idea: un agente resuelve, varios colaboran."

---

## Notas finales para el presentador

- Si el tiempo lo permite, hacer una demo en vivo: procesar una PO AOG, ver el CSV actualizado, mostrar el dashboard con el nuevo registro. Es el cierre más efectivo.
- Si hay preguntas sobre el proyecto propio, remitir a `proyecto-alumno/README.md` y `checklist.md`. La rúbrica es clara.
- Recordar: la sesión no está 'terminada' hasta que el alumno tiene `pytest 8/8 verde` y el dashboard visible. El gate es el criterio, no el reloj.
