from dotenv import load_dotenv
load_dotenv()
from verbex import llm

# A1: el system prompt (PERSONA.md + SKILL.md concatenados)
sp = llm.cargar_system_prompt()
print(f"System prompt: {len(sp)} caracteres, {len(sp.splitlines())} líneas")
print("──── Primeras 5 líneas ────")
for line in sp.splitlines()[:5]:
    print(" ", line)

# A2: el mensaje de usuario que recibe Claude
msgs = llm.build_messages("Purchase Order PO-TEST. Stratos Systems. Part: ST9-HTP-RIB-047, 5 EA.")
print("\n──── Mensaje de usuario ────")
print(f"  role   : {msgs[0]['role']}")
print(f"  content: {msgs[0]['content'][:120]}…")
