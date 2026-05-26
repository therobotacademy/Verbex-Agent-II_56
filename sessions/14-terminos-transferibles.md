# Notas de presentador — Slide 14: En términos transferibles

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 3.3 El principio E5 en acción — el antipatrón E4 y la "regla de oro" son el corazón de lo que hace transferible el patrón a cualquier dominio
> - § 4.4 La frontera E5 en llm.py — explica dónde termina la capa cognitiva y empieza la lógica determinista; esa frontera es lo transferible
> - § 7.2 Por qué la modularización no puede esperar más — "Lo modular se opera; lo monolítico se rehace" es la frase transferible del slide

**Slide:** MARCO TEÓRICO · SESIÓN 5 · D · CIERRE — "En términos transferibles"  
**Duración estimada:** 5 min

---

## Qué decir

"Última pieza de teoría. Cada sesión del curso termina con un slide así: el concepto abstracto, cómo lo hemos implementado en VERBEX, y cómo se traslada a otro dominio completamente distinto."

---

## El concepto abstracto: sistema operable

"Sistema operable no es sinónimo de sistema que funciona. Un sistema operable tiene tres propiedades: se observa (sabes qué está pasando), se recupera de fallos (no muere con el primer error), y deja rastro auditable (puedes demostrar lo que ocurrió)."

"Un script que funciona en vuestra máquina pero que nadie sabe cómo arrancarlo, que no loggea nada y que no tiene tests no es operable. Puede ser útil — pero no es operable."

---

## En VERBEX · II-6

"Lo hemos construido con las herramientas más simples posibles: logging de stdlib, CSV, Streamlit, un bat de dos líneas. No hemos usado Kubernetes, ni Grafana, ni Airflow. No los necesitamos. El principio es el mismo: observar, recuperar, dejar rastro."

---

## En otro dominio: farma · FDA 21 CFR Part 11

"Tomad el mismo principio y aplicadlo a alertas de planta en una empresa farmacéutica. La FDA exige audit trail, integridad de datos y trazabilidad. Los requisitos no son distintos: el sistema tiene que poder demostrar que procesó cada alerta, que las reglas se aplicaron correctamente, y que ningún dato fue modificado sin registro."

"El patrón VERBEX — logging + CSV + reglas deterministas — es una implementación mínima de esos requisitos. No la más robusta, pero sí transferible."

---

## Pregunta de dominio (para el grupo)

"En vuestro proyecto propio — el que vais a entregar al final del curso — ¿qué dejaría rastro auditable? ¿Cómo demostraríais que vuestro sistema se recupera de un fallo?"

Esperar respuestas. Esta pregunta no tiene una respuesta correcta única — es para que piensen en su dominio específico.

---

## Énfasis

- El slide de "términos transferibles" es el que más valor tiene para alumnos de dominios distintos a la aeronáutica. Hacedlo concreto con su dominio si lo conocéis.
- La respuesta a la pregunta de dominio es el punto de partida para el proyecto propio.

---

## Transición

→ Último slide: la pregunta que cierra la sesión.
