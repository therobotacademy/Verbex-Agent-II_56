from dotenv import load_dotenv
load_dotenv()
import os
import urllib.request, json

token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not token:
    print("ERROR: TELEGRAM_BOT_TOKEN no está en .env")
else:
    url = f"https://api.telegram.org/bot{token}/getMe"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())
    print(f"Bot conectado: @{data['result']['username']}")
    print(f"Nombre      : {data['result']['first_name']}")
    