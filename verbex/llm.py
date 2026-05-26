"""verbex/llm.py — Capa cognitiva: llamada a Claude.

Equivale a tres nodos del workflow n8n de II-4:
  · "Construir body API"        → build_messages()
  · "Cognitivo · Llamada Claude API" → normalizar()
  · "Validar JSON LLM"          → _parsear_respuesta() (parser anti-alucinación)

Idea clave del puente: el *system prompt* NO se reescribe. Se carga desde PERSONA.md
y SKILL.md (los mismos ficheros que usaste en n8n) y se concatena. El LLM recibe
exactamente el mismo texto que recibía a través del nodo de n8n.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from anthropic import Anthropic

# Mismo modelo que el workflow n8n de II-3/II-4 (consistencia: "solo cambia el contenedor").
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1500
TEMPERATURE = 0.1

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Catálogo autoritativo de PN proveedor (= PNS_VALIDOS del nodo "Validar JSON LLM").
# El parser anula cualquier PN que el LLM se invente fuera de esta lista.
PNS_VALIDOS = {
    "VBX-COMP-4471-B", "VBX-COMP-4472-C", "VBX-COMP-3301-A", "VBX-COMP-3302-A",
    "VBX-COMP-3303-B", "VBX-COMP-5501-A", "VBX-COMP-5502-A", "VBX-COMP-2201-C",
    "VBX-COMP-2202-C", "VBX-COMP-6601-A", "VBX-COMP-6602-A", "VBX-COMP-7701-B",
    "VBX-COMP-7702-B", "VBX-COMP-8801-A", "VBX-COMP-9901-A", "VBX-COMP-9902-A",
}


def cargar_system_prompt() -> str:
    """Lee PERSONA.md + SKILL.md y los concatena en un único system prompt.

    En n8n estos dos textos vivían dentro del nodo Claude API. Aquí viven en
    ficheros versionables y se cargan en tiempo de ejecución. Mismo contenido,
    mismo comportamiento del modelo.
    """
    persona = (_REPO_ROOT / "PERSONA.md").read_text(encoding="utf-8")
    skill = (_REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
    return f"{persona}\n\n---\n\n{skill}"


def build_messages(texto_po: str) -> list[dict]:
    """Construye el array de mensajes para la API (= nodo 'Construir body API')."""
    return [{"role": "user", "content": f"Texto de la PO a normalizar:\n\n{texto_po}"}]


def _parsear_respuesta(raw: str) -> dict:
    """Parser anti-alucinación (= nodo 'Validar JSON LLM').

    1. Quita posibles fences markdown ```json ... ```.
    2. Parsea el JSON (lanza si no es válido).
    3. Si el LLM clasificó como no_pedido, normaliza a estado ERROR.
    4. Anula cualquier part_number_proveedor que NO esté en PNS_VALIDOS
       (el LLM no puede inventarse PNs de proveedor).
    """
    clean = raw.strip()
    if clean.startswith("```"):
        # elimina la primera línea (```json) y el fence de cierre
        clean = clean.split("\n", 1)[-1]
        clean = clean.rsplit("```", 1)[0]
    clean = clean.strip()

    try:
        po = json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON_PARSE_ERROR: {e}") from e

    if po.get("error") == "no_pedido":
        return {
            **po,
            "estado_normalizacion": "ERROR",
            "alertas": [f"LLM clasificó como no_pedido: {po.get('mensaje', '')}"],
            "lineas": [],
            "aog": False,
            "confianza": 0,
        }

    if not po.get("lineas"):
        raise ValueError("SCHEMA_ERROR: lineas[] vacío")

    alertas = list(po.get("alertas", []))
    for linea in po["lineas"]:
        pn = linea.get("part_number_proveedor")
        if pn and pn not in PNS_VALIDOS:
            alertas.append(
                f"PARSER: PN proveedor inventado por el LLM línea "
                f"{linea.get('linea_id')}: {pn}"
            )
            linea["part_number_proveedor"] = None
    po["alertas"] = alertas
    return po


def normalizar(texto_po: str, client: Anthropic | None = None) -> dict:
    """Llama a Claude y devuelve la PO normalizada como dict.

    Es el punto donde 'texto libre → JSON estructurado'. A partir de aquí,
    las reglas deterministas de rules.py toman el relevo (principio E5).
    """
    if client is None:
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=cargar_system_prompt(),
        messages=build_messages(texto_po),
    )
    return _parsear_respuesta(resp.content[0].text)
