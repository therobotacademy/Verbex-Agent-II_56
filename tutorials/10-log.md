# Log de ejecución — Tutorial 10: Bot Telegram en vivo

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13  
**Resultado global:** ⏭ Tutorial no ejecutado en este dry run — requiere credenciales Telegram activas (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID_*`). El tutorial está validado como correcto en su lógica.

---

## Estado de ejecución

Este tutorial requiere:
1. Un bot de Telegram creado con @BotFather (token activo)
2. `TELEGRAM_CHAT_ID_PRODUCCION` y `TELEGRAM_CHAT_ID_CALIDAD` configurados en `.env`
3. Acceso a internet (polling de Telegram API)

En el entorno del dry run no están disponibles credenciales Telegram. El tutorial no fue ejecutado.

---

## Validación por componentes

### `telegram_bot.py` como adaptador (lógica verificada)

El código de `telegram_bot.py` fue inspeccionado en la sesión anterior. Su estructura es:

```python
async def handle_message(update, context):
    texto = update.message.text
    resultado = main.process(texto)   # mismo main.process() de Tutorial 01
    await update.message.reply_text(...)
```

`main.process()` fue verificado end-to-end en Tutorial 01. El bot solo añade la capa de transporte Telegram.

### Verificación del token (Paso 1)

El script de verificación (`run_t10_check.py`) usa `urllib.request` puro — no necesita `python-telegram-bot`. Un alumno con token válido puede ejecutarlo sin instalar dependencias adicionales.

### Casos del curso (Pasos 3 y 4)

Los 4 casos del tutorial (PO válida, AOG, PN desconocido, no-PO) están todos verificados en tutoriales anteriores:
- PO válida → Tutorial 01 Fase 1
- AOG → Tutorial 07 Experimento A
- PN desconocido → Tutorial 02 Experimento 1 (R04)
- No-PO → Tutorial 09 Guardia 3
- Duplicado → Tutorial 05 Experimento A

El bot produce exactamente los mismos resultados que los tutoriales anteriores porque usa `main.process()`.

---

## Notas para el presentador

1. **Demo en vivo:** si se dispone de credenciales Telegram durante la sesión, este tutorial es el más impactante visualmente — la respuesta del bot en el móvil es inmediata y concreta.
2. **Sin credenciales:** el tutorial puede presentarse conceptualmente usando los resultados de Tutorial 01 como proxy — la cadena es idéntica.
3. **SMTP:** en la configuración del curso, SMTP suele no estar configurado. El pipeline falla en el fan-out de email *después* de escribir en CSV — comportamiento esperado y documentado.

---

## Resumen de validación

| Paso | Estado | Nota |
|------|--------|------|
| 1 — Verificar token Telegram | ⏭ | Requiere TELEGRAM_BOT_TOKEN |
| 2 — Levantar bot | ⏭ | Requiere token + red |
| 3 — Enviar PO estándar | ⏭ | Lógica verificada en Tutorial 01 |
| 4 — Casos AOG/error/no-PO/dup | ⏭ | Lógica verificada en T07/T02/T09/T05 |
| 5 — Verificar CSV | ⏭ | Lógica verificada en Tutorial 08 |
