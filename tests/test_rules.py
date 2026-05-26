"""tests/test_rules.py — Los 8 casos de prueba de las reglas (= los 8 casos de n8n).

Cada test ejercita una regla a través de `rules.aplicar_reglas()`, igual que en n8n
validabas el set de 8 POs end-to-end. Solo importan `rules` (funciones puras), así que
NO necesitan red, API keys ni ficheros: corren con `pytest tests/ -v` en cualquier sitio.

En el STARTER KIT estos 8 tests fallan (rules.py es esqueleto). Cuando implementes las
reglas en II-5, pasan a verde. Ese es tu Gate de II-5.
"""

import copy
import datetime as dt

import rules


def po_base() -> dict:
    """PO estándar de Stratos ya extraída por el LLM (antes de aplicar reglas).

    Es válida en todo: PN conocido, cliente registrado, cantidad y unidad OK,
    confianza alta, sin AOG. Cada test parte de aquí y muta lo justo.
    """
    return copy.deepcopy({
        "numero_pedido": "PO-2025-STRA-0847",
        "cliente": {"nombre": "Stratos Systems", "tier": "TIER_1", "codigo_erp": "STRA-001"},
        "lineas": [{
            "linea_id": 1,
            "part_number_cliente": "ST9-HTP-RIB-047",
            "part_number_proveedor": "VBX-COMP-4471-B",
            "descripcion": "Costilla composite HTP sección delantera",
            "cantidad": 12,
            "unidad": "EA",
            "fecha_entrega_requerida": "2025-09-15",
            "programa": "ST900",
            "prioridad": "NORMAL",
            "requiere_coc": True,
            "requiere_easa_form1": False,
        }],
        "estado_normalizacion": "COMPLETO",
        "confianza": 0.97,
        "alertas": [],
        "aog": False,
    })


def test_caso_estandar():
    """Golden path: PO válida → COMPLETO y prioridad NORMAL."""
    po = rules.aplicar_reglas(po_base())
    assert po["estado_normalizacion"] == "COMPLETO"
    assert po["prioridad_calculada"] == "NORMAL"


def test_r01_aog():
    """R01: aog=True → prioridad_calculada AOG y cada línea AOG."""
    po = po_base()
    po["aog"] = True
    out = rules.aplicar_reglas(po)
    assert out["prioridad_calculada"] == "AOG"
    assert all(l["prioridad"] == "AOG" for l in out["lineas"])


def test_r02_fecha_urgente():
    """R02: fecha de entrega a 3 días → PRIORITARIO."""
    po = po_base()
    po["lineas"][0]["fecha_entrega_requerida"] = (dt.date.today() + dt.timedelta(days=3)).isoformat()
    out = rules.aplicar_reglas(po)
    assert out["prioridad_calculada"] == "PRIORITARIO"


def test_r03_confianza_baja():
    """R03: confianza < 0.80 → degrada COMPLETO a PARCIAL."""
    po = po_base()
    po["confianza"] = 0.60
    out = rules.aplicar_reglas(po)
    assert out["estado_normalizacion"] == "PARCIAL"


def test_r04_pn_desconocido():
    """R04: PN cliente fuera de la tabla de equivalencias → ERROR."""
    po = po_base()
    po["lineas"][0]["part_number_cliente"] = "ST9-HTP-RIB-999"
    out = rules.aplicar_reglas(po)
    assert out["estado_normalizacion"] == "ERROR"


def test_r05_r06_doc_requerida():
    """R05+R06: CoC + EASA Form 1 → doc_requerida poblada."""
    po = po_base()
    po["cliente"] = {"nombre": "Kairos Aerospace", "tier": "TIER_1", "codigo_erp": "KAIRO-001"}
    po["lineas"][0]["part_number_cliente"] = "HX7-FUS-PNL-331"
    po["lineas"][0]["part_number_proveedor"] = "VBX-COMP-3301-A"
    po["lineas"][0]["requiere_coc"] = True
    po["lineas"][0]["requiere_easa_form1"] = True
    out = rules.aplicar_reglas(po)
    assert out["lineas"][0]["doc_requerida"] == ["CoC", "EASA Form 1"]


def test_r07_cliente_no_registrado():
    """R07: codigo_erp no registrado → cliente_no_registrado y PARCIAL."""
    po = po_base()
    po["cliente"] = {"nombre": None, "tier": None, "codigo_erp": None}
    out = rules.aplicar_reglas(po)
    assert out["cliente_no_registrado"] is True
    assert out["estado_normalizacion"] == "PARCIAL"


def test_r08_cantidad_invalida():
    """R08: cantidad <= 0 → ERROR."""
    po = po_base()
    po["lineas"][0]["cantidad"] = 0
    out = rules.aplicar_reglas(po)
    assert out["estado_normalizacion"] == "ERROR"
