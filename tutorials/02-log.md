# Log de ejecución — Tutorial 02: Reglas sin red

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.x · sin API key  
**Resultado global:** ✅ Tutorial funcional sin correcciones. Todos los experimentos producen la salida exacta descrita.

---

## Experimento 1 · R04+R08: validaciones de línea

```
R04 - PN desconocido
  estado : ERROR
  alertas: ['R04: PN cliente desconocido: ST9-UNKNOWN-999 (línea 1)']

R08 - cantidad 0
  estado : ERROR
  alertas: ['R08: cantidad inválida: 0 (línea 1)']

R08 - unidad inválida
  estado : ERROR
  alertas: ['R08: unidad inválida: PZ (línea 1)']
```

**Observaciones:**
- `R04` produce `estado=ERROR` y alerta con el PN que falló y el número de línea.
- `R08` detecta tanto `cantidad=0` como `unidad` fuera de `UNIDADES_VALIDAS = {"EA", "KG", "ML", "M2"}`.
- La alerta incluye el valor incorrecto y la línea — útil para debugging en producción.
- La firma de alerta es `R04:` / `R08:` — el prefijo `R0X:` identifica qué regla disparó, diferenciándolo de las alertas del parser (`PARSER:`) y del LLM (sin prefijo).

> **Nota Windows:** las alertas con acentos (ínválida, línea) pueden aparecer con caracteres mojibake en la consola por defecto. El dato es correcto en memoria; es solo un problema de encoding de la consola. En producción, los CSV usan UTF-8 y los logs también.

---

## Experimento 2 · R07: cliente no registrado

```
R07 - cliente no registrado
  estado              : PARCIAL
  cliente_no_registrado: True
  alertas             : ['R07: cliente no registrado en ERP: CLIENTE-NUEVO']
```

**Observaciones:**
- `R07` degrada a `PARCIAL`, no a `ERROR`. Semántica intencional: el cliente podría ser nuevo y válido, la PO puede procesarse con supervisión humana.
- El campo `cliente_no_registrado=True` es una señal estructurada para el dashboard (II-6): permite filtrar POs que requieren validación manual de cliente.
- `CLIENTES_VALIDOS = {"STRA-001", "KAIRO-001", "KAIRO-002", "HELI-001", "VECT-001"}` — conjunto pequeño, mantenido en `rules.py`. En producción esto vendría de ERP.

---

## Experimento 3 · R01+R02: prioridad

```
R01 - AOG
  prioridad_calculada: AOG
  prioridad linea 1  : AOG

R02 - fecha a 3 días
  prioridad_calculada: PRIORITARIO

R02 - fecha lejana
  prioridad_calculada: NORMAL
```

**Observaciones:**
- `R01` propaga `AOG` tanto a nivel de PO (`prioridad_calculada`) como a cada línea (`lineas[i]["prioridad"]`). El LLM detecta `aog=True`; la regla propaga la señal estructurada.
- `R02` calcula `(fecha - hoy).days` y aplica umbral de 7 días. Con `days=3` → `PRIORITARIO`. Con `2027-01-01` → `NORMAL`.
- El umbral está hardcoded en `rules.py` (≤7 días). Cambiar la política de urgencia es cambiar una constante, no prompting.

---

## Experimento 4 · R05+R06: doc_requerida

```
R05 - solo CoC
  doc_requerida: ['CoC']

R05+R06 - CoC + EASA
  doc_requerida: ['CoC', 'EASA Form 1']

Ninguno requerido
  doc_requerida: None
```

**Observaciones:**
- `doc_requerida` es una lista (puede contener 0, 1, o 2 elementos) o `None` si ningún doc es requerido. Nunca lista vacía `[]`.
- El orden dentro de la lista es determinista: CoC siempre antes que EASA Form 1 (orden de aplicación de R05 y R06).
- `None` cuando ninguno es requerido — el código downstream lo trata con `.get("doc_requerida")` para no romper si el campo no existe.

---

## Experimento 5 · R03: confianza baja

```
R03 - confianza 0.60
  estado : PARCIAL
  alertas: ['R03: confianza baja (0.60 < 0.80)']

R03 - confianza 0.85
  estado : COMPLETO
```

**Observaciones:**
- Umbral: `confianza < 0.80` degrada `COMPLETO → PARCIAL`. El LLM puede devolver `COMPLETO` con confianza 0.75; R03 lo corrige.
- La alerta incluye el valor exacto y el umbral: `(0.60 < 0.80)`. Facilita auditoría.
- `confianza 0.85` no dispara degradación — `COMPLETO` se mantiene.
- Si el LLM ya devolvió `PARCIAL` (por sus propias razones), R03 no cambia nada (ya es PARCIAL).

---

## Experimento 6 · El orden importa: aplicar_reglas()

```
aog=True + confianza=0.60
  estado    : PARCIAL
  prioridad : AOG
```

**Observaciones:**
- `estado=PARCIAL` (R03 degradó) y `prioridad=AOG` (R01 elevó): **dos dimensiones independientes**. Esto no es contradictorio: una PO puede ser urgentísima (AOG) y al mismo tiempo tener datos ambiguos (PARCIAL).
- El orden de ejecución en `aplicar_reglas()` es: R04+R08 → R07 → R01+R02 → R05+R06 → R03. R03 va al final porque evalúa el estado final de la PO, no un campo de negocio.
- `copy.deepcopy` interno garantiza que la PO original no muta. El alumno puede reutilizar `po_base()` sin preocuparse.

---

## Correcciones aplicadas

Ninguna corrección al código ni al tutorial fue necesaria. El tutorial funciona tal como está escrito.

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| 1 — R04: PN desconocido | ✅ | ERROR + alerta con PN y línea |
| 1 — R08: cantidad=0 | ✅ | ERROR + alerta |
| 1 — R08: unidad inválida | ✅ | ERROR + alerta con valor incorrecto |
| 2 — R07: cliente desconocido | ✅ | PARCIAL + cliente_no_registrado=True |
| 3 — R01: AOG | ✅ | AOG propagado a PO y líneas |
| 3 — R02: fecha urgente | ✅ | PRIORITARIO |
| 3 — R02: fecha lejana | ✅ | NORMAL |
| 4 — R05: solo CoC | ✅ | ['CoC'] |
| 4 — R05+R06: ambos | ✅ | ['CoC', 'EASA Form 1'] |
| 4 — ninguno | ✅ | None |
| 5 — R03: confianza 0.60 | ✅ | PARCIAL + alerta con umbral |
| 5 — R03: confianza 0.85 | ✅ | COMPLETO sin degradar |
| 6 — orden aplicar_reglas | ✅ | PARCIAL + AOG (dimensiones independientes) |
