import json
import os
import telebot
from datetime import datetime
import pytz
from urllib.parse import quote
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        hora = e.get("hora")
        
        # Se existir horário preenchido no JSON
        if hora:
            mensagem += f'{hora} - {e["evento"]} ({e["local"]})\n'
        # Se não tiver horário, coloca apenas o nome do evento e local
        else:
            mensagem += f'{e["evento"]} ({e["local"]})\n'

# Verifica se a mensagem tem conteúdo além do cabeçalho
if mensagem != "📅 Agenda da Paróquia\n\n":
    
    # Prepara o link para o botão do WhatsApp
    texto_para_link = quote(mensagem)
    link_whatsapp = f"https://wa.me/5538991467612?text={texto_para_link}"

    # Cria o botão
    markup = InlineKeyboardMarkup()
    botao = InlineKeyboardButton(text="📲 Enviar para Sarah", url=link_whatsapp)
    markup.add(botao)

    # Envia a mensagem
    bot.send_message(CHAT_ID, mensagem, reply_markup=markup)
