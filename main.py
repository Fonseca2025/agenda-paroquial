import json
import os
import telebot
from datetime import datetime, timedelta
import pytz
from urllib.parse import quote
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURAÇÕES ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
NUMERO_SARAH = "5538991467612"

bot = telebot.TeleBot(TOKEN)
tz = pytz.timezone("America/Sao_Paulo")
agora = datetime.now(tz)

# --- CARREGAR EVENTOS ---
try:
    with open("eventos.json", encoding='utf-8') as f:
        eventos = json.load(f)
except FileNotFoundError:
    print("Erro: Arquivo eventos.json não encontrado.")
    eventos = []

# --- FUNÇÕES AUXILIARES ---

def formatar_evento_texto(evento):
    """Formata o evento para texto simples."""
    hora = evento.get("hora")
    if hora:
        return f'{hora} - {evento["evento"]} ({evento["local"]})'
    return f'{evento["evento"]} ({evento["local"]})'

def criar_botao_whatsapp(texto_mensagem):
    """Cria o teclado inline com o botão para o WhatsApp."""
    # Codifica o texto para ser aceito na URL (espaços viram %20)
    texto_encoded = quote(texto_mensagem)
    link = f"https://wa.me/{NUMERO_SARAH}?text={texto_encoded}"
    
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="📲 Enviar para Sarah", url=link)
    markup.add(btn)
    return markup

def gerar_mensagem_periodo(tipo_periodo):
    """Gera o texto da agenda baseada no filtro (hoje, semana, mes)."""
    
    # Configurações de datas e títulos
    data_inicio = agora.date()
    data_fim = None
    titulo = ""
    
    if tipo_periodo == 'hoje':
        titulo = "📅 Agenda de Hoje"
        data_fim = data_inicio
    
    elif tipo_periodo == 'semana':
        titulo = "🗓 Agenda Semanal"
        data_fim = data_inicio + timedelta(days=7)
        
    elif tipo_periodo == 'mes':
        titulo = f"📊 Agenda do Mês ({agora.strftime('%m/%Y')})"
        # Lógica para pegar até o fim do mês
        proximo_mes = agora.replace(day=28) + timedelta(days=4)
        ultimo_dia_mes = proximo_mes - timedelta(days=proximo_mes.day)
        data_fim = ultimo_dia_mes.date()

    # Construção do texto
    texto_final = titulo + "\n\n"
    tem_evento = False
    
    for e in eventos:
        try:
            data_evento = datetime.strptime(e["data"], "%Y-%m-%d").date()
            
            if data_inicio <= data_evento <= data_fim:
                prefixo_data = ""
                # Se não for agenda diária, mostra a data antes do evento
                if tipo_periodo != 'hoje':
                    prefixo_data = f"{data_evento.strftime('%d/%m')}: "
                
                texto_final += f"{prefixo_data}{formatar_evento_texto(e)}\n"
                tem_evento = True
        except ValueError:
            continue

    if tem_evento:
        return texto_final
    return None

# ==============================================================================
# 1. ENVIO DA AGENDA DO DIA
# ==============================================================================
msg_hoje = gerar_mensagem_periodo('hoje')

if msg_hoje:
    markup = criar_botao_whatsapp(msg_hoje)
    bot.send_message(CHAT_ID, msg_hoje, reply_markup=markup)
else:
    print("Sem eventos para hoje.")

# ==============================================================================
# 2. ENVIO DA AGENDA SEMANAL
# ==============================================================================
msg_semana = gerar_mensagem_periodo('semana')

if msg_semana:
    markup = criar_botao_whatsapp(msg_semana)
    # Adiciono um cabeçalho extra para você saber que é o teste semanal no Telegram
    bot.send_message(CHAT_ID, "--- VISUALIZAÇÃO SEMANAL ---", disable_notification=True) 
    bot.send_message(CHAT_ID, msg_semana, reply_markup=markup)

# ==============================================================================
# 3. ENVIO DA AGENDA MENSAL
# ==============================================================================
msg_mes = gerar_mensagem_periodo('mes')

if msg_mes:
    markup = criar_botao_whatsapp(msg_mes)
    bot.send_message(CHAT_ID, "--- VISUALIZAÇÃO MENSAL ---", disable_notification=True)
    bot.send_message(CHAT_ID, msg_mes, reply_markup=markup)

# ==============================================================================
# 4. ENVIO DO PDF
# ==============================================================================
print("Verificando PDF...")

try:
    import gerar_pdf 
    nome_arquivo = "agenda.pdf" 

    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "rb") as doc:
            bot.send_document(CHAT_ID, doc, caption="📂 Arquivo PDF gerado")
        print("PDF enviado.")
    else:
        # Apenas loga no console, não manda msg de erro para não poluir o chat
        print("Arquivo PDF não encontrado.")

except Exception as e:
    print(f"Erro no módulo PDF: {e}")
