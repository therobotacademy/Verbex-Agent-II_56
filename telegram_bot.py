"""telegram_bot.py — Trigger del agente: recibe POs por Telegram.

Equivale al "Manual Trigger" / webhook de Telegram del workflow n8n. En n8n el
trigger arrancaba el pipeline; aquí un bucle de long-polling escucha mensajes y
llama a `main.process(texto)` por cada uno.

Usa la API HTTP del bot (getUpdates / sendMessage) con `requests` — totalmente
síncrono y transparente, igual que hace n8n por debajo. Sin frameworks async.

Arranque:
    python telegram_bot.py

NOTA: en el starter kit `main.process()` aún no está implementado (II-5), así que
el bot arranca y escucha, pero al recibir una PO responde que rules.py/main.py
están pendientes. Cuando completes II-5, empieza a procesar de verdad.

Las credenciales se leen en tiempo de ejecución (no al importar), de modo que
`import telegram_bot` funciona aunque todavía no exista `.env`.
"""

from __future__ import annotations

import os
import time

import requests
from dotenv import load_dotenv

import main
from verbex import observability


def _api() -> str:
    return f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}"


def _allowed() -> set[str]:
    raw = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "")
    return {c.strip() for c in raw.split(",") if c.strip()}


def _send(chat_id: int | str, text: str) -> None:
    requests.post(f"{_api()}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=15)


def _resumen(po: dict) -> str:
    """Resumen legible de la PO procesada, para responder en el chat."""
    return (
        "✅ PO procesada\n"
        f"Número: {po.get('numero_pedido')}\n"
        f"Estado: {po.get('estado_normalizacion')} · Prioridad: {po.get('prioridad_calculada')}\n"
        f"Líneas: {len(po.get('lineas', []))}"
        + (" · DUPLICADA" if po.get("duplicado") else "")
    )


def _handle(chat_id: int | str, texto: str) -> None:
    if (allowed := _allowed()) and str(chat_id) not in allowed:
        _send(chat_id, "⛔ Chat no autorizado.")
        return
    try:
        po = main.process(texto)
        _send(chat_id, _resumen(po))
    except NotImplementedError:
        _send(chat_id, "🔧 rules.py / main.py aún sin implementar (se completa en II-5).")
    except Exception as e:  # noqa: BLE001 — en clase queremos ver el error en el chat
        observability.registrar_excepcion(e, origen="telegram_bot._handle", texto_original=texto)
        _send(chat_id, f"❌ Error procesando la PO: {e}")


def run() -> None:
    load_dotenv()
    observability.setup_logging()
    api = _api()  # valida que TELEGRAM_BOT_TOKEN existe antes de entrar al bucle
    print("VERBEX bot escuchando… (Ctrl+C para parar)")
    offset = None
    while True:
        params = {"timeout": 30}
        if offset is not None:
            params["offset"] = offset
        try:
            resp = requests.get(f"{api}/getUpdates", params=params, timeout=40)
            updates = resp.json().get("result", [])
        except requests.RequestException as e:
            print(f"[warn] getUpdates falló: {e}; reintento en 3 s")
            time.sleep(3)
            continue
        for upd in updates:
            offset = upd["update_id"] + 1
            msg = upd.get("message") or {}
            texto = msg.get("text")
            chat_id = (msg.get("chat") or {}).get("id")
            if texto and chat_id is not None:
                _handle(chat_id, texto)


if __name__ == "__main__":
    run()
