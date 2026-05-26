"""main.py — Orquestador del agente VERBEX (ESQUELETO · se implementa en II-5).

Este fichero es el equivalente del GRAFO del workflow n8n `workflow_II4-csv.json`:
las conexiones entre nodos se convierten en llamadas secuenciales y condicionales.

    texto → llm.normalizar → rules.aplicar_reglas → R09 duplicado →
        ├─ duplicado → notify.telegram_operador_duplicado  (y para)
        └─ no duplicado → fan-out:
              ├─ persistence.append_pedido + append_lineas
              ├─ Switch prioridad → telegram AOG / PRIORITARIO
              ├─ Filter certificación → telegram_calidad
              └─ email_enviar

ESTADO: la función `process()` está esbozada con TODOs numerados por sección del
workflow. En II-5 la completas usando rules.py (ya implementado) y los módulos de
verbex/ (ya completos). `telegram_bot.py` importa `process` y la llama por cada mensaje.
"""

from __future__ import annotations

import logging

import rules
from verbex import llm, notify, persistence

log = logging.getLogger("verbex")


def process(texto_po: str) -> dict:
    """Procesa una PO en texto libre de principio a fin. Devuelve la PO final (dict).

    Devolver el dict permite a telegram_bot.py responder un resumen al usuario y
    facilita los tests de integración.
    """
    # 1. Capa cognitiva: texto → JSON (= nodos Construir body + Claude API + Validar)
    po = llm.normalizar(texto_po)
    log.info("LLM: %s estado=%s confianza=%s",
             po.get("numero_pedido"), po.get("estado_normalizacion"), po.get("confianza"))

    # 2. Reglas deterministas R04+R08 → R07 → R01+R02 → R05+R06 → R03
    po = rules.aplicar_reglas(po)
    log.info("Reglas: estado=%s prioridad=%s alertas=%d",
             po.get("estado_normalizacion"), po.get("prioridad_calculada"),
             len(po.get("alertas", [])))

    # 3. R09 · anti-duplicado (= nodo lookup CSV + Evaluar duplicado)
    po["duplicado"] = persistence.es_duplicado(po["numero_pedido"])

    # 4. IF ¿es duplicado? → avisar al operador y PARAR
    if po.get("duplicado"):
        log.warning("Duplicado: %s — no se reenvía", po.get("numero_pedido"))
        notify.telegram_operador_duplicado(po)
        return po

    # 5. Fan-out (solo si NO es duplicado):
    # 5a. Persistencia
    persistence.append_pedido(po, texto_po)
    persistence.append_lineas(po)

    # 5b. Switch por prioridad (= nodo Switch)
    if po["prioridad_calculada"] == "AOG":
        notify.telegram_produccion_aog(po)
    elif po["prioridad_calculada"] == "PRIORITARIO":
        notify.telegram_produccion_prioritario(po)
    # NORMAL no notifica a producción (por diseño, igual que en n8n)

    # 5c. Filter certificación (= nodo Filter)
    if any(l.get("requiere_coc") or l.get("requiere_easa_form1") for l in po["lineas"]):
        notify.telegram_calidad(po)

    # 5d. Email al cliente
    notify.email_enviar(po)

    log.info("PO %s procesada y distribuida", po.get("numero_pedido"))
    return po


if __name__ == "__main__":
    # Prueba rápida por CLI con la PO estándar de Stratos (sin levantar el bot).
    from dotenv import load_dotenv
    from verbex import observability

    load_dotenv()
    observability.setup_logging()
    demo = (
        "Purchase Order PO-2025-STRA-0847. Stratos Systems.\n"
        "Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.\n"
        "Ref: ST-900 program. CoC required."
    )
    try:
        resultado = process(demo)
        print(resultado)
    except Exception as e:  # noqa: BLE001
        observability.registrar_excepcion(e, origen="main.__main__")
        raise
