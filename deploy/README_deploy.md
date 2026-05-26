# Despliegue y operación · VERBEX MVP (Python)

Guía operativa del MVP en Python puro. El sistema son **2 procesos**: el bot de Telegram (`telegram_bot.py`) y el dashboard (`dashboard/app.py`). La persistencia es CSV local (`data/`); no hay n8n, ni Google Sheets, ni Service Account.

---

## Estructura en producción

```
verbex-agent/
├── telegram_bot.py        proceso 1 · escucha POs por Telegram
├── main.py                orquestador del pipeline
├── rules.py               reglas R01–R09
├── verbex/                llm · persistence · notify · observability
├── dashboard/app.py       proceso 2 · dashboard read-only (Streamlit)
├── data/                  Pedidos.csv · Lineas.csv · Errores.csv  ← memoria del agente
├── logs/verbex.log        log rotado a mano (se crea solo)
├── deploy/                start_verbex.bat · task-scheduler.md · este README
└── .env                   credenciales (NO se versiona)
```

---

## Setup inicial por máquina

1. **Clonar / copiar** el repo a una ruta sin caracteres especiales (evita `Mi unidad/…`; usa p.ej. `C:\verbex\verbex-agent`).
2. **Crear entorno** e instalar dependencias:
   ```powershell
   cd C:\verbex\verbex-agent
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r dashboard\requirements.txt
   ```
3. **Configurar `.env`** (copia de `.env.example`): `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS`, y SMTP si activas email.
4. **Probar en frío:**
   ```powershell
   pytest tests\ -v                 # 8/8 verde si rules.py está implementado
   python main.py                   # procesa la PO demo y escribe en data/
   python -m streamlit run dashboard\app.py   # abre el dashboard
   ```
5. **Arranque automático:** seguir [`task-scheduler.md`](task-scheduler.md).

---

## Operación diaria

**Por la mañana** — verifica que las 2 ventanas (`VERBEX Bot`, `VERBEX Dashboard`) están abiertas; si no, doble clic en `start_verbex.bat`. Abre el dashboard en `http://localhost:8501`.

**Cuando llega un pedido** — el remitente autorizado envía la PO al bot por Telegram; el agente responde con el resumen en segundos y la fila aparece en el dashboard al refrescar (60 s).

**Final del día** — un vistazo a la pestaña **Errores recientes** del dashboard y al final de `logs/verbex.log` para detectar fallos técnicos (timeouts SMTP, errores de API).

---

## Métricas a vigilar (en el dashboard)

| KPI | Qué indica | Señal de alarma |
|---|---|---|
| Tasa de éxito | % de POs en estado COMPLETO | caída brusca → revisar prompts o catálogo |
| Errores 7d | fallos técnicos recientes | > 0 sostenido → problema de credenciales/red |
| AOGs activos | urgencias en curso | revisar que se hayan atendido |

---

## Procedimientos frecuentes

- **Añadir un cliente:** edita `CLIENTES_VALIDOS` en `rules.py` y la tabla del `SKILL.md` (para que el LLM lo reconozca).
- **Añadir un PN:** edita `EQUIVALENCIAS` en `rules.py` y la tabla de equivalencias del `SKILL.md`.
- **Cambiar el comportamiento del LLM:** edita `PERSONA.md` / `SKILL.md` — no toques `rules.py`. No requiere reiniciar si solo cambias los prompts (se leen en cada llamada).
- **Rotar credenciales:** edita `.env` y reinicia el bot.

---

## Backup mínimo

Copia periódica de `data/*.csv` (es toda la memoria del agente) y del `.env`. El log (`logs/verbex.log`) es útil para post-mortems pero no es crítico.

---

## Coste mensual estimado (≈50 POs/día · ~1500/mes)

| Componente | Coste |
|---|---|
| Anthropic Claude API | ~20 € |
| Telegram Bot | gratis |
| SMTP (cuenta propia) | gratis |
| Dashboard / persistencia (local) | gratis |
| **Total** | **~20 €/mes** |

---

*COIIAOC · Parte 2 · Fork Python · Operación del MVP (2 procesos)*
