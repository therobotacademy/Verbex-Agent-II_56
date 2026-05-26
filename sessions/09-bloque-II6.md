# Notas de presentador — Slide 09: Sección II-6

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 7.1 Lo que queda fuera de scope en II4 — lista explícita de lo que II5/II6 añaden (Error Trigger, retry logic, Streamlit dashboard)
> - § 7.2 Por qué la modularización no puede esperar más — la frase que ancla este bloque: "Lo modular se opera; lo monolítico se rehace"

**Slide:** BLOQUE II-6 · GOBERNANZA Y ORQUESTACIÓN — "Operación y Despliegue"  
**Duración estimada:** 1 min (slide de transición)

---

## Qué decir

"II-5 terminado: `pytest` en verde, `main.py` funcionando, una PO procesada end-to-end. Muy bien."

"Ahora la pregunta que separa un prototipo de un sistema: **¿qué pasa cuando algo falla a las 3 de la mañana y no hay nadie mirando?**"

"Un agente que funciona en demo pero no tiene observabilidad, no tiene deploy automatizado y no deja rastro no es un sistema — es un script. II-6 convierte el script en sistema."

---

## Énfasis

- La frase que ancla II-6: *"un workflow que funciona no es todavía un sistema operable"*.
- Tres capacidades que añade II-6: **observar** (qué pasa), **recuperarse** (qué hacer cuando falla), **dejar rastro** (poder demostrar lo que ocurrió).

---

## Transición

→ Primer pilar de II-6: observabilidad.
