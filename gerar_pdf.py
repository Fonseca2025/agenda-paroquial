import json
from fpdf import FPDF
from datetime import datetime
import pytz

def gerar():
    # Carrega os eventos
    with open("eventos.json", encoding="utf-8") as f:
        eventos = json.load(f)

    # Configura o fuso horário para pegar o mês correto
    tz = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(tz)
    mes_atual = agora.month
    ano_atual = agora.year

    # Inicializa o PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título com o Mês e Ano
    titulo = f"Agenda Paroquial - {agora.strftime('%m/%Y')}"
    pdf.cell(200, 10, titulo, ln=True, align="C")
    pdf.ln(5) # Pula uma linha

    tem_evento = False

    # Filtra os eventos do mês
    for e in eventos:
        try:
            # Converte a data do JSON para verificar o mês
            data_evento = datetime.strptime(e["data"], "%Y-%m-%d")
            
            if data_evento.month == mes_atual and data_evento.year == ano_atual:
                # Formata para o padrão brasileiro DD/MM/YYYY
                data_br = data_evento.strftime("%d/%m/%Y")
                hora = e.get("hora", "--:--")
                
                linha = f'{data_br} - {hora} - {e["evento"]} - {e["local"]}'
                
                # Tratamento para evitar erro com acentos (FPDF usa latin-1)
                linha = linha.encode('latin-1', 'replace').decode('latin-1')
                
                pdf.cell(200, 10, linha, ln=True)
                tem_evento = True
        except ValueError:
            continue # Pula se houver erro na data

    # Se não tiver nenhum evento no mês
    if not tem_evento:
        pdf.cell(200, 10, "Nenhum evento cadastrado para este mes.", ln=True)

    # Salva o arquivo
    pdf.output("agenda_paroquial.pdf")

# Se o arquivo for rodado direto, ele executa a função
if __name__ == "__main__":
    gerar()
