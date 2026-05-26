# Skill — Normalización de Purchase Orders VERBEX


## Cuándo activar esta skill

Cuando el mensaje contenga elementos que sugieran una Purchase Order: número de PO, referencias de Part Number, cantidades + unidades, fechas de entrega, mención de un programa aeronáutico (HX-7, ST-900, RT-55, VX-4) o de un cliente Tier 1 / OEM.

Si el texto NO parece una PO (consultas administrativas, facturación, saludos, preguntas sobre stock), devuelve:

```json
{ "error": "no_pedido", "mensaje": "descripción breve" }
```

---

## Pasos de extracción

### 1. Identificar `numero_pedido`

Busca patrones tipo `PO-YYYY-XXX-####`, `Purchase Order ###`, `Pedido ###`, `HELIONLINK-...`, `AOG-...`. Si hay sufijo "Rev. X" o "Amendment", inclúyelo en el número (ej. `PO-2025-STRA-0847-RevB`) y añade alerta de amendment.

### 2. Identificar cliente

Mapeo nombre → código ERP:

| Nombre detectado          | `codigo_erp` | `tier` | `programa_principal` |
| ------------------------- | -------------- | -------- | ---------------------- |
| Stratos Systems           | STRA-001       | TIER_1   | ST900                  |
| Kairos Aerospace          | KAIRO-001      | TIER_1   | HX7                    |
| Kairos Defense            | KAIRO-002      | TIER_1   | HX7                    |
| Helion Aircraft           | HELI-001       | OEM      | HX7                    |
| Vectair Industries Iberia | VECT-001       | OEM      | VX4                    |

Si el cliente NO está en la tabla, devuelve `"codigo_erp": null` (R07 lo flagueará).

### 3. Extraer líneas

Por cada PN cliente que aparezca:

- **`part_number_cliente`**: tal como aparece en el texto.
- **`part_number_proveedor`**: mapea contra la tabla "Equivalencias PN" (siguiente sección). Si no existe equivalencia, deja `null` y baja la confianza global.
- **`cantidad`**: número entero o decimal extraído del texto.
- **`unidad`**: una de `{EA, KG, ML, M2}`.
  - `EA` = "each" (unidades discretas)
  - `KG` = kilogramos
  - `ML` = metros lineales
  - `M2` = metros cuadrados
  - Si no se puede determinar, asume `EA` y añade alerta.
- **`fecha_entrega_requerida`**: en formato ISO `YYYY-MM-DD`.
  - `"15/09/2025"` → `"2025-09-15"`
  - `"September 30, 2025"` → `"2025-09-30"`
  - `"Need Date 15/09/25"` → `"2025-09-15"`
  - Si no figura → `null`.
- **`programa`**: `HX7` | `ST900` | `RT55` | `VX4` | `OTRO`. Inferir del PN proveedor (ver tabla catálogo) o del texto explícito.
- **`requiere_coc`, `requiere_easa_form1`**: mira la tabla "Catálogo VERBEX" por `part_number_proveedor`.
- **`prioridad`**: SIEMPRE `"NORMAL"` por defecto. R01/R02 las recalcula.

### 4. Detectar AOG

Si el texto contiene "AOG", "Aircraft on Ground", "inmovilizado", o urgencia extrema explícita, marca `"aog": true` y añade alerta descriptiva en `alertas[]`.

### 5. Calcular `confianza` (0.0–1.0)

| Rango                | Significado                                                    |
| -------------------- | -------------------------------------------------------------- |
| **0.95–1.00** | Texto estructurado (HelionLink CSV, PO con campos canónicos). |
| **0.80–0.95** | Texto libre estándar con todos los campos identificables.     |
| **0.60–0.80** | Algún PN desconocido o campo ambiguo.                         |
| **< 0.60**     | Varios campos faltantes o ambigüedades múltiples.            |

R03 usa el umbral 0.80 para escalar a `PARCIAL`.

---

## Equivalencias PN cliente → PN proveedor (tabla autoritativa)

```
ST9-HTP-RIB-047    →  VBX-COMP-4471-B  (Costilla HTP delantera, ST900)
ST9-HTP-RIB-048    →  VBX-COMP-4472-C  (Costilla HTP trasera, ST900)
HX7-FUS-PNL-331    →  VBX-COMP-3301-A  (Panel fuselaje central, HX7)
HX7-FUS-PNL-332    →  VBX-COMP-3302-A  (Panel fuselaje lateral, HX7)
HX7-BHD-332        →  VBX-COMP-3303-B  (Mamparo presurización, HX7)
ST9-LE-PNL-550     →  VBX-COMP-5501-A  (Borde de ataque ala, ST900)
HX7-ELV-220        →  VBX-COMP-2201-C  (Timón profundidad, RT55)
```

Si el PN cliente NO está en esta tabla, devuelve `"part_number_proveedor": null` y baja la confianza. R04 marcará el pedido como ERROR.

---

## Catálogo VERBEX (consulta `requiere_coc` / `requiere_easa_form1`)

| PN proveedor    | Programa | requiere_coc | requiere_easa_form1 |
| --------------- | -------- | ------------ | ------------------- |
| VBX-COMP-4471-B | ST900    | true         | false               |
| VBX-COMP-4472-C | ST900    | true         | false               |
| VBX-COMP-3301-A | HX7      | true         | true                |
| VBX-COMP-3302-A | HX7      | true         | true                |
| VBX-COMP-3303-B | HX7      | true         | true                |
| VBX-COMP-5501-A | ST900    | true         | false               |
| VBX-COMP-5502-A | ST900    | true         | false               |
| VBX-COMP-2201-C | RT55     | true         | true                |
| VBX-COMP-2202-C | RT55     | true         | true                |
| VBX-COMP-6601-A | HX7      | false        | false               |
| VBX-COMP-6602-A | HX7      | false        | false               |
| VBX-COMP-7701-B | ST900    | false        | false               |
| VBX-COMP-7702-B | HX7      | true         | false               |
| VBX-COMP-8801-A | ST900    | true         | false               |
| VBX-COMP-9901-A | OTRO     | false        | false               |
| VBX-COMP-9902-A | OTRO     | true         | false               |

---

## Schema JSON estricto

```json
{
  "numero_pedido": "string",
  "cliente": {
    "nombre": "string|null",
    "tier": "TIER_1|OEM|null",
    "codigo_erp": "string|null"
  },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "string",
      "part_number_proveedor": "string|null",
      "descripcion": "string",
      "cantidad": "number",
      "unidad": "EA|KG|ML|M2",
      "precio_unitario": null,
      "fecha_entrega_requerida": "YYYY-MM-DD|null",
      "programa": "HX7|ST900|RT55|VX4|OTRO",
      "prioridad": "NORMAL",
      "requiere_coc": "boolean",
      "requiere_easa_form1": "boolean"
    }
  ],
  "estado_normalizacion": "COMPLETO|PARCIAL|ERROR",
  "confianza": 0.97,
  "alertas": ["string"],
  "aog": false
}
```

---

## 5 Ejemplos few-shot

### Ejemplo 1 — PO estándar Stratos (email PDF)

**INPUT:**

```
Purchase Order PO-2025-STRA-0847. Stratos Systems.
Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.
Ref: ST-900 program. CoC required.
```

**OUTPUT:**

```json
{
  "numero_pedido": "PO-2025-STRA-0847",
  "cliente": { "nombre": "Stratos Systems", "tier": "TIER_1", "codigo_erp": "STRA-001" },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "ST9-HTP-RIB-047",
      "part_number_proveedor": "VBX-COMP-4471-B",
      "descripcion": "Costilla composite HTP sección delantera",
      "cantidad": 12,
      "unidad": "EA",
      "precio_unitario": null,
      "fecha_entrega_requerida": "2025-09-15",
      "programa": "ST900",
      "prioridad": "NORMAL",
      "requiere_coc": true,
      "requiere_easa_form1": false
    }
  ],
  "estado_normalizacion": "COMPLETO",
  "confianza": 0.97,
  "alertas": [],
  "aog": false
}
```

### Ejemplo 2 — HelionLink CSV (Kairos)

**INPUT:**

```
HELIONLINK|HX7-FUS-PNL-331|24|EA|2025-10-01|HX7|KAIRO-001|Normal
```

**OUTPUT:**

```json
{
  "numero_pedido": "HELIONLINK-HX7-FUS-PNL-331-2025-10-01",
  "cliente": { "nombre": "Kairos Aerospace", "tier": "TIER_1", "codigo_erp": "KAIRO-001" },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "HX7-FUS-PNL-331",
      "part_number_proveedor": "VBX-COMP-3301-A",
      "descripcion": "Panel fuselaje composite sección central HX-7",
      "cantidad": 24,
      "unidad": "EA",
      "precio_unitario": null,
      "fecha_entrega_requerida": "2025-10-01",
      "programa": "HX7",
      "prioridad": "NORMAL",
      "requiere_coc": true,
      "requiere_easa_form1": true
    }
  ],
  "estado_normalizacion": "COMPLETO",
  "confianza": 0.99,
  "alertas": [],
  "aog": false
}
```

### Ejemplo 3 — AOG alert

**INPUT:**

```
URGENT AOG - EC-MKL inmovilizado Aeropuerto Sevilla.
Necesitamos HX7-FUS-PNL-332 x2 inmediatamente.
Contacto: Juan García 654321098
```

**OUTPUT:**

```json
{
  "numero_pedido": "AOG-EC-MKL-PNL-332",
  "cliente": { "nombre": null, "tier": null, "codigo_erp": null },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "HX7-FUS-PNL-332",
      "part_number_proveedor": "VBX-COMP-3302-A",
      "descripcion": "Panel fuselaje composite sección lateral HX-7",
      "cantidad": 2,
      "unidad": "EA",
      "precio_unitario": null,
      "fecha_entrega_requerida": null,
      "programa": "HX7",
      "prioridad": "NORMAL",
      "requiere_coc": true,
      "requiere_easa_form1": true
    }
  ],
  "estado_normalizacion": "PARCIAL",
  "confianza": 0.85,
  "alertas": [
    "AOG detectado - verificar stock inmediatamente",
    "Cliente no identificado - contacto Juan García 654321098"
  ],
  "aog": true
}
```

### Ejemplo 4 — Amendment

**INPUT:**

```
PO-2025-STRA-0847 Rev. B. Amendment: cantidad línea 1 cambia de 12 a 8 EA.
Nueva Need Date: 30/09/2025.
```

**OUTPUT:**

```json
{
  "numero_pedido": "PO-2025-STRA-0847-RevB",
  "cliente": { "nombre": "Stratos Systems", "tier": "TIER_1", "codigo_erp": "STRA-001" },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "ST9-HTP-RIB-047",
      "part_number_proveedor": "VBX-COMP-4471-B",
      "descripcion": "Costilla composite HTP sección delantera",
      "cantidad": 8,
      "unidad": "EA",
      "precio_unitario": null,
      "fecha_entrega_requerida": "2025-09-30",
      "programa": "ST900",
      "prioridad": "NORMAL",
      "requiere_coc": true,
      "requiere_easa_form1": false
    }
  ],
  "estado_normalizacion": "COMPLETO",
  "confianza": 0.94,
  "alertas": [
    "Amendment - revisar PO original PO-2025-STRA-0847 Rev. A"
  ],
  "aog": false
}
```

### Ejemplo 5 — PN desconocido

**INPUT:**

```
Pedido 5521. Componente ST9-HTP-RIB-999 x4 EA. Entrega: 01/11/2025.
```

**OUTPUT:**

```json
{
  "numero_pedido": "5521",
  "cliente": { "nombre": null, "tier": null, "codigo_erp": null },
  "lineas": [
    {
      "linea_id": 1,
      "part_number_cliente": "ST9-HTP-RIB-999",
      "part_number_proveedor": null,
      "descripcion": "PN no encontrado en tabla de equivalencias",
      "cantidad": 4,
      "unidad": "EA",
      "precio_unitario": null,
      "fecha_entrega_requerida": "2025-11-01",
      "programa": "ST900",
      "prioridad": "NORMAL",
      "requiere_coc": false,
      "requiere_easa_form1": false
    }
  ],
  "estado_normalizacion": "PARCIAL",
  "confianza": 0.60,
  "alertas": [
    "PN cliente ST9-HTP-RIB-999 no encontrado en tabla de equivalencias",
    "Cliente no identificado"
  ],
  "aog": false
}
```

---

*VERBEX COMPOSITES · Agente normalizador de POs · Skill prompt + few-shot examples*
