"""verbex/observability.py — Logging y registro de errores del agente (II-6).

En n8n la observabilidad eran dos cosas: el panel *Executions* (qué pasó) y un
*Error Trigger Workflow* global que escribía los fallos en la hoja `Errores`.
Aquí ambas se reducen a la librería estándar `logging` + una función de persistencia.

Los 3 pilares de observabilidad que se enseñan en II-6:
  · logs    → qué pasó y cuándo            (logs/verbex.log)
  · métricas → con qué frecuencia          (el dashboard las agrega sobre los CSV)
  · trazas  → por qué falló                (el campo error_raw de Errores.csv)
"""

from __future__ import annotations

import logging
from pathlib import Path

from verbex import persistence

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "verbex.log"
_FORMATO = "%(asctime)s · %(levelname)s · %(name)s · %(message)s"

_configurado = False


def setup_logging(nivel: int = logging.INFO) -> logging.Logger:
    """Configura el logger `verbex` (fichero + consola). Idempotente.

    Llamar una vez al arrancar (telegram_bot.run o main.__main__). Las funciones
    de negocio solo hacen `logging.getLogger("verbex")` sin reconfigurar handlers.
    """
    global _configurado
    log = logging.getLogger("verbex")
    if _configurado:
        return log
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter(_FORMATO)
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    log.setLevel(nivel)
    log.handlers.clear()
    log.addHandler(fh)
    log.addHandler(sh)
    _configurado = True
    return log


def registrar_excepcion(
    exc: BaseException,
    origen: str,
    numero_pedido: str = "",
    texto_original: str = "",
) -> None:
    """Loggea la excepción y la persiste en Errores.csv (= Error Trigger de n8n).

    Punto único de captura de fallos técnicos: lo llaman el handler del bot y la
    ejecución por CLI. No se usa para los ERROR de negocio (PO rechazada por una
    regla) — esos son una salida válida y viven en Pedidos.csv con estado ERROR.
    """
    logging.getLogger("verbex").error(
        "Excepción en %s (PO %s): %s", origen, numero_pedido or "?", exc
    )
    persistence.append_error(
        tipo_error=type(exc).__name__,
        origen=origen,
        error_raw=str(exc),
        numero_pedido=numero_pedido,
        texto_original=texto_original,
    )
