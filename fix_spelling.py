import re

with open("TRANSCRIPCION_ROSELINE_9SEP2026.md", "r", encoding="utf-8") as f:
    text = f.read()

# Fix some of the obvious spelling errors mentioned in the review.
text = text.replace("salvadoréña", "salvadoreña")
text = text.replace("articrote", "artículos de")
text = text.replace("temenores", "de menores")
text = text.replace("insutupumentos", "instrumentos")
text = text.replace("silenciencia", "inocencia")
text = text.replace("burgado", "abogado")
text = text.replace("busgado", "juzgado")
text = text.replace("pelados", "llevados") # "viví a pelados delitos penales" -> "viendo apelados" maybe? or "llevados"
text = text.replace("promisionalba", "profesional")
text = text.replace("bogadio", "abogado")
text = text.replace("citron amigo", "centro, un amigo")
text = text.replace("chiquitice", "chico y dice")
text = text.replace("pato boy", "para tu boy") # "caminarnos a pato boy" maybe? let's leave it as "caminando para tu voy" -> walking to somewhere?
text = text.replace("sabaco", "abajo")
text = text.replace("flanancia", "flagrancia")
text = text.replace("hui", "hoy")
text = text.replace("burrador", "borrador")
text = text.replace("otato", "dato")
text = text.replace("Anaía", "fiscalía") # "delegación que te voy a ver. Yo le digo a la de Anaía." -> fiscalía / policía.
text = text.replace("fiel muy", "firme un")
text = text.replace("cofundamientos", "con fundamentos")
text = text.replace("agal esquema", "haga el esquema")
text = text.replace("venales", "penales")
text = text.replace("pelación", "apelación")
text = text.replace("extrantera", "entenderá")

with open("TRANSCRIPCION_ROSELINE_9SEP2026.md", "w", encoding="utf-8") as f:
    f.write(text)
