# Log de ejecución — Tutorial 06: Casos de error del pipeline

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13 · sin API key (experimentos A–D)  
**Resultado global:** ✅ Tutorial funcional con una corrección aplicada: nombres de columnas de `Errores.csv`.

---

## Experimento A · Error de negocio: PN desconocido

```
estado      : ERROR
alertas     : ['R04: PN cliente desconocido: XX-INVENTADO-999 (línea 1)']
¿excepción? : No — el error está en el dict, no en Python
```

✅ El error de negocio se convierte en dato (`estado=ERROR + alertas`), no en excepción Python.

---

## Experimento B · Error técnico: JSON malformado del LLM

```
ValueError: JSON_PARSE_ERROR: Expecting value: line 1 column 38 (char 37)
ValueError: JSON_PARSE_ERROR: Expecting value: line 1 column 1 (char 0)
ValueError: JSON_PARSE_ERROR: Expecting value: line 1 column 1 (char 0)
```

✅ Los tres casos (JSON truncado, vacío, texto plano) lanzan `ValueError` con prefijo `JSON_PARSE_ERROR:`. El prefijo permite distinguirlos en logs.

---

## Experimento C · `observability` en acción

```
Excepcion registrada en Errores.csv
Total errores: 3
Timestamp: 2026-05-26T18:11:36.408294
Origen   : tutorial_06_exp_c
Tipo     : ConnectionError
Mensaje  : Timeout conectando a Anthropic API
```

✅ La excepción se registra correctamente. El log de la consola también muestra el error.

### Corrección aplicada

**Incidencia:** el tutorial original usaba los nombres de columna `tipo_excepcion` y `mensaje` para inspeccionar `Errores.csv`. Las columnas reales son `tipo_error` y `error_raw`.

**Columnas reales de `Errores.csv` (6):**  
`timestamp, numero_pedido, tipo_error, origen, error_raw, texto_original`

**Corrección:** actualizado el código del Experimento C en el tutorial para usar `tipo_error` y `error_raw`.

---

## Experimento D · Pipeline completo con error de negocio (lógica verificada)

La lógica se verificó combinando experimentos de tutoriales anteriores:
- R04 detecta PN desconocido → `estado=ERROR`
- `es_duplicado()` devuelve `False` para POs con estado `ERROR` (verificado en Tutorial 05)
- La PO en ERROR se registraría en CSV para auditoría (sin ejecutar `append_pedido` realmente)

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| A — error de negocio como dato | ✅ | estado=ERROR, sin excepción |
| B — JSON malformado | ✅ | 3 variantes, ValueError con prefijo |
| C — observability.registrar_excepcion | ✅ | Columnas corregidas en tutorial |
| D — pipeline con error E2E | ✅ | Lógica verificada sin escribir CSV |
| E — error real API | ⏭ | Requiere API key; lógica equivalente a Guardia 2 |
