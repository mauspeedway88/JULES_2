import json
import random
import unicodedata
import re
import itertools

def remove_accents(input_str):
    return "".join(c for c in unicodedata.normalize('NFKD', input_str) if not unicodedata.combining(c))

stop_words = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero",
    "porque", "para", "por", "en", "con", "sin", "sobre", "entre", "hasta",
    "desde", "hacia", "como", "es", "son", "se", "del", "al", "su", "sus",
    "este", "esta", "estos", "estas", "que", "lo", "mas", "muy", "tiene",
    "tienen", "forma", "forman", "parte", "gran", "mayor", "menor", "donde",
    "cuando", "ha", "han", "sido", "esta", "estan", "puede", "pueden", "cuyo",
    "cuya", "fue", "este", "esta", "esto"
}

def extract_keywords(text):
    words = re.findall(r'\b[a-záéíóúñ]+\b', text.lower())
    valid_words = [remove_accents(w) for w in words if w not in stop_words and len(w) > 4]

    unique_words = list(dict.fromkeys(valid_words))

    # We need 4 to 6 keywords
    if len(unique_words) >= 6:
        return random.sample(unique_words, random.randint(4, 6))
    elif len(unique_words) >= 4:
        return unique_words
    else:
        fallback = ["geografia", "planeta", "naturaleza", "estudio", "ciencia", "tierra"]
        for fb in fallback:
            if fb not in unique_words:
                unique_words.append(fb)
            if len(unique_words) >= 4:
                break
        return unique_words[:6]

categories = {
    "montanas": {
        "conceptos": [
            ("La montaña", "es una inmensa elevación natural del relieve geográfico terrestre"),
            ("El pico", "es la cumbre más elevada de una cadena montañosa"),
            ("La cordillera", "es una extensa sucesión geológica de enormes montañas enlazadas"),
            ("La sierra", "es un prominente subconjunto montañoso dentro de extensa cordillera"),
            ("El macizo", "es una masiva sección de la corteza delimitada topográficamente"),
            ("La colina", "es una suave elevación de terreno de menor altura"),
            ("El cerro", "es una eminencia topográfica aislada en regiones mayormente planas"),
            ("El nevado", "es una altísima cumbre cubierta constantemente por nieves perpetuas"),
            ("El promontorio", "es una rocosa elevación masiva que sobresale del relieve"),
            ("El farallón", "es una altísima pared rocosa cortada casi en vertical")
        ],
        "procesos": [
            "Su origen obedece al prolongado choque continuo de placas.",
            "Fue modelada lentamente por la implacable acción atmosférica natural.",
            "Este territorio fue transformado por constante erosión hídrica milenaria.",
            "Se formó debido a intensa y prolongada actividad geomorfológica.",
            "Su estructura cambió por gigantesca presión tectónica subterránea acumulada."
        ],
        "importancias": [
            "Alberga diversidad biológica extraordinaria protegiendo numerosas especies salvajes endémicas.",
            "Cumple un papel fundamental regulando el clima regional adyacente.",
            "Representa abundante reserva natural proporcionando indispensables recursos hídricos minerales.",
            "Evita avance descontrolado de erosión protegiendo valiosos suelos productivos.",
            "Proporciona ecosistema equilibrado para óptimo desarrollo de floras locales."
        ],
        "contextos": [
            "Su constante estudio científico revela antiguos invaluables secretos terrestres.",
            "Comprender su geografía permite organizar eficientemente grandes asentamientos modernos.",
            "Proteger estas áreas naturales garantiza firmemente mejor futuro ecológico.",
            "El conocimiento profundo de estructura evita devastadores desastres naturales.",
            "Analizar este territorio fomenta necesario y urgente respeto medioambiental."
        ]
    },
    "rios": {
        "conceptos": [
            ("El río", "es un caudaloso y continuo flujo hídrico dulce superficial"),
            ("El arroyo", "es una breve corriente natural fluvial de constante caudal"),
            ("La cuenca", "es un extenso territorio que drena hacia un cauce"),
            ("El delta", "es un amplio terreno fértil ubicado en la desembocadura"),
            ("El estuario", "es la zona acuática donde un caudal desemboca directamente"),
            ("El acuífero", "es una masiva formación subterránea que almacena agua filtrada"),
            ("El manantial", "es una hermosa fuente natural donde brota agua subterránea"),
            ("La cascada", "es una espectacular caída vertical de abundante caudal acuático"),
            ("El meandro", "es una pronunciada curva sinuosa formada en curso fluvial"),
            ("El lago", "es una profunda masa continental de agua dulce estancada")
        ],
        "procesos": [
            "Su cauce fue trazado por incesante erosión hídrica milenaria.",
            "Se alimenta constantemente de intensas precipitaciones lluviosas estacionales periódicas.",
            "Su caudal nace del continuo deshielo de cumbres nevadas.",
            "Fluye ininterrumpidamente superando los múltiples y diversos obstáculos topográficos.",
            "Su volumen acuático varía según cambiantes ciclos climáticos globales."
        ],
        "importancias": [
            "Es fuente hídrica esencial para garantizar vital supervivencia humana.",
            "Mantiene frágil equilibrio ecológico sustentando variada y rica biodiversidad.",
            "Facilita irrigación natural de enormes territorios agrícolas altamente productivos.",
            "Modela constantemente paisaje geográfico depositando invaluables sedimentos altamente nutritivos.",
            "Sirve como corredor biológico indispensable para migración de especies."
        ],
        "contextos": [
            "La preservación de recursos hídricos asegura futura sostenibilidad ambiental.",
            "El riguroso análisis científico revela importantes datos climáticos históricos.",
            "Evitar su preocupante contaminación resulta prioritario para ecosistemas frágiles.",
            "Estudiar comportamiento geográfico previene catastróficas inundaciones en zonas pobladas.",
            "Su conocimiento profundo es fundamental diseñando óptimas infraestructuras hidráulicas."
        ]
    },
    "oceanos": {
        "conceptos": [
            ("El océano", "es una inmensa e insondable masa de agua salada"),
            ("El mar", "es una extensa porción acuática salada de tamaño menor"),
            ("El golfo", "es una profunda entrada oceánica rodeada parcialmente por territorios"),
            ("La bahía", "es una entrada acuática costera reducida ideal para puertos"),
            ("El estrecho", "es un angosto paso marítimo conectando dos grandes océanos"),
            ("El arrecife", "es una compleja estructura rocosa submarina habitada por corales"),
            ("La península", "es una masiva extensión de tierra rodeada por mar"),
            ("El archipiélago", "es un conjunto disperso de islas agrupadas en mares"),
            ("La fosa", "es una profunda y oscura depresión del fondo marino"),
            ("La marea", "es un periódico movimiento vertical de gigantescas masas oceánicas")
        ],
        "procesos": [
            "Se originó tras paulatina acumulación de precipitaciones globales milenarias.",
            "Su dinámica está dominada por fuerza gravitatoria de astros.",
            "Sus corrientes fueron moldeadas por la constante rotación terrestre.",
            "Fue transformado por violentas y colosales erupciones volcánicas submarinas.",
            "Su fondo se expande debido al continuo movimiento tectónico."
        ],
        "importancias": [
            "Regula el clima mundial absorbiendo enormes cantidades de calor.",
            "Representa hábitat marino más extenso para incontables formas vivientes.",
            "Produce gran parte del oxígeno terrestre gracias al fitoplancton.",
            "Proporciona recursos alimenticios vitales para numerosas poblaciones humanas costeras.",
            "Facilita comercio internacional conectando distantes continentes de forma económica."
        ],
        "contextos": [
            "Explorar profundidades marinas sigue siendo gigantesco reto científico moderno.",
            "Proteger esta inmensidad azul garantiza delicado y frágil equilibrio.",
            "Comprender dinámica marítima es absolutamente crucial enfrentando calentamiento global.",
            "Su estudio continuo aporta invaluables respuestas sobre origen vital.",
            "Conservar ecosistemas marinos asegura supervivencia de maravillosas especies acuáticas."
        ]
    },
    "desiertos": {
        "conceptos": [
            ("El desierto", "es una extensa región árida con bajísimas precipitaciones anuales"),
            ("La estepa", "es un vasto territorio árido con escasa vegetación resistente"),
            ("El oasis", "es un aislado y verde paraje situado dentro desiertos"),
            ("La duna", "es una colina arenosa suavemente moldeada por fuerza eólica"),
            ("El cañón", "es un valle profundo excavado por erosiones hídricas milenarias"),
            ("La llanura", "es un plano territorio sin elevaciones topográficas realmente significativas"),
            ("El páramo", "es un ecosistema andino frío constantemente cubierto de niebla"),
            ("La sabana", "es una tropical planicie cubierta predominantemente por altas hierbas"),
            ("El salar", "es un brillante depósito cristalino de sal antigua evaporada"),
            ("El barranco", "es un vertical precipicio provocado por históricos hundimientos terrestres")
        ],
        "procesos": [
            "Su sequedad resulta de constante y alta presión atmosférica.",
            "Fue desertificado debido a drásticos cambios climáticos terrestres prehistóricos.",
            "La falta de lluvia moldeó un paisaje severamente agreste.",
            "La constante fuerza del viento esculpió sus curiosas formaciones.",
            "Las drásticas variaciones térmicas diarias fracturan sus rocas superficiales."
        ],
        "importancias": [
            "Alberga ecosistema único con especies endémicas asombrosamente adaptadas climáticamente.",
            "Contiene inmensos depósitos minerales subterráneos de altísimo valor comercial.",
            "Representa fascinante laboratorio natural ideal estudiando extremas adaptaciones biológicas.",
            "Mantiene frágil equilibrio hídrico vital mediante profundos acuíferos subterráneos.",
            "Sirve como perfecto entorno para estudiar directa radiación solar."
        ],
        "contextos": [
            "Investigar ambiente extremo permite comprender creciente y alarmante desertificación.",
            "Su atenta preservación previene pérdida acelerada de insustituible biodiversidad.",
            "Estudiar organismos resistentes inspira formidables e innovadores desarrollos tecnológicos.",
            "Valorar aparente desolación ayuda protegiendo ecosistemas sumamente vulnerables modernos.",
            "Conocer su geomorfología es indispensable prediciendo drásticos cambios climáticos."
        ]
    },
    "placas": {
        "conceptos": [
            ("La placa", "es un inmenso fragmento rígido de la corteza terrestre"),
            ("La falla", "es una extensa fractura estructural profunda de nuestro planeta"),
            ("El borde", "es la zona destructiva donde dos placas colisionan brutalmente"),
            ("El límite", "es el área constructiva donde placas forman nueva corteza"),
            ("La dorsal", "es una inmensa cordillera formada al separarse placas marinas"),
            ("La subducción", "es un violento proceso geológico donde una placa subduce"),
            ("La litosfera", "es la capa exterior terrestre formada por rocas sólidas"),
            ("La astenosfera", "es la capa plástica del manto donde flotan placas"),
            ("La zanja", "es una hondísima zanja topográfica creada por intensas subducciones"),
            ("El rift", "es una profunda grieta continental originada por fuerzas separadoras")
        ],
        "procesos": [
            "Su desplazamiento resulta de intensas corrientes conectivas del manto.",
            "Acumula peligrosa tensión elástica durante largos e impredecibles periodos.",
            "Su constante fricción genera altísimas presiones tectónicas subterráneas destructivas.",
            "Modifica incesantemente la distribución continental mediante un proceso milenario.",
            "Destruye y crea constante corteza oceánica equilibrando volumen terrestre."
        ],
        "importancias": [
            "Es principal motor responsable construyendo gigantescas cadenas montañosas imponentes.",
            "Genera continua renovación química impulsando ciclo fundamental de rocas.",
            "Condiciona permanentemente distribución mundial de inmensos y vitales minerales.",
            "Su actividad volcánica formó la primitiva atmósfera y océanos.",
            "Mantiene vital dinámica térmica evitando rápido enfriamiento del planeta."
        ],
        "contextos": [
            "Comprender funcionamiento es totalmente vital intentando predecir sismos destructivos.",
            "El análisis de bordes convergentes localiza importantes yacimientos metálicos.",
            "Su estudio constante ayuda mitigando inmensos y severos riesgos.",
            "La investigación detallada protege cruciales e indispensables infraestructuras urbanas.",
            "Enseñar esta dinámica fomenta profunda conciencia frente fuerzas naturales."
        ]
    },
    "sismos": {
        "conceptos": [
            ("El sismo", "es una brusca y destructiva vibración de corteza superficial"),
            ("El terremoto", "es un violento movimiento telúrico generado por fuerzas subterráneas"),
            ("El tsunami", "es una colosal ola oceánica producida por inmenso terremoto"),
            ("El epicentro", "es el punto superficial ubicado sobre la liberación energética"),
            ("El hipocentro", "es el foco subterráneo profundo donde origina fractura rocosa"),
            ("La onda", "es la veloz energía propagada por el interior terrestre"),
            ("El magma", "es una incandescente espesa masa de roca interna fundida"),
            ("El volcán", "es una extensa elevación volcánica creada por flujos basálticos"),
            ("El cráter", "es la abertura geológica donde emergen materiales volcánicos ardientes"),
            ("La caldera", "es una gigantesca depresión hundida formada tras erupciones colosales")
        ],
        "procesos": [
            "Se produce por violenta y súbita liberación energética subterránea.",
            "Propaga intensas ondas elásticas deformando severamente el suelo circundante.",
            "Transforma bruscamente topografía local abriendo profundas grietas superficiales peligrosas.",
            "Desencadena aterradores deslizamientos masivos alterando rápidamente el complejo relieve.",
            "Expulsa violentamente inmensas nubes volcánicas modificando drásticamente clima atmosférico."
        ],
        "importancias": [
            "Libera inmensa presión interna terrestre manteniendo su equilibrio geológico.",
            "Las erupciones aportan valiosos minerales generando terrenos sumamente fértiles.",
            "Genera abundante energía geotérmica renovable útil para usos humanos.",
            "Evidencia la fascinante e incesante actividad térmica interna terrestre.",
            "Crea continuamente fascinantes formaciones enriqueciendo majestuoso paisaje natural planetario."
        ],
        "contextos": [
            "Implementar rigurosas normas constructivas es indispensable salvando vidas humanas.",
            "Monitoreo científico ininterrumpido permite emitir eficaces alertas tempranas preventivas.",
            "El riguroso estudio vulcanológico ayuda protegiendo comunidades rurales cercanas.",
            "Comprender impredecibles fenómenos fomenta valiosas estrategias de prevención comunitaria.",
            "Analizar detalladamente su registro histórico mejora complejos mapas modernos."
        ]
    },
    "glaciares": {
        "conceptos": [
            ("El glaciar", "es una pesada masa móvil de hielo acumulada naturalmente"),
            ("El iceberg", "es un colosal bloque de hielo flotando en mar"),
            ("La morrena", "es una cordillera de sedimentos rocosos arrastrados por glaciares"),
            ("El fiordo", "es un estrecho valle costero inundado excavado por hielos"),
            ("La tundra", "es un extenso ecosistema helado con subsuelos permanentemente congelados"),
            ("El permafrost", "es la dura capa de suelo subterráneo permanentemente congelada"),
            ("La banquisa", "es la extensa capa superficial de hielo oceánico polar"),
            ("El valle", "es una enorme depresión topográfica geológica moldeada por hielo"),
            ("El circo", "es una profunda cuenca rocosa donde se acumula nieve"),
            ("El casquete", "es una continental capa de hielo cubriendo vastas regiones")
        ],
        "procesos": [
            "Se formó por incesante compactación de nieves durante milenios.",
            "Avanza lentamente debido a implacable fuerza de gravedad terrestre.",
            "Retrocede aceleradamente sufriendo derretimientos masivos por peligroso calentamiento climático.",
            "Talla profundamente rocas subyacentes modificando el duro relieve montañoso.",
            "Libera gradualmente purísima agua dulce alimentando numerosos cauces fluviales."
        ],
        "importancias": [
            "Contiene mayor e invaluable reserva mundial de agua dulce.",
            "Actúa como vital regulador del intrincado clima y temperaturas.",
            "Su enorme superficie blanca refleja poderosamente intensa radiación solar.",
            "Sustenta y protege ecosistemas fríos asombrosamente únicos y adaptados.",
            "Modela constantemente espectaculares paisajes geográficos de altísimo valor escénico."
        ],
        "contextos": [
            "Medir su rápido derretimiento sirve como alarmante indicador ecológico.",
            "Proteger este inmenso hielo impide futuro aumento oceánico destructivo.",
            "Su estudio detallado ayuda inmensamente comprendiendo pasadas eras glaciares.",
            "Conservar asombroso ambiente garantiza indispensable futuro hídrico mundial seguro.",
            "Investigar profundidades congeladas revela antiquísimos secretos biológicos evolutivos sorprendentes."
        ]
    },
    "valles": {
        "conceptos": [
            ("El valle", "es una extensa llanura geográficamente deprimida flanqueada por cumbres"),
            ("La depresión", "es una vastísima cóncava zona topográfica bajo nivel marino"),
            ("El altiplano", "es una enorme planicie situada a gran altura cordillerana"),
            ("La vega", "es un terreno bajo húmedo irrigado por río cercano"),
            ("El prado", "es una extensa pradera verde cubierta de pastos frescos"),
            ("La pampa", "es una gigantesca región llana cubierta completamente por hierbas"),
            ("La selva", "es un denso bosque tropical poseedor de biodiversidad exuberante"),
            ("El bosque", "es un extenso ecosistema dominado por altísimos árboles majestuosos"),
            ("La marisma", "es un pantanoso terreno costero inundado por mareas marítimas"),
            ("El manglar", "es un denso bosque costero dominado por árboles acuáticos")
        ],
        "procesos": [
            "Fue rellenado lentamente a través de incesante acumulación hídrica.",
            "Se originó tras colapso topográfico producido por fallas tectónicas.",
            "Es constantemente inundado por regulares y abundantes lluvias tropicales.",
            "Su relieve fue suavizado por larguísima y constante erosión.",
            "El continuo depósito fluvial formó estas extensas llanuras productivas."
        ],
        "importancias": [
            "Ofrece terrenos asombrosamente fértiles ideales para intensivo desarrollo agrícola.",
            "Facilita construcción de grandes y modernas infraestructuras urbanas viales.",
            "Concentra gigantesca y valiosa densidad biomasa productiva y salvaje.",
            "Filtra y purifica naturalmente enormes cantidades de aguas dulces.",
            "Actúa como gigante pulmón verde fijando muchísimo carbono perjudicial."
        ],
        "contextos": [
            "Su óptima y equilibrada gestión garantiza necesaria seguridad alimentaria.",
            "Evitar destructiva deforestación ayuda inmensamente combatir perjudicial cambio climático.",
            "Planificar inteligentemente uso evita catastrófico e irreversible agotamiento edáfico.",
            "Proteger celosamente su intrincada biodiversidad mantiene ecosistemas únicos irrepetibles.",
            "Conservar intacto ecosistema asegura pervivencia de incontables especies endémicas."
        ]
    }
}

def generate_concepts():
    items = []
    index = 1

    for cat_name, data in categories.items():
        conceptos = data["conceptos"]
        procesos = data["procesos"]
        importancias = data["importancias"]
        contextos = data["contextos"]

        all_combinations = list(itertools.product(conceptos, procesos, importancias, contextos))
        random.seed(42 + len(cat_name))
        random.shuffle(all_combinations)

        # Take up to 95 to get around 760 items
        selected_combinations = all_combinations[:95]

        for idx, (concepto_tuple, proceso, importancia, contexto) in enumerate(selected_combinations):
            concepto_name, definicion = concepto_tuple

            base_response = f"{concepto_name} {definicion}. {proceso} {importancia} {contexto}"

            # Verify length
            words = base_response.split()
            if len(words) < 35:
                # Append a generic padding phrase if somehow it's too short
                base_response += " Representa una valiosa maravilla."
                words = base_response.split()
            if len(words) > 50:
                # Remove extra words from the end and add a period
                base_response = " ".join(words[:50])
                if not base_response.endswith("."):
                    base_response += "."

            intent_id = f"geografia_fisica_{cat_name}_{index:03d}"
            keywords = extract_keywords(base_response)

            item = {
                "intent_id": intent_id.lower(),
                "keywords": keywords,
                "base_response": base_response
            }
            items.append(item)
            index += 1

            if len(items) >= 750:
                break
        if len(items) >= 750:
            break

    return items

def main():
    items = generate_concepts()
    with open("MM_brain_56.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
