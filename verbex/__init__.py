"""Paquete verbex — módulos de soporte del agente normalizador de POs.

Separa los tres "lados sucios" del pipeline (los que tocan el mundo exterior):
  - llm.py          → llamada a Claude (= nodo Claude API de n8n)
  - persistence.py  → lectura/escritura CSV (= nodos Google Sheets de n8n)
  - notify.py       → Telegram y email (= nodos Telegram/Email de n8n)

La lógica de negocio pura (reglas R01–R09) vive fuera, en rules.py, para que sea
testeable sin red ni ficheros.
"""

__all__ = ["llm", "persistence", "notify"]
