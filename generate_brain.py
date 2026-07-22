import json
import re
import sys

# Define strict stop words to exclude from keywords
STOP_WORDS = {
    "y", "e", "ni", "o", "u", "pero", "mas", "sino", "que", "porque", "como", "cuando", "donde",
    "aunque", "si", "el", "la", "los", "las", "un", "una", "unos", "unas", "a", "ante", "bajo",
    "cabe", "con", "contra", "de", "desde", "durante", "en", "entre", "hacia", "hasta", "mediante",
    "para", "por", "segun", "sin", "so", "sobre", "tras", "versus", "via", "del", "al", "me", "te",
    "se", "nos", "os", "le", "les", "lo", "mi", "tu", "su", "mis", "tus", "sus", "yo", "nosotros",
    "ellos", "ellas", "este", "esta", "esto", "estos", "estas", "ese", "esa", "eso", "esos", "esas",
    "aquel", "aquella", "aquello", "aquellos", "aquellas", "todo", "todos", "toda", "todas", "quien",
    "quienes", "cual", "cuales", "algo", "alguien", "nada", "nadie", "no", "ya", "muy", "tan",
    "tambien", "tampoco", "aun", "solo", "and", "or", "but", "with", "the"
}

concepts = [
    # Subtema 1: Memoria auditiva de secuencias musicales (3 concepts)
    {
        "intent_id": "memoria_auditiva_secuencial",
        "keywords": ["retencion", "orden", "patrones", "tonos"],
        "base_response": "La memoria auditiva secuencial es la capacidad de recordar y reproducir un orden preciso de sonidos musicales escuchados previamente. Esta destreza permite a los estudiantes identificar variaciones melódicas, recordar tonadas complejas y estructurar mentalmente composiciones extensas sin necesidad de apoyo visual o partituras escritas."
    },
    {
        "intent_id": "entrenamiento_memoria_tonal",
        "keywords": ["desarrollo", "retencion", "intervalos", "melodia"],
        "base_response": "El entrenamiento de la retención tonal consiste en ejercicios repetitivos para grabar intervalos y distancias entre notas en la mente. Practicar constantemente esta habilidad auditiva facilita la improvisación, optimiza la afinación al cantar y ayuda a transcribir melodías complejas directamente al papel sin cometer errores."
    },
    {
        "intent_id": "reconocimiento_patrones_auditivos",
        "keywords": ["identificacion", "estructuras", "frases", "sonoras"],
        "base_response": "El reconocimiento de patrones auditivos implica agrupar sonidos en unidades con significado para facilitar su almacenamiento en la memoria a largo plazo. Los músicos utilizan este proceso cognitivo para anticipar el desarrollo de una obra musical, facilitando el aprendizaje rápido de piezas extensas y complejas."
    },

    # Subtema 2: Apreciación crítica de audiciones musicales (3 concepts)
    {
        "intent_id": "apreciacion_critica_musical",
        "keywords": ["analisis", "escucha", "elementos", "estetica"],
        "base_response": "La apreciación crítica de audiciones consiste en analizar activamente los componentes de una obra sonora, como textura, forma y dinámica. Esta práctica desarrolla el pensamiento crítico en los alumnos, permitiéndoles emitir juicios fundamentados sobre el valor artístico y el contexto cultural de diversas creaciones musicales."
    },
    {
        "intent_id": "audicion_activa_analitica",
        "keywords": ["atencion", "desglose", "texturas", "timbres"],
        "base_response": "La audición activa analítica requiere enfocar la atención consciente en el desglose de los diferentes timbres y planos sonoros de una composición. Mediante este ejercicio auditivo, los estudiantes aprenden a diferenciar los instrumentos participantes y a comprender cómo se entrelazan las voces en una obra."
    },
    {
        "intent_id": "contextualizacion_estetica_obra",
        "keywords": ["valoracion", "entorno", "estilo", "creacion"],
        "base_response": "La contextualización estética de una obra implica relacionar el sonido escuchado con la época histórica y social en que fue creado. Este análisis ayuda a comprender las razones detrás de la instrumentación utilizada, las innovaciones técnicas de la época y el mensaje que el compositor deseaba transmitir."
    },

    # Subtema 3: Clave de sol musical escrita (3 concepts)
    {
        "intent_id": "clave_sol_pentagrama",
        "keywords": ["registro", "agudo", "lectura", "grafico"],
        "base_response": "La clave de sol es un signo gráfico colocado al principio del pentagrama que establece la posición de las notas agudas. Su dibujo se origina en la segunda línea, asignando a esta la nota sol, sirviendo como punto de partida indispensable para la lectura de melodías escritas."
    },
    {
        "intent_id": "origen_clave_sol",
        "keywords": ["evolucion", "simbolo", "letra", "notacion"],
        "base_response": "El origen de la clave de sol se remonta a la antigua letra ge utilizada en la notación musical medieval para representar dicha nota. Con los siglos, los copistas estilizaron este trazo gótico hasta convertirlo en el elegante símbolo espiral que hoy corona la música escrita."
    },
    {
        "intent_id": "uso_instrumentos_agudos",
        "keywords": ["melodia", "flauta", "violin", "registro"],
        "base_response": "El uso de la clave de sol es estándar para registrar melodías tocadas por instrumentos agudos como flautas, violines y oboes. Escribir en esta clave evita el uso excesivo de líneas adicionales debajo del pentagrama, facilitando una lectura fluida y rápida para los músicos intérpretes."
    },

    # Subtema 4: Clave de fa para bajos (3 concepts)
    {
        "intent_id": "clave_fa_registro",
        "keywords": ["notacion", "grave", "lineas", "puntos"],
        "base_response": "La clave de fa es el símbolo musical utilizado para representar el registro grave dentro del pentagrama de cinco líneas. Se sitúa comúnmente en la cuarta línea, marcada por dos puntos característicos, asignando a esta la nota fa y facilitando la escritura de instrumentos de tesitura baja."
    },
    {
        "intent_id": "instrumentos_clave_fa",
        "keywords": ["violonchelo", "tuba", "registro", "lectura"],
        "base_response": "La clave de fa es esencial para la lectura y escritura de la música de instrumentos graves como el violonchelo, la tuba y el contrabajo. El uso de este signo musical evita que las notas se dibujen muy por debajo del pentagrama, simplificando la interpretación visual."
    },
    {
        "intent_id": "clave_fa_cuarta",
        "keywords": ["referencia", "posicion", "grave", "pentagrama"],
        "base_response": "La clave de fa en cuarta línea establece un punto de referencia crucial para estructurar la base armónica de cualquier pieza musical. Al definir el fa grave, permite a los compositores trazar líneas de bajo sólidas que sirven de soporte a las melodías agudas superiores."
    },

    # Subtema 5: Instrumentos musicales de percusión rítmica (3 concepts)
    {
        "intent_id": "percusion_ritmica_definicion",
        "keywords": ["golpe", "timbre", "ritmo", "membrana"],
        "base_response": "Los instrumentos de percusión rítmica producen sonido al ser golpeados, sacudidos o raspados, careciendo generalmente de una afinación tonal definida. Su función primordial en cualquier agrupación es establecer la base del ritmo, mantener el pulso constante y aportar variedad tímbrica a la pieza ejecutada."
    },
    {
        "intent_id": "clasificacion_percusion_idofonos",
        "keywords": ["vibracion", "cuerpo", "material", "madera"],
        "base_response": "La percusión rítmica incluye idiófonos, donde todo el cuerpo del instrumento vibra para generar el sonido, como claves o castañuelas. Estos objetos musicales dependen de la densidad de su material, sea madera o metal, para proyectar golpes secos indispensables en la marcación del pulso."
    },
    {
        "intent_id": "membranofonos_percusion_cuero",
        "keywords": ["tension", "parche", "resonancia", "golpe"],
        "base_response": "Los membranófonos son instrumentos de percusión que producen sonido mediante la vibración de un parche o membrana tensada sobre un resonador. El sonido se genera al golpear el cuero con las manos o baquetas, variando el tono según el tamaño del instrumento."
    },

    # Subtema 6: Instrumentos musicales de viento madera (3 concepts)
    {
        "intent_id": "viento_madera_timbre",
        "keywords": ["boquilla", "caña", "soplo", "acustica"],
        "base_response": "Los instrumentos de viento madera producen sonido al soplar aire a través de una boquilla con caña o un bisel tallado. Aunque hoy muchos se construyen de metal, se clasifican así por su mecanismo tradicional de producción sonora y su timbre cálido característico."
    },
    {
        "intent_id": "mecanismo_llaves_madera",
        "keywords": ["orificios", "digitacion", "afinacion", "tubo"],
        "base_response": "El mecanismo de llaves en los instrumentos de viento madera permite tapar orificios lejanos para modificar la longitud del tubo resonador. Al alterar la columna de aire interna mediante la digitación del músico, se consiguen notas de diferente altura con gran agilidad técnica."
    },
    {
        "intent_id": "cana_doble_viento",
        "keywords": ["vibracion", "oboe", "fagot", "timbre"],
        "base_response": "Los instrumentos de caña doble, como el oboe y el fagot, utilizan dos finas láminas de madera que vibran entre sí. Al soplar, esta vibración directa genera un sonido penetrante y nasal muy apreciado para interpretar pasajes solistas expresivos en las orquestas."
    },

    # Subtema 7: Instrumentos musicales de viento metal (3 concepts)
    {
        "intent_id": "viento_metal_caracteristicas",
        "keywords": ["boquilla", "labios", "bronce", "vibracion"],
        "base_response": "Los instrumentos de viento metal generan sonido por la vibración de los labios del músico contra una boquilla con forma de copa. Construidos principalmente de latón o bronce, estos instrumentos canalizan el aire a través de un largo tubo cónico que amplifica la potencia sonora."
    },
    {
        "intent_id": "mecanismo_pistones_metal",
        "keywords": ["valvulas", "recorrido", "columna", "tuberia"],
        "base_response": "El mecanismo de pistones o válvulas en el viento metal desvía la columna de aire hacia tuberías de diferentes longitudes adicionales. Al presionar estos botones, el recorrido del aire cambia, permitiendo al intérprete ejecutar escalas cromáticas completas con precisión y velocidad."
    },
    {
        "intent_id": "funcion_vara_trombon",
        "keywords": ["deslizamiento", "tubo", "afinacion", "glissando"],
        "base_response": "La vara móvil del trombón es un mecanismo de deslizamiento que altera continuamente la longitud del tubo para cambiar la afinación. Al no depender de pistones fijos, permite realizar transiciones suaves entre notas, recurso técnico característico conocido popularmente como glissando musical."
    },

    # Subtema 8: Instrumentos musicales de cuerda frotada (3 concepts)
    {
        "intent_id": "cuerda_frotada_arco",
        "keywords": ["cerdas", "friccion", "cuerpo", "violin"],
        "base_response": "Los instrumentos de cuerda frotada producen sonido mediante la fricción de un arco de cerdas de caballo sobre cuerdas tensadas. Esta vibración constante se transmite a través del puente de madera hacia la caja de resonancia, amplificando el sonido característico del violín."
    },
    {
        "intent_id": "puente_caja_resonancia",
        "keywords": ["vibracion", "madera", "amplificacion", "alma"],
        "base_response": "El puente en los instrumentos de cuerda frotada soporta la tensión y transmite la vibración física a la tapa armónica. Dentro de la caja, una pequeña pieza cilíndrica de madera llamada alma propaga estas ondas, logrando un timbre equilibrado y resonante."
    },
    {
        "intent_id": "tecnica_vibrato_cuerda",
        "keywords": ["oscilacion", "afinacion", "dedo", "expresividad"],
        "base_response": "La técnica del vibrato consiste en una oscilación rápida y controlada del dedo sobre la cuerda frotada para embellecer el sonido. Este leve movimiento altera la afinación de la nota, aportando una calidez y expresividad únicas que emulan las cualidades de la voz humana."
    },

    # Subtema 9: Pulso constante del ritmo musical (3 concepts)
    {
        "intent_id": "pulso_musical_constante",
        "keywords": ["latido", "regularidad", "tiempo", "estructura"],
        "base_response": "El pulso musical es el latido interno y constante que organiza el ritmo y la duración de las notas en una obra. Esta regularidad temporal invisible divide el tiempo en partes iguales, sirviendo como guía indispensable para mantener la sincronía entre los ejecutantes."
    },
    {
        "intent_id": "metronomo_medida_pulso",
        "keywords": ["dispositivo", "velocidad", "oscilacion", "tiempo"],
        "base_response": "El metrónomo es un dispositivo que produce clics regulares para medir y guiar el pulso exacto de la música. Ajustar su velocidad permite fijar el tiempo de ejecución de una pieza, ayudando al estudiante a desarrollar una precisión rítmica impecable."
    },
    {
        "intent_id": "pulso_acentuacion_compas",
        "keywords": ["regularidad", "patron", "fuerte", "debil"],
        "base_response": "La acentuación del pulso agrupa los latidos regulares en patrones repetitivos que definen la estructura métrica de un compás. Al destacar ciertos pulsos fuertes frente a otros débiles, se crea el marco rítmico esencial para la danza y la interpretación orquestal."
    },

    # Subtema 10: Síncopa rítmica en tiempos débiles (3 concepts)
    {
        "intent_id": "sincopa_ritmica_definicion",
        "keywords": ["desplazamiento", "acento", "tiempo", "debil"],
        "base_response": "La síncopa rítmica es el efecto que rompe la regularidad del pulso al acentuar una nota que comienza en un tiempo débil. Esta técnica prolonga el sonido sobre el tiempo fuerte siguiente, generando una tensión rítmica muy común en el jazz y ritmos latinos."
    },
    {
        "intent_id": "efecto_tension_sincopa",
        "keywords": ["sorpresa", "ritmo", "inversion", "dinamica"],
        "base_response": "El efecto de tensión por síncopa se logra al burlar la expectativa del oyente, que espera escuchar el acento en el pulso fuerte. Esta inversión temporal genera dinamismo, invitando al movimiento físico y enriqueciendo la variedad expresiva de la composición musical."
    },
    {
        "intent_id": "sincopa_escritura_ligadura",
        "keywords": ["notacion", "union", "duracion", "figura"],
        "base_response": "En la notación escrita, la síncopa se representa frecuentemente uniendo una figura colocada en tiempo débil con otra en tiempo fuerte mediante una ligadura. Esta unión suma los valores de duración, creando un sonido continuo que desafía la regularidad del compás."
    },

    # Subtema 11: Alteraciones musicales de sostenido bemol (3 concepts)
    {
        "intent_id": "alteraciones_sostenido_bemol",
        "keywords": ["modificacion", "tono", "notacion", "simbolo"],
        "base_response": "Las alteraciones son símbolos que modifican la altura original de las notas escritas en el pentagrama por medio tono. El sostenido eleva la nota un semitono, mientras que el bemol la desciende en la misma medida, variando el color de la melodía."
    },
    {
        "intent_id": "sostenido_teclado_funcion",
        "keywords": ["semitono", "derecha", "tecla", "altura"],
        "base_response": "El sostenido desplaza la ejecución de una nota un semitono hacia arriba, lo que en el piano equivale a la tecla inmediata derecha. Este signo altera la afinación natural de la nota, permitiendo construir escalas mayores y menores con distancias tonales precisas."
    },
    {
        "intent_id": "bemol_desplazamiento_grave",
        "keywords": ["semitono", "izquierda", "tecla", "notacion"],
        "base_response": "El bemol indica que una nota debe ejecutarse un semitono más abajo, desplazándose hacia la izquierda inmediata en un teclado convencional. Esta alteración cromática suaviza la tensión de ciertos intervalos, modificando la dirección y el carácter expresivo de una frase musical."
    },

    # Subtema 12: Tonalidad musical de obras sonoras (3 concepts)
    {
        "intent_id": "tonalidad_musical_definicion",
        "keywords": ["jerarquia", "tonica", "escala", "armonia"],
        "base_response": "La tonalidad es el sistema de relaciones jerárquicas que organiza las notas y acordes en torno a un centro tonal llamado tónica. Este punto de atracción da estabilidad a la obra, definiendo la escala y las reglas de tensión y distensión armónica."
    },
    {
        "intent_id": "armadura_clave_tonalidad",
        "keywords": ["notacion", "alteraciones", "escala", "pentagrama"],
        "base_response": "La armadura de clave es el conjunto de sostenidos o bemoles escritos al principio del pentagrama que define la tonalidad de la pieza. Estas alteraciones constantes indican al músico las notas que deben modificarse sistemáticamente a lo largo de toda la obra."
    },
    {
        "intent_id": "tonos_mayores_menores",
        "keywords": ["caracter", "escala", "alegria", "melancolia"],
        "base_response": "Las tonalidades se dividen principalmente en mayores y menores, cada una con una sonoridad y carácter expresivo propio. Las escalas mayores suelen evocar sentimientos de alegría y claridad, mientras que las menores tienden a transmitir melancolía, misterio y una mayor introspección emocional."
    },

    # Subtema 13: Solfeo cantado de notas musicales (3 concepts)
    {
        "intent_id": "solfeo_cantado_afinacion",
        "keywords": ["entonacion", "silabas", "lectura", "notas"],
        "base_response": "El solfeo cantado es el ejercicio de entonar las notas musicales pronunciando sus nombres correspondientes mientras se mantiene el ritmo preciso del compás. Esta práctica une la lectura musical visual con la emisión vocal, afinando la audición interna de manera integral."
    },
    {
        "intent_id": "solfeo_silabas_guido",
        "keywords": ["origen", "himno", "nombre", "notas"],
        "base_response": "Las sílabas de solfeo utilizadas hoy provienen de un himno religioso medieval adaptado por el monje Guido de Arezzo. Él utilizó las primeras sílabas de cada verso para fijar la altura de las notas, facilitando que los monjes memorizaran cantos rápidamente."
    },
    {
        "intent_id": "afinacion_solfeo_cantado",
        "keywords": ["control", "vocal", "oido", "intervalo"],
        "base_response": "Practicar solfeo cantado habitualmente educa el oído interno para predecir e interpretar la afinación exacta antes de emitir cualquier sonido. Esta coordinación muscular y mental entre oído y cuerdas vocales es la base de un canto afinado y preciso."
    },

    # Subtema 14: Fraseo expresivo en interpretación musical (3 concepts)
    {
        "intent_id": "fraseo_expresivo_musical",
        "keywords": ["puntuacion", "discurso", "linea", "sentido"],
        "base_response": "El fraseo expresivo consiste en agrupar las notas musicales en unidades con sentido, similar a la puntuación en un discurso hablado. Esta técnica permite al intérprete dar coherencia a la melodía, decidiendo dónde respirar, acentuar o suavizar para transmitir emociones claras."
    },
    {
        "intent_id": "articulacion_legato_staccato",
        "keywords": ["union", "separacion", "notas", "expresion"],
        "base_response": "El fraseo se enriquece mediante el uso de articulaciones contrastantes como el legato, que une las notas suavemente, o el staccato, que las separa de forma cortante. Estas opciones técnicas definen el carácter rítmico y la fluidez expresiva de la obra."
    },
    {
        "intent_id": "respiracion_fraseo_vocal",
        "keywords": ["pausa", "aire", "canto", "sentido"],
        "base_response": "En el canto y los instrumentos de viento, la respiración planificada es un componente vital del fraseo expresivo. Pausar en el momento armónico adecuado evita romper el sentido de la melodía, permitiendo entregar la frase completa con excelente soporte de aire."
    },

    # Subtema 15: Repertorio musical para coros escolares (3 concepts)
    {
        "intent_id": "repertorio_coro_escolar",
        "keywords": ["obras", "seleccion", "voces", "pedagogia"],
        "base_response": "El repertorio para coros escolares es la selección de piezas adaptadas a las capacidades vocales de niños y jóvenes. Estas obras deben seleccionarse bajo criterios pedagógicos que estimulen la afinación, fomenten el trabajo en equipo y despierten el interés por la diversidad cultural."
    },
    {
        "intent_id": "canto_unisono_escolar",
        "keywords": ["grupo", "voz", "afinacion", "coordinacion"],
        "base_response": "El canto al unísono, donde todas las voces ejecutan la misma melodía, es el primer peldaño del repertorio coral escolar. Esta práctica unifica el timbre del grupo, enseña a escuchar a los compañeros y establece las bases para cantar afinados juntos."
    },
    {
        "intent_id": "canon_coro_polifonia",
        "keywords": ["entrada", "melodia", "voces", "imitacion"],
        "base_response": "El canon es una forma polifónica ideal para coros escolares, donde los grupos interpretan la misma melodía pero inician en momentos diferentes. Esta imitación musical entrena a los alumnos a mantener su línea melódica independiente sin distraerse con las otras voces."
    },

    # Subtema 16: Matices de expresión musical escrita (3 concepts)
    {
        "intent_id": "matices_dinamicos_escritos",
        "keywords": ["volumen", "notacion", "piano", "forte"],
        "base_response": "Los matices de expresión son símbolos y palabras italianas que indican el volumen con el que debe interpretarse un pasaje. Signos comunes como forte para sonar con fuerza o piano para tocar suavemente guían la dinámica e intensidad expresiva de la obra."
    },
    {
        "intent_id": "crescendo_decrescendo_volumen",
        "keywords": ["transicion", "gradual", "fuerza", "simbolo"],
        "base_response": "El crescendo y el decrescendo indican variaciones graduales en la intensidad del sonido a lo largo de una frase. Representados por cuñas abiertas o cerradas, estos matices dinámicos añaden tensión dramática y guían la expresividad de la interpretación musical escrita."
    },
    {
        "intent_id": "matices_tempo_escritura",
        "keywords": ["velocidad", "terminos", "andante", "allegro"],
        "base_response": "Los matices de velocidad regulan el pulso de la pieza usando términos tradicionales escritos como adagio, andante o allegro. Estas palabras situadas sobre el primer pentagrama comunican al director y ejecutantes la velocidad y el carácter general que requiere la obra."
    },

    # Subtema 17: Rango de tesitura vocal musical (3 concepts)
    {
        "intent_id": "tesitura_vocal_definicion",
        "keywords": ["rango", "notas", "comodidad", "voz"],
        "base_response": "La tesitura vocal es el rango de notas en el cual un cantante emite sonido de forma cómoda, sana y con buena calidad tímbrica. A diferencia de la extensión máxima de la voz, la tesitura define la zona donde el artista puede desempeñarse fluidamente."
    },
    {
        "intent_id": "clasificacion_voces_registro",
        "keywords": ["soprano", "tenor", "altura", "clasificacion"],
        "base_response": "Las voces se clasifican por su tesitura en registros agudos como soprano para mujeres y tenor para hombres, y graves como contralto y bajo. Esta división permite asignar a cada cantante la parte coral adecuada para evitar fatiga o daño vocal."
    },
    {
        "intent_id": "cuidado_tesitura_escolar",
        "keywords": ["limites", "crecimiento", "salud", "pedagogia"],
        "base_response": "Identificar la tesitura en coros escolares requiere evaluar cuidadosamente las voces de los alumnos, que están en constante crecimiento y cambio. Seleccionar repertorio dentro de sus límites sanos previene la fatiga, promoviendo un aprendizaje coral alegre y libre de tensiones."
    },

    # Subtema 18: Canto a capela sin instrumentos (3 concepts)
    {
        "intent_id": "canto_a_capela",
        "keywords": ["vocal", "instrumentos", "afinacion", "silencio"],
        "base_response": "El canto a capela es la interpretación musical realizada exclusivamente por la voz humana, prescindiendo de cualquier acompañamiento instrumental. Esta modalidad exige un riguroso control de la afinación grupal, la sincronía y el equilibrio dinámico entre todas las secciones vocales."
    },
    {
        "intent_id": "origen_termino_capela",
        "keywords": ["historia", "iglesia", "vocal", "tradicion"],
        "base_response": "El término a capela deriva del italiano y hace referencia a la tradición de cantar en las capillas de las iglesias sin instrumentos. Históricamente, estos recintos religiosos prohibían el uso de órganos o vientos, fomentando el desarrollo de polifonías puramente vocales."
    },
    {
        "intent_id": "beneficios_canto_vocal",
        "keywords": ["desarrollo", "oido", "sincronia", "grupo"],
        "base_response": "Interpretar música a capela fomenta el desarrollo de un oído sumamente fino y atento a los armónicos naturales del canto en grupo. Al no tener soporte instrumental externo, los cantantes aprenden a ajustar su volumen y afinación en tiempo real."
    },

    # Subtema 19: Música folclórica de tradiciones culturales (3 concepts)
    {
        "intent_id": "musica_folclorica_tradicion",
        "keywords": ["identidad", "comunidad", "herencia", "oral"],
        "base_response": "La música folclórica es la expresión sonora que refleja la identidad, historia y costumbres de una comunidad transmitida por tradición oral. Estas composiciones acompañan comúnmente celebraciones religiosas, labores agrícolas y rituales, uniendo generaciones a través de cantos y ritmos tradicionales."
    },
    {
        "intent_id": "transmision_oral_folclor",
        "keywords": ["memoria", "generaciones", "cambio", "preservacion"],
        "base_response": "La transmisión oral de la música folclórica prescinde de partituras, apoyándose en la memoria, la imitación directa y la práctica comunitaria activa. Este proceso dinámico permite que las canciones se transformen sutilmente en cada generación, adaptándose a nuevos contextos sociales."
    },
    {
        "intent_id": "instrumentos_autoctonos_folclor",
        "keywords": ["materiales", "regionales", "sonoridad", "cultura"],
        "base_response": "La música tradicional utiliza instrumentos autóctonos construidos con materiales naturales de su región, como maderas locales, cañas o arcilla. Estos objetos configuran una sonoridad única ligada estrechamente a la ecología de la comunidad que expresa su cultura a través de ellos."
    },

    # Subtema 20: Instrumentos musicales electrónicos o sintetizadores (3 concepts)
    {
        "intent_id": "sintetizadores_electronicos_sonido",
        "keywords": ["señal", "oscilador", "teclado", "modificacion"],
        "base_response": "Los sintetizadores son instrumentos electrónicos que generan sonido mediante la manipulación directa de señales eléctricas a través de osciladores y filtros. Estos dispositivos permiten a los músicos crear timbres completamente nuevos e imitar con precisión instrumentos acústicos tradicionales."
    },
    {
        "intent_id": "ondas_sintetizador_forma",
        "keywords": ["frecuencia", "timbre", "modulacion", "digital"],
        "base_response": "Los sintetizadores modifican formas de onda para definir el timbre inicial, variando entre ondas senoidales, cuadradas o de sierra. Mediante la modulación de estas frecuencias y envolventes, se obtienen texturas sonoras idóneas para el diseño de música cinematográfica moderna."
    },
    {
        "intent_id": "evolucion_sintesis_digital",
        "keywords": ["tecnologia", "computadora", "sonido", "desarrollo"],
        "base_response": "La evolución de la síntesis musical pasó de pesados módulos analógicos de válvulas a ligeros sintetizadores digitales y software especializado en computadoras. Esta democratización tecnológica expandió los límites de la creación sonora, permitiendo producir producciones musicales profesionales desde un hogar."
    },

    # Subtema 21: Altura del sonido musical afinado (3 concepts)
    {
        "intent_id": "altura_sonido_afinacion",
        "keywords": ["frecuencia", "hercios", "agudo", "grave"],
        "base_response": "La altura es la cualidad física que define si un sonido musical es agudo o grave en función de su frecuencia de vibración. Medida en hercios, una frecuencia alta genera notas agudas, mientras que oscilaciones más lentas dan origen a tonos graves."
    },
    {
        "intent_id": "frecuencia_patron_afinacion",
        "keywords": ["hercios", "estandar", "afinador", "vibracion"],
        "base_response": "El estándar de afinación internacional fija la nota la en cuatrocientos cuarenta hercios de vibración constante. Esta frecuencia de referencia permite que orquestas e instrumentos construidos en diferentes países puedan acoplarse armónicamente con total precisión acústica."
    },
    {
        "intent_id": "afinacion_tension_cuerda",
        "keywords": ["altura", "fuerza", "clavija", "vibracion"],
        "base_response": "En los instrumentos de cuerda, la altura de la nota se modifica regulando la tensión de la cuerda con la clavija. Al apretar y aumentar la fuerza interna, la cuerda vibra más rápido, elevando la afinación del sonido hacia el registro agudo."
    },

    # Subtema 22: Forma musical de estrofa estribillo (3 concepts)
    {
        "intent_id": "forma_estrofa_estribillo",
        "keywords": ["estructura", "cancion", "repeticion", "seccion"],
        "base_response": "La forma de estrofa estribillo es la estructura compositiva más popular en la música moderna para organizar una pieza. Alterna secciones con letras diferentes que narran una historia, llamadas estrofas, con una sección lírica pegadiza que se repite idéntica."
    },
    {
        "intent_id": "funcion_estrofa_letra",
        "keywords": ["narracion", "desarrollo", "cancion", "armonia"],
        "base_response": "La estrofa aporta dinamismo lírico y narrativo a la canción, desarrollando los detalles de la historia de forma progresiva. Su armonía suele ser estable y conduce suavemente la atención del oyente hacia la llegada del estribillo, momento culminante de la composición."
    },
    {
        "intent_id": "estribillo_fuerza_tema",
        "keywords": ["memoria", "repeticion", "energia", "melodia"],
        "base_response": "El estribillo concentra la fuerza melódica y el mensaje principal de la obra, repitiendo siempre la misma letra y melodía. Al ser fácil de recordar, esta sección genera familiaridad en el público, uniendo todas las partes del tema musical."
    },

    # Subtema 23: Contrapunto de melodías musicales simultáneas (3 concepts)
    {
        "intent_id": "contrapunto_melodico_simultaneo",
        "keywords": ["voces", "independencia", "armonia", "lineas"],
        "base_response": "El contrapunto es la técnica compositiva que entrelaza múltiples líneas melódicas independientes para ejecutarse de manera simultánea en una obra. Cada voz posee su propio sentido rítmico y melódico, logrando una rica textura polifónica gobernada por leyes de armonía específicas."
    },
    {
        "intent_id": "contrapunto_bach_polifonia",
        "keywords": ["fuga", "historia", "armonia", "voces"],
        "base_response": "El compositor Johann Sebastian Bach perfeccionó el contrapunto mediante el desarrollo formal de la fuga, donde un tema musical migra entre diferentes voces. Esta intrincada red polifónica exige un riguroso balance para evitar que una voz ensombrezca a las demás."
    },
    {
        "intent_id": "contrapunto_notacion_reglas",
        "keywords": ["composicion", "reglas", "armonico", "intervalos"],
        "base_response": "Escribir contrapunto musical requiere respetar reglas estrictas de conducción de voces para garantizar la claridad de cada melodía independiente. Los compositores deben vigilar las distancias armónicas entre las notas, previniendo choques sonoros desagradables que confundan al oyente."
    },

    # Subtema 24: Acústica del sonido en aulas (3 concepts)
    {
        "intent_id": "acustica_sonido_aulas",
        "keywords": ["reverberacion", "ondas", "materiales", "absorcion"],
        "base_response": "La acústica en aulas estudia el comportamiento de las ondas sonoras dentro de un espacio cerrado dedicado a la enseñanza. Un diseño acústico equilibrado controla la reverberación y los ecos no deseados, asegurando que el habla y la música se escuchen claras."
    },
    {
        "intent_id": "reverberacion_eco_aulas",
        "keywords": ["reflexion", "tiempo", "paredes", "sonido"],
        "base_response": "La reverberación excesiva ocurre cuando las ondas del sonido rebotan constantemente en paredes, techos y pisos duros de un aula. Este rebote prolonga el sonido original, dificultando la inteligibilidad de las palabras del docente y causando fatiga en los estudiantes."
    },
    {
        "intent_id": "materiales_absorbentes_acustica",
        "keywords": ["paneles", "espuma", "control", "reflexion"],
        "base_response": "Instalar materiales absorbentes, como paneles de espuma acústica o cortinas gruesas, es indispensable para mejorar las aulas ruidosas. Estos elementos porosos capturan las ondas sonoras en lugar de reflejarlas, reduciendo el nivel de ruido general para facilitar la concentración."
    },

    # Subtema 25: Dictado musical de entrenamiento auditivo (3 concepts)
    {
        "intent_id": "dictado_musical_oido",
        "keywords": ["transcripcion", "escucha", "notacion", "pentagrama"],
        "base_response": "El dictado musical consiste en escuchar una melodía o ritmo e identificar y transcribir sus notas correspondientes sobre un pentagrama. Este ejercicio técnico entrena la concentración auditiva, desarrollando una conexión directa entre el oído físico y la notación musical escrita."
    },
    {
        "intent_id": "dictado_ritmico_pulsos",
        "keywords": ["figuras", "ritmo", "duracion", "escritura"],
        "base_response": "El dictado rítmico se enfoca en transcribir la duración de los sonidos agrupando las figuras musicales según los compases indicados. El alumno debe percibir el pulso inicial para plasmar con precisión negras, corcheas y silencios en el papel."
    },
    {
        "intent_id": "dictado_melodico_intervalos",
        "keywords": ["entonacion", "notas", "altura", "reconocimiento"],
        "base_response": "El dictado melódico requiere reconocer la altura exacta de las notas y las distancias de intervalo entre sonidos consecutivos. Practicar habitualmente este ejercicio ayuda a asimilar las distancias de tono y semitono, potenciando las destrezas de lectura a primera vista."
    },

    # Subtema 26: Dirección orquestal de conjuntos musicales (3 concepts)
    {
        "intent_id": "direccion_orquestal_conjuntos",
        "keywords": ["batuta", "director", "gestos", "sincronia"],
        "base_response": "La dirección orquestal coordina la interpretación colectiva de un conjunto musical mediante gestos, miradas y el uso de la batuta. El director establece el pulso, define la velocidad inicial y unifica la intensidad expresiva de las diferentes secciones instrumentales participantes."
    },
    {
        "intent_id": "batuta_dibujo_compas",
        "keywords": ["mano", "grafico", "pulso", "visual"],
        "base_response": "El director de orquesta utiliza la batuta para dibujar en el aire figuras geométricas que representan visualmente cada compás. Este trazo constante indica el inicio de cada pulso, sirviendo como guía espacial para que los músicos toquen sincronizados."
    },
    {
        "intent_id": "comunicacion_gestual_orquesta",
        "keywords": ["expresion", "dinamica", "mirada", "coherencia"],
        "base_response": "La comunicación gestual y la mirada del director transmiten matices sutiles de expresión y fuerza que la partitura no puede detallar. Con su mano izquierda, modela el volumen, señala las entradas de los instrumentos y unifica el carácter emotivo general."
    },

    # Subtema 27: Improvisación musical sobre bases rítmicas (3 concepts)
    {
        "intent_id": "improvisacion_musical_creacion",
        "keywords": ["espontaneidad", "escala", "ritmo", "melodia"],
        "base_response": "La improvisación musical consiste en crear e interpretar melodías de forma espontánea sobre una base armónica o rítmica preexistente. Esta práctica requiere un profundo conocimiento de las escalas musicales, gran agilidad mental y una estrecha coordinación técnica con el pulso rítmico."
    },
    {
        "intent_id": "base_ritmica_guia",
        "keywords": ["soporte", "tempo", "estructura", "improvisacion"],
        "base_response": "La base rítmica proporciona el soporte temporal e instrumental indispensable para guiar al músico durante su improvisación creativa. Al mantener el pulso estable, esta guía previene que el intérprete se desvíe del tempo, permitiéndole experimentar ritmos con total confianza."
    },
    {
        "intent_id": "improvisacion_escalas_notacion",
        "keywords": ["tonalidad", "recursos", "notas", "armonia"],
        "base_response": "Improvisar requiere seleccionar recursos melódicos afines a la tonalidad de la base, utilizando escalas mayor, menor o pentatónica. El músico combina estas notas de manera intuitiva, equilibrando la tensión de saltos inesperados con la distensión de notas estables armónicamente."
    }
]

def clean_word(w):
    # Strip non-alphabetic chars, but keep letters
    w = w.lower().strip()
    return re.sub(r'[^a-zñáéíóúü]', '', w)

# Strict validations
seen_intent_ids = set()
seen_keywords_tuples = set()
seen_closing_sentences = set()

# Print detailed validation stats
print(f"Total concepts defined: {len(concepts)}")

if len(concepts) < 70 or len(concepts) > 115:
    print(f"Error: Total concepts must be between 70 and 115. Found {len(concepts)}")
    sys.exit(1)

for idx, item in enumerate(concepts):
    intent_id = item['intent_id']
    keywords = item['keywords']
    base_response = item['base_response']

    # 1. intent_id format
    if not re.match(r'^[a-z_]+$', intent_id):
        print(f"Error: intent_id '{intent_id}' at index {idx} has invalid characters (must be lowercase, underscore-separated, no numbers).")
        sys.exit(1)
    if intent_id in seen_intent_ids:
        print(f"Error: duplicate intent_id '{intent_id}' at index {idx}.")
        sys.exit(1)
    seen_intent_ids.add(intent_id)

    # Check for sequential trailing digits or numbers inside the intent_id
    if any(char.isdigit() for char in intent_id):
        print(f"Error: intent_id '{intent_id}' contains digits.")
        sys.exit(1)

    # 2. keywords validations
    if len(keywords) < 4 or len(keywords) > 6:
        print(f"Error: keywords list {keywords} at index {idx} must be between 4 and 6 words. Length: {len(keywords)}")
        sys.exit(1)

    # Check keywords for tildes, casing, and stop words
    for kw in keywords:
        if re.search(r'[áéíóúÁÉÍÓÚüÜ]', kw):
            print(f"Error: keyword '{kw}' in intent '{intent_id}' contains accents/tildes or diacritics.")
            sys.exit(1)
        if kw != kw.lower():
            print(f"Error: keyword '{kw}' in intent '{intent_id}' must be lowercase.")
            sys.exit(1)
        # Check against blacklisted stop words
        if kw in STOP_WORDS:
            print(f"Error: keyword '{kw}' in intent '{intent_id}' is a blacklisted stop word/function word.")
            sys.exit(1)

    # Check duplicate keyword array
    kw_tuple = tuple(sorted(keywords))
    if kw_tuple in seen_keywords_tuples:
        print(f"Error: duplicate keywords array {keywords} in intent '{intent_id}'.")
        sys.exit(1)
    seen_keywords_tuples.add(kw_tuple)

    # 3. base_response validations
    resp_words = base_response.split()
    word_count = len(resp_words)
    if word_count < 35 or word_count > 50:
        print(f"Error: base_response in intent '{intent_id}' must be between 35 and 50 words. Current count: {word_count}.")
        print(f"Text: {base_response}")
        sys.exit(1)

    # Check blacklisted conversational words
    blacklist = ["hola", "claro", "recuerda", "segun wikipedia", "en internet", "and"]
    for word in resp_words:
        cleaned = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', '', word).lower()
        if cleaned in blacklist:
            print(f"Error: base_response in intent '{intent_id}' contains blacklisted word/conjunction '{cleaned}'.")
            sys.exit(1)

    # Check duplicate closing sentence (robotic template check)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', base_response.strip()) if s.strip()]
    if sentences:
        last_s = sentences[-1]
        # Allow some repetition but no more than 2 times to be extremely safe (the prompt/audit checks limit to <3)
        if last_s in seen_closing_sentences:
            print(f"Error: Robotic template detection! Last sentence repeated: '{last_s}' in intent '{intent_id}'")
            sys.exit(1)
        seen_closing_sentences.add(last_s)

print("All validation checks passed successfully!")

# Save to destination file
destination = "GBX_brain_83B.json"
with open(destination, "w", encoding="utf-8") as out:
    json.dump(concepts, out, ensure_ascii=False, indent=2)

print(f"Successfully generated {len(concepts)} concepts and wrote to '{destination}'.")
