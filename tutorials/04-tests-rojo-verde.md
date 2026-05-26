# Tutorial 04 · Tests: de rojo a verde

Arranca con `pytest` en rojo y hazlo pasar. Entenderás qué prueba cada test antes de leer la implementación — el test como especificación ejecutable.

| Tiempo | Credenciales | Fichero |
|--------|-------------|---------|
| ~20 min | **Ninguna** | `tests/test_rules.py` |

---

## Por qué los tests primero

```
pytest tests/ -v    # los 8 tests pasan (starter kit ya implementado)
```

En el flujo de trabajo del curso, los tests **ya pasan** porque `rules.py` está completo. Este tutorial te enseña a leerlos como especificación: cada test describe un requisito de negocio antes de que el código exista.

---

## Estructura de `tests/test_rules.py`

```python
# tests/test_rules.py — estructura completa
import pytest
import datetime as dt
import rules

@pytest.fixture
def po_base():
    return { ... }  # PO mínima válida de Stratos

def test_caso_estandar(po_base): ...         # R01–R09, PO limpia → COMPLETO
def test_r01_aog(po_base): ...               # AOG → prioridad=AOG
def test_r02_fecha_urgente(po_base): ...     # fecha ≤7 días → PRIORITARIO
def test_r03_confianza_baja(po_base): ...    # confianza<0.80 → PARCIAL
def test_r04_pn_desconocido(po_base): ...    # PN fuera de EQUIVALENCIAS → ERROR
def test_r05_r06_doc_requerida(po_base): ... # requiere_coc+easa → doc_requerida
def test_r07_cliente_no_registrado(po_base):... # cliente fuera de CLIENTES_VALIDOS → PARCIAL
def test_r08_cantidad_invalida(po_base): ... # cantidad=0 → ERROR
```

---

## Experimento A · Leer un test como especificación

Abre `tests/test_rules.py` y lee `test_r04_pn_desconocido`:

```python
def test_r04_pn_desconocido(po_base):
    po_base["lineas"][0]["part_number_cliente"] = "ST9-UNKNOWN-999"
    out = rules.r04_r08_validar_lineas(po_base)
    assert out["estado_normalizacion"] == "ERROR"
    assert any("ST9-UNKNOWN-999" in a for a in out["alertas"])
```

**Qué especifica este test:**
1. Dado un PN de cliente que no está en `EQUIVALENCIAS`...
2. ...el estado debe ser `ERROR`...
3. ...y debe haber al menos una alerta que contenga el PN que falló.

No especifica el texto exacto de la alerta — solo que contiene el PN. Eso es intencional: el mensaje puede mejorar sin romper el test.

---

## Experimento B · Ejecutar los 8 tests

```bash
pytest tests/ -v
```

### Salida esperada

```
tests/test_rules.py::test_caso_estandar         PASSED
tests/test_rules.py::test_r01_aog               PASSED
tests/test_rules.py::test_r02_fecha_urgente     PASSED
tests/test_rules.py::test_r03_confianza_baja    PASSED
tests/test_rules.py::test_r04_pn_desconocido    PASSED
tests/test_rules.py::test_r05_r06_doc_requerida PASSED
tests/test_rules.py::test_r07_cliente_no_registrado PASSED
tests/test_rules.py::test_r08_cantidad_invalida PASSED

8 passed in 0.02s
```

0.02 segundos. Sin red. Sin API key. Esto es lo que significa "funciones puras testeables".

---

## Experimento C · Romper un test a propósito

Para entender qué prueba cada test, rómpelo y lee el mensaje de error.

Guarda como `run_t04c.py`:

```python
import rules

# Modificamos rules directamente (solo para el experimento)
# Guardamos el original
_original = rules.EQUIVALENCIAS.copy()

# Eliminar un PN de la tabla para que R04 falle en el test estándar
del rules.EQUIVALENCIAS["ST9-HTP-RIB-047"]

po = {
    "numero_pedido": "PO-T",
    "cliente": {"codigo_erp": "STRA-001"},
    "lineas": [{
        "linea_id": 1,
        "part_number_cliente": "ST9-HTP-RIB-047",
        "cantidad": 5, "unidad": "EA",
        "fecha_entrega_requerida": "2026-12-01",
        "requiere_coc": False, "requiere_easa_form1": False,
    }],
    "estado_normalizacion": "COMPLETO",
    "confianza": 0.97, "alertas": [], "aog": False,
}

out = rules.r04_r08_validar_lineas(po)
print("estado  :", out["estado_normalizacion"])
print("alertas :", out["alertas"])

# Restaurar
rules.EQUIVALENCIAS.update(_original)
print("\n(EQUIVALENCIAS restaurado)")
```

**Qué observar:** al eliminar `ST9-HTP-RIB-047` de `EQUIVALENCIAS`, el PN válido del test se convierte en desconocido. `test_caso_estandar` fallaría porque espera `COMPLETO` pero obtendría `ERROR`.

---

## Experimento D · Escribir un test nuevo

Añade este test al final de `tests/test_rules.py` (solo para practicar — elimínalo después):

```python
def test_r09_concepto(po_base):
    """R09 vive en persistence.py, no en rules.py — no es testeable aquí."""
    # Las reglas puras no comprueban duplicados: eso requiere leer CSV.
    # Este test documenta el límite del módulo rules.py.
    out = rules.aplicar_reglas(po_base)
    # R09 no aparece porque no existe en rules.py — es correcto.
    assert "R09" not in str(out.get("alertas", []))
```

```bash
pytest tests/ -v -k "test_r09"
```

**Qué aprende el alumno:** R09 (anti-duplicado) no está en `rules.py` porque requiere leer el CSV — viola la pureza. Ese test "negativo" documenta el límite del módulo.

---

## Experimento E · Cobertura de tests

```bash
pytest tests/ --tb=short -q
```

El flag `-q` reduce el output. `--tb=short` muestra traceback corto en caso de fallo. Útil en CI.

Para ver qué líneas de `rules.py` cubre el test suite:

```bash
pip install pytest-cov
pytest tests/ --cov=rules --cov-report=term-missing
```

**Qué observar:** los 8 tests cubren las ramas principales de cada función. Las ramas no cubiertas (si las hay) suelen ser condiciones de borde — casos que el equipo decidió no testear explícitamente.

---

## Lo que acabas de aprender

- Los tests son especificaciones ejecutables: cada `assert` documenta un requisito de negocio.
- `pytest` con funciones puras es instantáneo (0.02 s). Sin mocks, sin fixtures complejas.
- Romper un test a propósito enseña más que leerlo en verde.
- El límite del módulo `rules.py` (sin CSV, sin LLM) está documentado por lo que **no** hay en los tests.

---

## Siguiente tutorial

→ **[05 · Anti-duplicado: R09 y el CSV](05-anti-duplicado.md)** — la única regla que no está en `rules.py` y por qué.  
→ **[06 · Casos de error del pipeline](06-casos-de-error.md)** — qué pasa cuando el LLM devuelve basura, la red cae o el CSV está corrupto.
