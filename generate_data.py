import json
import re
import unicodedata

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def process_keywords(keywords_list):
    stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'e', 'ni', 'o', 'u', 'de', 'del', 'a', 'ante', 'bajo', 'con', 'contra', 'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 'por', 'segun', 'sin', 'sobre', 'tras'}
    cleaned = []
    for word in keywords_list:
        word = normalize_text(word.lower())
        if word not in stop_words and word.isalpha():
            cleaned.append(word)
    return list(dict.fromkeys(cleaned))[:6]

data = [
    {
        "intent_id": "numeros_naturales",
        "keywords": ["numeros", "naturales", "contar", "ordenar", "infinitos", "positivos"],
        "base_response": "Los números naturales constituyen el conjunto básico utilizado para contar y ordenar elementos. Comienzan convencionalmente desde el uno, aunque algunos autores incluyen el cero. Son infinitos, siempre positivos y fundamentales para comprender las operaciones aritméticas elementales y construir sistemas numéricos complejos."
    },
    {
        "intent_id": "numeros_enteros",
        "keywords": ["numeros", "enteros", "negativos", "cero", "deuda", "resta"],
        "base_response": "El conjunto de los números enteros amplía los naturales al incorporar los valores negativos correspondientes y el cero. Esta extensión matemática permite representar situaciones de deuda, temperaturas bajo cero o profundidades, garantizando que la operación de resta siempre tenga una solución válida."
    },
    {
        "intent_id": "numeros_racionales",
        "keywords": ["numeros", "racionales", "fracciones", "cociente", "decimales", "medir"],
        "base_response": "Los números racionales son aquellos que pueden expresarse como el cociente de dos números enteros, donde el denominador nunca es cero. Incluyen fracciones y números decimales finitos o periódicos, siendo esenciales para medir cantidades continuas y dividir objetos en partes exactamente iguales."
    },
    {
        "intent_id": "numeros_irracionales",
        "keywords": ["numeros", "irracionales", "infinitos", "aperiodicos", "raices", "inexactos"],
        "base_response": "Los números irracionales poseen infinitas cifras decimales no periódicas y no pueden escribirse como fracciones simples. Representan magnitudes inconmensurables, como la longitud de la diagonal de un cuadrado, siendo ejemplos clásicos la raíz de dos, el número pi y el número áureo."
    },
    {
        "intent_id": "sistema_reales",
        "keywords": ["sistema", "reales", "recta", "continuidad", "conjuntos", "union"],
        "base_response": "El sistema de los números reales resulta de la unión completa entre conjuntos racionales e irracionales. Completan la recta numérica sin dejar huecos, proporcionando el marco riguroso necesario para el cálculo diferencial e integral, describiendo magnitudes continuas en la física moderna."
    },
    {
        "intent_id": "numeros_imaginarios",
        "keywords": ["numeros", "imaginarios", "raices", "negativas", "complejos", "ecuaciones"],
        "base_response": "Los números imaginarios surgen de extraer raíces cuadradas a valores negativos, introduciendo la unidad imaginaria. Amplían el horizonte algebraico al permitir resolver ecuaciones cuadráticas sin solución real, formando junto con los reales la poderosa estructura matemática de los números complejos multidimensionales."
    },
    {
        "intent_id": "formacion_subconjuntos",
        "keywords": ["formacion", "subconjuntos", "elementos", "inclusion", "relacion", "partes"],
        "base_response": "La formación de subconjuntos ocurre cuando todos los elementos de una agrupación pertenecen simultáneamente a otra agrupación más amplia. Esta relación fundamental de inclusión estructura la teoría de conjuntos y permite clasificar objetos matemáticos creando jerarquías lógicas desde lo particular a general."
    },
    {
        "intent_id": "diagramas_venn",
        "keywords": ["diagramas", "venn", "representacion", "grafica", "interseccion", "conjuntos"],
        "base_response": "Los diagramas de Venn proporcionan una representación visual mediante círculos cerrados superpuestos para ilustrar agrupaciones matemáticas. Facilitan enormemente la comprensión intuitiva de relaciones lógicas como inclusiones, uniones y exclusiones, convirtiéndose en una herramienta pedagógica imprescindible para estudiantes de matemáticas elementales modernas."
    },
    {
        "intent_id": "interseccion_conjuntos",
        "keywords": ["interseccion", "conjuntos", "comunes", "elementos", "superposicion", "operacion"],
        "base_response": "La intersección de conjuntos es una operación matemática que genera una nueva agrupación constituida exclusivamente por aquellos elementos compartidos simultáneamente entre dos o más conjuntos originales. Visualmente se ubica en el área central donde los círculos representativos se cruzan directamente compartiendo propiedades."
    },
    {
        "intent_id": "union_elementos",
        "keywords": ["union", "elementos", "conjuntos", "agrupacion", "suma", "totalidad"],
        "base_response": "La unión de elementos combina la totalidad de los miembros pertenecientes a dos o más conjuntos para formar una nueva agrupación integral. En esta operación fundamental se eliminan los elementos duplicados, garantizando que cada miembro único aparezca exactamente una vez en resultado."
    },
    {
        "intent_id": "diferencia_conjuntos",
        "keywords": ["diferencia", "conjuntos", "resta", "exclusivos", "operacion", "elementos"],
        "base_response": "La diferencia entre conjuntos identifica exactamente aquellos elementos que pertenecen al primer grupo pero que no están presentes en el segundo. Actúa como una resta lógica, aislando las características exclusivas de una agrupación y eliminando cualquier rasgo compartido con otros grupos evaluados."
    },
    {
        "intent_id": "complemento_conjuntos",
        "keywords": ["complemento", "conjuntos", "universo", "restantes", "excluidos", "totalidad"],
        "base_response": "El complemento de un conjunto está formado por todos los elementos del conjunto universal que no pertenecen a dicha agrupación específica. Define lo que falta para completar el universo total del discurso, dependiendo siempre del contexto delimitado por las reglas matemáticas rigurosas establecidas."
    },
    {
        "intent_id": "pertenencia_elementos",
        "keywords": ["pertenencia", "elementos", "relacion", "simbolo", "miembro", "inclusiones"],
        "base_response": "La relación de pertenencia vincula un elemento individual con el conjunto que lo contiene formalmente. Se representa mediante un símbolo especial similar a una letra épsilon, estableciendo el vínculo más primitivo y fundamental sobre el cual se construye toda la teoría matemática conjuntista."
    },
    {
        "intent_id": "notacion_comprension",
        "keywords": ["notacion", "comprension", "propiedad", "regla", "condicion", "describir"],
        "base_response": "La notación por comprensión define un conjunto enunciando una propiedad característica o regla lógica que cumplen obligatoriamente todos sus miembros. Este método resulta sumamente eficiente para expresar agrupaciones con infinitos elementos o patrones complejos sin necesidad de listar individualmente cada componente aislado."
    },
    {
        "intent_id": "notacion_extension",
        "keywords": ["notacion", "extension", "enumerar", "lista", "elementos", "llaves"],
        "base_response": "La notación por extensión requiere enumerar explícitamente cada uno de los elementos de un conjunto, separándolos mediante comas y encerrándolos entre llaves. Es sumamente útil y clara para agrupaciones finitas pequeñas, permitiendo visualizar inmediatamente la totalidad de los miembros sin posibles ambigüedades lógicas."
    },
    {
        "intent_id": "recta_numerica",
        "keywords": ["recta", "numerica", "representacion", "puntos", "distancia", "orden"],
        "base_response": "La recta numérica real es una representación geométrica unidimensional donde cada punto corresponde biunívocamente a un número real. Organiza visualmente los valores estableciendo ordenamiento, magnitud y distancia, ubicando el cero al centro, los positivos hacia la derecha y negativos hacia la izquierda direccional."
    },
    {
        "intent_id": "cardinalidad_conjunto",
        "keywords": ["cardinalidad", "conjunto", "cantidad", "tamano", "finito", "elementos"],
        "base_response": "La cardinalidad determina la cantidad exacta de elementos distintos que conforman un conjunto específico delimitado. En agrupaciones finitas se expresa mediante un número natural simple, mientras que para conjuntos infinitos requiere conceptos transinfinitos avanzados para comparar tamaños y clasificar diferentes niveles escalares de infinitud."
    },
    {
        "intent_id": "conjunto_vacio",
        "keywords": ["conjunto", "vacio", "nulo", "cero", "elementos", "ausencia"],
        "base_response": "El conjunto vacío o nulo carece absolutamente de elementos en su interior matemático. Aunque parezca contraintuitivo, es un concepto riguroso y esencial, considerado subconjunto de cualquier otra agrupación existente, y funciona estructuralmente como el cero dentro de las operaciones lógicas entre conjuntos teóricos."
    },
    {
        "intent_id": "conjunto_universal",
        "keywords": ["conjunto", "universal", "base", "totalidad", "referencia", "contexto"],
        "base_response": "El conjunto universal o base engloba la totalidad absoluta de elementos considerados pertinentes dentro de un problema matemático específico. Define estrictamente el contexto del discurso operativo, limitando las posibilidades y permitiendo definir operaciones complementarias de forma coherente sin ambigüedades lógicas o paradojas analíticas indeseadas."
    },
    {
        "intent_id": "clasificacion_numeros",
        "keywords": ["clasificacion", "numeros", "tipos", "jerarquia", "sistemas", "propiedades"],
        "base_response": "La clasificación de los números organiza sistemáticamente los diferentes conjuntos numéricos según sus propiedades matemáticas inherentes. Comienza desde los simples naturales, escalando jerárquicamente por los enteros, racionales e irracionales, hasta completar el poderoso sistema continuo de los reales y los abstractos complejos espaciales multidimensionales."
    },
    {
        "intent_id": "propiedad_cerradura",
        "keywords": ["propiedad", "cerradura", "operacion", "resultado", "interno", "conjuntos"],
        "base_response": "La propiedad de cerradura establece que al realizar una operación matemática específica entre dos elementos de un conjunto, el resultado final obligatoriamente pertenece al mismo conjunto original. Garantiza la consistencia estructural del sistema algebraico impidiendo resultados imprevistos fuera del dominio numérico analítico establecido previamente."
    },
    {
        "intent_id": "elementos_pares",
        "keywords": ["elementos", "pares", "positivos", "divisibles", "mitades", "enteros"],
        "base_response": "Los elementos pares positivos son aquellos números naturales que pueden dividirse exactamente entre dos sin generar residuos fraccionarios indeseados. Se representan algebraicamente mediante la fórmula del doble, formando una secuencia aritmética infinita que resulta fundamental para entender reglas básicas de divisibilidad elemental aplicada escolarmente."
    },
    {
        "intent_id": "elementos_impares",
        "keywords": ["elementos", "impares", "positivos", "indivisibles", "residuos", "enteros"],
        "base_response": "Los elementos impares positivos comprenden todos aquellos números naturales que al dividirse entre dos producen invariablemente un residuo unitario constante. Intercalados perfectamente con los números pares, se representan mediante fórmulas consecutivas y poseen propiedades matemáticas únicas al ser sumados o multiplicados repetidamente entre sí mismos."
    },
    {
        "intent_id": "multiplos_numericos",
        "keywords": ["multiplos", "numericos", "basicos", "producto", "tabla", "infinitos"],
        "base_response": "Los múltiplos numéricos básicos se obtienen al multiplicar un número entero específico por cualquier otro número del mismo conjunto algebraico. Constituyen sucesiones infinitas que fundamentan las conocidas tablas de multiplicar escolares, siendo conceptos imprescindibles para encontrar denominadores comunes al operar aritméticamente con fracciones numéricas."
    },
    {
        "intent_id": "divisores_numericos",
        "keywords": ["divisores", "numericos", "exactos", "factores", "division", "finitos"],
        "base_response": "Los divisores numéricos exactos son aquellos valores que logran fragmentar un número de manera perfecta, dejando siempre un residuo absolutamente nulo. A diferencia de los múltiplos, forman agrupaciones finitas y limitadas, constituyendo los bloques de construcción teóricos fundamentales en estudios analíticos sobre factorización matemática elemental."
    },
    {
        "intent_id": "numeros_primos",
        "keywords": ["numeros", "primos", "fundamentales", "divisores", "unicos", "indivisibles"],
        "base_response": "Los números primos fundamentales poseen exactamente dos divisores distintos: el número uno universal y ellos mismos indivisibles. Actúan verdaderamente como los ladrillos estructurales de toda la aritmética moderna, ya que cualquier cantidad superior puede expresarse únicamente como un producto exclusivo multiplicativo de estos fascinantes números."
    },
    {
        "intent_id": "numeros_compuestos",
        "keywords": ["numeros", "compuestos", "divisibles", "factores", "multiples", "primos"],
        "base_response": "Los números compuestos divisibles son aquellos valores enteros mayores que uno que cuentan con al menos tres divisores diferentes comprobables. A diferencia absoluta de los elementos primos, pueden descomponerse exitosamente en múltiples factores matemáticos más pequeños utilizando rigurosamente el teorema fundamental de la aritmética clásica."
    },
    {
        "intent_id": "criba_eratostenes",
        "keywords": ["criba", "eratostenes", "algoritmo", "primos", "metodo", "eliminar"],
        "base_response": "La criba de Eratóstenes constituye un antiguo e ingenioso algoritmo matemático diseñado específicamente para identificar rápidamente todos los números primos hasta cierto límite superior. Consiste simplemente en tachar sistemáticamente los múltiplos conocidos, revelando visualmente aquellos valores puramente indivisibles que logran sobrevivir ilesos al proceso."
    },
    {
        "intent_id": "valor_absoluto",
        "keywords": ["valor", "absoluto", "numerico", "distancia", "magnitud", "positivo"],
        "base_response": "El valor absoluto numérico representa rigurosamente la distancia geométrica pura que existe desde cualquier cifra hasta el cero sobre la recta numérica espacial. Desprecia completamente el signo direccional negativo, arrojando siempre una magnitud escalar estrictamente positiva utilizada frecuentemente en ecuaciones para modelar distancias reales tangibles."
    },
    {
        "intent_id": "opuesto_aditivo",
        "keywords": ["opuesto", "aritmetico", "aditivo", "inverso", "signo", "cancelacion"],
        "base_response": "El opuesto aritmético aditivo corresponde al mismo valor numérico exacto pero ostentando un signo direccional radicalmente contrario. Cuando ambos valores antagónicos se suman algebraicamente, se aniquilan mutuamente originando invariablemente el número cero, cumpliendo así el principio del elemento neutro en ecuaciones fundamentales del sistema resolutivo."
    },
    {
        "intent_id": "propiedades_naturales",
        "keywords": ["propiedades", "naturales", "sumar", "multiplicar", "reglas", "basicas"],
        "base_response": "Las propiedades matemáticas de los números naturales establecen pautas claras sobre su comportamiento analítico al ser sumados o multiplicados entre sí. Destacan principalmente la ley conmutativa y asociativa, asegurando que el orden específico agrupado de los factores involucrados no modifique en absoluto el producto obtenido final."
    },
    {
        "intent_id": "propiedades_enteros",
        "keywords": ["propiedades", "enteros", "signos", "reglas", "operaciones", "algebra"],
        "base_response": "Las propiedades de los enteros incorporan la compleja ley de los signos para poder operar matemáticamente combinando valores analíticos positivos y negativos. Estas reglas inquebrantables definen detalladamente cómo la adición, sustracción o multiplicación afectan las direcciones sobre la conocida recta numérica escolar bidimensional de manera predecible."
    },
    {
        "intent_id": "suma_racionales",
        "keywords": ["suma", "racionales", "fracciones", "denominador", "comun", "partes"],
        "base_response": "La suma de números racionales requiere homogeneizar previamente las partes involucradas calculando un denominador común adecuado mediante mínimo común múltiplo elemental. Posteriormente, las porciones proporcionales de los numeradores pueden combinarse directamente para obtener un solo cociente integrado de altísima precisión matemática fraccionaria sumamente útil escolarmente."
    },
    {
        "intent_id": "producto_racionales",
        "keywords": ["producto", "racionales", "multiplicacion", "directa", "numerador", "denominador"],
        "base_response": "La multiplicación algorítmica de números racionales se ejecuta de manera absolutamente lineal y directa entre numeradores correspondientes superiores y denominadores subyacentes inferiores. Este proceso algebraico sencillo produce velozmente una nueva fracción representativa que frecuentemente requiere ser simplificada para mostrar su mínima expresión numérica válida irreducible final."
    },
    {
        "intent_id": "decimales_exactos",
        "keywords": ["decimales", "exactos", "finitos", "fracciones", "limite", "cifras"],
        "base_response": "Los números decimales exactos poseen una cantidad estrictamente finita y contable de cifras posteriores al punto separador decimal establecido. Resultan de fracciones cuyos denominadores están compuestos exclusivamente por potencias primas binarias o quinarias, permitiendo divisiones matemáticas absolutamente perfectas sin restos perpetuamente iterativos sobrantes o complejos."
    },
    {
        "intent_id": "decimales_periodicos",
        "keywords": ["decimales", "periodicos", "repeticion", "infinita", "patron", "racionales"],
        "base_response": "Los decimales periódicos presentan un patrón infinito repetitivo de cifras después de la conocida marca de separación fraccionaria estándar internacional. Aunque su extensión sea inagotable, pueden reconvertirse mediante técnicas algebraicas ingeniosas en simples fracciones racionales exactas, demostrando propiedades matemáticas profundamente fascinantes y predictivas para estudiantes aplicados."
    },
    {
        "intent_id": "raices_cuadradas",
        "keywords": ["raices", "cuadradas", "inversas", "potencias", "base", "calculo"],
        "base_response": "Las raíces cuadradas operan como herramientas matemáticas inversas diseñadas para deshacer multiplicaciones iterativas sobre un mismo factor idéntico original analizado. Su extracción precisa puede arrojar soluciones racionales cristalinas o irracionales infinitamente extensas dependiendo intrínsecamente del valor numérico radicado que esté siendo exhaustivamente examinado por estudiantes algebraicos."
    },
    {
        "intent_id": "constante_pi",
        "keywords": ["constante", "circulos", "diametro", "perimetro", "irracional", "geometria"],
        "base_response": "El célebre número pi refleja la constante proporción inalterable que existe entre el perímetro total de cualquier círculo perfecto y su propio diámetro interno atravesado. Al ser puramente irracional, cuenta con infinitos decimales desordenados impredecibles, desempeñando un papel analítico imprescindible dentro de la vasta geometría analítica moderna."
    },
    {
        "intent_id": "constante_euler",
        "keywords": ["constante", "euler", "crecimiento", "logaritmo", "natural", "calculo"],
        "base_response": "El número de Euler constituye una base trascendental indispensable para modelar sistemas caracterizados por un veloz crecimiento exponencial continuo en ciencias modernas aplicadas. Al igual que otras constantes irracionales complejas, presenta infinitas cifras decimales sin patrones periódicos obvios, sustentando poderosamente funciones fundamentales del cálculo diferencial avanzado."
    },
    {
        "intent_id": "numero_aureo",
        "keywords": ["numero", "aureo", "proporcion", "divina", "belleza", "sucesion"],
        "base_response": "El fascinante número áureo describe una proporción matemática irracional profundamente vinculada con patrones estéticos espaciales y crecimientos armónicos hallados frecuentemente en maravillosas estructuras naturales visuales. Su relación intrínseca con la sucesión armónica de Fibonacci lo posiciona como un concepto didáctico sumamente cautivador para múltiples estudiantes curiosos analíticos."
    },
    {
        "intent_id": "axiomas_peano",
        "keywords": ["axiomas", "peano", "fundamentos", "logica", "sucesion", "naturales"],
        "base_response": "Los axiomas de Peano establecen los cimientos lógicos más elementales para estructurar el conjunto infinito de los números naturales desde sus orígenes primitivos. A través del concepto inquebrantable de función sucesora estructurada, permiten deducir matemáticamente todas las reglas aritméticas clásicas sin requerir presuposiciones previas adicionales innecesarias complejas."
    },
    {
        "intent_id": "ley_asociativa",
        "keywords": ["ley", "asociativa", "agrupacion", "parentesis", "suma", "resultado"],
        "base_response": "La ley asociativa postula matemáticamente que la manera específica de agrupar operandos mediante paréntesis no altera bajo ninguna circunstancia el resultado final analítico obtenido. Esta propiedad facilita enormemente simplificar cálculos largos y complejos desglosándolos de forma conveniente y ordenada durante operaciones puramente aditivas o multiplicativas estructurales continuas."
    },
    {
        "intent_id": "ley_conmutativa",
        "keywords": ["ley", "conmutativa", "orden", "factores", "alteracion", "producto"],
        "base_response": "La ley conmutativa garantiza inquebrantablemente que el ordenamiento posicional escogido para situar los factores o sumandos nunca modificará el resultado final numérico arrojado esperado. Facilita reorganizar algebraicamente ecuaciones complejas para simplificarlas eficazmente antes de continuar operando lógicamente, reduciendo significativamente la posibilidad real de cometer errores humanos procedimentales comunes."
    },
    {
        "intent_id": "ley_distributiva",
        "keywords": ["ley", "distributiva", "repartir", "multiplicacion", "sumas", "algebra"],
        "base_response": "La ley distributiva conecta simultáneamente la operación multiplicativa con procesos aditivos internos dentro de paréntesis lógicos, permitiendo expandir expresiones algebraicas eficientemente paso a paso analítico. Facilita repartir matemáticamente factores externos hacia cada sumando interno contenido, siendo la base procedimental indispensable para resolver ecuaciones y realizar notables factorizaciones algebraicas correctas."
    },
    {
        "intent_id": "neutro_aditivo",
        "keywords": ["neutro", "aditivo", "identidad", "cero", "suma", "inalterado"],
        "base_response": "El elemento neutro aditivo, comúnmente materializado por el número cero cardinal absoluto, posee la característica funcional exclusiva de dejar completamente inalterado cualquier valor numérico sumado a él iterativamente. Esta propiedad de identidad estructural resulta imprescindible para construir y mantener el balance simétrico interno en cualquier ecuación algebraica analítica resoluble lógicamente."
    },
    {
        "intent_id": "neutro_multiplicativo",
        "keywords": ["neutro", "multiplicativo", "identidad", "uno", "producto", "inalterado"],
        "base_response": "El elemento neutro multiplicativo es representado por el número uno, y tiene la capacidad matemática única de preservar intacta la identidad de cualquier factor al multiplicarse. Esta particularidad permite estructurar descomposiciones fraccionarias lógicas y fundamenta la consistencia teórica de los sistemas algebraicos contemporáneos completos."
    },
    {
        "intent_id": "inverso_multiplicativo",
        "keywords": ["inverso", "multiplicativo", "fraccion", "volteada", "producto", "uno"],
        "base_response": "El inverso multiplicativo o recíproco algebraico consiste en intercambiar las posiciones del numerador y denominador dentro de una expresión fraccionaria. Al multiplicar ambos factores entre sí se obtiene invariablemente la unidad neutra perfecta, cancelando variables eficazmente durante complejos procedimientos algebraicos abstractos."
    },
    {
        "intent_id": "teorema_aritmetica",
        "keywords": ["teorema", "aritmetica", "factorizacion", "primos", "unica", "descomposicion"],
        "base_response": "El teorema fundamental de la aritmética afirma que todo número compuesto mayor que uno puede descomponerse en factores primos de manera absolutamente única e irrepetible. Este principio proporciona las invaluables bases teóricas estructurales sobre las cuales reposan complejos sistemas modernos de seguridad y criptografía."
    },
    {
        "intent_id": "principio_orden",
        "keywords": ["principio", "orden", "menor", "elemento", "conjuntos", "naturales"],
        "base_response": "El principio del buen orden establece lógicamente que cualquier subconjunto no vacío perteneciente a los números naturales posee un elemento mínimo cuantificable verificable. Este cimiento teórico aparentemente sencillo fundamenta métodos analíticos indispensables para demostraciones precisas, como el poderoso mecanismo de inducción matemática escolar."
    },
    {
        "intent_id": "relacion_equivalencia",
        "keywords": ["relacion", "equivalencia", "simetria", "transitividad", "reflexividad", "igualdad"],
        "base_response": "La relación de equivalencia engloba condiciones estrictas de reflexividad, perfecta simetría bidireccional y conectividad lógica transitiva aplicadas entre elementos evaluados objetivamente. Permite agrupar objetos abstractos lógicos compartiendo idénticas propiedades analíticas relevantes dentro de sistemas altamente complejos, forjando clases estructurales unificadas sumamente útiles en álgebra."
    }
]

valid_data = []

for item in data:
    word_count = len(re.findall(r'\b\w+\b', item['base_response'], re.UNICODE))
    if word_count < 40 or word_count > 50:
        print(f"Warning: Item {item['intent_id']} has {word_count} words")
    item['keywords'] = process_keywords(item['keywords'])
    if len(item['keywords']) < 4 or len(item['keywords']) > 6:
         print(f"Warning: Item {item['intent_id']} has {len(item['keywords'])} keywords")
    valid_data.append(item)

with open("MM_brain_01.json", "w", encoding="utf-8") as f:
    json.dump(valid_data, f, ensure_ascii=False, indent=2)

print(f"Generated {len(valid_data)} items successfully.")
