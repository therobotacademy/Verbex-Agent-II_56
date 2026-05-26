# Notas de presentador — Slide 02: Sección II-5

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 7.2 Por qué la modularización no puede esperar más — justifica el salto de monolito a módulos
> - § 7.3 Checklist pre-II5 — estado de partida que se asume al abrir este bloque

**Slide:** BLOQUE II-5 · GOBERNANZA Y ORQUESTACIÓN — "Implementación y Pruebas"  
**Duración estimada:** 30 s (slide de transición)

---

## Qué decir

"Primer bloque. Implementación y pruebas. Aquí el trabajo es vuestro."

"Vamos a empezar por la teoría que justifica las decisiones de diseño del repo — tres slides cortos — y después nos ponemos a picar código."

---

## Énfasis

- Este bloque termina cuando `pytest tests/ -v` devuelve **8 passed**. Ese es el criterio, no el reloj.
- La teoría no es decorativa: cada concepto de los próximos tres slides tiene un correlato directo en el código que vais a escribir.

---

## Transición

→ Primera pieza de teoría: modularidad y cohesión.
