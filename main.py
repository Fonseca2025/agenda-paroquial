import json
import os
import telebot
from datetime import datetime
import pytz
from urllib.parse import quote # Importação necessária para formatar o texto para link
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton # Importação dos botões

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
        mensagem += f'{e.get("hora", "Horário a definir")} - {e["evento"]} ({e["local"]})\n'

# Verifica se há eventos para enviar
if mensagem != "📅 Agenda da Paróquia\n\n":
    
    # 1. Codifica a mensagem para funcionar dentro de um link (transforma espaços em %20, etc)
    texto_para_link = quote(mensagem)
    
    # 2. Cria o link com o número da Sarah e o texto da agenda
    link_whatsapp = f"https://wa.me/5538991467612?text={texto_para_link}"

    # 3. Cria o teclado inline (o botão)
    markup = InlineKeyboardMarkup()
    botao = InlineKeyboardButton(text="📲 Enviar para Sarah", url=link_whatsapp)
    markup.add(botao)

    # 4. Envia a mensagem com o botão (reply_markup)
    bot.send_message(CHAT_ID, mensagem, reply_markup=markup)
