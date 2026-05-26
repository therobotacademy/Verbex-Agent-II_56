# Notas de presentador — Slide 08: Reglas deterministas R01–R09

> **Referencia en `docs/verbex-agent-guia-tecnica.docx`:**
> - § 3. Pipeline de reglas deterministas — R01–R09 — diagrama D3, visión general del módulo `rules.py`
> - § 3.1 El orden canónico y por qué importa — explicación detallada de por qué R04+R08 → R07 → R01+R02 → R05+R06 → R03 y no otro orden
> - § 3.2 Validación dura vs. degradación suave — distinción ERROR (rojo) vs PARCIAL (ámbar) y sus consecuencias operativas
> - § 3.3 El principio E5 en acción — "regla de oro": si puedes escribirlo como expresión Python, no necesitas el LLM; incluye el antipatrón E4

**Slide:** REGLAS DETERMINISTAS · II-5 — "R01–R09 como funciones"  
**Duración estimada:** 7 min

---

## Qué decir

"Esta tabla es vuestro mapa de trabajo para II-5. Cinco funciones, nueve reglas, ocho tests."

Recorrer fila a fila:

---

### r04_r08_validar_lineas (R04 · R08)

"R04: si el `part_number_cliente` que viene del LLM no está en la tabla `EQUIVALENCIAS` de `rules.py`, la PO no puede procesarse. Resultado: `estado = ERROR` y una alerta descriptiva. No es PARCIAL — es ERROR porque sin un PN válido no podemos fabricar ni trazar nada."

"R08: cantidad cero o unidad fuera del conjunto `{EA, KG, ML, M2}`. Mismo resultado: ERROR. Una línea con `cantidad=0` no es una línea de pedido, es un error de transcripción."

"Dos tests los verifican: `test_r04` y `test_r08`."

---

### r07_validar_cliente (R07)

"Si `codigo_erp` no está en el conjunto de clientes válidos del ERP, marcamos `cliente_no_registrado=True` y degradamos de COMPLETO a PARCIAL. No es un ERROR porque quizás el cliente existe y simplemente aún no está dado de alta — alguien tiene que revisarlo. PARCIAL es la señal correcta."

---

### r01_r02_prioridad (R01 · R02)

"R01: AOG. Si el LLM detectó `aog=True`, toda la PO se eleva a prioridad AOG y cada línea individual también. Es la prioridad más alta. Sin excepciones."

"R02: urgencia por fecha. Si la `fecha_entrega_requerida` de una línea está a 7 días o menos (y a 0 o más — no fechas en el pasado), esa línea se marca PRIORITARIO. Si al menos una línea es PRIORITARIO, la PO sube de NORMAL a PRIORITARIO."

"¿Por qué R02 no sube a AOG? Porque AOG es una declaración explícita del cliente, no se infiere solo de la fecha."

---

### r05_r06_doc_requerida (R05 · R06)

"Construye el campo `doc_requerida` de cada línea. Si `requiere_coc=True`, añade `"CoC"`. Si `requiere_easa_form1=True`, añade `"EASA Form 1"`. Ambos pueden coexistir. Si ninguno aplica, el campo es lista vacía."

"Un solo test cubre ambas reglas porque son simétricas."

---

### r03_confianza (R03)

"Si la confianza del LLM es menor de 0,80 y el estado es COMPLETO, lo degradamos a PARCIAL. Un COMPLETO con confianza 0,65 es una contradicción — el LLM no estaba seguro de lo que extrajo, así que no podemos tratarlo como si lo estuviera."

---

## La nota al pie: R09 no está en rules.py

"Fijáos en la nota del slide. R09 — el anti-duplicado — no vive en `rules.py`. ¿Por qué? Porque necesita leer el CSV para saber si el `numero_pedido` ya existe. Una función que lee un fichero no es pura — tiene un efecto secundario. Por eso R09 vive en `persistence.es_duplicado()` y lo llama `main.py`, no `aplicar_reglas()`."

"Este es un buen ejemplo de por qué el principio 'funciones puras' no es dogma sino consecuencia: cuando la función necesita leer el disco, tiene que salir de `rules.py`."

---

## Consejo de implementación para el grupo

"Implementad de arriba abajo, un test a la vez. Corred `pytest tests/test_r04_pn_desconocido.py -v`, implementad `r04_r08_validar_lineas`, pasad ese test, seguid. No intentéis implementar todo antes de correr el primero."

---

## Transición

→ II-5 en vuestras manos. Ahora pasamos al segundo bloque: II-6, operación y despliegue.
