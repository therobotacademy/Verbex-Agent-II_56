"""verbex/notify.py — Capa de salida: Telegram y email.

Equivale a los nodos de notificación del workflow n8n de II-4:
  · "Telegram · Operador (duplicado)"      → telegram_operador_duplicado()
  · "Telegram · Producción AOG"            → telegram_produccion_aog()
  · "Telegram · Producción PRIORITARIO"    → telegram_produccion_prioritario()
  · "Telegram · Calidad"                   → telegram_calidad()
  · "Render email HTML" + "Email · Enviar" → render_email_html() + email_enviar()

Los textos de los mensajes son los mismos que en n8n. Telegram se envía con la
API HTTP del bot (requests); el email con smtplib (librería estándar).
"""

from __future__ import annotations

import datetime as _dt
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

_TG_API = "https://api.telegram.org/bot{token}/sendMessage"


# --------------------------------------------------------------------------- #
# Telegram
# --------------------------------------------------------------------------- #
def _telegram_send(chat_id: str, text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    resp = requests.post(
        _TG_API.format(token=token),
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    )
    resp.raise_for_status()


def telegram_operador_duplicado(po: dict) -> None:
    chat = os.environ["TELEGRAM_CHAT_ID_PRODUCCION"]
    cliente = (po.get("cliente") or {}).get("nombre") or "no identificado"
    text = (
        "⚠ VERBEX · PO duplicada\n\n"
        f"PO: {po['numero_pedido']}\n"
        f"Cliente: {cliente}\n\n"
        f"{' · '.join(po.get('alertas', []))}\n\n"
        "No se reenvía notificación."
    )
    _telegram_send(chat, text)


def telegram_produccion_aog(po: dict) -> None:
    chat = os.environ["TELEGRAM_CHAT_ID_PRODUCCION"]
    cliente = (po.get("cliente") or {}).get("nombre") or "no identificado"
    text = (
        "🚨 AOG · VERBEX\n\n"
        f"PO: {po['numero_pedido']}\n"
        f"Cliente: {cliente}\n"
        f"Líneas: {len(po.get('lineas', []))}\n"
        f"Confianza: {po.get('confianza')}\n\n"
        "⚠ Acción: verificar stock inmediatamente.\n\n"
        f"{' · '.join(po.get('alertas', []))}"
    )
    _telegram_send(chat, text)


def telegram_produccion_prioritario(po: dict) -> None:
    chat = os.environ["TELEGRAM_CHAT_ID_PRODUCCION"]
    cliente = (po.get("cliente") or {}).get("nombre") or "no identificado"
    text = (
        "⚠ PO PRIORITARIA · VERBEX\n\n"
        f"PO: {po['numero_pedido']}\n"
        f"Cliente: {cliente}\n"
        f"Líneas: {len(po.get('lineas', []))}\n"
        "Entrega ≤ 7 días.\n\n"
        "Revisar planificación de producción."
    )
    _telegram_send(chat, text)


def telegram_calidad(po: dict) -> None:
    chat = os.environ["TELEGRAM_CHAT_ID_CALIDAD"]
    cliente = (po.get("cliente") or {}).get("nombre") or "no identificado"
    lineas_doc = [
        f"· {l.get('part_number_proveedor') or l.get('part_number_cliente')} "
        f"→ {', '.join(l['doc_requerida'])}"
        for l in po.get("lineas", [])
        if l.get("doc_requerida")
    ]
    text = (
        "📋 Documentación requerida · VERBEX\n\n"
        f"PO: {po['numero_pedido']}\n"
        f"Cliente: {cliente}\n\n"
        "Líneas con certificación:\n"
        f"{chr(10).join(lineas_doc)}\n\n"
        "Preparar documentación antes de envío."
    )
    _telegram_send(chat, text)


# --------------------------------------------------------------------------- #
# Email
# --------------------------------------------------------------------------- #
def render_email_html(po: dict) -> str:
    """Genera el email HTML branded VERBEX (= nodo 'Render email HTML')."""
    filas = []
    for l in po.get("lineas", []):
        pn = l.get("part_number_proveedor") or l.get("part_number_cliente")
        doc = ", ".join(l.get("doc_requerida") or []) or "—"
        filas.append(
            '<tr>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;font-family:monospace;font-size:11px;">{pn}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;">{l.get("descripcion","")}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;">{l.get("cantidad","")} {l.get("unidad","")}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;">{l.get("fecha_entrega_requerida") or "—"}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;font-size:10px;">{doc}</td>'
            '</tr>'
        )
    lineas_html = "".join(filas)

    alertas = po.get("alertas") or []
    alertas_html = ""
    if alertas:
        alertas_html = (
            '<div style="margin:16px 0;padding:12px 16px;background:#FFF7ED;'
            'border-left:3px solid #C2510A;border-radius:0 4px 4px 0;font-size:12px;color:#4A3000;">'
            '<strong style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#C2510A;">Observaciones</strong>'
            f'<br>{"<br>".join(alertas)}</div>'
        )

    cliente = (po.get("cliente") or {}).get("nombre") or "Cliente"
    return (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"></head>'
        '<body style="margin:0;padding:0;background:#F5F2EC;font-family:Arial,Helvetica,sans-serif;color:#1C1C1C;">'
        '<table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#F5F2EC;padding:32px 0;"><tr><td align="center">'
        '<table cellpadding="0" cellspacing="0" border="0" width="600" style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);">'
        '<tr><td style="background:#1E3A5F;padding:24px 32px;color:#fff;font-size:22px;font-weight:bold;">VERBEX <span style="color:#FF8C3B;">COMPOSITES</span></td></tr>'
        '<tr><td style="padding:32px;"><h2 style="margin:0 0 16px;font-size:18px;">Confirmación de pedido</h2>'
        f'<p style="margin:0 0 12px;font-size:14px;">Estimado/a <strong>{cliente}</strong>,</p>'
        f'<p style="margin:0 0 16px;font-size:14px;">Hemos recibido y normalizado su Purchase Order <strong>{po["numero_pedido"]}</strong>.</p>'
        '<table style="width:100%;border-collapse:collapse;font-size:13px;margin:16px 0;"><thead><tr style="background:#FAFAF7;">'
        '<th align="left" style="padding:8px 10px;font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.1em;">PN</th>'
        '<th align="left" style="padding:8px 10px;font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.1em;">Descripción</th>'
        '<th align="right" style="padding:8px 10px;font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.1em;">Cant.</th>'
        '<th align="left" style="padding:8px 10px;font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.1em;">Entrega</th>'
        '<th align="left" style="padding:8px 10px;font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.1em;">Doc.</th>'
        f'</tr></thead><tbody>{lineas_html}</tbody></table>'
        f'<p style="font-size:13px;"><strong>Estado:</strong> {po.get("estado_normalizacion")} · '
        f'<strong>Prioridad:</strong> {po.get("prioridad_calculada")} · '
        f'<strong>Confianza:</strong> {po.get("confianza")}</p>'
        f'{alertas_html}'
        '<p style="font-size:11px;color:#666;margin-top:24px;">Si detecta cualquier discrepancia con su pedido original, '
        'responda a este email en un plazo máximo de 24 h. Pasado ese plazo, el pedido se considera aceptado y entra en planificación.</p>'
        '<p style="font-size:10px;color:#999;font-family:monospace;letter-spacing:.05em;margin-top:16px;">'
        f'VERBEX COMPOSITES S.L. · Parque Aeronáutico Cartuja · Sevilla<br>Procesado: {_dt.datetime.now().isoformat()}</p>'
        '</td></tr></table></td></tr></table></body></html>'
    )


def email_enviar(po: dict) -> None:
    """Envía el email de confirmación por SMTP (= nodo 'Email · Enviar confirmación')."""
    smtp_from = os.environ["SMTP_FROM"]
    destino = (po.get("cliente") or {}).get("email_contacto") or smtp_from
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Confirmación de pedido VERBEX · {po['numero_pedido']}"
    msg["From"] = smtp_from
    msg["To"] = destino
    msg.attach(MIMEText(render_email_html(po), "html"))

    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("SMTP_USER", smtp_from)
    password = os.environ["SMTP_PASSWORD"]
    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.sendmail(smtp_from, [destino], msg.as_string())
