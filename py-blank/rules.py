"""rules.py — Reglas deterministas R01–R09 (ESQUELETO · se implementa en II-5).

Cada función equivale a un nodo Code del workflow n8n de II-2/II-3/II-4. Son
**funciones puras**: reciben un dict `po`, devuelven un dict `po` modificado, y NO
tocan el mundo exterior (ni CSV, ni Telegram, ni LLM). Eso las hace testeables con
pytest sin red — los 8 casos de `tests/test_rules.py` son los mismos 8 casos que
validaste en n8n.

ESTADO: las firmas y las tablas de referencia están dadas. Los cuerpos están sin
implementar (`raise NotImplementedError`). En la sesión II-5 los rellenas y
`pytest tests/ -v` pasa de rojo a verde.

Principio E5 (no romper): el LLM extrae, las reglas deciden. Aquí NO se llama al LLM.
"""

from __future__ import annotations

import copy
import datetime as _dt

# --- Tablas de referencia (dadas: son conocimiento de dominio, no lógica) ------- #

# R04 · equivalencias PN cliente → PN proveedor (mismas que en SKILL.md)
EQUIVALENCIAS = {
    "ST9-HTP-RIB-047": "VBX-COMP-4471-B",
    "ST9-HTP-RIB-048": "VBX-COMP-4472-C",
    "HX7-FUS-PNL-331": "VBX-COMP-3301-A",
    "HX7-FUS-PNL-332": "VBX-COMP-3302-A",
    "HX7-BHD-332": "VBX-COMP-3303-B",
    "ST9-LE-PNL-550": "VBX-COMP-5501-A",
    "HX7-ELV-220": "VBX-COMP-2201-C",
}

# R07 · clientes registrados en el ERP
CLIENTES_VALIDOS = {"STRA-001", "KAIRO-001", "KAIRO-002", "HELI-001", "VECT-001"}

# R08 · unidades válidas
UNIDADES_VALIDAS = {"EA", "KG", "ML", "M2"}


# --- Reglas (esqueleto) --------------------------------------------------------- #
def r04_r08_validar_lineas(po: dict) -> dict:
    """R04 + R08: valida cada línea.

    R04 — si part_number_cliente NO está en EQUIVALENCIAS: añade alerta y marca ERROR.
    R08 — si cantidad <= 0 o unidad no está en UNIDADES_VALIDAS: añade alerta y marca ERROR.
    """
    raise NotImplementedError("II-5: implementa R04+R08 (validar líneas)")


def r07_validar_cliente(po: dict) -> dict:
    """R07: si el codigo_erp no está en CLIENTES_VALIDOS, marca cliente_no_registrado=True
    y degrada estado COMPLETO → PARCIAL. Añade alerta.
    """
    raise NotImplementedError("II-5: implementa R07 (validar cliente)")


def r01_r02_prioridad(po: dict) -> dict:
    """R01 + R02: calcula prioridad_calculada (AOG / PRIORITARIO / NORMAL).

    R01 — si po["aog"] es True: prioridad_calculada = "AOG" y cada línea prioridad="AOG".
    R02 — si una línea tiene fecha_entrega_requerida a <= 7 días (y >= 0) de hoy:
          línea prioridad="PRIORITARIO"; si el global era NORMAL, sube a PRIORITARIO.
    """
    raise NotImplementedError("II-5: implementa R01+R02 (prioridad)")


def r05_r06_doc_requerida(po: dict) -> dict:
    """R05 + R06: por cada línea, construye doc_requerida a partir de los flags.

    requiere_coc → añade "CoC"; requiere_easa_form1 → añade "EASA Form 1".
    Guarda la lista en l["doc_requerida"] (solo si hay alguna).
    """
    raise NotImplementedError("II-5: implementa R05+R06 (doc requerida)")


def r03_confianza(po: dict) -> dict:
    """R03: si confianza < 0.80 y estado es COMPLETO, lo degrada a PARCIAL. Añade alerta."""
    raise NotImplementedError("II-5: implementa R03 (umbral de confianza)")


def aplicar_reglas(po: dict) -> dict:
    """Orquesta las reglas en el MISMO orden que el workflow n8n:

        R04+R08 → R07 → R01+R02 → R05+R06 → R03

    Trabaja sobre una copia para no mutar la entrada (las funciones puras lo agradecen).
    """
    po = copy.deepcopy(po)
    po = r04_r08_validar_lineas(po)
    po = r07_validar_cliente(po)
    po = r01_r02_prioridad(po)
    po = r05_r06_doc_requerida(po)
    po = r03_confianza(po)
    return po
