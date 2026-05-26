# Log de ejecución — Tutorial 08: Leer los CSV

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13 · sin API key  
**Resultado global:** ✅ Tutorial funcional con una corrección aplicada: columnas reales de `Pedidos.csv` difieren de las documentadas en el tutorial original.

---

## Experimento A · Estructura de `Pedidos.csv`

```
PEDIDOS.CSV
Columnas: 15 : ['timestamp', 'numero_pedido', 'cliente_nombre', 'codigo_erp', 'tier',
                'estado_normalizacion', 'prioridad_calculada', 'confianza', 'aog',
                'total_lineas', 'alertas_count', 'cliente_no_registrado', 'duplicado',
                'texto_original', 'alertas_resumen']
Total POs: 6
  PO-2025-STRA-0847                   estado=COMPLETO   prioridad=NORMAL       conf=0.97
  PO-2026-STRA-0901                   estado=COMPLETO   prioridad=NORMAL       conf=0.97
  PO-2026-KAI-0055-AOG                estado=COMPLETO   prioridad=AOG          conf=0.95
  PO-2026-VECT-0012                   estado=ERROR      prioridad=NORMAL       conf=0.65
  PO-2026-STRA-E2E-143002             estado=COMPLETO   prioridad=NORMAL       conf=0.97
  PO-2025-STRA-SMOKE-01               estado=COMPLETO   prioridad=NORMAL       conf=0.97
```

**Corrección aplicada:** el tutorial original listaba `COLS_PEDIDOS` como `[numero_pedido, cliente_codigo_erp, cliente_nombre, ..., modelo_llm, version_rules]`. Las columnas reales no incluyen `modelo_llm` ni `version_rules`, pero sí incluyen `tier`, `duplicado`, `texto_original`, `alertas_resumen`, `alertas_count`. El tutorial fue actualizado con las columnas reales.

---

## Experimento B · Estructura de `Lineas.csv`

```
LINEAS.CSV
Columnas: 14 : ['timestamp', 'numero_pedido', 'linea_id', 'part_number_cliente',
                'part_number_proveedor', 'descripcion', 'cantidad', 'unidad',
                'fecha_entrega_requerida', 'programa', 'prioridad', 'requiere_coc',
                'requiere_easa_form1', 'doc_requerida']
Total lineas: 7
```

✅ 14 columnas. La join es `numero_pedido`. `doc_requerida` está persistida (resultado de R05+R06). `prioridad` por línea está persistida (resultado de R01).

---

## Experimento D · Estadísticas

```
Estados: {'COMPLETO': 5, 'ERROR': 1}
Prioridades: {'NORMAL': 5, 'AOG': 1}
Confianza media (COMPLETO): 0.966
```

✅ Análisis correcto. El CSV contiene 6 POs de muestra que ilustran los diferentes estados del sistema.

**Observación:** `PO-2026-KAI-0055-AOG` con `prioridad=AOG` y `confianza=0.95` es el único caso AOG en los datos de muestra. La confianza media de 0.966 es representativa de POs bien estructuradas.

---

## Correcciones aplicadas al tutorial

| # | Fichero | Descripción |
|---|---------|-------------|
| 1 | `08-leer-los-csv.md` | Columnas reales de Pedidos.csv corregidas (añadido: tier, duplicado, texto_original, alertas_resumen, alertas_count; eliminado: modelo_llm, version_rules) |

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| A — Pedidos.csv estructura | ✅ | 15 columnas, corregidas en tutorial |
| B — Lineas.csv estructura | ✅ | 14 columnas como esperado |
| C — Errores.csv estructura | ✅ | 6 columnas, 3 errores de sesión anterior |
| D — estadísticas básicas | ✅ | 5 COMPLETO / 1 ERROR / 1 AOG |
| E — join Pedidos+Lineas | ✅ | 7 líneas para 6 POs |
