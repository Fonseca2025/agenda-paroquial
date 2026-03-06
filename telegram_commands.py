import requests

TOKEN = "SEU_TOKEN"

def ler_mensagens(update_id=None):

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    params = {"timeout": 100}

    if update_id:
        params["offset"] = update_id

    response = requests.get(url, params=params)

    return response.json()
