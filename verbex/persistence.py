"""verbex/persistence.py — Memoria del agente: CSV local.

Equivale a los tres nodos Google Sheets del workflow n8n de II-4:
  · "R09 · Buscar PO en CSV"  → buscar_po() / es_duplicado()
  · "CSV · Append Pedidos"    → append_pedido()
  · "CSV · Append Lineas"     → append_lineas()

Usa el módulo `csv` de la librería estándar, que ya implementa el comillado
RFC 4180 (campos con comas o comillas) — el mismo que en n8n hubo que escribir
a mano en JavaScript. Los ficheros y cabeceras son idénticos a los de la
carpeta `sheets/` del workflow, así que los datos son intercambiables con Sheets.
"""

from __future__ import annotations

import csv
import datetime as _dt
import os
from pathlib import Path

# Carpeta de datos: por defecto data/ del repo; configurable con CSV_DATA_DIR (= $env de n8n).
_DEFAULT_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR = Path(os.environ.get("CSV_DATA_DIR", _DEFAULT_DIR))

PEDIDOS_CSV = "Pedidos.csv"
LINEAS_CSV = "Lineas.csv"
ERRORES_CSV = "Errores.csv"

COLS_PEDIDOS = [
    "timestamp", "numero_pedido", "cliente_nombre", "codigo_erp", "tier",
    "estado_normalizacion", "prioridad_calculada", "confianza", "aog",
    "total_lineas", "alertas_count", "cliente_no_registrado", "duplicado",
    "texto_original", "alertas_resumen",
]

COLS_LINEAS = [
    "timestamp", "numero_pedido", "linea_id", "part_number_cliente",
    "part_number_proveedor", "descripcion", "cantidad", "unidad",
    "fecha_entrega_requerida", "programa", "prioridad", "requiere_coc",
    "requiere_easa_form1", "doc_requerida",
]

# Errores técnicos del pipeline (= hoja "Errores" que en n8n alimentaba el Error Trigger).
COLS_ERRORES = [
    "timestamp", "numero_pedido", "tipo_error", "origen", "error_raw", "texto_original",
]


def _ruta(nombre: str) -> Path:
    return DATA_DIR / nombre


def _asegurar_cabecera(path: Path, cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(cols)


def buscar_po(numero_pedido: str) -> list[dict]:
    """R09 lookup: filas de Pedidos.csv con ese numero_pedido y estado COMPLETO.

    Devuelve lista de matches (vacía si no hay). Equivale al nodo de lookup que
    en n8n consultaba la hoja `Pedidos`.
    """
    path = _ruta(PEDIDOS_CSV)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            row for row in reader
            if row.get("numero_pedido") == numero_pedido
            and row.get("estado_normalizacion") == "COMPLETO"
        ]


def es_duplicado(numero_pedido: str) -> bool:
    """True si la PO ya está registrada como COMPLETO (anti-spam R09)."""
    return len(buscar_po(numero_pedido)) > 0


def append_pedido(po: dict, texto_original: str = "") -> dict:
    """Aplana la PO y añade una fila a Pedidos.csv. Devuelve la fila escrita."""
    path = _ruta(PEDIDOS_CSV)
    _asegurar_cabecera(path, COLS_PEDIDOS)
    cliente = po.get("cliente") or {}
    alertas = po.get("alertas") or []
    fila = {
        "timestamp": _dt.datetime.now().isoformat(),
        "numero_pedido": po.get("numero_pedido", ""),
        "cliente_nombre": cliente.get("nombre") or "",
        "codigo_erp": cliente.get("codigo_erp") or "",
        "tier": cliente.get("tier") or "",
        "estado_normalizacion": po.get("estado_normalizacion", ""),
        "prioridad_calculada": po.get("prioridad_calculada", ""),
        "confianza": po.get("confianza", ""),
        "aog": po.get("aog", False),
        "total_lineas": len(po.get("lineas", [])),
        "alertas_count": len(alertas),
        "cliente_no_registrado": po.get("cliente_no_registrado", False),
        "duplicado": po.get("duplicado", False),
        "texto_original": texto_original[:1000],
        "alertas_resumen": " · ".join(alertas)[:500],
    }
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=COLS_PEDIDOS).writerow(fila)
    return fila


def append_lineas(po: dict) -> list[dict]:
    """Añade una fila por cada línea de la PO a Lineas.csv. Devuelve las filas escritas."""
    path = _ruta(LINEAS_CSV)
    _asegurar_cabecera(path, COLS_LINEAS)
    ts = _dt.datetime.now().isoformat()
    filas = []
    for l in po.get("lineas", []):
        doc = l.get("doc_requerida") or []
        filas.append({
            "timestamp": ts,
            "numero_pedido": po.get("numero_pedido", ""),
            "linea_id": l.get("linea_id", ""),
            "part_number_cliente": l.get("part_number_cliente", ""),
            "part_number_proveedor": l.get("part_number_proveedor") or "",
            "descripcion": l.get("descripcion", ""),
            "cantidad": l.get("cantidad", ""),
            "unidad": l.get("unidad", ""),
            "fecha_entrega_requerida": l.get("fecha_entrega_requerida") or "",
            "programa": l.get("programa", ""),
            "prioridad": l.get("prioridad", "NORMAL"),
            "requiere_coc": l.get("requiere_coc", False),
            "requiere_easa_form1": l.get("requiere_easa_form1", False),
            "doc_requerida": ", ".join(doc) if isinstance(doc, list) else (doc or ""),
        })
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLS_LINEAS)
        for fila in filas:
            writer.writerow(fila)
    return filas


def append_error(
    tipo_error: str,
    origen: str,
    error_raw: str,
    numero_pedido: str = "",
    texto_original: str = "",
) -> dict:
    """Registra un fallo técnico en Errores.csv. Devuelve la fila escrita.

    Es el equivalente en Python del Error Trigger Workflow de n8n: en lugar de un
    workflow aparte que escribe en la hoja `Errores`, una función de la stdlib
    añade una fila. El dashboard (II-6) lee este fichero en su pestaña de errores.
    """
    path = _ruta(ERRORES_CSV)
    _asegurar_cabecera(path, COLS_ERRORES)
    fila = {
        "timestamp": _dt.datetime.now().isoformat(),
        "numero_pedido": numero_pedido or "",
        "tipo_error": tipo_error,
        "origen": origen,
        "error_raw": str(error_raw)[:500],
        "texto_original": (texto_original or "")[:500],
    }
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=COLS_ERRORES).writerow(fila)
    return fila
