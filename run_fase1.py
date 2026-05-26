import json
from dotenv import load_dotenv
load_dotenv()                  # carga .env antes de cualquier import que lea credenciales
from verbex import llm, observability
import rules

observability.setup_logging()

TEXTO_PO = (
    "Purchase Order PO-2025-STRA-0847. Stratos Systems.\n"
    "Part: ST9-HTP-RIB-047, Qty: 12 EA, Need Date: 15/09/2025.\n"
    "Ref: ST-900 program. CoC required."
)

print("\n── Texto original ──────────────────────────────")
print(TEXTO_PO)

print("\n── Tras el LLM (claude-sonnet) ─────────────────")
po = llm.normalizar(TEXTO_PO)
print(json.dumps(po, indent=2, ensure_ascii=False))

print("\n── Tras las reglas R01–R09 ─────────────────────")
po = rules.aplicar_reglas(po)
print(f"  estado      : {po['estado_normalizacion']}")
print(f"  prioridad   : {po['prioridad_calculada']}")
print(f"  confianza   : {po['confianza']}")
print(f"  alertas     : {po['alertas']}")
print(f"  doc línea 1 : {po['lineas'][0].get('doc_requerida')}")
