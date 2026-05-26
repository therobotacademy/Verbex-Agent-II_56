# Notas de presentador — Slide 03: Modularidad y cohesión

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 1. El repositorio en una imagen — arquitectura modular — diagrama D1, visión general de los cuatro módulos
> - § 1.1 main.py como orquestador puro — cómo cada módulo tiene una sola responsabilidad y `test_rules.py` corre sin red
> - § 1.2 La equivalencia n8n ↔ Python — el bloque MONOLITO explicado desde la comparativa de contenedores
> - § 3.3 El principio E5 en acción — "el LLM extrae, las reglas deciden"; por qué `rules.py` no llama al LLM

**Slide:** MARCO TEÓRICO · SESIÓN 5 · A — "Modularidad y cohesión / Trade-off monolítico / modular"  
**Duración estimada:** 6–8 min

---

## Qué decir (bloque MONOLITO, izquierda)

"Mirad el workflow de n8n que tenéis de la sesión anterior. ¿Cuántos nodos tiene? Veintiséis. Cuando queréis cambiar algo — por ejemplo, un umbral en una regla — ¿qué tocáis? El nodo Code. Pero ese nodo Code convive con el routing, con las conexiones a Sheets, con los splits. Tocar una cosa toca todo."

"¿Cómo probáis una sola regla? Tenéis que ejecutar el workflow completo, con credenciales activas, con Google Sheets disponible, con Telegram respondiendo. Si algo falla, no sabéis si es la regla, la conexión, o el token caducado."

Eso es un monolito funcional: todo acoplado, todo o nada.

---

## Qué decir (bloque MODULAR, derecha — DESARROLLAR)

### Los cuatro módulos y su responsabilidad única

El repositorio Python rompe el monolito en cuatro módulos, cada uno con **una sola razón para cambiar**:

| Módulo | Fichero | Responsabilidad única |
|--------|---------|----------------------|
| Cognitivo | `verbex/llm.py` | Texto libre → JSON. Solo habla con Claude. No sabe lo que son reglas. |
| Lógica | `rules.py` | Validar, calcular, decidir. No llama al LLM. No escribe nada. No envía nada. |
| Persistencia | `verbex/persistence.py` | Leer y escribir CSV. No sabe qué significa una PO, solo columnas y filas. |
| Notificación | `verbex/notify.py` | Enviar Telegram y email. No sabe de reglas ni de CSV. Solo formato y envío. |

"Si mañana cambiáis de Claude a otro LLM, solo tocáis `llm.py`. Si cambiáis de CSV a una base de datos, solo tocáis `persistence.py`. El resto del sistema no se entera."

### La consecuencia más importante: E5

"Pero el beneficio más práctico para vosotros hoy es éste: `rules.py` **se prueba sin red**."

Explicar despacio:

> En el monolito n8n, para saber si la regla R03 funciona correctamente, necesitáis: una conexión activa a n8n, las credenciales de Google configuradas, un mensaje de Telegram entrante, y que el workflow esté publicado y arriba. Son cinco puntos de fallo antes de llegar a la regla.

> En Python, ejecutáis:
> ```
> pytest tests/test_r03_confianza_baja.py -v
> ```
> Resultado en **0,03 segundos**, sin credenciales, sin red, sin nada. El test le pasa un diccionario a la función y comprueba que el diccionario de salida tiene `estado_normalizacion == "PARCIAL"`. Eso es todo.

"Esto es posible porque `rules.py` son **funciones puras**: reciben un `dict`, devuelven un `dict`, sin efectos secundarios. La pureza no es una restricción académica — es lo que os permite hacer el test en cero milisegundos."

### ¿Por qué `llm.py` no puede ser pura?

"Una pregunta que suele surgir: ¿por qué no hacemos también el LLM testeable sin red?"

Respuesta: porque `llm.py` llama a la API de Claude — inherentemente tiene efectos secundarios (red, latencia, coste). Lo que sí hacemos es **aislarla**: el parser anti-alucinación de `llm.py` garantiza que lo que sale de la capa cognitiva es JSON válido con PNs reales. Así, la frontera entre el LLM y las reglas está limpia. Las reglas pueden fiarse de su input.

### Recapitulación visual

Dibujar o señalar en la diapositiva:

```
[texto] → llm.py → [JSON limpio] → rules.py → [PO enriquecida]
                                        ↑
                               sin red · sin LLM · testeable
```

"La separación en la diapositiva no es estética. Es la razón por la que vuestros tests van a correr en 0,03 segundos y os van a decir exactamente qué función falla."

---

## Pregunta al grupo

"Antes de seguir: ¿alguien puede decirme qué pasaría si `rules.py` llamase al LLM para calcular la prioridad? ¿Qué se rompe?"

Respuesta esperada: los tests ya no pueden correr sin la API key; el principio E5 se rompe; el módulo deja de ser puro; el debugging se complica porque no sabes si el fallo es en la lógica o en la API.

---

## Énfasis adicional para el presentador

- El trade-off NO es "monolítico malo, modular bueno siempre". El monolito n8n era perfecto para prototipar. La modularidad Python es mejor para operar. Son herramientas distintas para fases distintas.
- Cohesión alta + acoplamiento bajo: esto es lo que cada módulo respeta. No hace falta nombrar el principio — basta con describir el efecto.

---

## Transición

→ La modularidad nos da testeabilidad. Pero los sistemas también fallan de formas inesperadas. Siguiente slide: cómo clasificar esos fallos.
