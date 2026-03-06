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

bot = telebot.TeleBot(TOKEN)
tz = pytz.timezone("America/Sao_Paulo")
agora = datetime.now(tz)
hoje_str = agora.strftime("%Y-%m-%d")

# --- CARREGAR EVENTOS ---
try:
    with open("eventos.json", encoding='utf-8') as f:
        eventos = json.load(f)
except FileNotFoundError:
    print("Erro: Arquivo eventos.json não encontrado.")
    eventos = []

# --- FUNÇÕES AUXILIARES ---

def formatar_evento_texto(evento):
    """Formata o evento para texto (sem 'Horário a definir')."""
    hora = evento.get("hora")
    # Se tiver hora, mostra "19:00 - Evento". Se não, mostra só "Evento"
    if hora:
        return f'{hora} - {evento["evento"]} ({evento["local"]})'
    return f'{evento["evento"]} ({evento["local"]})'

def gerar_mensagem_periodo(tipo_periodo):
    """Gera o texto da agenda para Hoje, Semana ou Mês."""
    
    lista_mensagens = []
    titulo = ""
    
    # Define o intervalo de datas
    data_inicio = agora.date()
    data_fim = None
    
    if tipo_periodo == 'hoje':
        titulo = "📅 *Agenda de Hoje*"
        data_fim = data_inicio
    
    elif tipo_periodo == 'semana':
        titulo = "🗓 *Agenda Semanal*"
        data_fim = data_inicio + timedelta(days=7)
        
    elif tipo_periodo == 'mes':
        titulo = f"📊 *Agenda do Mês ({agora.strftime('%m/%Y')})*"
        # Vai até o último dia do mês (aproximação simples: 31 dias a frente ou fim do mês)
        proximo_mes = agora.replace(day=28) + timedelta(days=4)
        ultimo_dia_mes = proximo_mes - timedelta(days=proximo_mes.day)
        data_fim = ultimo_dia_mes.date()

    # Filtra os eventos
    tem_evento = False
    texto_final = titulo + "\n\n"
    
    for e in eventos:
        try:
            data_evento = datetime.strptime(e["data"], "%Y-%m-%d").date()
            
            if data_inicio <= data_evento <= data_fim:
                # Formata a data para dia/mês se não for agenda diária
                prefixo_data = ""
                if tipo_periodo != 'hoje':
                    prefixo_data = f"*{data_evento.strftime('%d/%m')}*: "
                
                texto_final += f"{prefixo_data}{formatar_evento_texto(e)}\n"
                tem_evento = True
        except ValueError:
            continue # Pula datas inválidas no json

    if tem_evento:
        return texto_final
    return None

# ==============================================================================
# 1. ENVIO DA AGENDA DO DIA (PRINCIPAL)
# ==============================================================================
msg_hoje = gerar_mensagem_periodo('hoje')

if msg_hoje:
    # Cria o botão para você encaminhar manualmente para a Sarah via WhatsApp Web/App
    texto_para_link = quote(msg_hoje.replace('*', '')) # Remove asteriscos para o link ficar limpo
    link_zap = f"https://wa.me/5538991467612?text={texto_para_link}"
    
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="📲 Abrir no WhatsApp (Sarah)", url=link_zap)
    markup.add(btn)
    
    bot.send_message(CHAT_ID, msg_hoje, parse_mode="Markdown", reply_markup=markup)
else:
    print("Sem eventos para hoje.")

# ==============================================================================
# 2. TESTES DE PERÍODO (SEMANAL E MENSAL)
# ==============================================================================

# Teste Semanal
msg_semana = gerar_mensagem_periodo('semana')
if msg_semana:
    bot.send_message(CHAT_ID, "--- TESTE SEMANAL ---\n" + msg_semana, parse_mode="Markdown")

# Teste Mensal
msg_mes = gerar_mensagem_periodo('mes')
if msg_mes:
    bot.send_message(CHAT_ID, "--- TESTE MENSAL ---\n" + msg_mes, parse_mode="Markdown")

# ==============================================================================
# 3. GERAÇÃO E ENVIO DE PDF
# ==============================================================================
print("Iniciando geração de PDF...")

# Importa o script gerar_pdf.py (isso executa o código que está nele)
try:
    import gerar_pdf 
    
    # Se o seu gerar_pdf.py tiver uma função específica, chame ela aqui. 
    # Ex: gerar_pdf.criar_arquivo()
    # Se ele roda direto ao importar, não precisa fazer nada além do import.

    nome_arquivo = "agenda.pdf" # Nome que o seu script gera

    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "rb") as doc:
            bot.send_document(CHAT_ID, doc, caption="📂 Arquivo PDF gerado")
        print("PDF enviado.")
    else:
        bot.send_message(CHAT_ID, "⚠️ O script rodou, mas o arquivo 'agenda.pdf' não foi encontrado.")

except ImportError:
    bot.send_message(CHAT_ID, "⚠️ Erro: Script 'gerar_pdf.py' não encontrado.")
except Exception as e:
    bot.send_message(CHAT_ID, f"❌ Erro ao processar PDF: {str(e)}")
