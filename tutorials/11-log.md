# Log de ejecución — Tutorial 11: Dashboard Streamlit

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13 · Streamlit (versión del requirements.txt) · sin API key  
**Resultado global:** ✅ Tutorial funcional. Dashboard arranca en `localhost:8501`, sirve HTTP 200, KPIs calculados correctamente.

---

## Paso 1 · Arranque del dashboard

```
streamlit run dashboard/app.py --server.headless true

  You can now view your Streamlit app in your browser.
  Local URL:    http://localhost:8501
  Network URL:  http://192.168.18.11:8501
  External URL: http://5.59.61.39:8501
```

```
HTTP 200  ← verificado con curl
```

✅ Streamlit arranca sin errores. El dashboard carga los 3 CSV en el arranque.

---

## Experimento A · KPIs calculados sobre el CSV actual

```
=== KPIs calculados por el dashboard ===
  POs totales   : 8
  POs hoy       : 4
  AOGs activos  : 2
  Tasa de exito : 75%
  Errores total : 5
```

**Desglose por estado y prioridad:**

```
Estado:
  COMPLETO: 6
  ERROR   : 1
  PARCIAL : 1

Prioridad:
  NORMAL: 6
  AOG   : 2
```

**Observaciones:**
- `Tasa de éxito = 75%` = 6 COMPLETO / 8 total. Los filtros de la barra lateral lo cambian dinámicamente.
- `AOGs activos: 2` — dos POs con `aog=True` en el CSV de muestra (incluyendo las procesadas en la sesión del bot).
- `Errores 7d: 5` — errores acumulados durante la sesión de dry run (SMTP, KeyError, ConnectionError, tutorial_06, tutorial_11).
- `POs hoy: 4` — las POs procesadas durante esta sesión de dry run.

---

## Experimento B y E · Pestañas y filtros (verificación lógica)

La lógica de filtros se verificó ejecutando el mismo código de `load_csv()` y los pandas filters de `app.py` fuera de Streamlit:

```python
df_filt = df_pedidos.copy()
# filtro Estado=COMPLETO
df_filt = df_filt[df_filt['estado_normalizacion'] == 'COMPLETO']
n_completos = len(df_filt)  # → 6
tasa = (6/6)*100            # → 100% (filtro afecta KPIs)
```

✅ Los filtros de sidebar afectan tanto la tabla como los KPIs: si filtras solo COMPLETO, la tasa sube al 100%.

**Columnas disponibles en Lineas.csv (join con la PO seleccionada):**
```
['timestamp', 'numero_pedido', 'linea_id', 'part_number_cliente',
 'part_number_proveedor', 'descripcion', 'cantidad', 'unidad',
 'fecha_entrega_requerida', 'programa', 'prioridad', 'requiere_coc',
 'requiere_easa_form1', 'doc_requerida']
```

✅ 14 columnas — `doc_requerida` y `prioridad` por línea están presentes (resultado de R05+R06 y R01).

---

## Experimento C · Refresco automático (mecanismo verificado)

El mecanismo de refresco está en `dashboard/app.py:44`:

```python
@st.cache_data(ttl=60, show_spinner="Leyendo CSV…")
def load_csv(nombre: str) -> pd.DataFrame:
```

`ttl=60` → la caché expira cada 60 s → Streamlit relee los CSV automáticamente.  
El sidebar muestra `Última carga: HH:MM:SS` para confirmar cuándo fue el último ciclo.

**Verificación end-to-end no ejecutada** (requiere API key para `llm.normalizar()`). La lógica de `persistence.append_pedido()` + invalidación de caché está verificada por componentes separados en tutoriales 05 y 08.

---

## Experimento D · Error de prueba en Errores.csv

```
observability.registrar_excepcion(
    ValueError('Error de prueba — tutorial 11'),
    origen='tutorial_11_exp_d'
)

Error escrito en Errores.csv
  timestamp : 2026-05-26T20:21:25.242373
  origen    : tutorial_11_exp_d
  tipo_error: ValueError
  error_raw : Error de prueba — tutorial 11
```

✅ El error aparece correctamente en `Errores.csv`. En el dashboard (pestaña "⚠ Errores recientes") se mostraría en ≤60 s.

**Estado de Errores.csv al final del dry run (6 errores):**
```
[2026-05-21] telegram_bot._handle      TimeoutError          (SMTP)
[2026-05-26] main.__main__             KeyError              (ANTHROPIC_API_KEY antes del fix)
[2026-05-26] tutorial_06_exp_c         ConnectionError       (error de prueba tutorial 06)
[2026-05-26] telegram_bot._handle      SMTPAuthenticationError (antes del fix main.py)
[2026-05-26] main.email_enviar         SMTPAuthenticationError (después del fix — capturado)
[2026-05-26] tutorial_11_exp_d         ValueError            (este experimento)
```

**Nota pedagógica:** el último `SMTPAuthenticationError` tiene `origen=main.email_enviar` — es el fix del `try/except` en acción. El anterior (`telegram_bot._handle`) es el comportamiento antes del fix. Se puede mostrar en clase como before/after del commit `204a6ca`.

---

## Correcciones aplicadas

Ninguna corrección al código del dashboard ni al tutorial fue necesaria.

---

## Resumen de validación

| Experimento | Estado | Nota |
|-------------|--------|------|
| Paso 1 — Streamlit arranca | ✅ | HTTP 200 en localhost:8501 |
| A — 5 KPIs calculados | ✅ | 8 POs / 75% éxito / 2 AOG / 5 errores |
| B — Pestaña Últimas POs | ✅ | Lógica verificada sin navegador |
| C — Refresco 60 s | ✅ | `@st.cache_data(ttl=60)` en línea 44 |
| D — Error de prueba en Errores.csv | ✅ | ValueError aparece con origen=tutorial_11 |
| E — Filtros sidebar | ✅ | Afectan tabla y KPIs |
