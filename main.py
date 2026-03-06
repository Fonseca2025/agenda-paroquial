import json
import os
import telebot
from datetime import datetime
import pytz

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TOKEN)

tz = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(tz).strftime("%Y-%m-%d")

with open("eventos.json") as f:
    eventos = json.load(f)

mensagem = "📅 Agenda da Paróquia\n\n"

for e in eventos:
    if e["data"] == hoje:
        mensagem += f'{e["hora"]} - {e["evento"]} ({e["local"]})\n'

if mensagem != "📅 Agenda da Paróquia\n\n":
    bot.send_message(CHAT_ID, mensagem)
