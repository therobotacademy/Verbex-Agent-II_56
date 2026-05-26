# Presencia de conftest.py en la raíz → pytest añade esta carpeta a sys.path,
# de modo que `import rules` y `from verbex import ...` funcionan al correr
# `pytest tests/` desde la raíz del repo. No necesita contenido.
