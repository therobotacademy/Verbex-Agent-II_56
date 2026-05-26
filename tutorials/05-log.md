# Log de ejecución — Tutorial 05: Anti-duplicado

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13 · sin API key  
**Resultado global:** ✅ Tutorial funcional. Anti-duplicado opera correctamente. Corrección menor aplicada: la nota sobre `COLS_PEDIDOS` menciona columnas incorrectas.

---

## Experimento A · `es_duplicado` directamente

```
Es duplicado 'PO-2025-STRA-0847'?  →  True
Es duplicado 'PO-2099-TEST-NEVER'?  →  False
```

✅ La función detecta correctamente la PO existente en el CSV de muestra y retorna `False` para una inexistente.

---

## Experimento B · ¿Qué cuenta como duplicado?

```
Total POs en CSV: 6
  PO-2025-STRA-0847                   estado= COMPLETO  dup= True
  PO-2026-STRA-0901                   estado= COMPLETO  dup= True
  PO-2026-KAI-0055-AOG                estado= COMPLETO  dup= True
  PO-2026-VECT-0012                   estado= ERROR     dup= False
  PO-2026-STRA-E2E-143002             estado= COMPLETO  dup= True
  PO-2025-STRA-SMOKE-01               estado= COMPLETO  dup= True
```

**Observación clave:** `PO-2026-VECT-0012` está en el CSV con `estado=ERROR` y `es_duplicado()` devuelve `False`. La condición `estado_normalizacion == COMPLETO` es necesaria — una PO con error puede reprocesarse.

---

## Corrección al tutorial

**Incidencia:** las columnas reales de `Pedidos.csv` son distintas a las listadas en el Experimento D del tutorial.

**Columnas reales (15):**  
`timestamp, numero_pedido, cliente_nombre, codigo_erp, tier, estado_normalizacion, prioridad_calculada, confianza, aog, total_lineas, alertas_count, cliente_no_registrado, duplicado, texto_original, alertas_resumen`

**Columnas documentadas en el tutorial (incorrecto):**  
`numero_pedido, cliente_codigo_erp, cliente_nombre, estado_normalizacion, ...modelo_llm, version_rules`

**Corrección aplicada en tutorial 08** (que describe los CSVs en detalle) con las columnas reales.

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| A — es_duplicado directa | ✅ | True/False correctos |
| B — PO ERROR no es duplicado | ✅ | PO-2026-VECT-0012 retorna False |
| C — simular pipeline con duplicado | ✅ | Lógica verificada |
| D — COLS_PEDIDOS | ⚠ | Columnas reales corregidas en tutorial 08 |
