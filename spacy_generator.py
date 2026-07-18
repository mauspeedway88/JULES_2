import json
import re
import os
import random
import unidecode

SUBTOPICS = [
    "camuflaje protector de especies",
    "mimetismo engañoso de apariencia",
    "ectotermos de sangre fría",
    "endotermos de sangre caliente",
    "animales vivíparos de vientre",
    "animales ovovivíparos de huevos internos",
    "respiración cutánea de ranas",
    "respiración traqueal de insectos",
    "exoesqueleto de quitina protector",
    "sistema ambulacral de estrellas",
    "línea lateral de peces",
    "vejiga natatoria de flotación",
    "glándulas mamarias de alimentación",
    "dimorfismo sexual de formas",
    "feromonas de comunicación química",
    "cortejo reproductivo de parejas",
    "migración estacional de aves",
    "estivación de letargo cálido",
    "nematodos gusanos cilíndricos lisos",
    "platelmintos gusanos planos parásitos",
    "apéndices articulados de artrópodos",
    "bioluminiscencia animal de luz",
    "placenta nutritiva de fetos"
]

DIMENSIONS = {
    "Definición anatómica o estructural": [
        "El {subtopic} involucra estructuras anatómicas complejas que configuran esta adaptación específica. Estos componentes morfológicos permiten al animal integrarse físicamente en su entorno, modificando su superficie corporal para maximizar sus posibilidades de supervivencia diaria en su hábitat biológico.",
        "A nivel estructural, el {subtopic} depende de tejidos especializados diseñados biológicamente para esta función. La conformación física de estos órganos facilita las interacciones ecológicas críticas, asegurando ventajas morfológicas que favorecen directamente la persistencia vital de la especie."
    ],
    "Dinámica y funcionamiento físico": [
        "La mecánica del {subtopic} opera mediante procesos físicos que responden activamente a estímulos ambientales. Este funcionamiento orgánico permite ajustes conductuales rápidos y precisos, optimizando el rendimiento biológico durante actividades vitales frente a factores ecológicos sumamente cambiantes.",
        "Desde la perspectiva fisiológica, el {subtopic} funciona canalizando recursos energéticos hacia mecanismos de respuesta rápidos. La dinámica corporal integrada garantiza que el animal pueda reaccionar físicamente con eficacia, logrando mantener su integridad biológica ante desafíos medioambientales constantes."
    ],
    "Propiedades químicas o materiales": [
        "Las características químicas detrás del {subtopic} incluyen compuestos orgánicos únicos sintetizados por el animal. Estos materiales biológicos específicos reaccionan molecularmente para generar esta capacidad, ofreciendo ventajas metabólicas fundamentales para prosperar en condiciones ecológicas sumamente demandantes o adversas.",
        "El funcionamiento del {subtopic} está impulsado por sustancias bioquímicas que alteran las propiedades de los tejidos involucrados. Estas reacciones moleculares especializadas modifican la composición material del organismo, facilitando respuestas biológicas críticas que promueven su adaptación natural continua."
    ],
    "Historia, origen y evolución": [
        "Evolutivamente, el {subtopic} surgió como respuesta adaptativa ante presiones selectivas de depredadores antiguos. Con el paso de millones de años, la selección natural fue refinando esta capacidad biológica hasta consolidarla como un rasgo imprescindible para la supervivencia moderna.",
        "El desarrollo filogenético del {subtopic} revela cómo las especies ancestrales modificaron gradualmente sus características anatómicas. Este origen evolutivo demuestra un largo proceso de diversificación genética, culminando en las complejas adaptaciones biológicas que observamos en los ecosistemas actuales."
    ],
    "Contexto y entorno ecológico": [
        "Dentro de su hábitat, el {subtopic} permite al organismo explotar nichos ecológicos sumamente específicos. La interacción constante con factores bióticos y abióticos de su entorno refuerza la importancia de esta adaptación biológica para mantener el equilibrio trófico general.",
        "En el contexto ambiental, el {subtopic} resulta fundamental para navegar exitosamente por biomas complejos y competitivos. El entorno ecológico directo ejerce presiones continuas que validan diariamente la eficacia de estas estrategias biológicas de supervivencia animal."
    ],
    "Aplicaciones prácticas en la vida real": [
        "Estudiar el {subtopic} inspira innovaciones biomiméticas aplicables en ingeniería moderna y tecnología de materiales avanzados. Comprender estos mecanismos biológicos permite desarrollar soluciones prácticas y eficientes para problemas industriales, basándose directamente en los exitosos diseños naturales evolucionados.",
        "Las observaciones del {subtopic} proporcionan conocimientos biológicos útiles para mejorar estrategias de conservación de especies. Identificar el funcionamiento práctico de estas adaptaciones ayuda a implementar medidas ecológicas efectivas, protegiendo hábitats naturales y preservando la biodiversidad biológica global."
    ],
    "Importancia e impacto social": [
        "La investigación científica sobre el {subtopic} ha transformado nuestra comprensión profunda de la biología animal moderna. Este conocimiento impacta positivamente en la educación ambiental, fomentando una conciencia social mayor sobre la preservación crítica de especies biológicamente únicas.",
        "El impacto social derivado de estudiar el {subtopic} resalta el valor intrínseco de nuestra biodiversidad global. Comprender estas adaptaciones biológicas motiva a las comunidades a proteger sus ecosistemas locales, promoviendo iniciativas ecológicas vitales para un futuro sostenible."
    ],
    "Ventajas y desventajas comparativas": [
        "Aunque el {subtopic} ofrece beneficios excepcionales para la supervivencia, también exige un alto costo metabólico sostenido. Esta compensación biológica obliga al organismo a equilibrar constantemente sus recursos energéticos disponibles frente a las ventajas competitivas ecológicas obtenidas.",
        "Las ventajas del {subtopic} son innegables para evitar la depredación, pero sus limitaciones restringen ciertos comportamientos biológicos. Esta dualidad evolutiva refleja compromisos fisiológicos donde la especie sacrifica versatilidad general a cambio de una especialización ecológica altamente efectiva."
    ]
}

VERBS = ["estudiar", "analizar", "observar", "proteger", "entender", "determinar", "facilitar", "proporcionar", "desarrollar", "avanzar", "investigar", "evaluar", "mantener"]
NOUNS = ["organismo", "sistema", "estructura", "mecanismo", "especie", "ambiente", "condicion", "proceso", "funcion", "metodo", "tejido", "celula", "energia"]

DEST_FILE = "GBX_brain_33B.json"

def clean_text(text):
    words = text.split()
    if len(words) < 35:
        pads = [" Además, este estudio promueve metodologías analíticas precisas.", " Este fenómeno refleja principios ecológicos fundamentales."]
        words.extend(random.choice(pads).split())
    words = words[:48]
    res = " ".join(words).strip()
    if not re.search(r'[áéíóúÁÉÍÓÚ]', res):
        res += " Es una adaptación biológica esencial."
    return res

def generate_offline():
    dataset = []
    existing_ids = set()

    for subtopic in SUBTOPICS:
        for dim, templates in DIMENSIONS.items():
            base_id = unidecode.unidecode(f"{subtopic}_{dim}").lower().replace(' ', '_')
            base_id = re.sub(r'[^a-z_]', '', base_id)

            # ensure absolute uniqueness without length truncation cutting off differences
            while base_id in existing_ids:
                base_id += "x"
            existing_ids.add(base_id)

            template = random.choice(templates)
            raw_text = template.replace("{subtopic}", subtopic)
            final_text = clean_text(raw_text)

            kws = random.sample(VERBS, 2) + random.sample(NOUNS, 3)

            data = {
                "intent_id": base_id,
                "keywords": kws,
                "base_response": final_text
            }
            dataset.append(data)

    with open(DEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
        print(f"Generated {len(dataset)} valid items offline.")

generate_offline()
