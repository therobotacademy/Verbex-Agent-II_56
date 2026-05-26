# Notas de presentador — Slide 10: Observabilidad — Los tres pilares

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 7.1 Lo que queda fuera de scope en II4 — el Error Trigger global y el retry configurable como deuda técnica explícita que II5/II6 saldan
> - § 2.3 El fan-out y la deuda técnica hacia II5 — introduce el problema de resiliencia que la observabilidad en II6 viene a resolver
> - § 5.3 Idempotencia asimétrica — la distinción entre ERROR de negocio (Pedidos.csv) y fallo técnico (Errores.csv) tiene su base aquí

**Slide:** OBSERVABILIDAD · II-6 — "Los tres pilares"  
**Duración estimada:** 6 min

---

## Qué decir

"Observabilidad es la capacidad de entender el estado interno de un sistema desde fuera, mirando sus salidas. Tres preguntas, tres pilares."

---

## Logs — "Qué pasó y cuándo"

"`verbex/observability.py` configura el logger estándar de Python: un fichero `logs/verbex.log` más salida a consola. No es un servicio externo — es la stdlib `logging`. Cada PO procesada, cada excepción capturada, cada notificación enviada queda registrada con timestamp."

"Abrid `logs/verbex.log` después de procesar una PO y veréis la traza completa del pipeline. Eso es lo que os permite decir 'la PO PO-2026-KAI-0055-AOG entró a las 09:14:32 y salió como AOG a las 09:14:34'."

---

## Métricas — "Con qué frecuencia"

"Las métricas no son tiempo real — son agregaciones sobre los CSV. El dashboard calcula: POs totales, POs de hoy, AOGs activos, tasa de éxito (COMPLETO / total), errores en los últimos 7 días."

"¿Por qué sobre CSV y no sobre una base de datos? Porque el CSV ya existe, es legible, es portable, y para el volumen de VERBEX (decenas de POs al día, no millones) es suficiente. No añadimos complejidad que no necesitamos."

---

## Trazas — "Por qué falló"

"`data/Errores.csv` guarda los fallos técnicos: tipo de error, módulo de origen, el `error_raw` completo (el mensaje de excepción), y el `numero_pedido` o texto original que lo provocó."

"La distinción importante del slide: los ERROR de negocio — una PO rechazada por R04 porque el PN no existe — viven en `Pedidos.csv` con `estado=ERROR`. Los fallos técnicos — SMTP no responde, API de Anthropic timeout — viven en `Errores.csv`. Son categorías distintas: uno lo decide una regla, el otro lo lanza Python."

---

## Pregunta al grupo

"Si un operario llega por la mañana y quiere saber si el agente procesó correctamente las POs del turno de noche, ¿qué mira?"

Respuesta esperada: el dashboard (métricas agregadas, tasa de éxito), y si algo falló, `logs/verbex.log` para el qué y `Errores.csv` para el por qué.

---

## Énfasis

- Observabilidad no es un añadido de lujo — es lo que separa un script de un sistema en producción.
- En el contexto aeronáutico (AS9100), el rastro auditable no es opcional: necesitas poder demostrar que el sistema procesó correctamente cada PO. Los CSV más los logs son el audit trail de VERBEX.

---

## Transición

→ Tenemos observabilidad. Ahora, cómo arrancamos el sistema y lo dejamos funcionando sin intervención manual.
