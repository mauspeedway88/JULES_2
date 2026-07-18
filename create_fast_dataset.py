import json

dataset = [
    {
        "intent_id": "silbido_rapido_altos",
        "keywords": ["onda", "sonido", "frecuencia", "tono", "vibracion"],
        "base_response": "Las frecuencias altas corresponden a oscilaciones acústicas extremadamente veloces en el medio. Estructuralmente, estas ondas cortas transmiten sonidos muy agudos que resultan claramente perceptibles para el sistema auditivo humano sano bajo condiciones atmosféricas completamente normales."
    },
    {
        "intent_id": "ultrasonido_umbral_auditivo",
        "keywords": ["espectro", "frecuencia", "onda", "longitud", "eco"],
        "base_response": "Las vibraciones acústicas superan los veinte mil hertzios sobrepasando la capacidad auditiva humana promedio. Estructuralmente son ondas mecánicas longitudinales extremadamente cortas imposibles de percibir naturalmente sin utilizar tecnología especializada avanzada en centros de diagnóstico médico."
    },
    {
        "intent_id": "infrasonido_registro_humano",
        "keywords": ["onda", "sonido", "vibracion", "frecuencia", "amplitud"],
        "base_response": "Estas ondas acústicas son inferiores a veinte hertzios caracterizándose por longitudes enormes imposibles de percibir auditivamente. Dinámicamente generan vibraciones muy lentas que desplazan inmensos volúmenes de aire logrando viajar vastas distancias sin perder energía acústica."
    },
    {
        "intent_id": "efecto_doppler_movimiento",
        "keywords": ["velocidad", "frecuencia", "onda", "fuente", "receptor"],
        "base_response": "Este fenómeno consiste en una variación aparente de frecuencia que nota un observador cuando existe movimiento relativo respecto a la fuente. Al acercarse, los frentes ondulatorios se aprietan elevando el tono significativamente ante el receptor acústico."
    },
    {
        "intent_id": "resonancia_vibratoria_materiales",
        "keywords": ["resonancia", "frecuencia", "amplitud", "vibracion", "material"],
        "base_response": "Es una situación física donde un cuerpo vibra con amplitud gigantesca al recibir frecuencias que coinciden con su naturaleza estructural. La energía externa se acumula rítmicamente en el objeto aumentando las oscilaciones hasta niveles extremos mecánicos."
    },
    {
        "intent_id": "reverberacion_prolongada_salas",
        "keywords": ["eco", "reflexion", "sonido", "onda", "acustica"],
        "base_response": "Consiste en la persistencia del sonido en un espacio cerrado debido a múltiples reflexiones que continúan tras apagarse la fuente original. Las ondas chocan continuamente contra techos y paredes mezclándose en un caos acústico intenso audible."
    },
    {
        "intent_id": "difraccion_obstaculos",
        "keywords": [ "onda", "desviacion", "trayectoria", "obstaculo", "sonido" ],
        "base_response": "Ocurre una desviación evidente de las ondas acústicas al encontrar barreras o aberturas cuyo tamaño es comparable a su longitud fundamental. El frente ondulatorio se curva invadiendo completamente la zona de sombra geométrica posterior existente estructuralmente."
    },
    {
        "intent_id": "refraccion_cambio_ambiental",
        "keywords": [ "temperatura", "velocidad", "onda", "trayectoria", "desviacion" ],
        "base_response": "Se define como la curvatura de la trayectoria sonora debida a variaciones de velocidad propagativa al cambiar temperatura o densidad ambiental. Las capas térmicas atmosféricas distintas modifican la celeridad sonora, desviando los frentes acústicos de manera continua y predecible."
    },
    {
        "intent_id": "estruendo_supersonico_aviones",
        "keywords": [ "presion", "onda", "velocidad", "choque", "sonido" ],
        "base_response": "Se forma una onda de choque explosiva generada cuando un objeto supera la barrera del sonido en la atmósfera abierta. Los frentes de presión se acumulan formando un cono geométrico masivo que barre el terreno inferior violentamente."
    },
    {
        "intent_id": "numero_mach_aereo",
        "keywords": [ "velocidad", "sonido", "medida", "aeronautica", "aire" ],
        "base_response": "Representa una medida adimensional que relaciona la rapidez de un cuerpo sólido con la velocidad local del sonido circundante. Valores superiores a la unidad indican regímenes supersónicos donde cambian radicalmente las leyes aerodinámicas físicas aplicables constantemente."
    },
    {
        "intent_id": "frente_esferico_expansion",
        "keywords": [ "onda", "energia", "superficie", "propagacion", "distancia" ],
        "base_response": "Constituye una superficie tridimensional geométrica donde todas las partículas del medio comparten la misma fase ondulatoria constantemente. Irradiando desde una fuente puntual isotrópica, la energía acústica radiante disminuye su intensidad muy rápidamente al aumentar la distancia física."
    },
    {
        "intent_id": "patron_estacionario_cuerdas",
        "keywords": [ "interferencia", "onda", "nodo", "antinodo", "frecuencia" ],
        "base_response": "Se produce una interferencia acústica resultante de dos ondas idénticas viajando opuestamente en el mismo medio, creando nodos fijos y antinodos oscilantes. Las reflexiones en extremos fijos confinan energía formando perfiles vibratorios extremadamente estables y musicalmente muy puros."
    },
    {
        "intent_id": "armonicos_progresion_multiple",
        "keywords": [ "frecuencia", "timbre", "sonido", "onda", "multiplo" ],
        "base_response": "Son frecuencias secundarias que resultan ser múltiplos matemáticos exactos de una vibración acústica fundamental generadora principal constante. Se superponen a la onda base original alterando la forma del perfil oscilatorio determinando firmemente las riquezas tonales de cada instrumento."
    },
    {
        "intent_id": "pulsaciones_desfase_leve",
        "keywords": [ "volumen", "frecuencia", "fluctuacion", "interferencia", "sonido" ],
        "base_response": "Consiste en una fluctuación periódica de volumen resultante de la interferencia entre dos frecuencias sonoras ligeramente diferentes interactuando acústicamente en un medio. Los frentes ondulatorios entran y salen de fase rítmicamente alternando interferencias constructivas y destructivas totalmente audibles para todos."
    },
    {
        "intent_id": "absorcion_amortiguadora_ruido",
        "keywords": [ "ruido", "material", "energia", "acustica", "calor" ],
        "base_response": "Es un proceso físico donde materiales porosos especiales convierten energía acústica incidente en diminuto calor disipado internamente de forma constante. La fricción viscosa del aire vibrando intensamente dentro de pequeñas cavidades materiales reduce la amplitud sonora reflejada significativamente siempre."
    },
    {
        "intent_id": "hertzios_repeticion_periodica",
        "keywords": [ "frecuencia", "ciclo", "tiempo", "medida", "tono" ],
        "base_response": "Se trata de una unidad internacional de medida para frecuencia, equivalente a un ciclo oscilatorio acústico completo por cada segundo transcurrido temporalmente. Esta magnitud física cuantitativa determina directamente el tono musical percibido por el oyente humano diariamente en su entorno."
    }
]

with open('GBX_brain_19B.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

print("Dataset GBX_brain_19B.json created with 16 high-quality entries.")
