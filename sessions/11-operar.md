# Notas de presentador — Slide 11: Dashboard, deploy y entrega

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 7.1 Lo que queda fuera de scope en II4 — el Streamlit dashboard y los sub-workflows aparecen aquí como entregables pendientes
> - § 7.3 Checklist pre-II5 — el estado de CSV, `.env` y tests que se asume cumplido antes de activar el dashboard y el deploy
> - § 1.3 Archivos de configuración — la nota sobre `.gitignore` y credenciales es especialmente relevante antes de cualquier deploy

**Slide:** OPERAR · II-6 — "Dashboard, deploy y entrega"  
**Duración estimada:** 7 min

---

## Qué decir (cuatro bloques)

---

### Dashboard CSV

"Streamlit. Sin credenciales, sin Google, sin Sheets. Lee directamente los CSV que escribe el agente."

"Cinco KPIs en la parte superior: POs totales, POs de hoy, AOGs activos, tasa de éxito, errores en 7 días. Filtros por programa, estado y prioridad. Tabla de últimas POs con el detalle de líneas. Una pestaña separada para `Errores.csv`."

"Para levantarlo:"
```bash
pip install -r dashboard/requirements.txt
python -m streamlit run dashboard/app.py
```
"Abrís http://localhost:8501 y ya está. Read-only: el dashboard nunca escribe nada."

Demo en vivo si el entorno está preparado: procesar una PO desde `main.py`, refrescar el dashboard, mostrar que aparece.

---

### Deploy — 2 procesos, doble clic

"`deploy/start_verbex.bat` arranca dos ventanas de cmd: una con el bot de Telegram, otra con el dashboard de Streamlit. No hay que hacer nada más. Doble clic y el sistema está activo."

"`deploy/task-scheduler.md` explica paso a paso cómo registrar ese bat en Windows Task Scheduler para que se ejecute automáticamente al iniciar sesión. El agente arranca solo cuando el PC arranca."

"Esta es la diferencia entre un sistema que funciona cuando alguien lo recuerda y un sistema operable."

---

### Gobernanza — checklist 48 ítems · AS9100

"Antes de poner esto en producción real, hay que repasar `gobernanza-checklist.md`. 48 ítems que cubren: seguridad de credenciales, retención de datos 7 años (requisito AS9100), trazabilidad de decisiones, procedimiento de rotación de tokens, política de costes de API."

"Para vuestro proyecto del curso, no es obligatorio completarlo — pero es el documento que diferencia 'lo construimos en clase' de 'esto podría ir a producción'."

---

### Proyecto propio — vuestro reto

"Lo que habéis construido en VERBEX es un patrón: `PERSONA + SKILL → llm → rules → persistence + notify`. Ese patrón se transfiere a cualquier dominio."

"El proyecto del curso os pide que lo adaptéis: nuevo dominio, nuevo catálogo, nuevas reglas puras, nuevos tests en verde. El brief está en `proyecto-alumno/README.md` y la rúbrica en `checklist.md`."

---

## Énfasis

- El dashboard no es un nice-to-have — es la interfaz de operación. Sin él, el operario tiene que abrir CSV a mano para saber qué pasó.
- El doble clic de deploy es la metáfora correcta: si necesitas un ingeniero para arrancar el sistema cada mañana, no es un sistema operable.

---

## Transición

→ Para cerrar II-6, el contrato formal de la sesión: inputs, outputs, reglas y excepciones.
