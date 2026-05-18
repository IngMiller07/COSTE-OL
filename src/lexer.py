# =============================================================
#  COSTEÑOL — Lexer del Malecón
#  src/lexer.py
# =============================================================
#
#  ¿QUÉ ES ESTO?
#  El Lexer (o analizador léxico) es el primer paso del compilador.
#  Su trabajo es leer el código fuente carácter por carácter y
#  agrupar esos caracteres en unidades con significado llamadas
#  TOKENS.
#
#  Ejemplo:
#    Entrada:  num1 Entero;
#    Salida:   [ID('num1'), TIPO('Entero'), PUNTO_COMA(';')]
#
#  ¿POR QUÉ SLY?
#  SLY es una librería Python que usa metaclases y expresiones
#  regulares para definir tokens de forma limpia y declarativa.
#  Ideal para proyectos académicos: poco código, mucha legibilidad.
#
#  Flujo:
#    Código fuente (string) → LexerMalecon → lista de tokens
# =============================================================

from sly import Lexer


class LexerMalecon(Lexer):
    """
    El Lexer del Malecón — Analizador léxico del Compilador Costeñol.

    Convierte el código fuente en tokens uno por uno.
    Cada token tiene un tipo (type) y un valor (value).

    Nombre costeño: 'Malecón' → lugar donde empieza todo,
    como el malecón de Barranquilla donde arranca la fiesta.
    """

    # ----------------------------------------------------------
    # TOKENS
    # Lista de TODOS los tipos de token que este lexer reconoce.
    # SLY la usa internamente para validar que todo esté declarado.
    # ----------------------------------------------------------
    tokens = {
        # Tipos de dato del lenguaje Costeñol
        ENTERO, TEXTO, REAL, LOGICO,

        # Literales de valor
        NUMERO_REAL,       # Ej: 3.14, 2.5
        NUMERO_ENTERO,     # Ej: 42, 100
        CADENA,            # Ej: "Hola cuadro"
        VERDADERO,         # true
        FALSO,             # false

        # Identificadores y palabras clave de acción
        ID,                # Nombres de variables: num1, nombre, x
        CAPTURA,           # Captura (para Captura.Texto(), etc.)
        MENSAJE,           # Mensaje (para Mensaje.Texto(...))

        # Operadores aritméticos
        MAS,               # +
        MENOS,             # -
        POR,               # *
        ENTRE,             # /
        POTENCIA,          # ^

        # Operadores de comparación
        IGUAL_IGUAL,       # ==
        DIFERENTE,         # !=
        MAYOR_IGUAL,       # >=
        MENOR_IGUAL,       # <=
        MAYOR,             # >
        MENOR,             # <

        # Operadores lógicos
        Y,                 # &&
        O,                 # ||
        NO,                # !

        # Operador de asignación
        IGUAL,             # =

        # Delimitadores
        LPAREN,            # (
        RPAREN,            # )
        PUNTO_COMA,        # ;
        PUNTO,             # .
    }

    # ----------------------------------------------------------
    # IGNORADOS
    # Caracteres que el lexer debe saltar sin generar token.
    # Los espacios, tabs y retornos de carro no tienen significado
    # sintáctico en Costeñol, así que los ignoramos.
    # ----------------------------------------------------------
    ignore = ' \t\r'

    # Comentarios de una línea: // Este es un comentario costeño
    ignore_comment = r'//[^\n]*'

    # ----------------------------------------------------------
    # TOKENS CON EXPRESIONES REGULARES SIMPLES (constantes)
    # Orden importante: los más largos primero para evitar
    # que '==' sea reconocido como dos '=' separados.
    # ----------------------------------------------------------

    # Operadores de comparación (2 caracteres) — VAN PRIMERO
    IGUAL_IGUAL  = r'=='
    DIFERENTE    = r'!='
    MAYOR_IGUAL  = r'>='
    MENOR_IGUAL  = r'<='
    MAYOR        = r'>'
    MENOR        = r'<'

    # Operadores lógicos
    Y            = r'&&'
    O            = r'\|\|'

    # Operadores aritméticos
    MAS          = r'\+'
    MENOS        = r'-'
    POR          = r'\*'
    ENTRE        = r'/'
    POTENCIA     = r'\^'

    # Operador de asignación (1 carácter) — VA DESPUÉS de ==
    IGUAL        = r'='

    # Operador lógico NOT (1 carácter) — VA DESPUÉS de !=
    NO           = r'!'

    # Delimitadores
    LPAREN       = r'\('
    RPAREN       = r'\)'
    PUNTO_COMA   = r';'

    # El PUNTO necesita ir antes que NUMERO_REAL para no confundir
    # "3.14" con "3" + PUNTO + "14".
    # SLY resuelve esto porque los métodos (funciones) tienen
    # prioridad sobre las cadenas simples.

    # ----------------------------------------------------------
    # TOKENS CON LÓGICA ESPECIAL (métodos @_)
    # Usamos métodos cuando un token necesita:
    #   - Lógica adicional (ej: convertir a int/float)
    #   - Distinguir palabras reservadas de identificadores
    #   - Manejar caracteres especiales dentro del patrón
    # ----------------------------------------------------------

    @_(r'\d+\.\d+')
    def NUMERO_REAL(self, t):
        """
        Reconoce números reales como 3.14 o 2.5.
        Convierte el string a float de Python.
        Patrón: uno o más dígitos, punto, uno o más dígitos.
        """
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def NUMERO_ENTERO(self, t):
        """
        Reconoce números enteros como 42 o 100.
        Convierte el string a int de Python.
        Patrón: uno o más dígitos.
        """
        t.value = int(t.value)
        return t

    @_(r'"[^"]*"')
    def CADENA(self, t):
        """
        Reconoce cadenas de texto entre comillas dobles.
        Ej: "Hola cuadro" → almacena sin las comillas.
        Patrón: comilla, cualquier carácter excepto comilla, comilla.
        """
        # Quitamos las comillas del principio y del final
        t.value = t.value[1:-1]
        return t

    @_(r'[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ_][a-zA-ZáéíóúÁÉÍÓÚüÜñÑ_0-9]*')
    def ID(self, t):
        """
        Reconoce identificadores y palabras reservadas.

        Primero comprueba si el texto es una palabra reservada del
        lenguaje (ENTERO, TEXTO, etc.). Si lo es, cambia el tipo
        del token. Si no, lo deja como ID (nombre de variable).

        Patrón: letra o guion bajo, seguido de letras, dígitos o guion bajo.
        Soporta caracteres con tilde y ñ para el espíritu costeño. 🌴
        """
        # Tabla de palabras reservadas del lenguaje Costeñol
        palabras_reservadas = {
            'Entero':    'ENTERO',
            'Texto':     'TEXTO',
            'Real':      'REAL',
            'Logico':    'LOGICO',
            'Captura':   'CAPTURA',
            'Mensaje':   'MENSAJE',
            'verdadero': 'VERDADERO',
            'falso':     'FALSO',
        }

        # Si el identificador es una palabra reservada, cambiamos su tipo
        t.type = palabras_reservadas.get(t.value, 'ID')
        return t

    @_(r'\.')
    def PUNTO(self, t):
        """
        Reconoce el punto '.' usado en:
          - Captura.Texto()
          - Mensaje.Texto(...)
        Se define como método para tener prioridad adecuada.
        """
        return t

    # ----------------------------------------------------------
    # SALTO DE LÍNEA
    # No generamos token, pero SÍ actualizamos el contador de
    # líneas para que los mensajes de error sean precisos.
    # ----------------------------------------------------------
    @_(r'\n+')
    def newline(self, t):
        """
        Cuenta las líneas del código fuente.
        self.lineno lleva el registro interno de SLY.
        Esto permite decir: "Eche, error en la línea 5, cuadro."
        """
        self.lineno += t.value.count('\n')

    # ----------------------------------------------------------
    # MANEJO DE ERRORES LÉXICOS
    # Cuando el lexer encuentra un carácter que no reconoce,
    # llama a este método. Aquí mostramos un mensaje costeño
    # y avanzamos un carácter para no quedar en bucle infinito.
    # ----------------------------------------------------------
    def error(self, t):
        """
        Detector de chicharrones léxicos.
        Reporta el carácter desconocido con estilo costeño.
        """
        print(f"\n  🚨 Barro léxico en la línea {self.lineno}: "
              f"¿Qué es ese '{t.value[0]}', cuadro? Eso no existe en Costeñol.")
        # Avanzar un carácter para no quedar pegado
        self.index += 1
