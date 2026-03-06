import json
from ics import Calendar, Event

with open("eventos.json") as f:
    eventos = json.load(f)

c = Calendar()

for item in eventos:
    e = Event()
    e.name = item["evento"]
    e.begin = item["data"] + " " + item.get("hora", "08:00:00")
    e.location = item["local"]
    c.events.add(e)

with open("agenda_paroquia.ics", "w") as f:
    f.writelines(c)
