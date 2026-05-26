# Notas de presentador — Slide 13: Gate y cierre de sesión

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 6.2 Criterio Gate F4 — la tabla de criterios de cumplimiento que corresponde a los cuatro ítems del Gate del slide
> - § 6.1 Los tres casos — los casos de prueba que deben estar pasando antes de declarar el gate cumplido
> - § 7. Hoja de ruta hacia II5 — el preview de la sesión 6 está prefigurado en la lista de lo que queda fuera de scope en II4

**Slide:** GATE · CIERRE · SESIÓN 5 — "Criterio de cumplimiento"  
**Duración estimada:** 4 min

---

## Qué decir

"El gate de la sesión son cuatro comprobaciones binarias. O están o no están:"

1. `pytest 8/8 verde` — la lógica es correcta
2. El agente procesa una PO end-to-end — el pipeline completo funciona
3. El dashboard muestra POs y KPIs desde CSV — la operación es visible
4. `start_verbex.bat` arranca bot + dashboard — el deploy es reproducible

"Si las cuatro están, habéis salido de la sesión con un sistema operable. Si falta alguna, tenéis trabajo pendiente antes de pasar a II-6."

---

## Preview sesión 6: CrewAI

"La siguiente sesión da un salto conceptual: de un agente a varios agentes colaborando."

"La idea clave de la sesión 6 es 'un agente resuelve; varios colaboran'. Vais a construir un crew de tres agentes especializados — NCR (no conformidad), 8D (resolución de problemas) y CAPA (acción correctiva) — y vais a ver cómo se comunican y se pasan el control."

"También haremos la comparativa honesta: n8n vs Python vs CrewAI. Cada uno tiene su sitio. No hay una respuesta correcta para todos los casos."

---

## Énfasis

- El gate no es subjetivo. No es "¿os parece que funciona?", es "¿el comando devuelve 8 passed?". La objetividad del criterio es parte del diseño.
- La comparativa n8n/Python/CrewAI en la sesión 6 cierra el arco: habrán construido el mismo agente de tres formas distintas y podrán opinar con criterio propio.

---

## Transición

→ Un último slide de teoría: los conceptos de esta sesión en términos transferibles a otros dominios.
