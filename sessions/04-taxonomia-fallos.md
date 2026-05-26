# Notas de presentador — Slide 04: Taxonomía de fallos

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 2.3 El fan-out y la deuda técnica hacia II5 — introduce la asimetría de idempotencia y la vulnerabilidad del monolito ante fallos en nodos tardíos
> - § 5.3 Idempotencia asimétrica — explica en detalle el perfil de fallo de cada canal (Sheets idempotente, Telegram/Email no idempotentes) y la implicación para el retry
> - § 7.2 Por qué la modularización no puede esperar más — el Bulkhead como argumento central para sub-workflows independientes

**Slide:** MARCO TEÓRICO · SESIÓN 5 · B — "Taxonomía de fallos"  
**Duración estimada:** 5 min

---

## Qué decir

"Los sistemas fallan. La pregunta no es si, sino cómo. Y según cómo fallen, la respuesta es completamente distinta."

Recorrer la tabla de izquierda a derecha:

**Transitorio** — "El reintento lo resuelve. Un timeout de red, un pico de latencia en la API de Claude. En VERBEX lo registramos en `verbex.log` para saber que ocurrió, pero el sistema puede reintentar y seguir."

**Permanente** — "Requiere intervención humana. Un PN que no existe en el catálogo, una PO con cantidad cero. Ningún reintento lo va a arreglar. Lo capturamos como excepción, lo volcamos a `Errores.csv` y alguien tiene que actuar."

**Silencioso** — "El más peligroso de los tres, y el que más cuesta detectar en producción. El sistema procesa, no lanza excepción, devuelve algo… pero ese algo está mal. En VERBEX lo combatimos con dos mecanismos: el campo `alertas[]` en la PO (si el LLM inventa un PN, el parser lo anula y añade una alerta), y el estado visible en el dashboard. Un PARCIAL que nadie revisa es un fallo silencioso."

---

## Patrones aplicados en el repo

**Bulkhead (mamparo):** "Si `notify.py` falla — por ejemplo, el servidor SMTP no responde — eso no tumba la extracción ni la persistencia. La PO ya está en el CSV. El error queda en `Errores.csv`. El módulo de notificación falla de forma aislada."

**Circuit-breaker:** "El parser anti-alucinación de `llm.py` actúa como cortocircuito: antes de que un PN inventado llegue a `persistence.py`, lo detiene. No persistimos basura."

---

## Pregunta al grupo (opcional)

"¿Cuál de los tres tipos de fallo es más común en un agente LLM en producción?"

Respuesta esperada: el silencioso — el LLM puede producir JSON sintácticamente correcto pero semánticamente erróneo (PN inventado, fecha calculada mal). Por eso el parser anti-alucinación existe.

---

## Transición

→ Con modularidad para testear y taxonomía para diagnosticar, tenemos el vocabulario. Siguiente: cómo los tests son la especificación ejecutable del sistema.
