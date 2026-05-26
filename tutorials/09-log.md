# Log de ejecución — Tutorial 09: Parser anti-alucinación

**Fecha de ejecución:** 2026-05-26  
**Entorno:** Windows 11 · Python 3.13 · sin API key  
**Resultado global:** ✅ Tutorial funcional sin correcciones. Las 4 guardias se comportan exactamente como se describe.

---

## Guardia 1 · Strip de fences markdown

```
=== GUARDIA 1: strip fences ===
  estado: COMPLETO
  PN    : ST9-HTP-RIB-047
```

✅ El JSON dentro de ` ```json ... ``` ` se parsea correctamente. Guardia activa.

**Nota de implementación:** la regex en `llm.py` elimina tanto ` ```json ` como ` ``` ` simples al inicio y al final. La guardia es robusta ante variaciones del formato de salida de Claude.

---

## Guardia 2 · JSON malformado

```
=== GUARDIA 2: JSON malformado ===
  JSON truncado  : ValueError - JSON_PARSE_ERROR: Expecting value: line 1 column 38 (char 37)
  Respuesta vacia: ValueError - JSON_PARSE_ERROR: Expecting value: line 1 column 1 (char 0)
  Solo texto     : ValueError - JSON_PARSE_ERROR: Expecting value: line 1 column 1 (char 0)
```

✅ Los 3 casos lanzan `ValueError` con prefijo `JSON_PARSE_ERROR:`. Posición del error incluida en el mensaje (útil para debugging).

**Observación:** "Respuesta vacía" y "Solo texto" producen el mismo mensaje de error (`char 0`). Son distinguibles por el `origen` en `Errores.csv`, no por el mensaje de error.

---

## Guardia 3 · Respuesta `no_pedido`

```
=== GUARDIA 3: no_pedido ===
  estado  : ERROR
  alertas : ['LLM clasificó como no_pedido: Consulta de disponibilidad']
  lineas  : []
  confianza: 0
```

✅ El JSON `{"error": "no_pedido", ...}` se normaliza a `estado=ERROR + lineas=[] + confianza=0`. El campo `mensaje` del JSON del LLM se incluye en la alerta — el operador sabe qué clasificó el LLM.

---

## Guardia 4 · PN proveedor inventado

```
=== GUARDIA 4: PN proveedor inventado ===
  PN proveedor: None
  alertas     : ['PARSER: PN proveedor inventado por el LLM línea 1: VBX-COMP-9999-Z']

=== GUARDIA 4b: PN valido (no actua) ===
  PN proveedor: VBX-COMP-4471-B
  alertas     : []
```

✅ `VBX-COMP-9999-Z` (fuera de `PNS_VALIDOS`) se anula a `None` y genera alerta con prefijo `PARSER:`. `VBX-COMP-4471-B` (en `PNS_VALIDOS`) pasa sin modificación y sin alerta.

**Taxonomía de prefijos de alerta confirmada:**
- Sin prefijo → generada por el LLM (campo `alertas[]` en la respuesta JSON)
- `PARSER:` → generada por `_parsear_respuesta()` (guardia 4)
- `R0X:` → generada por `rules.py` (reglas de negocio)

Esta taxonomía permite en los logs y el dashboard distinguir en qué capa ocurrió cada alerta.

---

## Correcciones aplicadas

Ninguna corrección al código ni al tutorial fue necesaria.

---

## Resumen de validación

| Guardia | Estado | Resultado observado |
|---------|--------|---------------------|
| 1 — Strip fences | ✅ | COMPLETO, PN correcto |
| 2a — JSON truncado | ✅ | ValueError + posición |
| 2b — Respuesta vacía | ✅ | ValueError JSON_PARSE_ERROR |
| 2c — Solo texto | ✅ | ValueError JSON_PARSE_ERROR |
| 3 — no_pedido | ✅ | ERROR + lineas=[] + confianza=0 |
| 4a — PN inventado | ✅ | None + alerta PARSER: |
| 4b — PN válido | ✅ | PN conservado, sin alerta |
