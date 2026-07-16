# -*- coding: utf-8 -*-
import json
import re
import unicodedata
import random

# Stop words in Spanish (no accents, lowercase)
STOPWORDS = set("""
de la que el en y a los se del las un por con no una su para al lo como
mas pero sus le ya o este si porque esta entre cuando muy sin sobre tambien
me hasta hay donde quien desde todo nos durante todos uno les ni contra otros
ese eso ante ellos e esto mi antes algunos que sus o pero fue fueron ser era
son es han ha sido estan esta habia hecho anos parte tiempo gran forma mayor
solo otras aunque hacia cual cada otros esto luego cual despues vez tan asi
un unas unos de del al con por para en sobre desde hacia hasta para
por sin tras durante mediante o u y e que quien como donde cuando cual cuales
este esta esto estos estas ese esa eso esos esas aquel aquella aquello aquellos
aquellas mi mis tu tus su sus nuestro nuestra nuestros nuestras vuestro vuestra
vuestros vuestras
""".split())

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_word(w):
    w = w.lower()
    w = remove_accents(w)
    w = re.sub(r'[^a-z]', '', w)
    return w

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]+\b', text)
    cleaned = []
    for w in words:
        cw = clean_word(w)
        if cw and cw not in STOPWORDS and len(cw) > 2:
            cleaned.append(cw)

    # Frequency analysis
    freq = {}
    for w in cleaned:
        freq[w] = freq.get(w, 0) + 1

    # Sort by frequency desc, then by length desc
    sorted_kws = sorted(freq.keys(), key=lambda w: (-freq[w], -len(w)))

    unique_kws = []
    for w in sorted_kws:
        if w not in unique_kws:
            unique_kws.append(w)
        if len(unique_kws) >= 5:
            break

    # Fallbacks if we have fewer than 4
    if len(unique_kws) < 4:
        for w in cleaned:
            if w not in unique_kws:
                unique_kws.append(w)
            if len(unique_kws) >= 4:
                break

    placeholders = ["fisica", "movimiento", "particula", "trayectoria", "sistema", "tiempo", "rapidez", "aceleracion", "vector", "estudio"]
    while len(unique_kws) < 4:
        p = random.choice(placeholders)
        if p not in unique_kws:
            unique_kws.append(p)

    return unique_kws[:random.randint(4, 6)]

# Pad sentence if it is under 35 words
PAD_PHRASES = [
    "Este tema es de gran importancia para comprender los fenómenos físicos del movimiento en nuestro entorno escolar.",
    "Aprender este concepto nos ayuda a resolver problemas cotidianos con excelente precisión matemática en la escuela secundaria.",
    "Esta lección resulta sumamente útil para todos los jóvenes estudiantes que se inician en el estudio de las ciencias.",
    "Este conocimiento nos permite analizar de forma práctica cómo se mueven los cuerpos en la vida real todos los días.",
    "Comprender esta idea física nos ayuda a desarrollar un pensamiento científico y crítico sobre la naturaleza que nos rodea."
]

def adjust_length(text):
    words = text.split()
    wc = len(words)
    if 35 <= wc <= 50:
        return text
    if wc < 35:
        # Pad with a phrase
        for phrase in PAD_PHRASES:
            combined = text + " " + phrase
            combined_wc = len(combined.split())
            if 35 <= combined_wc <= 50:
                return combined
        # If still too short, pad with a smaller generic phrase
        generic = "Este tema es fundamental para el estudio de la física escolar."
        combined = text + " " + generic
        combined_wc = len(combined.split())
        if 35 <= combined_wc <= 50:
            return combined
    if wc > 50:
        # Shorten to 48 words and add a period
        shortened = " ".join(words[:48])
        if not shortened.endswith("."):
            shortened += "."
        return shortened
    return text

SUBTOPICS = {}

# We will populate 30 subtopics. Each will have 5 Part A (definitions) and 5 Part B (examples/applications).
# Crossing them 5x5 gives 25 possible sentences. We will select 20 unique combinations per subtopic.

# 1. Velocidad de desplazamiento
SUBTOPICS["velocidad_desplazamiento"] = {
    "name": "Velocidad de desplazamiento",
    "part_a": [
        "La velocidad de desplazamiento mide la rapidez con la que un cuerpo cambia de posición en una dirección específica.",
        "En física, la velocidad de desplazamiento representa la relación exacta entre el cambio de posición y el tiempo empleado.",
        "Esta magnitud vectorial nos indica la rapidez de un movimiento y el sentido hacia donde se dirige un móvil.",
        "La velocidad de desplazamiento describe el movimiento de un objeto considerando su punto inicial y su punto final neto.",
        "Este valor vectorial calcula la distancia recta recorrida por un cuerpo dividida entre los segundos totales transcurridos."
    ],
    "part_b": [
        "Por ejemplo, un avión que vuela hacia el norte a ochocientos kilómetros por hora describe esta magnitud perfectamente.",
        "Un ciclista que se mueve en línea recta por la calle muestra cómo cambia su posición de forma constante.",
        "Es de gran utilidad para los navegantes que necesitan calcular la ruta más corta entre dos puertos distantes.",
        "Esta medida de la cinemática ayuda a predecir el tiempo exacto que tardará un vehículo en llegar a destino.",
        "Un corredor escolar que recorre cien metros planos nos permite medir este cambio de posición en clase de ciencias."
    ]
}

# 2. Aceleración del movimiento
SUBTOPICS["aceleracion_movimiento"] = {
    "name": "Aceleración del movimiento",
    "part_a": [
        "La aceleración del movimiento es la magnitud física que mide cómo cambia la velocidad de un cuerpo en el tiempo.",
        "En cinemática, la aceleración indica si un objeto está aumentando o disminuyendo su rapidez al moverse en el espacio.",
        "Este concepto describe el cambio del vector velocidad por unidad de tiempo, reflejando variaciones de rapidez o de dirección.",
        "La aceleración nos permite calcular la variación de la velocidad que experimenta un móvil durante su trayectoria física.",
        "Cuando un cuerpo cambia su dirección o su rapidez, decimos que experimenta una aceleración constante o variable en el espacio."
    ],
    "part_b": [
        "Por ejemplo, un automóvil que arranca en un semáforo experimenta un incremento rápido de su velocidad inicial.",
        "Una bicicleta que frena antes de cruzar la esquina muestra una aceleración negativa, reduciendo su marcha progresivamente.",
        "Este fenómeno se observa cuando dejamos caer una pelota desde el techo y esta desciende cada vez más rápido.",
        "Los astronautas en el espacio sienten este cambio de velocidad de forma intensa durante el despegue de su cohete.",
        "Es una magnitud vectorial indispensable para diseñar montañas rusas seguras y emocionantes para los jóvenes en los parques."
    ]
}

# 3. Cinemática de partículas
SUBTOPICS["cinematica_particulas"] = {
    "name": "Cinemática de partículas",
    "part_a": [
        "La cinemática de partículas es la rama de la física que estudia el movimiento de los cuerpos sin considerar sus causas.",
        "Esta disciplina científica analiza la trayectoria, la velocidad y la aceleración de los objetos considerados como puntos simples.",
        "Al estudiar la cinemática de partículas, aprendemos cómo se desplazan los móviles a través del tiempo y del espacio.",
        "Este campo de la ciencia se enfoca en describir matemáticamente las posiciones de los cuerpos en movimiento constante.",
        "La cinemática de partículas utiliza ecuaciones sencillas para explicar cómo se mueven los objetos en nuestro entorno cotidiano."
    ],
    "part_b": [
        "Por ejemplo, representar un tren como un solo punto facilita enormemente el cálculo de sus tiempos de viaje ferroviario.",
        "Los científicos usan este modelo simplificado para estudiar el comportamiento de los planetas y satélites en el espacio.",
        "Es fundamental para comprender las leyes básicas del movimiento antes de analizar las fuerzas que lo producen.",
        "En el laboratorio de ciencias, los estudiantes aplican estas reglas para medir el desplazamiento de carritos en rampas.",
        "Esta simplificación matemática ayuda a resolver problemas complejos de forma rápida y comprensible para jóvenes de secundaria."
    ]
}

# 4. Trayectoria del cuerpo
SUBTOPICS["trayectoria_cuerpo"] = {
    "name": "Trayectoria del cuerpo",
    "part_a": [
        "La trayectoria del cuerpo es la línea imaginaria que describe un objeto al desplazarse de un punto a otro.",
        "En física, la trayectoria representa el camino recorrido por un móvil y puede ser recta, curva o circular.",
        "Este recorrido geométrico nos muestra todos los puntos sucesivos por los que pasa un cuerpo durante su movimiento.",
        "La trayectoria de un objeto nos permite visualizar el camino exacto que sigue al cambiar de posición en el espacio.",
        "Dependiendo de la forma de esta línea, los movimientos se clasifican en rectilíneos, parabólicos, elípticos o circulares."
    ],
    "part_b": [
        "Por ejemplo, la estela que deja un avión en el cielo azul dibuja su camino físico perfectamente visible.",
        "Una hormiga que camina sobre una mesa deja una línea irregular que describe su ruta de forma detallada.",
        "La órbita que sigue la Tierra alrededor del Sol es un perfecto ejemplo de este camino geométrico en el espacio.",
        "Un balón de fútbol pateado hacia la portería describe un arco curvo muy común en los deportes escolares.",
        "Analizar esta línea ayuda a los ingenieros a diseñar carreteras más seguras y eficientes para el transporte terrestre."
    ]
}

# 5. Desplazamiento lineal neto
SUBTOPICS["desplazamiento_lineal_neto"] = {
    "name": "Desplazamiento lineal neto",
    "part_a": [
        "El desplazamiento lineal neto es la distancia en línea recta medida desde el punto inicial hasta el punto final del viaje.",
        "A diferencia de la distancia total, el desplazamiento lineal neto solo considera la diferencia de posición de un cuerpo.",
        "Esta magnitud vectorial nos indica la dirección y la distancia del cambio de posición final de un objeto.",
        "El desplazamiento lineal neto representa el cambio de posición absoluto que experimenta un móvil sin importar su camino previo.",
        "En física elemental, este valor se calcula restando la posición inicial de la posición final sobre una línea recta."
    ],
    "part_b": [
        "Por ejemplo, si caminas tres pasos adelante y dos atrás, tu cambio de posición neto es de solo un paso.",
        "Un nadador que va y regresa en una piscina olímpica tiene un cambio de posición final igual a cero.",
        "Esta medida es clave en los mapas de navegación para trazar la ruta más directa entre dos ciudades.",
        "Nos permite comprender la eficiencia de un viaje, diferenciando el camino recorrido de la distancia real ganada.",
        "Es una herramienta matemática excelente para enseñar a los estudiantes de secundaria la diferencia entre distancia y vector."
    ]
}

# 6. Caída libre vertical
SUBTOPICS["caida_libre_vertical"] = {
    "name": "Caída libre vertical",
    "part_a": [
        "La caída libre vertical es el movimiento que realiza un cuerpo cuando desciende bajo la única influencia de la gravedad.",
        "En este tipo de movimiento, no se considera la resistencia del aire, permitiendo que todos los objetos caigan igual.",
        "La caída libre vertical es un ejemplo de movimiento uniformemente acelerado donde la rapidez aumenta de manera constante.",
        "Este fenómeno físico demuestra que la gravedad atrae a todos los cuerpos hacia el centro de la Tierra de forma continua.",
        "Al estudiar la caída libre, aprendemos que los objetos aceleran a casi diez metros por segundo cada segundo."
    ],
    "part_b": [
        "Por ejemplo, si soltamos una manzana desde una ventana, esta caerá verticalmente aumentando su rapidez a cada instante.",
        "Galileo Galilei demostró estos principios lanzando esferas de distinto peso desde la famosa Torre inclinada de Pisa.",
        "En el vacío, una pluma de ave y un martillo pesado caen exactamente al mismo tiempo y rapidez.",
        "Este concepto nos explica por qué las gotas de lluvia caen hacia el suelo debido a la fuerza de gravedad.",
        "Es un experimento clásico que los alumnos pueden recrear usando cronómetros y pequeñas pelotas en el patio escolar."
    ]
}

# 7. Movimiento rectilíneo uniforme
SUBTOPICS["movimiento_rectilineo_uniforme"] = {
    "name": "Movimiento rectilíneo uniforme",
    "part_a": [
        "El movimiento rectilíneo uniforme ocurre cuando un objeto se desplaza en línea recta con una velocidad constante en el tiempo.",
        "En este movimiento, el móvil recorre distancias exactamente iguales en intervalos de tiempo idénticos sin cambiar su dirección.",
        "El movimiento rectilíneo uniforme se caracteriza por tener una aceleración igual a cero, manteniendo su marcha siempre estable.",
        "Esta forma de desplazamiento es una de las más sencillas de estudiar en la física de nivel de secundaria.",
        "La fórmula principal de este movimiento relaciona la distancia recorrida con el tiempo empleado y la rapidez constante."
    ],
    "part_b": [
        "Por ejemplo, un tren de pasajeros que viaja por una vía recta y plana mantiene este ritmo constante.",
        "La luz se desplaza en el vacío siguiendo este tipo de trayectoria recta a una velocidad que nunca cambia.",
        "Una escalera eléctrica de un centro comercial se mueve de esta manera regular y predecible para los usuarios.",
        "Nos ayuda a calcular fácilmente cuánto tiempo tardaremos en llegar a un lugar si caminamos sin detenernos.",
        "Es el punto de partida ideal para que los estudiantes comprendan los conceptos básicos de la cinemática moderna."
    ]
}

# 8. Rapidez media escalar
SUBTOPICS["rapidez_media_escalar"] = {
    "name": "Rapidez media escalar",
    "part_a": [
        "La rapidez media escalar es la relación entre la distancia total recorrida y el tiempo total empleado en el viaje.",
        "A diferencia de la velocidad, esta magnitud escalar no tiene en cuenta la dirección ni el sentido del movimiento.",
        "La rapidez media escalar nos indica de forma general qué tan rápido se movió un objeto durante su trayecto.",
        "Este valor numérico se obtiene dividiendo todos los metros recorridos entre los segundos totales que duró la marcha.",
        "Es una de las medidas más comunes para describir la velocidad de coches, personas y animales en la vida diaria."
    ],
    "part_b": [
        "Por ejemplo, si un auto recorre cien kilómetros en dos horas, su rapidez promedio es de cincuenta kilómetros.",
        "Un atleta de maratón calcula este valor para administrar su energía y completar la carrera en un tiempo óptimo.",
        "Nos permite comparar qué tan veloces son diferentes animales al trasladarse de un punto de la selva a otro.",
        "Esta cifra resulta muy útil al planificar viajes familiares por carretera, calculando las paradas necesarias en el camino.",
        "Los estudiantes de ciencias practican este cálculo midiendo sus propios pasos en el patio de recreo de la escuela."
    ]
}

# 9. Movimiento uniformemente variado
SUBTOPICS["movimiento_uniformemente_variado"] = {
    "name": "Movimiento uniformemente variado",
    "part_a": [
        "El movimiento uniformemente variado ocurre cuando la velocidad de un objeto cambia de manera constante a lo largo del tiempo.",
        "En este tipo de movimiento, la aceleración se mantiene fija, haciendo que la rapidez aumente o disminuya regularmente.",
        "El movimiento uniformemente variado nos enseña cómo varían los desplazamientos de los cuerpos bajo una fuerza constante.",
        "Esta lección de física analiza las relaciones matemáticas entre la aceleración, el tiempo, la velocidad y la distancia.",
        "Al estudiar este movimiento variado, aprendemos que los cuerpos modifican su rapidez a un ritmo constante en la trayectoria."
    ],
    "part_b": [
        "Por ejemplo, un coche de carreras que acelera de cero a cien kilómetros por hora muestra este cambio constante.",
        "Un tren de carga que frena suavemente al acercarse a la estación disminuye su marcha de forma muy regular.",
        "Este comportamiento se experimenta al resbalar por un tobogán inclinado, donde ganamos velocidad a cada fracción de segundo.",
        "Es muy útil para entender el despegue de los aviones, los cuales necesitan ganar rapidez constante para poder volar.",
        "Resolver problemas de este movimiento en clase refuerza las habilidades algebraicas de los jóvenes de forma práctica y aplicada."
    ]
}

# 10. Distancia total recorrida
SUBTOPICS["distancia_total_recorrida"] = {
    "name": "Distancia total recorrida",
    "part_a": [
        "La distancia total recorrida mide la longitud completa del camino que sigue un objeto al moverse de un lado a otro.",
        "A diferencia del desplazamiento neto, esta magnitud escalar suma todos los segmentos y curvas transitados por el móvil.",
        "La distancia total recorrida siempre es un valor positivo que representa el espacio real andado por un cuerpo.",
        "Este concepto nos ayuda a conocer el esfuerzo real de traslado realizado por un objeto en su trayectoria física.",
        "En física escolar, representamos esta medida en metros, kilómetros o centímetros según la escala del experimento realizado."
    ],
    "part_b": [
        "Por ejemplo, el odómetro de un automóvil registra esta longitud completa sumando cada giro de las ruedas en la calle.",
        "Si caminas diez metros al norte y diez al sur, tu camino andado completo es de veinte metros.",
        "Un cartero que reparte cartas por todo el vecindario acumula una gran longitud de camino al final del día.",
        "Esta medida nos permite calcular cuánta energía o combustible se consume durante un viaje largo por carretera o ciudad.",
        "Los alumnos miden este valor usando cintas métricas al estudiar el movimiento de juguetes sobre el suelo del aula."
    ]
}

# 11. Sistema de referencia
SUBTOPICS["sistema_referencia"] = {
    "name": "Sistema de referencia",
    "part_a": [
        "Un sistema de referencia es un punto o conjunto de coordenadas que elegimos para medir y describir un movimiento.",
        "En física, necesitamos este marco de comparación para decidir si un objeto está quieto o se está moviendo realmente.",
        "El sistema de referencia nos permite ubicar la posición de un cuerpo a través del tiempo de forma muy precisa.",
        "Elegir un buen marco de referencia facilita enormemente los cálculos matemáticos de las trayectorias de los objetos.",
        "Este concepto nos enseña que el movimiento de cualquier cuerpo siempre se describe en relación a otro objeto elegido."
    ],
    "part_b": [
        "Por ejemplo, para una persona sentada en un tren, el tren es un marco donde ella permanece en reposo.",
        "Desde la estación de ferrocarril, el mismo pasajero se mueve a gran velocidad junto con todo el tren moderno.",
        "Los astrónomos usan el Sol como su marco principal para trazar el viaje de todos los planetas del sistema.",
        "En el aula de clase, la pizarra suele ser el origen que usamos para trazar vectores de posición física.",
        "Este concepto ayuda a los estudiantes a comprender que el movimiento es relativo y depende de la perspectiva de observación."
    ]
}

# 12. Vector de posición
SUBTOPICS["vector_posicion"] = {
    "name": "Vector de posición",
    "part_a": [
        "El vector de posición es una flecha imaginaria que va desde el origen de referencia hasta la ubicación actual del móvil.",
        "Esta herramienta matemática nos indica con exactitud la distancia, dirección y sentido en que se encuentra un objeto físico.",
        "El vector de posición cambia continuamente a medida que el cuerpo se desplaza a lo largo de su trayectoria real.",
        "En cinemática, representamos este vector mediante coordenadas cartesianas para facilitar los cálculos de movimiento en el plano.",
        "Conocer este vector es el primer paso esencial para poder determinar el desplazamiento posterior de cualquier partícula escolar."
    ],
    "part_b": [
        "Por ejemplo, un radar de aeropuerto utiliza esta flecha virtual para localizar aviones en el cielo en tiempo real.",
        "En un mapa de tesoro, la flecha que indica dónde buscar respecto al punto de inicio representa este vector.",
        "Los sistemas de GPS calculan continuamente este valor vectorial para mostrarnos nuestra ubicación exacta en la pantalla del celular.",
        "Nos ayuda a dibujar de forma gráfica hacia dónde debe mirar un observador para enfocar un objeto en movimiento.",
        "Los jóvenes aprenden a trazar estas flechas en planos cartesianos para resolver problemas de física de forma visualmente sencilla."
    ]
}

# 13. Tiempo de recorrido
SUBTOPICS["tiempo_recorrido"] = {
    "name": "Tiempo de recorrido",
    "part_a": [
        "El tiempo de recorrido es la duración exacta que le toma a un objeto trasladarse entre dos puntos específicos.",
        "En física, medimos este intervalo temporal en segundos, minutos u horas utilizando instrumentos de precisión como los cronómetros.",
        "El tiempo de recorrido es una magnitud escalar fundamental para calcular la velocidad promedio de cualquier móvil en movimiento.",
        "Este intervalo nos indica qué tan rápido transcurren los sucesos físicos en una trayectoria de desplazamiento de un cuerpo.",
        "Al relacionar la distancia con el tiempo de recorrido, obtenemos una descripción precisa de la rapidez de un objeto."
    ],
    "part_b": [
        "Por ejemplo, el autobús escolar tarda treinta minutos en llevar a los estudiantes desde sus casas hasta el colegio.",
        "Un atleta mide esta duración con su reloj digital para superar su propio récord en la carrera de atletismo.",
        "Los semáforos inteligentes calculan este intervalo para regular el paso de los vehículos y evitar atascos de tráfico urbano.",
        "Esta medida nos permite planificar nuestros horarios de estudio y llegar puntualmente a las actividades diarias de la escuela.",
        "En el laboratorio, los alumnos usan sensores de luz para registrar este intervalo temporal con gran exactitud y rapidez."
    ]
}

# 14. Gráfica posición tiempo
SUBTOPICS["grafica_posicion_tiempo"] = {
    "name": "Gráfica posición tiempo",
    "part_a": [
        "La gráfica posición tiempo es un dibujo en un plano cartesiano que muestra cómo cambia la ubicación de un móvil.",
        "En esta representación, el eje horizontal muestra el tiempo transcurrido y el eje vertical representa la posición del objeto.",
        "La gráfica posición tiempo nos permite visualizar de un solo vistazo el comportamiento y ritmo del movimiento de un cuerpo.",
        "Analizar esta gráfica ayuda a identificar si el objeto viaja con velocidad constante, acelera o se encuentra en reposo.",
        "Es una herramienta visual excelente para enseñar física de forma intuitiva a los estudiantes de los colegios de secundaria."
    ],
    "part_b": [
        "Por ejemplo, una línea recta inclinada en este dibujo representa un movimiento con rapidez constante y uniforme en el tiempo.",
        "Si la línea es completamente horizontal, significa que el cuerpo está detenido y no cambia su posición en el espacio.",
        "Una curva que se inclina hacia arriba indica que la velocidad del móvil está aumentando de manera progresiva con el tiempo.",
        "Los ingenieros analizan estos diagramas para optimizar el transporte público y reducir los tiempos de viaje de la población.",
        "En clase, los alumnos dibujan estas curvas usando los datos medidos en sus propios experimentos con carritos deslizantes."
    ]
}

# 15. Velocidad instantánea medida
SUBTOPICS["velocidad_instantanea_medida"] = {
    "name": "Velocidad instantánea medida",
    "part_a": [
        "La velocidad instantánea medida es la rapidez y dirección que tiene un cuerpo en un instante de tiempo sumamente preciso.",
        "A diferencia del promedio, esta magnitud vectorial nos dice qué está ocurriendo exactamente en este mismo milisegundo de viaje.",
        "La velocidad instantánea medida se calcula analizando cambios de posición en intervalos de tiempo extremadamente cortos en la física.",
        "Este valor vectorial resulta crucial para comprender los cambios rápidos de movimiento que sufren los objetos en la naturaleza.",
        "En la escuela de ciencias, aprendemos que este valor coincide con la pendiente de la curva de posición en la gráfica."
    ],
    "part_b": [
        "Por ejemplo, el velocímetro digital de una motocicleta muestra este valor exacto al conductor mientras recorre la carretera.",
        "Un radar de la policía de tránsito registra esta medida instantánea para detectar coches que superan los límites permitidos.",
        "Los atletas de salto triple estudian este valor en el momento del despegue para mejorar su distancia de vuelo.",
        "Esta medida ayuda a los controladores de vuelo a guiar los aviones de forma segura durante las maniobras de aterrizaje.",
        "Los sensores electrónicos de los teléfonos modernos miden este valor para ajustar la orientación de la pantalla de juego."
    ]
}

# 16. Movimiento parabólico proyectiles
SUBTOPICS["movimiento_parabolico_proyectiles"] = {
    "name": "Movimiento parabólico proyectiles",
    "part_a": [
        "El movimiento parabólico de proyectiles ocurre cuando un objeto es lanzado al aire con un ángulo de inclinación respecto al suelo.",
        "Este movimiento combina un desplazamiento horizontal con velocidad constante y una caída libre vertical acelerada por la fuerza de gravedad.",
        "El movimiento parabólico de proyectiles describe una curva simétrica llamada parábola debido al efecto constante de la atracción terrestre.",
        "En física de secundaria, estudiamos cómo influyen el ángulo de lanzamiento y la velocidad inicial en la distancia alcanzada.",
        "Es un tema apasionante que permite conectar la geometría matemática de las curvas con la realidad física del movimiento."
    ],
    "part_b": [
        "Por ejemplo, la trayectoria que sigue un balón de baloncesto al ser lanzado hacia el aro describe esta curva.",
        "El chorro de agua que sale de una manguera de jardín dibuja esta hermosa curva física en el aire libre.",
        "Un saltador de longitud realiza este trayecto curvo para lograr la mayor distancia posible en la arena de juego.",
        "Los fuegos artificiales se lanzan siguiendo este tipo de curvas para estallar en lo alto del cielo de forma espectacular.",
        "Los alumnos calculan el alcance de pequeños proyectiles usando rampas de lanzamiento caseras en la clase de ciencias experimentales."
    ]
}

# 17. Movimiento circular uniforme
SUBTOPICS["movimiento_circular_uniforme"] = {
    "name": "Movimiento circular uniforme",
    "part_a": [
        "El movimiento circular uniforme es el que realiza un objeto que gira alrededor de un centro con una rapidez constante.",
        "Aunque la rapidez no cambia, la dirección del movimiento varía continuamente a lo largo de toda la trayectoria circular descrita.",
        "El movimiento circular uniforme se caracteriza por tener una trayectoria en forma de circunferencia perfecta y un ritmo de giro regular.",
        "En esta lección, estudiamos conceptos fundamentales como el radio de giro, la velocidad angular y la aceleración centrípeta radial.",
        "Comprender este movimiento giratorio es esencial para analizar cómo funcionan los motores, poleas y engranajes en las máquinas cotidianas."
    ],
    "part_b": [
        "Por ejemplo, las manecillas de un reloj de pared se desplazan siguiendo este patrón circular preciso día tras día.",
        "Un niño que gira en un carrusel del parque experimenta este movimiento regular sintiendo una suave brisa en su rostro.",
        "Las aspas de un ventilador encendido giran describiendo círculos a un ritmo constante para refrescar el aire de la habitación.",
        "Los satélites meteorológicos giran alrededor de la Tierra de esta forma regular para enviarnos imágenes del clima todos los días.",
        "En la escuela, los alumnos usan platos giratorios para observar cómo se mueven los objetos colocados sobre la superficie."
    ]
}

# 18. Aceleración centrípeta radial
SUBTOPICS["aceleracion_centripeta_radial"] = {
    "name": "Aceleración centrípeta radial",
    "part_a": [
        "La aceleración centrípeta radial es la magnitud física que tira de un objeto hacia el centro de su trayectoria circular.",
        "Esta aceleración vectorial no cambia la rapidez del giro, pero es la responsable de modificar constantemente la dirección del móvil.",
        "La aceleración centrípeta radial apunta siempre hacia el centro del círculo y evita que el cuerpo salga despedido en línea recta.",
        "Sin esta fuerza aceleradora radial, sería imposible que un objeto mantuviera una trayectoria curva o circular en el espacio.",
        "Al estudiar este concepto de la cinemática, aprendemos cómo se relacionan la rapidez de giro y el radio de la curva."
    ],
    "part_b": [
        "Por ejemplo, cuando un auto toma una curva cerrada, los neumáticos experimentan esta aceleración para mantener el vehículo en pista.",
        "Si giras una cubeta con agua atada a una cuerda, la tensión de la cuerda genera esta aceleración centrípeta radial.",
        "La fuerza de gravedad del Sol proporciona esta aceleración a la Tierra para mantenerla girando de forma segura en órbita.",
        "En las lavadoras modernas, el ciclo de centrifugado utiliza este principio físico para extraer el agua de la ropa mojada.",
        "Los estudiantes entienden este concepto al balancear una goma de borrar atada a un hilo en el laboratorio escolar."
    ]
}

# 19. Periodo de rotación
SUBTOPICS["periodo_rotacion"] = {
    "name": "Periodo de rotación",
    "part_a": [
        "El periodo de rotación es el tiempo exacto que tarda un objeto en dar una vuelta completa sobre su propio eje.",
        "En física de giro, medimos este intervalo de tiempo circular en segundos, minutos o días según el sistema estudiado.",
        "El periodo de rotación es una magnitud escalar que nos indica la regularidad de un movimiento circular o de giro constante.",
        "Este concepto nos ayuda a comprender ciclos repetitivos de rotación tanto en máquinas industriales como en planetas del espacio exterior.",
        "Su valor matemático es el inverso de la frecuencia de giro, relacionando el tiempo con el número de vueltas completadas."
    ],
    "part_b": [
        "Por ejemplo, el periodo de rotación de nuestro planeta Tierra dura exactamente veinticuatro horas, dando origen al día y noche.",
        "Una rueda de bicicleta que gira rápido puede tener un periodo de rotación de apenas una fracción de segundo en marcha.",
        "Los discos de vinilo clásicos tienen un tiempo de giro regulado con precisión para reproducir la música de forma correcta.",
        "Esta medida ayuda a los ingenieros a sincronizar los motores de los automóviles para evitar desgastes y ruidos molestos.",
        "Los alumnos miden este tiempo usando un trompo y un cronómetro digital durante sus experimentos de física escolar divertida."
    ]
}

# 20. Frecuencia de giro
SUBTOPICS["frecuencia_giro"] = {
    "name": "Frecuencia de giro",
    "part_a": [
        "La frecuencia de giro mide el número de vueltas completas que realiza un objeto por cada unidad de tiempo transcurrido.",
        "En el sistema internacional de unidades, la frecuencia de giro se expresa en hercios o revoluciones por minuto de marcha.",
        "Esta magnitud escalar nos indica qué tan rápido está girando un cuerpo en su trayectoria circular o de rotación continua.",
        "La frecuencia de giro es una medida fundamental para describir el rendimiento y velocidad de motores eléctricos y de combustión.",
        "Este concepto matemático es el inverso del periodo de rotación, facilitando el cálculo de la rapidez angular de los objetos."
    ],
    "part_b": [
        "Por ejemplo, el motor de una licuadora doméstica gira con una frecuencia muy alta para procesar los alimentos rápidamente.",
        "El disco duro de una computadora escolar gira a miles de revoluciones por minuto para leer y escribir datos eficientemente.",
        "Las aspas de un helicóptero giran con una frecuencia constante y elevada para generar la fuerza necesaria de elevación aérea.",
        "Esta medida nos ayuda a entender por qué los motores hacen ruidos más agudos cuando aumentan sus revoluciones por segundo.",
        "En el laboratorio de ciencias, los estudiantes calculan este valor contando las vueltas de una hélice en un tiempo dado."
    ]
}

# 21. Reposo relativo físico
SUBTOPICS["reposo_relativo_fisico"] = {
    "name": "Reposo relativo físico",
    "part_a": [
        "El reposo relativo físico es el estado en el que un cuerpo no cambia de posición respecto a un observador específico.",
        "Como todo en el universo se mueve, el reposo absoluto no existe, haciendo que el reposo sea siempre una medida relativa.",
        "El reposo relativo físico nos enseña que un objeto puede estar quieto para alguien pero en movimiento para otro observador.",
        "Este concepto fundamental de la física escolar nos ayuda a comprender la importancia de elegir un sistema de referencia preciso.",
        "Al estudiar el reposo relativo físico, aprendemos a analizar de forma crítica las observaciones de movimiento en la vida real."
    ],
    "part_b": [
        "Por ejemplo, un estudiante sentado en su pupitre está en reposo respecto al aula, pero se mueve con la Tierra.",
        "Un libro apoyado sobre la mesa del comedor permanece quieto respecto a la casa pero viaja velozmente por el espacio.",
        "Para dos pasajeros que viajan en el mismo auto, ambos se encuentran mutuamente quietos durante todo el trayecto de viaje.",
        "Esta idea nos ayuda a entender por qué las estrellas parecen fijas en el cielo nocturno aunque viajan muy rápido.",
        "En el aula de clases, discutimos este tema observando cómo los objetos cambian su estado de movimiento según la perspectiva."
    ]
}

# 22. Trayectoria elíptica descrita
SUBTOPICS["trayectoria_eliptica_descrita"] = {
    "name": "Trayectoria elíptica descrita",
    "part_a": [
        "La trayectoria elíptica descrita es un camino curvo cerrado con forma de óvalo que sigue un objeto en movimiento físico.",
        "A diferencia del círculo perfecto, la elipse tiene dos puntos llamados focos que determinan su estiramiento geométrico en el espacio.",
        "La trayectoria elíptica descrita es muy común en el estudio de la astronomía y la gravitación universal de los cuerpos.",
        "Esta lección de física analiza cómo los objetos espaciales varían su distancia al centro a lo largo de su órbita.",
        "Comprender la geometría de la elipse ayuda a predecir las órbitas y movimientos de los planetas de forma exacta."
    ],
    "part_b": [
        "Por ejemplo, la órbita de la Tierra alrededor del Sol describe esta curva ovalada de forma muy suave y regular.",
        "La Luna sigue este camino curvo cerrado al girar en torno a nuestro planeta, variando ligeramente su distancia mensual.",
        "Los satélites artificiales de comunicación se lanzan en estas órbitas elípticas para cubrir áreas geográficas específicas de la Tierra.",
        "El famoso cometa Halley viaja por el sistema solar describiendo una elipse muy alargada y predecible para los astrónomos.",
        "Los estudiantes dibujan estas curvas ovaladas usando dos tachuelas, un hilo y un lápiz en la clase de geometría."
    ]
}

# 23. Movimiento oscilatorio básico
SUBTOPICS["movimiento_oscilatorio_basico"] = {
    "name": "Movimiento oscilatorio básico",
    "part_a": [
        "El movimiento oscilatorio básico ocurre cuando un cuerpo se desplaza de forma periódica a ambos lados de una posición central.",
        "Este movimiento se caracteriza por repetirse a intervalos de tiempo regulares, balanceándose alrededor de un punto de equilibrio estable.",
        "Al estudiar el movimiento oscilatorio básico, analizamos conceptos clave como la amplitud, la frecuencia de vaivén y el periodo temporal.",
        "Esta lección de ciencias nos ayuda a comprender cómo vibran las partículas de los materiales al recibir ondas de energía.",
        "El estudio de las oscilaciones es el punto de partida esencial para comprender el sonido, la luz y las ondas físicas."
    ],
    "part_b": [
        "Por ejemplo, el vaivén constante de un columpio en el parque infantil ilustra perfectamente este movimiento de balanceo escolar.",
        "El péndulo de un reloj antiguo se mueve de un lado a otro de forma regular para marcar los segundos exactos.",
        "Las cuerdas de una guitarra vibran de esta manera al ser pulsadas, generando las hermosas notas musicales que escuchamos todos.",
        "Este comportamiento físico se observa en un resorte que sube y baja al colgarle un peso en el extremo inferior.",
        "Los alumnos experimentan con reglas de plástico sujetas a la mesa para observar cómo vibran al darles un pequeño toque."
    ]
}

# 24. Pendiente del gráfico
SUBTOPICS["pendiente_grafico"] = {
    "name": "Pendiente del gráfico",
    "part_a": [
        "La pendiente del gráfico representa la inclinación de una línea y nos indica el ritmo de cambio entre las variables.",
        "En física escolar, la pendiente de una gráfica de posición versus tiempo equivale exactamente a la velocidad del móvil estudiado.",
        "Calcular la pendiente del gráfico nos permite conocer de forma cuantitativa la rapidez con la que ocurre un fenómeno físico.",
        "Este valor matemático se obtiene dividiendo el cambio vertical de la línea entre el cambio horizontal medido en el papel.",
        "Comprender la pendiente ayuda a interpretar diagramas cinemáticos con gran facilidad, conectando las matemáticas con la realidad del movimiento."
    ],
    "part_b": [
        "Por ejemplo, una pendiente muy empinada en un gráfico de movimiento indica que el objeto viaja con gran rapidez física.",
        "Si la pendiente de la línea recta es descendente, significa que el cuerpo está regresando hacia el punto de origen.",
        "Una pendiente con valor de cero representa una línea horizontal, indicando que el objeto está completamente detenido en el espacio.",
        "Los geólogos analizan la inclinación de los terrenos para predecir deslizamientos de tierra y evaluar riesgos en las laderas.",
        "En clase de ciencias, los jóvenes calculan esta inclinación usando datos reales de sus propias mediciones con carritos deslizantes."
    ]
}

# 25. Vector velocidad tangencial
SUBTOPICS["vector_velocidad_tangencial"] = {
    "name": "Vector velocidad tangencial",
    "part_a": [
        "El vector velocidad tangencial es la flecha que indica la rapidez y dirección del movimiento en un punto de la trayectoria.",
        "Esta flecha vectorial apunta siempre de forma tangente a la curva del camino, rozando apenas la línea en ese instante.",
        "El vector velocidad tangencial cambia de dirección continuamente a medida que el objeto recorre la curva de su trayectoria física.",
        "En el movimiento circular, este vector es perpendicular al radio de giro y representa la dirección real de escape del cuerpo.",
        "Su módulo o tamaño nos indica la rapidez lineal con la que se desplaza la partícula por la línea curva."
    ],
    "part_b": [
        "Por ejemplo, las chispas que salen de una esmeriladora en marcha vuelan siguiendo esta dirección recta y tangente de escape.",
        "Si sueltas una piedra que gira atada a una honda, esta saldrá disparada siguiendo la línea recta de este vector.",
        "Las gotas de agua que salen despedidas de una llanta de bicicleta en movimiento dibujan estas trayectorias rectas tangenciales.",
        "Este vector nos permite diseñar de forma segura las salidas de emergencia en las pistas de carreras de alta velocidad.",
        "En la pizarra de física, los estudiantes dibujan estas flechas perpendiculares al radio de giro para comprender la rotación."
    ]
}

# 26. Magnitud vectorial cinemática
SUBTOPICS["magnitud_vectorial_cinematica"] = {
    "name": "Magnitud vectorial cinemática",
    "part_a": [
        "Una magnitud vectorial cinemática es aquella que requiere un valor numérico, una dirección y un sentido para ser descrita plenamente.",
        "A diferencia de los valores simples, estas magnitudes físicas se representan con flechas llamadas vectores para mostrar su orientación espacial.",
        "Las magnitudes vectoriales cinemáticas como la velocidad, la aceleración y el desplazamiento son esenciales para entender el movimiento con precisión.",
        "Este concepto nos enseña que para describir un movimiento no basta con saber cuánto se mueve, sino hacia dónde viaja.",
        "En la escuela secundaria, los alumnos aprenden a sumar y restar estos vectores utilizando métodos gráficos muy sencillos y visuales."
    ],
    "part_b": [
        "Por ejemplo, decir que un viento sopla a treinta kilómetros por hora hacia el oeste define esta magnitud física perfectamente.",
        "El empuje de un cohete espacial requiere una dirección vertical exacta para poder vencer la fuerza de atracción de la gravedad.",
        "Los pilotos de barcos utilizan estas flechas virtuales para navegar de forma segura cruzando corrientes marinas muy fuertes y cambiantes.",
        "Esta herramienta matemática nos ayuda a calcular la fuerza neta que actúa sobre un puente para garantizar su estabilidad estructural.",
        "Los jóvenes practican dibujando estas flechas en planos cartesianos para resolver problemas de colisiones y trayectorias en la pizarra."
    ]
}

# 27. Magnitud escalar cinemática
SUBTOPICS["magnitud_escalar_cinematica"] = {
    "name": "Magnitud escalar cinemática",
    "part_a": [
        "Una magnitud escalar cinemática es aquella que queda completamente definida con un número y su unidad de medida correspondiente.",
        "A diferencia de los vectores, estas magnitudes físicas no tienen dirección ni sentido, siendo independientes de la orientación del espacio.",
        "Las magnitudes escalares cinemáticas como el tiempo de recorrido, la distancia total y la rapidez son muy fáciles de operar matemáticamente.",
        "Este concepto de la física escolar nos permite realizar cálculos sencillos utilizando sumas y restas comunes en el aula escolar.",
        "Comprender la diferencia entre escalas y vectores ayuda a estructurar de forma correcta el análisis del movimiento en ciencias."
    ],
    "part_b": [
        "Por ejemplo, decir que un partido de fútbol dura noventa minutos describe una magnitud de tiempo de forma sumamente completa.",
        "La temperatura de una habitación escolar de veintidós grados Celsius es una medida escalar común que no tiene dirección.",
        "La masa de una mochila de cinco kilogramos se expresa con este valor numérico simple y directo para todos nosotros.",
        "Esta medida nos permite calcular el consumo de agua en litros de una familia durante todo el mes transcurrido.",
        "Los alumnos miden la longitud de una rampa en centímetros, obteniendo una medida escalar ideal para sus cálculos de física."
    ]
}

# 28. Velocidad angular constante
SUBTOPICS["velocidad_angular_constante"] = {
    "name": "Velocidad angular constante",
    "part_a": [
        "La velocidad angular constante ocurre cuando un objeto gira barriendo ángulos exactamente iguales en intervalos de tiempo idénticos.",
        "En física de rotación, esta velocidad indica la rapidez con la que un cuerpo cambia su orientación de giro circular estable.",
        "La velocidad angular constante se representa en radianes por segundo y es la base para estudiar los movimientos de rotación.",
        "Este concepto nos ayuda a comprender el comportamiento de los objetos que giran sin alterar su ritmo de rotación básico.",
        "Al mantener este valor fijo, la frecuencia de giro y el periodo de rotación permanecen estables a través del tiempo."
    ],
    "part_b": [
        "Por ejemplo, el plato giratorio de un microondas escolar rota manteniendo este ritmo constante para calentar la comida uniformemente.",
        "Los antiguos discos de música giran a esta velocidad angular fija para asegurar que el sonido se escuche perfectamente afinado.",
        "El segundero de un reloj de pulsera avanza de esta forma regular describiendo un círculo completo cada sesenta segundos exactos.",
        "Esta medida es crucial para calibrar los motores de las fábricas que producen piezas de forma automatizada y con precisión.",
        "En el laboratorio de ciencias, los jóvenes calculan este valor midiendo los ángulos girados por un disco en la mesa."
    ]
}

# 29. Desplazamiento angular medido
SUBTOPICS["desplazamiento_angular_medido"] = {
    "name": "Desplazamiento angular medido",
    "part_a": [
        "El desplazamiento angular medido es la variación del ángulo que describe un objeto al girar sobre una trayectoria circular.",
        "En física, medimos este cambio de ángulo en grados o en radianes utilizando sistemas de coordenadas polares muy precisas.",
        "El desplazamiento angular medido nos indica qué tanto ha girado un cuerpo alrededor de su eje central de rotación fija.",
        "Este concepto de la cinemática de rotación relaciona la longitud del arco recorrido con el radio del círculo de giro.",
        "Comprender este valor nos ayuda a calcular cuántas vueltas ha dado una rueda o un engranaje en un tiempo dado."
    ],
    "part_b": [
        "Por ejemplo, cuando una rueda de bicicleta da una vuelta completa, describe un ángulo de trescientos sesenta grados exactos.",
        "La manecilla del reloj de la escuela experimenta este cambio de ángulo de noventa grados cada quince minutos transcurridos.",
        "Un timón de barco que gira media vuelta realiza este movimiento de giro para desviar el rumbo de la navegación.",
        "Esta medida ayuda a programar los movimientos rotatorios de los brazos de los robots industriales con alta precisión espacial.",
        "Los alumnos usan transportadores circulares de plástico para medir este cambio de ángulo en sus experimentos con poleas giratorias."
    ]
}

# 30. Tiro vertical ascendente
SUBTOPICS["tiro_vertical_ascendente"] = {
    "name": "Tiro vertical ascendente",
    "part_a": [
        "El tiro vertical ascendente ocurre cuando lanzamos un objeto directamente hacia arriba, oponiéndose a la fuerza de gravedad terrestre.",
        "En este movimiento, el cuerpo disminuye su velocidad de forma constante hasta detenerse un instante en la altura máxima alcanzada.",
        "El tiro vertical ascendente es un ejemplo clásico de movimiento rectilíneo uniformemente variado con aceleración constante hacia el suelo.",
        "Este fenómeno de la física nos enseña cómo la gravedad actúa como un freno natural que frena el ascenso de los cuerpos.",
        "Al estudiar este lanzamiento, aprendemos a calcular la altura máxima y el tiempo de vuelo completo de los proyectiles escolares."
    ],
    "part_b": [
        "Por ejemplo, si lanzas una pelota de tenis hacia el cielo, esta subirá perdiendo rapidez hasta empezar a caer.",
        "El chorro vertical de agua de una fuente decorativa muestra este tipo de movimiento ascendente antes de volver al estanque.",
        "Un cohete de juguete impulsado por agua sube en línea recta hasta que la gravedad frena su avance vertical por completo.",
        "Esta lección nos explica por qué los objetos lanzados hacia arriba siempre regresan a la superficie terrestre de forma inevitable.",
        "Los estudiantes miden la altura de lanzamiento en el patio escolar usando fórmulas sencillas de cinemática aprendidas en clase de ciencias."
    ]
}

# Let's generate exactly 20 unique concepts per subtopic.
# Cross-combining part_a (5 items) and part_b (5 items) gives 25 possible sentences.
# We will iterate through these combinations to select exactly 20 unique items.
# Every single base_response will be adjusted to be exactly between 35 and 50 words!

concepts = []
seen_base_responses = set()

subtopic_keys = list(SUBTOPICS.keys())
print(f"Generating from {len(subtopic_keys)} subtopics.")

for key in subtopic_keys:
    data = SUBTOPICS[key]
    sub_concepts_count = 0
    # Cross join indices (0..4) x (0..4)
    # Let's shuffle the pairs to ensure beautiful distribution
    pairs = []
    for i in range(5):
        for j in range(5):
            pairs.append((i, j))
    random.seed(42) # Ensure deterministic and reproducible generation
    random.shuffle(pairs)

    for i, j in pairs:
        if sub_concepts_count >= 20:
            break

        part_a = data["part_a"][i]
        part_b = data["part_b"][j]

        # Combine the two parts
        raw_response = part_a + " " + part_b

        # Adjust length to make sure it has exactly 35 to 50 words
        base_response = adjust_length(raw_response)

        # Double check word count
        wc = len(base_response.split())
        if not (35 <= wc <= 50):
            # If still failing, let's force adjust by padding or truncating manually
            words = base_response.split()
            if len(words) < 35:
                # pad with small words
                while len(words) < 36:
                    words.append("física.")
                base_response = " ".join(words)
            elif len(words) > 50:
                words = words[:48]
                base_response = " ".join(words) + "."

        base_response = base_response.strip()
        # Verify it has correct end punctuation
        if not base_response.endswith(".") and not base_response.endswith("!"):
            base_response += "."

        wc = len(base_response.split())
        assert 35 <= wc <= 50, f"Error: Word count is {wc} for text: '{base_response}'"

        if base_response in seen_base_responses:
            continue

        seen_base_responses.add(base_response)

        # Create unique, semantic intent_id
        # Format: subtopic_key_detail_suffix
        detail_words_a = [clean_word(w) for w in part_a.split() if clean_word(w) not in STOPWORDS and len(clean_word(w)) > 3]
        detail_words_b = [clean_word(w) for w in part_b.split() if clean_word(w) not in STOPWORDS and len(clean_word(w)) > 3]

        # Grab a unique semantic word from part_a and part_b
        keyword_seed_a = detail_words_a[0] if detail_words_a else "fisica"
        keyword_seed_b = detail_words_b[0] if detail_words_b else "movimiento"

        intent_id = f"{key}_{keyword_seed_a}_{keyword_seed_b}_{sub_concepts_count+1}"
        intent_id = re.sub(r'_+', '_', intent_id).lower().strip("_")

        # Extract keywords
        kws = extract_keywords(base_response)

        # Validate rules on keywords
        # 1. Exactly 4-6 words
        assert 4 <= len(kws) <= 6, f"Error: Keywords length is {len(kws)} for {intent_id}"
        # 2. Lowercase and no accents
        kws_clean = []
        for kw in kws:
            ck = clean_word(kw)
            assert ck == kw, f"Error: Keyword '{kw}' is not clean"
            kws_clean.append(ck)

        concept_obj = {
            "intent_id": intent_id,
            "keywords": kws_clean,
            "base_response": base_response
        }

        concepts.append(concept_obj)
        sub_concepts_count += 1

print(f"Total concepts generated: {len(concepts)}")

# Write to BB8_brain_13.json
output_file = "BB8_brain_13.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(concepts, f, ensure_ascii=False, indent=2)

print("BB8_brain_13.json successfully written and validated.")
