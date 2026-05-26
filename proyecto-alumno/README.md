# Proyecto del Alumno · Tu agente Python en otro dominio

**Curso:** Automatización de Procesos con Agentes Inteligentes · COIIAOC · Parte 2
**Entrega:** al cierre del curso
**Tiempo estimado:** 4–6 h fuera de clase

---

## Brief

Has construido (y ejecutado) el agente VERBEX en Python: un normalizador de Purchase Orders Tier 2 composites. Ahora vas a **adaptar el mismo recetario a otro dominio**.

El objetivo no es construir algo distinto: es demostrar que **el patrón se transfiere**. Texto libre → LLM con `PERSONA`/`SKILL` → JSON validado → reglas deterministas en `rules.py` → notificación + registro en CSV. Reutilizas la arquitectura del repo `verbex-agent`; cambias solo el dominio.

---

## Dominios sugeridos

Elige uno (o propón el tuyo):

### A. Mantenimiento programado (preventive maintenance)

El técnico envía partes por Telegram al final de cada intervención:

> *"Cambio de filtro hidráulico en máquina M-12 línea L-04. Tiempo: 2.5h. Pieza usada: FLT-HID-5210. Próxima revisión: en 200h o 30 días, lo que llegue antes."*

**Schema:** `equipo`, `tipo_intervencion`, `tiempo`, `pieza_usada`, `proxima_revision_horas`, `proxima_revision_dias`.

**Reglas candidatas (`rules.py`):** urgente→notificar inmediato · revisión ≤7 días→flag · pieza fuera de catálogo→ERROR · intervención >8h→revisar · anti-spam por nº de parte.

### B. Gestión de no conformidades (NCR · Non-Conformance Reports)

> *"NCR-2026-0457. Pieza VBX-COMP-3301-A lote L-2026-W14: porosidad en zona B mayor a tolerancia (0.8mm vs spec 0.5mm). 2 unidades afectadas. Severidad: alta."*

**Schema:** `lote`, `pieza_afectada`, `tipo_no_conformidad`, `severidad`, `cantidad_afectada`, `accion_recomendada`.

> Nota: hay un caso NCR completo con CrewAI en la 6ª sesión — si eliges NCR aquí, no copies aquello; resuélvelo con el patrón Python de VERBEX.

### C. Control de stock crítico (kanban-style alerts)

> *"Stock RR-6205: 12 unidades. Consumo medio: 8/día. Estimación 1.5 días."*

**Schema:** `referencia`, `stock_actual`, `consumo_medio`, `dias_estimados`.
**Reglas:** `dias_estimados < 3`→AOG-equivalente · `< 7`→PRIORITARIO.

### D. Tu propio dominio

Criterios para que sea adecuado: entrada en texto libre · conjunto cerrado de "cosas" reconocibles (catálogo finito) · reglas de negocio deterministas · salida estructurada útil · notificación condicional.

---

## Entregables (mínimo para aprobar)

Repo Python con la misma estructura que `verbex-agent`:

1. **`data/catalogo.csv`** — la lista finita de tu dominio (≥ 10 entradas).
2. **`data/actores.csv`** — los autorizados a enviar inputs (≥ 3 entradas).
3. **Schema JSON de salida** documentado en el README (campos, tipos, obligatorios vs opcionales).
4. **`PERSONA.md` y `SKILL.md`** adaptados al dominio (con ≥ 3 ejemplos few-shot).
5. **`rules.py`** — ≥ 3 reglas deterministas como **funciones puras** (reciben dict, devuelven dict, sin LLM ni efectos).
6. **`tests/test_rules.py`** — ≥ 3 casos que pasen en verde (`pytest`), uno por regla.
7. **`main.py`** — orquestador que encadena `llm → rules → persistencia/notify`.
8. **README con IO/RE de cada capa** (Cognitiva · Lógica · Persistencia · Notificación) + cómo correr.

Opcionales (suben nota): `dashboard/app.py` adaptado · `notify` real por Telegram · `deploy/start_*.bat` · logging en `Errores.csv`.

---

## Cómo empezar

1. **Elige dominio** y escribe **una frase de input** que el agente recibirá.
2. **Diseña el schema JSON** que tu agente debe extraer de esa frase.
3. **Crea las tablas** (`catalogo.csv` + `actores.csv`). Mínimo 10 + 3 entradas.
4. **Copia el repo `verbex-agent`** como plantilla. Mantén `verbex/llm.py`, `persistence.py`, `notify.py` casi intactos (cambian tablas y textos).
5. **Adapta `PERSONA.md`** (identidad + reglas absolutas + manejo de no-pertinente) y **`SKILL.md`** (tablas + 3 ejemplos few-shot de tu dominio).
6. **Escribe tus reglas en `rules.py`** como funciones puras y sus **tests primero** (TDD: rojo → implementas → verde).
7. **Conecta `main.py`** y prueba con tus 3 ejemplos.
8. **Documenta** el README: decisiones tomadas y qué quedó fuera.

---

## Patrones que debes reusar (no reinventar)

✅ **Reusar literal:** estructura de `PERSONA.md`/`SKILL.md` · el parser anti-alucinación de `verbex/llm.py` · `persistence.py` (CSV) · el principio E5 (el LLM extrae, las reglas deciden) · los tests de reglas como red de seguridad.

❌ **Adaptar:** tablas (catálogo, actores) · reglas concretas de `rules.py` · schema JSON · textos de notificación.

---

## Antipatrones a EVITAR

❌ El LLM calcula valores numéricos o decide prioridad → eso es `rules.py` (rompe E5).
❌ No hay parser anti-alucinación → el agente guarda PNs/códigos inventados.
❌ `rules.py` con efectos secundarios (escribe CSV, llama al LLM) → deja de ser testeable.
❌ Sin tests → no puedes demostrar que las reglas funcionan.
❌ README pobre → el evaluador no puede correr tu proyecto.

---

## Formato de entrega

- **GitHub repo** (preferido) o **ZIP** con la estructura completa.
- README en la raíz. Sin `__pycache__`, sin `.env`, sin `.venv`.
- Plazo: cierre del curso (ver calendario COIIAOC).

Ver criterios detallados en [`checklist.md`](checklist.md).

---

*COIIAOC · Parte 2 · Fork Python · Brief del proyecto del alumno*
