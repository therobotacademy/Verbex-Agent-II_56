# Notas de presentador — Slide 12: Contrato IORE

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 6. Casos de prueba en clase — Gate F4 — los tres casos de prueba son el contrato operativo del sistema; el IORE es su formalización
> - § 6.2 Criterio Gate F4 — la tabla de criterios binarios de cumplimiento que corresponde directamente al bloque OUTPUTS del slide
> - § 2.2 La bifurcación del duplicado — explica en detalle la excepción R09 (duplicado → avisar y parar) que aparece en el bloque EXCEPCIONES

**Slide:** IO · RE · SESIÓN 5 — "Contrato IORE"  
**Duración estimada:** 4 min

---

## Qué decir

"El contrato IORE es el documento de una página que resume qué entra, qué sale, qué reglas rigen y qué excepciones están definidas. Es el contrato de la sesión con vosotros."

---

## INPUTS

"Lo que traéis a la sesión de hoy: el repo con el esqueleto, Python 3.10+ con pytest instalado, y las dos credenciales mínimas. Sin la API key de Anthropic no podéis probar el LLM, pero sí podéis implementar y testear las reglas — recordad, los tests no usan la API."

---

## OUTPUTS

"Lo que tiene que existir cuando cerremos II-6:"

- `rules.py` y `main.py` implementados
- `pytest 8/8` verde — sin excepción
- Dashboard en localhost:8501 mostrando datos reales
- `start_verbex.bat` funcionando (bot + dashboard en dos ventanas)

"Son cuatro entregables concretos. Si los cuatro están, la sesión está completa."

---

## REGLAS

"Las tres reglas de diseño que no se negocian: E5 (LLM extrae, reglas deciden), funciones puras en `rules.py`, efectos en `verbex/` orquestados por `main.py`. Son las mismas que hemos visto en teoría — aquí las veis como contrato."

---

## EXCEPCIONES

"Tres casos edge que el sistema maneja de forma explícita:"

1. **PO no-pertinente**: el LLM devuelve `{"error": "no_pedido"}`. Las reglas no se ejecutan. El operador recibe una respuesta cortés en Telegram.
2. **Fallo técnico**: SMTP caído, API timeout. La excepción se captura, se registra en `Errores.csv` y el operador recibe un mensaje en el chat. El sistema no muere.
3. **Duplicado (R09)**: el sistema avisa al operador y detiene el pipeline. No se sobreescribe ni se renotifica.

---

## Énfasis

- El contrato IORE sirve para que cualquier persona nueva al proyecto entienda en 2 minutos qué hace el sistema. Si no podéis escribirlo, el diseño no está claro todavía.
- Las excepciones explícitas son tan importantes como el flujo feliz. Un sistema que solo funciona cuando todo va bien no es un sistema.

---

## Transición

→ Criterio de cumplimiento: ¿cuándo podemos decir que la sesión está terminada?
