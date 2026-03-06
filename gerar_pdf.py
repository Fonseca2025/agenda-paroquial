import json
from fpdf import FPDF

with open("eventos.json") as f:
    eventos = json.load(f)

pdf = FPDF()
pdf.add_page()

pdf.set_font("Arial", size=14)

pdf.cell(200,10,"Agenda Paroquial",ln=True)

for e in eventos:
    linha = f'{e["data"]} - {e.get("hora", "--:--")} - {e["evento"]} - {e["local"]}'
    pdf.cell(200,10,linha,ln=True)

pdf.output("agenda_paroquial.pdf")
