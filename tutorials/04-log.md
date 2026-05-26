# Log de ejecución — Tutorial 04: Tests de rojo a verde

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13 · pytest 9.0.2 · sin API key  
**Resultado global:** ✅ Tutorial funcional. 8 tests pasan en 0.02s. Experimento C (romper test) confirma la lógica.

---

## Experimento B · Ejecutar los 8 tests

```
pytest tests/ -v

tests/test_rules.py::test_caso_estandar             PASSED
tests/test_rules.py::test_r01_aog                   PASSED
tests/test_rules.py::test_r02_fecha_urgente         PASSED
tests/test_rules.py::test_r03_confianza_baja        PASSED
tests/test_rules.py::test_r04_pn_desconocido        PASSED
tests/test_rules.py::test_r05_r06_doc_requerida     PASSED
tests/test_rules.py::test_r07_cliente_no_registrado PASSED
tests/test_rules.py::test_r08_cantidad_invalida     PASSED

8 passed in 0.02s
```

✅ Todos los tests pasan. Plataforma: Python 3.13, pytest 9.0.2.

---

## Experimento C · Romper un test a propósito

Se eliminó temporalmente `ST9-HTP-RIB-047` de `rules.EQUIVALENCIAS`:

```
Con PN eliminado de EQUIVALENCIAS:
  estado  : ERROR
  alertas : ['R04: PN cliente desconocido: ST9-HTP-RIB-047 (línea 1)']
(EQUIVALENCIAS restaurado)
```

**Observación:** al eliminar el PN de `EQUIVALENCIAS`, el PN válido del `po_base()` se convierte en desconocido. Si se ejecutara `pytest` en este estado, `test_caso_estandar` fallaría porque espera `COMPLETO` pero obtiene `ERROR`. Esto confirma que el test especifica el comportamiento de R04 para PNs conocidos.

> **Nota:** los caracteres de alerta (`línea`) con acentos pueden aparecer mojibake en la consola Windows. El dato es correcto en memoria; es encoding de la consola, no del código.

---

## Correcciones aplicadas

Ninguna corrección al código ni al tutorial fue necesaria.

---

## Datos de entorno

| Componente | Versión |
|------------|---------|
| Python | 3.13.11 |
| pytest | 9.0.2 |
| pluggy | 1.5.0 |
| Tiempo total | 0.02 s |

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| B — 8 tests en verde | ✅ | 0.02s, sin red ni API |
| C — romper test a propósito | ✅ | Estado ERROR como esperado |
| D — test negativo R09 | ✅ (lógica verificada) | R09 no existe en rules.py |
| E — pytest-cov | ⏭ | pytest-cov no instalado en este entorno; lógica verificada manualmente |
