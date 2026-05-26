# Checklist de Evaluación · Proyecto del Alumno (Python)

Para auto-evaluar antes de entregar y para que el instructor evalúe la entrega.

---

## Bloque obligatorio (mínimo para aprobar)

### 1. Schema JSON (15%)

- [ ] Schema documentado en el README.
- [ ] Todos los campos tienen tipo declarado (string, number, boolean, ISO date…).
- [ ] Indica qué campos son obligatorios y cuáles opcionales (`null`).
- [ ] Diferenciación entre datos **extraídos por el LLM** y datos **calculados por reglas** (ej. `prioridad_calculada` vs `prioridad`).

### 2. Tablas del dominio (10%)

- [ ] `catalogo.csv` con ≥ 10 entradas.
- [ ] `actores.csv` (clientes / técnicos / usuarios autorizados) con ≥ 3 entradas.
- [ ] Encoding UTF-8.
- [ ] Cabeceras consistentes con lo que usa el `SKILL.md`.

### 3. PERSONA.md (10%)

- [ ] Identidad del agente (quién es, para qué empresa).
- [ ] Lista numerada de reglas absolutas (mínimo 5).
- [ ] Schema JSON declarado.
- [ ] Manejo de "no pertinente" (qué hacer si el input no es del tipo esperado).

### 4. SKILL.md (10%)

- [ ] Pasos procedurales de extracción.
- [ ] Tablas del dominio (catálogo + actores) embebidas.
- [ ] **Mínimo 3 ejemplos few-shot** con INPUT y OUTPUT JSON completos.
- [ ] Los 3 ejemplos cubren casos distintos (no variaciones del mismo).

### 5. rules.py — reglas deterministas (20%)

- [ ] Mínimo 3 reglas implementadas como **funciones puras** (reciben dict `po`, devuelven dict; sin LLM, sin escribir ficheros).
- [ ] Cada regla tiene nombre identificativo (R01, R02…) y docstring.
- [ ] Documentadas en README: qué condición evalúan, qué hacen.
- [ ] Una función orquestadora `aplicar_reglas(po)` las encadena en un orden explícito.

### 6. tests/test_rules.py (15%)

- [ ] Mínimo 3 casos, uno por regla, parametrizados o separados.
- [ ] `pytest tests/ -v` pasa en **verde** (8/8 o los que tengas).
- [ ] Los tests no necesitan red ni `.env` (las reglas son puras).
- [ ] Al menos un caso de error (input que una regla rechaza → estado ERROR).

### 7. main.py — orquestador (10%)

- [ ] Encadena `llm.normalizar → rules.aplicar_reglas → persistencia/notify`.
- [ ] Anti-duplicado (equivalente a R09) antes de persistir.
- [ ] Routing condicional: al menos una rama según un campo del JSON (prioridad, severidad…).

### 8. README del proyecto (10%)

- [ ] Resumen del dominio elegido y por qué.
- [ ] Lista de capas (Cognitiva → Lógica → Persistencia → Notificación).
- [ ] **IO/RE de cada capa**: Inputs · Outputs · Reglas · Excepciones.
- [ ] Cómo correr el proyecto (paso a paso, incluido `pytest`).
- [ ] Qué decisiones tomaste y qué dejaste fuera.

---

## Bloque opcional (sube nota)

### 9. Polish técnico (3%)

- [ ] Naming consistente (snake_case).
- [ ] Comentarios mínimos pero claros.
- [ ] Sin secrets en git (`.gitignore` correcto).
- [ ] `.env.example` documentado.

### 10. Notificación (2%)

- [ ] Mensaje Telegram legible al usuario.
- [ ] Email (si aplica) con HTML básico.

### 11. Observabilidad (extras)

- [ ] `dashboard/app.py` adaptado que lea tus CSV.
- [ ] Logging + `Errores.csv` para fallos técnicos.

### 12. Deploy (extras)

- [ ] `start_*.bat` que arranque bot + dashboard con doble clic.
- [ ] Task Scheduler configurado (capturas de pantalla).

---

## Antipatrones a EVITAR (penalizan)

❌ **El LLM calcula valores numéricos o decide prioridad.** Eso lo hace `rules.py`. (-15%)

❌ **No hay parser anti-alucinación.** Si el LLM dice "el código es XYZ-9999" y lo guardas sin validar contra catálogo, falla E5. (-10%)

❌ **`rules.py` con efectos secundarios** (escribe CSV, llama al LLM). Deja de ser testeable. (-10%)

❌ **Sin tests** o tests en rojo. No puedes demostrar corrección. (-15%)

❌ **Sin diferenciación capa cognitiva vs determinista.** Todo en un mega-prompt o todo en código sin LLM. (-15%)

❌ **README pobre.** El evaluador no puede correr tu proyecto = no aprobado. (-20%)

---

## Qué hace que un proyecto destaque

✅ Caso de uso real, profesional, no inventado.
✅ Resuelve un problema concreto de tu día a día (o el de un colega).
✅ Los 3 ejemplos few-shot son del mundo real (anonimizados si hace falta).
✅ `PERSONA` con reglas absolutas que demuestran entendimiento del dominio (no copias VERBEX).
✅ Routing con lógica de negocio justificada.
✅ Tests que cubren los casos límite, no solo el camino feliz.
✅ README que explica el "por qué" además del "qué".

---

## Formato de entrega

Opción A · **GitHub repo** (preferido): estructura idéntica a `verbex-agent`, README en la raíz, enlace + permiso de lectura al instructor.

Opción B · **ZIP**: estructura completa, sin `__pycache__`, sin `.env`, sin `.venv`.

Plazo: cierre del curso (ver calendario COIIAOC).

---

*COIIAOC · Parte 2 · Fork Python · Checklist de evaluación*
