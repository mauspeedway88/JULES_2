# -*- coding: utf-8 -*-
import json
import re

# Información específica y precisa de cada uno de los 30 subtemas para garantizar exactitud matemática total
SUBTEMAS_DATA = {
    "conjunto_numeros_naturales": {
        "nombre": "el conjunto de numeros naturales",
        "keywords": ["numero", "natural", "contar", "elemento", "orden", "suma", "infinito", "sucesor", "aritmetica"],
        "definicion": "los numeros enteros positivos que utilizamos ordinariamente para contar elementos, comenzando desde el numero uno en adelante",
        "aplicacion": "el conteo de pupitres, la asignacion de turnos en una fila escolar y el ordenamiento correlativo de paginas en un libro",
        "ejemplo": "contar siete manzanas en una mesa o verificar que hay veinticinco estudiantes presentes en el salon de clases de primaria",
        "error": "incluir por equivocacion el cero o los numeros negativos en este grupo, los cuales no pertenecen a la categoria de conteo puro",
        "historia": "los albores de la civilizacion humana, cuando las tribus primitivas realizaban muescas en huesos para registrar cantidades de animales",
        "propiedad": "la propiedad del sucesor unico, la cual establece que para cada valor existe un entero inmediato superior que le sigue"
    },
    "conjunto_numeros_enteros": {
        "nombre": "el conjunto de numeros enteros",
        "keywords": ["entero", "negativo", "positivo", "cero", "resta", "opuesto", "conjunto", "operacion", "signo"],
        "definicion": "el sistema numerico que comprende a los numeros naturales positivos, sus correspondientes opuestos negativos y el valor nulo representado por el cero",
        "aplicacion": "el registro de temperaturas bajo cero, la medicion de altitudes respecto al nivel del mar y el control de deudas financieras",
        "ejemplo": "expresar una perdida de diez dolares como menos diez, o una altitud de cien metros sobre el nivel del mar",
        "error": "creer erroneamente que los numeros enteros incluyen fracciones o numeros decimales, cuando solo abarcan unidades completas positivas o negativas",
        "historia": "el desarrollo comercial medieval, donde matematicos de la India adoptaron el uso de numeros negativos para contabilizar perdidas y deudas",
        "propiedad": "la existencia del elemento opuesto aditivo, garantizando que al sumar cualquier entero con su simetrico el resultado sea siempre cero"
    },
    "conjunto_numeros_racionales": {
        "nombre": "el conjunto de numeros racionales",
        "keywords": ["racional", "fraccion", "numerador", "denominador", "decimal", "division", "proporcion", "cociente"],
        "definicion": "todos aquellos numeros que pueden expresarse formalmente como el cociente o fraccion de dos numeros enteros con denominador diferente de cero",
        "aplicacion": "la particion exacta de alimentos, el calculo de porcentajes de descuento y la medicion precisa de ingredientes en recetas culinarias",
        "ejemplo": "la fraccion de tres cuartos de pizza o la expresion decimal de cero punto cinco que representa una mitad exacta",
        "error": "olvidar que el denominador jamas puede tomar el valor de cero, pues la division entre cero no esta definida matematicamente",
        "historia": "el antiguo Egipto, donde los escribas utilizaban fracciones unitarias con fines de reparticion equitativa de tierras y tributos cosechados",
        "propiedad": "la densidad infinita en la recta real, que asegura que entre dos fracciones cualesquiera siempre existira otro numero racional"
    },
    "conjunto_numeros_irracionales": {
        "nombre": "el conjunto de numeros irracionales",
        "keywords": ["irracional", "decimal", "infinito", "raiz", "patron", "geometria", "medida", "periodico"],
        "definicion": "los numeros reales que no pueden escribirse como una fraccion comun debido a que poseen infinitas cifras decimales no periodicas",
        "aplicacion": "el calculo de circunferencias exactas, el diseno de espirales logaritmicas en ingenieria y el analisis de ondas de sonido",
        "ejemplo": "el numero pi que relaciona el diametro con su circunferencia, o la raiz cuadrada de dos que mide la diagonal unitaria",
        "error": "pensar que un decimal con muchas cifras es irracional, ignorando que si las cifras repiten un patron periodico es racional",
        "historia": "la escuela pitagorica de la Grecia antigua, donde el descubrimiento de la raiz de dos provoco una profunda crisis filosofica",
        "propiedad": "la imposibilidad de ser expresados como el cociente exacto de dos enteros, requiriendo simbolos especiales para su representacion cientifica"
    },
    "sistema_numeros_reales": {
        "nombre": "el sistema de numeros reales",
        "keywords": ["real", "recta", "union", "completo", "propiedad", "intervalo", "densidad", "continuo"],
        "definicion": "la union perfecta de los numeros racionales e irracionales que permite completar totalmente la recta numerica sin dejar ningun espacio vacio",
        "aplicacion": "la medicion continua de magnitudes fisicas en la ciencia, tales como el tiempo transcurrido, la temperatura ambiente o la presion",
        "ejemplo": "cualquier valor continuo que combine numeros enteros, fracciones ordinarias y raices inexactas en un unico marco numerico integral",
        "error": "asumir que las raices cuadradas de numeros negativos pertenecen a este conjunto, olvidando que corresponden al ambito de los complejos",
        "historia": "los rigurosos trabajos matematicos de Richard Dedekind y Georg Cantor en el siglo diecinueve para dar fundamento solido al calculo",
        "propiedad": "la propiedad de completitud, la cual garantiza que a cada punto de la recta numerica le corresponde exactamente un numero real"
    },
    "concepto_numeros_imaginarios": {
        "nombre": "el concepto de numeros imaginarios",
        "keywords": ["imaginario", "unidad", "raiz", "negativa", "complejo", "ecuacion", "algebra", "rotacion"],
        "definicion": "aquellos numeros que se obtienen al multiplicar un numero real por la unidad imaginaria, definida como la raiz de menos uno",
        "aplicacion": "la simulacion de corrientes electricas alternas, el procesamiento digital de senales de audio y el analisis mecanico de fluidos",
        "ejemplo": "la expresion de tres veces la unidad imaginaria, la cual resuelve ecuaciones cuadraticas que no cruzan el eje horizontal",
        "error": "considerar que estos numeros carecen de utilidad real en la ciencia, cuando son indispensables para describir fenomenos de ondas fisicas",
        "historia": "los intentos de resolver ecuaciones cubicas por parte de Gerolamo Cardano y Rafael Bombelli durante el renacimiento italiano",
        "propiedad": "la rotacion geometrica de noventa grados que ejerce el factor imaginario al operar en el plano cartesiano de dos dimensiones"
    },
    "formacion_de_subconjuntos": {
        "nombre": "la formacion de subconjuntos",
        "keywords": ["subconjunto", "inclusion", "elemento", "pertenencia", "vacio", "conjunto", "propio", "grupo"],
        "definicion": "el proceso de agrupar una parte de los elementos de un conjunto mayor que cumplen con una caracteristica especifica",
        "aplicacion": "la clasificacion de los estudiantes de un colegio en grados, generos, edades o actividades extracurriculares especificas del aula",
        "ejemplo": "seleccionar solamente los numeros pares dentro del conjunto general de los numeros naturales del uno al diez",
        "error": "olvidar que todo conjunto es subconjunto de si mismo y que el conjunto vacio siempre esta incluido en cualquier grupo",
        "historia": "el nacimiento de la teoria de conjuntos formal desarrollada por Georg Cantor a finales de la centuria decimononica",
        "propiedad": "la relacion de inclusion, que simboliza matematicamente como cada elemento del subconjunto pertenece obligatoriamente al conjunto contenedor original"
    },
    "diagramas_de_venn": {
        "nombre": "los diagramas de Venn",
        "keywords": ["diagrama", "venn", "interseccion", "union", "grafico", "circulo", "logica", "conjunto"],
        "definicion": "las representaciones graficas en forma de circulos que permiten ilustrar visualmente las relaciones de agrupacion, exclusion e interseccion",
        "aplicacion": "la clasificacion visual de datos escolares, la resolucion de silogismos logicos y la ensenanza elemental de la teoria asociativa",
        "ejemplo": "dibujar dos circulos entrelazados para clasificar alumnos que juegan futbol, los que juegan baloncesto y aquellos que practican ambos",
        "error": "omitir la zona de interseccion o no delimitar correctamente el conjunto universal mediante un rectangulo de referencia exterior basico",
        "historia": "el ano mil ochocientos ochenta, cuando el filosofo y logico britanico John Venn publico su celebre diseno de representacion visual",
        "propiedad": "la claridad interpretativa, que permite comprender de un solo vistazo la estructura logica y las relaciones matematicas entre agrupaciones"
    },
    "interseccion_de_conjuntos": {
        "nombre": "la interseccion de conjuntos",
        "keywords": ["interseccion", "conjunto", "comun", "elemento", "coincidencia", "operacion", "simbolo", "logica"],
        "definicion": "la operacion logica que produce un nuevo conjunto integrado unicamente por los elementos compartidos simultaneamente por dos o mas grupos",
        "aplicacion": "la busqueda automatizada de perfiles coincidentes, el filtrado de bases de datos de alumnos y la seleccion de criterios comunes",
        "ejemplo": "encontrar que numeros pares menores a diez son tambien multiplos de tres, obteniendo como resultado unico el elemento seis",
        "error": "asumir incorrectamente que si no existen elementos en comun la operacion no se puede realizar, ignorando que da el conjunto vacio",
        "historia": "el desarrollo de la logica simbolica formal por George Boole, estableciendo la interseccion como equivalente de la conjuncion logica",
        "propiedad": "la propiedad conmutativa, la cual asegura que intersectar el grupo a con el b produce exactamente el mismo resultado teorico"
    },
    "union_de_elementos": {
        "nombre": "la union de elementos",
        "keywords": ["union", "elemento", "conjunto", "agrupar", "combinar", "operacion", "simbolo", "total"],
        "definicion": "la operacion algebraica de conjuntos que unifica la totalidad de los miembros pertenecientes a dos o mas agrupaciones de origen",
        "aplicacion": "la consolidacion de listas escolares, la integracion de inventarios del aula y el diseno de consultas complejas en bases de datos",
        "ejemplo": "reunir un grupo de estudiantes de ajedrez con un grupo de atletismo para formar una sola delegacion deportiva escolar",
        "error": "duplicar los elementos repetidos en la lista final, olvidando que en la teoria matematica cada miembro se escribe una sola vez",
        "historia": "la formalizacion del algebra de clases en el siglo diecinueve, donde se establecio la analogia matematica entre union y suma",
        "propiedad": "la existencia del conjunto vacio como el elemento neutro de la union, el cual no altera la agrupacion original al unirse"
    },
    "diferencia_entre_conjuntos": {
        "nombre": "la diferencia entre conjuntos",
        "keywords": ["diferencia", "conjunto", "resta", "excluir", "elemento", "operacion", "simbolo", "unico"],
        "definicion": "la operacion que da como resultado un conjunto que contiene exclusivamente los elementos del primer grupo que no estan en el segundo",
        "aplicacion": "la depuracion de listas de asistencia, la exclusion de alumnos con tareas entregadas y la seleccion de materiales escolares sobrantes",
        "ejemplo": "restar al grupo de numeros del uno al cinco el conjunto de numeros pares, obteniendo unicamente los valores impares correspondientes",
        "error": "creer que el orden de los conjuntos no altera el resultado, olvidando que esta operacion no posee la propiedad conmutativa",
        "historia": "la axiomatizacion de las matematicas modernas a principios del siglo veinte, definiendo la diferencia de clases con gran precision",
        "propiedad": "la no conmutatividad, debido a que la diferencia entre a y b difiere por completo del resultado de restar a de b"
    },
    "complemento_de_conjuntos": {
        "nombre": "el complemento de conjuntos",
        "keywords": ["complemento", "universal", "exterior", "conjunto", "exclusion", "operacion", "simbolo", "contrario"],
        "definicion": "el conjunto formado por todos los elementos del universo de referencia que no pertenecen al conjunto especificado bajo estudio actualmente",
        "aplicacion": "la identificacion automatica de estudiantes ausentes, la determinacion de tareas pendientes y la logica de exclusion binaria en programacion",
        "ejemplo": "si el universo escolar es de treinta alumnos y diez asisten, el complemento seran los veinte estudiantes que faltaron hoy",
        "error": "definir el complemento sin establecer previamente un conjunto universal claro de referencia, lo cual anula el sentido de la operacion",
        "historia": "los avances de la logica formal inglesa, donde Augustus De Morgan propuso las leyes que rigen los complementos de uniones e intersecciones",
        "propiedad": "la propiedad de involucion, que establece que el complemento del complemento de cualquier conjunto devuelve exactamente el conjunto original"
    },
    "pertenencia_de_elementos": {
        "nombre": "la pertenencia de elementos",
        "keywords": ["pertenencia", "elemento", "conjunto", "simbolo", "relacion", "incluido", "miembro", "afiliacion"],
        "definicion": "la relacion directa y fundamental de primer nivel que se establece entre un objeto individual y el conjunto que lo contiene",
        "aplicacion": "verificar si un alumno figura en la lista de calificaciones de un aula, o si una palabra es parte de un diccionario",
        "ejemplo": "comprobar que el numero entero positivo cinco pertenece al conjunto de los enteros, denotandolo formalmente con el simbolo caracteristico",
        "error": "confundir la relacion de pertenencia elemento conjunto con la relacion de inclusion conjunto conjunto, que posee leyes formales distintas",
        "historia": "la transicion de la logica informal aristotelica a la teoria axiomatica de Giuseppe Peano, quien introdujo el simbolo estilizado de pertenencia",
        "propiedad": "la relacion binaria elemental, que unicamente admite dos respuestas logicas posibles: el elemento pertenece o no pertenece al grupo evaluado"
    },
    "notacion_por_comprension": {
        "nombre": "la notacion por comprension",
        "keywords": ["comprension", "notacion", "propiedad", "caracteristica", "conjunto", "definir", "regla", "condicion"],
        "definicion": "el metodo abreviado para definir un conjunto especificando unicamente la propiedad matematica comun que deben cumplir todos sus elementos integrantes",
        "aplicacion": "la programacion de algoritmos de filtrado, la redaccion matematica simplificada de teoremas y la definicion formal de propiedades numericas",
        "ejemplo": "escribir x tal que x es un numero primo menor que cien, definiendo un conjunto numerico sin tener que enumerarlo completo",
        "error": "redactar la condicion logica de forma ambigua, permitiendo que elementos no deseados cumplan con la regla y desestabilicen el conjunto",
        "historia": "la busqueda de rigor sintactico en el algebra alemana del siglo diecinueve para evitar paradojas asociadas al lenguaje coloquial ordinario",
        "propiedad": "la generalizacion estructural, que permite representar conjuntos de tamano infinito mediante una regla conceptual compacta, elegante y precisa"
    },
    "notacion_por_extension": {
        "nombre": "la notacion por extension",
        "keywords": ["extension", "notacion", "listar", "elemento", "conjunto", "llave", "enumerar", "escribir"],
        "definicion": "la forma explicita de representar un conjunto escribiendo y enumerando directamente cada uno de sus elementos individuales separados por comas",
        "aplicacion": "la elaboracion detallada de inventarios de clase, la redaccion de listas nominativas de estudiantes y la definicion de conjuntos pequenos",
        "ejemplo": "representar el conjunto de vocales de nuestro abecedario escribiendo directamente entre llaves las letras a, e, i, o, u",
        "error": "tratar de utilizar este metodo para conjuntos infinitos sin emplear puntos suspensivos que indiquen que la secuencia continua ordenadamente",
        "historia": "los origenes del conteo y registro en papiros antiguos, donde se requeria detallar minuciosamente cada recurso disponible del imperio",
        "propiedad": "la claridad nominativa, la cual elimina cualquier tipo de duda sobre si un elemento especifico forma parte o no de la agrupacion"
    },
    "recta_numerica_real": {
        "nombre": "la recta numerica real",
        "keywords": ["recta", "numerica", "real", "punto", "orden", "distancia", "origen", "coordenada"],
        "definicion": "la representacion grafica unidimensional donde cada numero real se asocia de forma biunivoca con un punto geometrico continuo del eje",
        "aplicacion": "la visualizacion geometrica de desigualdades algebraicas, la ensenanza didactica de la suma escolar y la representacion grafica de intervalos",
        "ejemplo": "marcar el origen cero, ubicar los enteros positivos a la derecha y situar con precision los valores negativos a la izquierda",
        "error": "creer que existen espacios vacios entre los numeros reales de la recta, ignorando la perfecta continuidad del conjunto numerico",
        "historia": "la integracion de la geometria de Descartes con el analisis numerico, permitiendo unificar el algebra y la representacion espacial continua",
        "propiedad": "el orden total, el cual garantiza que para dos puntos cualesquiera situados en la recta uno estara siempre a la izquierda del otro"
    },
    "cardinalidad_del_conjunto": {
        "nombre": "la cardinalidad del conjunto",
        "keywords": ["cardinalidad", "conjunto", "elemento", "tamano", "contar", "medida", "cantidad", "numero"],
        "definicion": "el numero o medida que indica la cantidad exacta de elementos unicos presentes dentro de un conjunto determinado bajo analisis",
        "aplicacion": "el control estadistico de estudiantes matriculados, la determinacion del tamano de muestras cientificas y el analisis combinatorio basico",
        "ejemplo": "establecer que la cardinalidad del conjunto de estaciones del ano es exactamente cuatro, pues consta de cuatro periodos definidos",
        "error": "contar varias veces un elemento repetido dentro del conjunto, lo cual sobreestima erroneamente la cardinalidad real del grupo estudiado",
        "historia": "el trabajo de Georg Cantor sobre los infinitos transitivos, demostrando que existen diferentes tamaños de infinito en la matematica pura",
        "propiedad": "la invarianza bajo biyecciones, la cual asegura que dos conjuntos tienen igual cardinalidad si se pueden emparejar uno a uno totalmente"
    },
    "conjunto_vacio_nulo": {
        "nombre": "el conjunto vacio nulo",
        "keywords": ["vacio", "nulo", "elemento", "conjunto", "simbolo", "cero", "ausencia", "propiedad"],
        "definicion": "el conjunto matematico especial que se caracteriza fundamentalmente por la total ausencia de elementos en su interior",
        "aplicacion": "la definicion de filtros sin coincidencias en bases de datos escolares, la logica proposicional extrema y el modelado de eventos imposibles",
        "ejemplo": "el conjunto de seres humanos vivos que tienen mas de trescientos anos de edad, el cual carece por completo de representantes",
        "error": "confundir el conjunto vacio con el numero cero o escribir el simbolo de vacio dentro de llaves, creando un conjunto de cardinalidad uno",
        "historia": "la sistematizacion de la logica formal y la teoria de conjuntos formalizada por Ernst Zermelo en el siglo veinte",
        "propiedad": "la propiedad de ser subconjunto unico de cualquier conjunto existente, lo cual constituye un axioma basico en las matematicas escolares"
    },
    "conjunto_universal_base": {
        "nombre": "el conjunto universal base",
        "keywords": ["universal", "base", "conjunto", "universo", "elemento", "referencia", "totalidad", "contener"],
        "definicion": "el conjunto de referencia que contiene la totalidad de los elementos y subconjuntos involucrados en un analisis matematico escolar particular",
        "aplicacion": "la delimitacion de censos demograficos de estudiantes, la definicion de rangos de busqueda de datos y la resolucion de diagramas escolares",
        "ejemplo": "establecer que el conjunto universal para un problema sobre escolares es la lista de alumnos matriculados en ese establecimiento",
        "error": "considerar que existe un conjunto universal absoluto que contiene a absolutamente todo, lo cual genera graves contradicciones y paradojas logicas",
        "historia": "la paradoja de Bertrand Russell que demostro la necesidad de limitar los universos de discurso para evitar colapsos logicos en la teoria",
        "propiedad": "la propiedad de ser el elemento neutro en la interseccion, ya que intersectar cualquier conjunto con su universo devuelve el mismo conjunto"
    },
    "clasificacion_de_numeros": {
        "nombre": "la clasificacion de numeros",
        "keywords": ["clasificacion", "numero", "conjunto", "tipo", "grupo", "propiedad", "estructura", "ordenar"],
        "definicion": "el proceso pedagogico de ordenar y categorizar los diferentes tipos de numeros en conjuntos anidados segun sus propiedades estructurales",
        "aplicacion": "la organizacion curricular de los programas de matematicas escolares y la simplificacion del analisis cientifico de variables continuas y discretas",
        "ejemplo": "estructurar los numeros de menor a mayor complejidad en naturales, enteros, racionales, reales y finalmente numeros complejos abstractos",
        "error": "colocar un numero racional fuera de los reales, ignorando que los reales engloban a todas las fracciones y decimales existentes",
        "historia": "la evolucion del pensamiento cientifico que fue incorporando nuevos numeros conforme surgian necesidades de resolucion de ecuaciones algebraicas",
        "propiedad": "la inclusion jerarquica sucesiva, que demuestra de forma didactica como cada conjunto numerico es subconjunto propio del siguiente sistema superior"
    },
    "propiedad_de_cerradura": {
        "nombre": "la propiedad de cerradura",
        "keywords": ["cerradura", "propiedad", "operacion", "conjunto", "resultado", "interno", "suma", "multiplicacion"],
        "definicion": "la propiedad que garantiza que al realizar una operacion matematica con elementos de un conjunto el resultado obtenido pertenezca al mismo conjunto",
        "aplicacion": "el diseno seguro de sistemas informaticos y la validacion de ecuaciones algebraicas dentro de un sistema numerico escolar cerrado",
        "ejemplo": "sumar dos numeros naturales cualesquiera da como resultado obligatorio otro numero natural, cumpliendo con la ley de clausura de la suma",
        "error": "creer que la resta es cerrada en los numeros naturales, ignorando que al restar cinco de tres el resultado es negativo",
        "historia": "el desarrollo de la teoria de estructuras algebraicas como grupos y anillos por matematicos del siglo diecinueve como Evariste Galois",
        "propiedad": "la estabilidad operativa del sistema, la cual permite trabajar matematicamente con absoluta certeza de no generar resultados fuera del dominio definido"
    },
    "elementos_pares_positivos": {
        "nombre": "los elementos pares positivos",
        "keywords": ["par", "positivo", "numero", "divisible", "multiplo", "conjunto", "entero", "paridad"],
        "definicion": "el subconjunto de numeros enteros mayores a cero que son exactamente divisibles entre dos, dejando un residuo igual a cero",
        "aplicacion": "la organizacion de turnos alternos en la escuela, la distribucion de filas en el aula y la programacion de algoritmos basicos de paridad",
        "ejemplo": "la secuencia numerica escolar integrada por los valores de dos, cuatro, seis, ocho, diez, doce y catorce sucesivamente",
        "error": "clasificar por equivocacion un numero decimal terminado en cifra par dentro de este grupo, ignorando que la paridad es exclusiva de enteros",
        "historia": "los estudios pitagoricos sobre la armonia de los numeros, donde los pares representaban principios de simetria y dualidad en el cosmos",
        "propiedad": "la propiedad de cerradura bajo la suma, la cual asegura que al sumar dos pares positivos obtenemos siempre otro valor par"
    },
    "elementos_impares_positivos": {
        "nombre": "los elementos impares positivos",
        "keywords": ["impar", "positivo", "numero", "paridad", "resto", "conjunto", "entero", "secuencia"],
        "definicion": "el subconjunto de numeros enteros mayores a cero que no son divisibles exactamente entre dos, dejando siempre un residuo igual a uno",
        "aplicacion": "el control de calendarios escolares alternados, la programacion de bucles informaticos y la distribucion simetrica de espacios en el plano",
        "ejemplo": "los numeros de uso escolar cotidiano como el uno, tres, cinco, siete, nueve, once y trece en orden progresivo infinito",
        "error": "pensar que el cero puede considerarse un numero impar, cuando en realidad es un numero par debido a su divisibilidad formal por dos",
        "historia": "la antigua matematica griega, que consideraba a los numeros impares como masculinos y dotados de propiedades de indivisibilidad misticas",
        "propiedad": "la regla del producto constante, la cual establece que al multiplicar dos impares cualesquiera el resultado es obligatoriamente otro impar"
    },
    "multiplos_numericos_basicos": {
        "nombre": "los multiplos numericos basicos",
        "keywords": ["multiplo", "numero", "multiplicar", "tabla", "producto", "conjunto", "secuencia", "factor"],
        "definicion": "los numeros que se obtienen al multiplicar un numero entero especifico por cada uno de los numeros naturales del sistema de forma secuencial",
        "aplicacion": "el calculo de periodos de tiempo coincidentes en la escuela, la sincronizacion de eventos y la resolucion de problemas de reparto",
        "ejemplo": "los multiplos de cinco representados por los valores de diez, quince, veinte, veinticinco y treinta obtenidos al multiplicar",
        "error": "confundir los multiplos de un numero con sus divisores, olvidando que los multiplos son infinitos mientras los divisores son de cantidad finita",
        "historia": "la sistematizacion de las tablas de multiplicar atribuida historicamente al gran pensador y matematico griego Pitagoras de Samos",
        "propiedad": "la infinitud del conjunto de multiplos, la cual asegura que no existe un multiplo maximo para ningun numero entero dado"
    },
    "divisores_numericos_exactos": {
        "nombre": "los divisores numericos exactos",
        "keywords": ["divisor", "exacto", "division", "resto", "cero", "factor", "numero", "entero"],
        "definicion": "los numeros enteros que dividen a otro numero de forma exacta, dando como resultado una division con residuo igual a cero",
        "aplicacion": "la particion equitativa de recursos en el salon de clases, la simplificacion de fracciones y el calculo del maximo comun divisor",
        "ejemplo": "establecer que los divisores exactos del numero doce son el uno, dos, tres, cuatro, seis y el propio numero doce",
        "error": "creer que los divisores de un numero entero pueden ser mayores que el propio numero estudiado, lo cual es logicamente imposible",
        "historia": "el desarrollo de la aritmetica basica por la civilizacion china antigua, quienes disenaron metodos de calculo basados en factores exactos",
        "propiedad": "la simetria de pares divisores, la cual establece que los divisores de un numero siempre se presentan en parejas asociadas por multiplicacion"
    },
    "numeros_primos_fundamentales": {
        "nombre": "los numeros primos fundamentales",
        "keywords": ["primo", "divisor", "unico", "numero", "unidad", "fundamental", "factorizacion", "conjunto"],
        "definicion": "los numeros enteros mayores que uno que unicamente poseen dos divisores exactos distintos: el numero uno y ellos mismos",
        "aplicacion": "la factorizacion unica de numeros en la escuela, la encriptacion de datos digitales y la seguridad de contrasenas en la web",
        "ejemplo": "los numeros de uso escolar tales como el dos, tres, cinco, siete, once, trece y diecisiete en orden de magnitud",
        "error": "considerar erroneamente al numero uno como un numero primo, omitiendo que la definicion exige tener exactamente dos divisores distintos",
        "historia": "los Elementos de Euclides escritos en el ano trescientos antes de Cristo, donde se demostro que los numeros primos son infinitos",
        "propiedad": "el teorema fundamental de la aritmetica, el cual dicta que todo numero compuesto se factoriza de forma unica como producto de primos"
    },
    "numeros_compuestos_divisibles": {
        "nombre": "los numeros compuestos divisibles",
        "keywords": ["compuesto", "divisor", "numero", "multiplo", "factor", "divisible", "sintesis", "conjunto"],
        "definicion": "los numeros enteros mayores que uno que poseen mas de dos divisores exactos, pudiendo descomponerse en factores primos mas simples",
        "aplicacion": "la resolucion de problemas escolares de distribucion, el empaquetado eficiente de productos en el comercio y el diseno de mallas",
        "ejemplo": "el numero cuatro que es divisible por uno, dos y cuatro, o el numero seis que se compone del producto de dos por tres",
        "error": "confundir los numeros compuestos con los numeros pares, olvidando que existen numeros compuestos impares muy comunes como el nueve",
        "historia": "las investigaciones de matematicos arabes medievales como Al-Juarismi en la sistematizacion de la descomposicion de enteros",
        "propiedad": "la propiedad de factorizacion, la cual garantiza que todo compuesto puede expresarse como la multiplicacion ordenada de valores primos basicos"
    },
    "criba_de_eratostenes": {
        "nombre": "la criba de Eratostenes",
        "keywords": ["criba", "eratostenes", "algoritmo", "primo", "filtrar", "numero", "tabla", "metodo"],
        "definicion": "el algoritmo pedagogico de filtrado sucesivo ideado para hallar de manera sistematica todos los numeros primos hasta un limite dado",
        "aplicacion": "la busqueda de numeros primos en programacion escolar, el diseno de actividades didacticas interactivas y el desarrollo del calculo mental",
        "ejemplo": "construir una tabla del uno al cien e ir tachando secuencialmente los multiplos de dos, tres, cinco y siete paso a paso",
        "error": "olvidar tachar el numero uno al inicio del proceso escolar, lo cual causaria considerarlo erroneamente como un numero primo resultante",
        "historia": "el matematico griego Eratostenes de Cirene, quien en el siglo tercero antes de Cristo diseno este ingenioso metodo de filtrado",
        "propiedad": "la eficiencia algoritmica elemental, que permite identificar numeros primos de forma visual y sistematica sin requerir realizar divisiones complejas individuales"
    },
    "valor_absoluto_numerico": {
        "nombre": "el valor absoluto numerico",
        "keywords": ["absoluto", "valor", "distancia", "origen", "positivo", "numero", "recta", "signo"],
        "definicion": "la distancia geometrica real y positiva que existe sobre la recta numerica real entre un numero determinado y el origen representado por el cero",
        "aplicacion": "el calculo de distancias fisicas entre coordenadas, la medicion del error absoluto en experimentos escolares y la resolucion de inecuaciones",
        "ejemplo": "establecer que el valor absoluto de menos cinco es exactamente cinco, puesto que se encuentra a cinco unidades del origen cero",
        "error": "asumir que el valor absoluto cambia siempre el signo del numero, cuando en realidad solo fuerza a que el resultado final sea positivo",
        "historia": "la introduccion formal del simbolo de barras verticales por el matematico aleman Karl Weierstrass en el ano mil ochocientos cuarenta y uno",
        "propiedad": "la propiedad de no negatividad, la cual define que el resultado de esta operacion es siempre mayor o igual a cero para todo numero real"
    },
    "opuesto_aritmetico_aditivo": {
        "nombre": "el opuesto aritmetico aditivo",
        "keywords": ["opuesto", "aditivo", "aritmetico", "suma", "cero", "signo", "negativo", "inverso"],
        "definicion": "el numero simetrico que tiene la misma distancia al origen pero con signo contrario, anulandose mutuamente al sumarse",
        "aplicacion": "el modelado de transacciones de balance de saldo escolar, la resolucion de restas algebraicas y el calculo de vectores simetricos en fisica",
        "ejemplo": "establecer que el opuesto aditivo de siete positivo es menos siete, puesto que al sumarlos obtenemos exactamente cero como resultado",
        "error": "confundir el opuesto aritmetico aditivo con el inverso multiplicativo, el cual invierte el numerador y el denominador de la fraccion",
        "historia": "el descubrimiento y formalizacion de las leyes de los signos y del elemento simetrico por matematicos de la antigua India y China",
        "propiedad": "la propiedad de simetria bilateral, la cual asegura que el opuesto aditivo del opuesto de un numero devuelve siempre el valor original"
    }
}

# Definición de los 30 enfoques educativos enriquecidos y adaptados para recibir variables específicas del subtema
ENFOQUES_PLANTILLAS = [
    {
        "nombre": "definicion",
        "plantilla": "El concepto de {nombre} representa uno de los pilares educativos mas importantes de la matematica. Se define formalmente como {definicion}, permitiendo resolver problemas practicos de forma estructurada, logica y ordenada en el aula."
    },
    {
        "nombre": "aplicacion",
        "plantilla": "La aplicacion didactica de {nombre} se observa de manera constante en multiples situaciones del entorno escolar cotidiano. Es de enorme utilidad practica en {aplicacion}, optimizando nuestro pensamiento matematico y destreza analitica."
    },
    {
        "nombre": "ejemplo",
        "plantilla": "Un ejemplo practico sobre {nombre} consiste en {ejemplo}. Al realizar esta actividad, los estudiantes del salon de clases comprenden visualmente las leyes asociadas de manera sencilla, dinamica, interactiva y enriquecedora."
    },
    {
        "nombre": "error",
        "plantilla": "Un error comun al estudiar {nombre} consiste en {error}. Es fundamental analizar con calma cada elemento de las tareas para evitar confusiones clasicas que alteran la correcta resolucion de los ejercicios de examen."
    },
    {
        "nombre": "historia",
        "plantilla": "La historia de {nombre} nos traslada a {historia}. El estudio continuo de estas estructuras y conceptos clave ha evolucionado constantemente, permitiendo a la humanidad disenar sistemas de calculo increiblemente eficientes y modernos."
    },
    {
        "nombre": "curriculo",
        "plantilla": "El estudio formal de {nombre} ocupa un lugar privilegiado en el curriculo escolar, ya que estimula el razonamiento logico del estudiante. Dominar este tema facilita la asimilacion progresiva de conceptos complejos en la educacion superior."
    },
    {
        "nombre": "propiedad",
        "plantilla": "La propiedad primordial de {nombre} radica en {propiedad}. Esta cualidad esencial asegura que todas las deducciones cientificas esten basadas en leyes logicas validas, claras, seguras y plenamente verificables por el maestro."
    },
    {
        "nombre": "relacion",
        "plantilla": "La estrecha relacion entre {nombre} y las demas agrupaciones del sistema numerico demuestra la armonia de la matematica didactica escolar. Cada componente interactua de forma directa para construir un conocimiento integrado que fortalece la comprension general."
    },
    {
        "nombre": "pregunta",
        "plantilla": "Una pregunta frecuente que formulan los alumnos sobre {nombre} es como diferenciarlo correctamente de estructuras conceptuales similares. La respuesta educativa consiste en revisar detalladamente las condiciones exclusivas que definen a este tema logico unico."
    },
    {
        "nombre": "juego",
        "plantilla": "Un juego interactivo util para comprender {nombre} consiste en organizar fichas numericas de colores siguiendo un criterio pedagogico preestablecido. Esta actividad escolar dinamica despierta el interes cientifico de los alumnos de manera divertida."
    },
    {
        "nombre": "visual",
        "plantilla": "Para visualizar facilmente {nombre}, resulta de enorme utilidad trazar representaciones graficas o esquemas ilustrativos en el cuaderno. Estos apoyos visuales aclaran la mente del estudiante, facilitando la comprension de las operaciones y calculos escolares."
    },
    {
        "nombre": "ciencia",
        "plantilla": "En el ambito de la ciencia y la tecnologia, {nombre} es una herramienta clave para modelar fenomenos naturales con rigor cientifico. Los investigadores usan estas estructuras para disenar programas, analizar datos de laboratorio y formular teorias."
    },
    {
        "nombre": "simbolo",
        "plantilla": "La representacion simbolica de {nombre} permite comunicar ideas complejas de manera abreviada, precisa y universal en la ciencia. Aprender a leer esta notacion ayuda al alumno a resolver problemas escolares con mayor confianza y autonomia."
    },
    {
        "nombre": "regla",
        "plantilla": "Una regla pedagogica practica para dominar {nombre} consiste en asociar cada palabra tecnica con un ejemplo visual de tu vida diaria. Este metodo de asociacion didactica mejora la memoria y facilita la explicacion del tema en clases."
    },
    {
        "nombre": "origen",
        "plantilla": "El origen etimologico del termino {nombre} alude a la necesidad de clasificar elementos para darles un sentido logico ordenado. Comprender esta raiz conceptual ayuda al estudiante a conectar la definicion abstracta con un concepto real y util."
    },
    {
        "nombre": "curiosidad",
        "plantilla": "Una curiosidad cientifica sobre {nombre} es que, a pesar de su estructura aparentemente simple, esconde propiedades matematicas asombrosas de gran profundidad. Su estudio continuo ha permitido resolver paradojas historicas y sigue fascinando a los docentes."
    },
    {
        "nombre": "desafio",
        "plantilla": "Te invitamos a resolver un divertido desafio escolar relacionado con {nombre}: busca tres aplicaciones reales de este concepto dentro de tu propio hogar. Compartir esta busqueda interactiva con tu familia facilitara la comprension didactica del tema."
    },
    {
        "nombre": "ventaja",
        "plantilla": "La ventaja principal de comprender a fondo {nombre} es el desarrollo de una mente mas agil, analitica y estructurada para tomar decisiones. Esta habilidad academica no solo mejora tus calificaciones, sino que optimiza tu capacidad de resolucion."
    },
    {
        "nombre": "limitacion",
        "plantilla": "Al estudiar {nombre}, es importante identificar sus limitaciones teoricas dentro de las operaciones matematicas permitidas del sistema. Reconocer estos limites previene que cometas errores conceptuales graves al realizar demostraciones o resolver problemas planteados por profesores."
    },
    {
        "nombre": "proceso",
        "plantilla": "El proceso pedagogico para dominar {nombre} consiste en tres pasos: primero identificar los elementos, segundo analizar la ley comun, y tercero comprobar sus propiedades. Seguir esta secuencia didactica garantiza un aprendizaje seguro, eficaz y altamente provechoso."
    },
    {
        "nombre": "semejanza",
        "plantilla": "La semejanza fundamental entre {nombre} y otros conceptos similares nos revela la hermosa conexion interna del pensamiento logico escolar. Ambos temas persiguen clasificar informacion de forma exacta, lo que te permite aplicar metodos de estudio comunes."
    },
    {
        "nombre": "diferencia",
        "plantilla": "Aprender la diferencia exacta entre {nombre} y otras estructuras del mismo nivel educativo es crucial para evitar errores en las evaluaciones. Mientras un concepto se enfoca en la agrupacion logica, el otro analiza las leyes operacionales del sistema."
    },
    {
        "nombre": "geometria",
        "plantilla": "Desde una perspectiva geometrica muy didactica, {nombre} puede representarse mediante puntos ordenados sobre lineas o regiones del plano visual. Esta analogia espacial favorece la comprension intuitiva, haciendo mas facil el analisis del tamano del conjunto."
    },
    {
        "nombre": "vocabulario",
        "plantilla": "Enriquecer tu vocabulario escolar con terminos asociados a {nombre} es indispensable para expresarte con propiedad academica en clases. Conceptos tecnicos como relacion, orden o elemento te permitiran comprender mejor las lecciones de tu profesor de matematicas."
    },
    {
        "nombre": "naturaleza",
        "plantilla": "Podemos observar la presencia de {nombre} en la naturaleza al contemplar los patrones simetricos de las flores o las galaxias. Estos asombrosos ejemplos reales demuestran que las estructuras matematicas escolares organizan y rigen de manera perfecta el universo."
    },
    {
        "nombre": "causa",
        "plantilla": "La causa de la invencion de {nombre} fue la necesidad que tenian las sociedades de cuantificar e intercambiar mercancias equitativamente. Los sabios crearon este marco conceptual para facilitar las transacciones comerciales y perfeccionar la administracion del territorio escolar."
    },
    {
        "nombre": "efecto",
        "plantilla": "El efecto directo de aplicar {nombre} en la resolucion de problemas cotidianos es una disminucion notable de la dificultad de calculo. Esta herramienta simplifica operaciones complejas, permitiendo hallar respuestas correctas de forma mas agil, segura y eficiente."
    },
    {
        "nombre": "orden",
        "plantilla": "La propiedad de orden y posicion de {nombre} establece un ordenamiento jerarquico riguroso que facilita la clasificacion de datos escolares. Esta organizacion secuencial es clave para comprender como se relacionan las variables numericas individuales en el sistema."
    },
    {
        "nombre": "conclusion",
        "plantilla": "Como conclusion didactica, {nombre} representa mucho mas que una definicion teorica que debes memorizar para el examen escolar de matematicas. Es una valiosa guia mental para comprender el orden logico y desarrollar una mentalidad cientifica."
    },
    {
        "nombre": "ejercicio",
        "plantilla": "Para realizar con exito un ejercicio sobre {nombre}, te sugerimos escribir de forma ordenada los datos en tu cuaderno escolar antes de operar. Al resolver paso a paso y revisar cada resultado, consolidaras este conocimiento didactico."
    }
]

# Lista de frases de ajuste de longitud (para rellenar si es necesario, de menor a mayor longitud)
FRASES_AJUSTE = [
    "Aprende siempre con gran entusiasmo hoy.",
    "Comprender este concepto es muy importante en la escuela.",
    "Usa este valioso conocimiento didactico escolar en tus tareas.",
    "Un concepto fundamental para tu educacion escolar de hoy en dia.",
    "Practica resolviendo ejercicios para dominar el tema escolar con tu maestro.",
    "Sigue estos consejos pedagogicos para mejorar tus habilidades matematicas en el salon."
]

def contar_palabras(texto):
    return len(texto.split())

def ajustar_longitud(texto, min_p=35, max_p=50):
    palabras = texto.split()
    conteo = len(palabras)

    if min_p <= conteo <= max_p:
        return texto

    if conteo < min_p:
        # Añadir frases de ajuste hasta cumplir con el mínimo
        for frase in FRASES_AJUSTE:
            texto_propuesto = texto + " " + frase
            conteo_propuesto = contar_palabras(texto_propuesto)
            if min_p <= conteo_propuesto <= max_p:
                return texto_propuesto
            if conteo_propuesto < min_p:
                texto = texto_propuesto # Acumular para el siguiente intento
        # Si sigue siendo menor, agregar palabras simples
        while contar_palabras(texto) < min_p:
            texto += " repasa siempre hoy."
        return texto

    if conteo > max_p:
        # En lugar de cortar palabras a la fuerza, dividimos por oraciones y nos quedamos con las que quepan
        oraciones = re.split(r'(?<=[.!?])\s+', texto)
        texto_acumulado = ""
        for oracion in oraciones:
            oracion = oracion.strip()
            if not oracion:
                continue
            test_texto = (texto_acumulado + " " + oracion).strip() if texto_acumulado else oracion
            if contar_palabras(test_texto) <= max_p:
                texto_acumulado = test_texto
            else:
                break

        # Si al quitar oraciones completas queda muy corto (menos de min_p), o si la primera oración ya es muy larga,
        # recortamos la primera oración de forma suave usando comas o puntos lógicos si existen, o simplemente palabras.
        # Pero nos aseguramos de que el texto conserve coherencia.
        if contar_palabras(texto_acumulado) < min_p:
            # Caso extremo de recorte por palabras:
            palabras_recortadas = palabras[:max_p]
            # Limpiar comas finales o conectores flotantes
            texto_recortado = " ".join(palabras_recortadas)
            texto_recortado = re.sub(r'[,;:\s]+$', '', texto_recortado)
            if not texto_recortado.endswith("."):
                texto_recortado += "."
            return texto_recortado

        return texto_acumulado

def generar_conceptos():
    conceptos = []

    # Procesar cada uno de los 30 subtemas en orden
    for subtema_key, subtema_info in SUBTEMAS_DATA.items():
        sub_nombre = subtema_info["nombre"]
        sub_keywords = subtema_info["keywords"]

        # Obtener los campos de datos específicos para la interpolación correcta y verídica
        definicion = subtema_info["definicion"]
        aplicacion = subtema_info["aplicacion"]
        ejemplo = subtema_info["ejemplo"]
        error = subtema_info["error"]
        historia = subtema_info["historia"]
        propiedad = subtema_info["propiedad"]

        for idx, enfoque in enumerate(ENFOQUES_PLANTILLAS):
            enfoque_nombre = enfoque["nombre"]
            plantilla = enfoque["plantilla"]

            # Reemplazar de forma verídica y personalizada según el subtema
            base_response = plantilla.format(
                nombre=sub_nombre,
                definicion=definicion,
                aplicacion=aplicacion,
                ejemplo=ejemplo,
                error=error,
                historia=historia,
                propiedad=propiedad
            )

            # Ajustar rigurosamente la longitud entre 35 y 50 palabras
            base_response = ajustar_longitud(base_response, min_p=35, max_p=50)

            # Generar el intent_id único
            intent_id = "{subtema}_v{v:02d}".format(subtema=subtema_key, v=idx+1)

            # Generar keywords únicas: de 4 a 6 palabras clave, solo minúsculas, sin tildes ni ñ
            enfoque_kw = enfoque_nombre
            kws = list(sub_keywords)
            pos = idx % (len(sub_keywords) - 1)
            kws.insert(pos, enfoque_kw)

            selected_kws = kws[:5]

            clean_kws = []
            for kw in selected_kws:
                kw_clean = kw.lower()
                kw_clean = kw_clean.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                kw_clean = kw_clean.replace("ñ", "n")
                kw_clean = re.sub(r'[^a-z0-9_]', '', kw_clean)
                if kw_clean:
                    clean_kws.append(kw_clean)

            if len(clean_kws) < 4:
                clean_kws.append("matematica")
            if len(clean_kws) > 6:
                clean_kws = clean_kws[:6]

            conceptos.append({
                "intent_id": intent_id,
                "keywords": clean_kws,
                "base_response": base_response
            })

    return conceptos

def validar_conceptos(conceptos):
    print("Iniciando validación rigurosa de los conceptos generados...")

    conteo = len(conceptos)
    print("Total de conceptos generados: {}".format(conteo))
    assert conteo == 900, "Error: Se esperaban exactamente 900 conceptos, pero se generaron {}.".format(conteo)

    intent_ids = set()
    stop_words_es = {"de", "la", "el", "un", "una", "y", "o", "en", "con", "para", "a", "los", "las", "un", "unos", "unas"}

    for idx, c in enumerate(conceptos):
        assert set(c.keys()) == {"intent_id", "keywords", "base_response"}, "Error en concepto {}: Estructura incorrecta.".format(idx)

        intent_id = c["intent_id"]
        keywords = c["keywords"]
        base_response = c["base_response"]

        assert intent_id == intent_id.lower(), "Error en intent_id {}: No está en minúsculas.".format(intent_id)
        assert re.match(r'^[a-z0-9_]+$', intent_id), "Error en intent_id {}: Contiene caracteres especiales prohibidos o tildes/ñ.".format(intent_id)
        assert intent_id not in intent_ids, "Error en intent_id {}: Duplicado.".format(intent_id)
        intent_ids.add(intent_id)

        assert len(keywords) >= 4 and len(keywords) <= 6, "Error en {}: Keywords debe tener entre 4 y 6 términos, tiene {}.".format(intent_id, len(keywords))
        for kw in keywords:
            assert kw == kw.lower(), "Error en {}: Palabra clave {} no está en minúsculas.".format(intent_id, kw)
            assert re.match(r'^[a-z0-9_]+$', kw), "Error en {}: Palabra clave {} contiene caracteres especiales, tildes o ñ.".format(intent_id, kw)
            assert kw not in stop_words_es, "Error en {}: Palabra clave {} es una stop-word prohibida.".format(intent_id, kw)

        p_conteo = contar_palabras(base_response)
        assert p_conteo >= 35 and p_conteo <= 50, "Error en {}: base_response tiene {} palabras, fuera del rango [35, 50]. Texto: {}".format(intent_id, p_conteo, base_response)

    print("¡Excelente! Todos los 900 conceptos han aprobado satisfactoriamente las estrictas reglas de validación.")

if __name__ == "__main__":
    conceptos = generar_conceptos()
    validar_conceptos(conceptos)

    with open("MM_brain_01.json", "w") as f:
        json.dump(conceptos, f, indent=4)
    print("Archivo MM_brain_01.json guardado exitosamente en la raíz.")
