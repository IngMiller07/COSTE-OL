# =============================================================
#  COSTEÑOL — Parser Bacano
#  src/parser.py
# =============================================================
#
#  ¿QUÉ ES EL PARSER?
#  El analizador sintáctico (parser) recibe la lista de tokens
#  del Lexer y verifica que sigan las reglas gramaticales del
#  lenguaje. Si la secuencia es válida, construye el AST.
#  Si no, reporta un error sintáctico (con estilo costeño).
#
#  ¿QUÉ ES UNA GRAMÁTICA?
#  Un conjunto de reglas que definen qué combinaciones de tokens
#  son válidas. Ejemplo:
#    declaracion : ID TIPO PUNTO_COMA
#  Significa: un identificador, seguido de un tipo, seguido de ';'
#
#  ¿QUÉ ES LA PRECEDENCIA?
#  Define qué operadores se evalúan antes.
#  En matemáticas: * tiene más precedencia que +
#  Aquí lo configuramos con la tabla `precedence`.
#
#  Flujo:
#    Tokens → ParserBacano → Lista de nodos AST
# =============================================================

from sly import Parser
from src.lexer import LexerMalecon
from src.ast_nodes import (
    NodoDeclaracion, NodoAsignacion, NodoCaptura, NodoMensaje,
    NodoNumeroEntero, NodoNumeroReal, NodoCadena, NodoBooleano,
    NodoIdentificador, NodoOperacion, NodoNegacion
)


class ParserBacano(Parser):
    """
    El Parser Bacano — Analizador sintáctico del Compilador Costeñol.

    Toma la secuencia de tokens del LexerMalecon y construye
    el Árbol Sintáctico Abstracto (AST).

    Nombre costeño: 'Bacano' → porque hace su trabajo bien hecho,
    sin chicharrones y con toda la actitud costeña.
    """

    # Le decimos a SLY qué lexer vamos a usar
    tokens = LexerMalecon.tokens

    # ----------------------------------------------------------
    # PRECEDENCIA DE OPERADORES
    # Se define de menor a mayor precedencia (de arriba a abajo).
    # 'left' = asociativo por la izquierda: a + b + c = (a + b) + c
    # 'right' = asociativo por la derecha: a ^ b ^ c = a ^ (b ^ c)
    # ----------------------------------------------------------
    precedence = (
        ('left', O),                          # || (menor precedencia)
        ('left', Y),                          # &&
        ('left', IGUAL_IGUAL, DIFERENTE),     # ==, !=
        ('left', MAYOR, MENOR, MAYOR_IGUAL, MENOR_IGUAL),  # >, <, >=, <=
        ('left', MAS, MENOS),                 # +, -
        ('left', POR, ENTRE),                 # *, /
        ('right', POTENCIA),                  # ^ (mayor precedencia)
        ('right', UMENOS, NO),                # negación unaria (la más alta)
    )

    # ----------------------------------------------------------
    # VARIABLE INTERNA DE ERRORES
    # Acumulamos los errores encontrados durante el parseo.
    # Así podemos reportar múltiples errores, no solo el primero.
    # ----------------------------------------------------------
    def __init__(self):
        self.errores = []  # Lista de errores sintácticos encontrados

    # ==========================================================
    #  REGLA RAÍZ: programa
    #  Un programa Costeñol es una lista de cero o más sentencias.
    # ==========================================================

    @_('sentencias')
    def programa(self, p):
        """
        El símbolo inicial de la gramática.
        Un programa es simplemente una lista de sentencias.
        """
        return p.sentencias

    @_('sentencias sentencia')
    def sentencias(self, p):
        """
        Regla recursiva: lista de sentencias.
        Se procesa de izquierda a derecha acumulando sentencias.
        """
        return p.sentencias + [p.sentencia]

    @_('')
    def sentencias(self, p):
        """
        Caso base: lista vacía de sentencias (programa vacío).
        SLY acepta el string vacío con @_('').
        """
        return []

    # ==========================================================
    #  SENTENCIAS
    #  Una sentencia es cualquier instrucción válida del lenguaje.
    # ==========================================================

    @_('declaracion')
    def sentencia(self, p):
        return p.declaracion

    @_('asignacion')
    def sentencia(self, p):
        return p.asignacion

    @_('captura')
    def sentencia(self, p):
        return p.captura

    @_('salida')
    def sentencia(self, p):
        return p.salida

    # ==========================================================
    #  DECLARACIÓN DE VARIABLE
    #  Sintaxis: ID TIPO ;
    #  Ejemplo:  num1 Entero;
    #            nombre Texto;
    # ==========================================================

    @_('ID ENTERO PUNTO_COMA')
    def declaracion(self, p):
        return NodoDeclaracion(p.ID, 'Entero', p.lineno)

    @_('ID TEXTO PUNTO_COMA')
    def declaracion(self, p):
        return NodoDeclaracion(p.ID, 'Texto', p.lineno)

    @_('ID REAL PUNTO_COMA')
    def declaracion(self, p):
        return NodoDeclaracion(p.ID, 'Real', p.lineno)

    @_('ID LOGICO PUNTO_COMA')
    def declaracion(self, p):
        return NodoDeclaracion(p.ID, 'Logico', p.lineno)

    # ==========================================================
    #  CAPTURA DE DATOS
    #  Sintaxis: ID = Captura . TIPO ( ) ;
    #  Ejemplo:  nombre = Captura.Texto();
    #            n1 = Captura.Entero();
    # ==========================================================

    @_('ID IGUAL CAPTURA PUNTO TEXTO LPAREN RPAREN PUNTO_COMA')
    def captura(self, p):
        return NodoCaptura(p.ID, 'Texto', p.lineno)

    @_('ID IGUAL CAPTURA PUNTO ENTERO LPAREN RPAREN PUNTO_COMA')
    def captura(self, p):
        return NodoCaptura(p.ID, 'Entero', p.lineno)

    @_('ID IGUAL CAPTURA PUNTO REAL LPAREN RPAREN PUNTO_COMA')
    def captura(self, p):
        return NodoCaptura(p.ID, 'Real', p.lineno)

    @_('ID IGUAL CAPTURA PUNTO LOGICO LPAREN RPAREN PUNTO_COMA')
    def captura(self, p):
        return NodoCaptura(p.ID, 'Logico', p.lineno)

    # ==========================================================
    #  ASIGNACIÓN
    #  Sintaxis: ID = expresion ;
    #  Ejemplo:  suma = num1 + num2;
    #            nombre = "Alejandra";
    #            pi = 3.1416;
    # ==========================================================

    @_('ID IGUAL expresion PUNTO_COMA')
    def asignacion(self, p):
        return NodoAsignacion(p.ID, p.expresion, p.lineno)

    # ==========================================================
    #  SALIDA
    #  Sintaxis: Mensaje . Texto ( expresion ) ;
    #  Ejemplo:  Mensaje.Texto("Hola cuadro");
    #            Mensaje.Texto(nombre);
    #            Mensaje.Texto(suma);
    #
    #  NOTA: La sintaxis template (El resultado es:"sum") se
    #  pre-procesa antes de llegar al parser. Ver compiler_api.py.
    # ==========================================================

    @_('MENSAJE PUNTO TEXTO LPAREN expresion RPAREN PUNTO_COMA')
    def salida(self, p):
        return NodoMensaje(p.expresion, p.lineno)

    # ==========================================================
    #  EXPRESIONES
    #  Las expresiones se definen con reglas recursivas que
    #  respetan la precedencia de operadores (definida arriba).
    #
    #  SLY maneja la precedencia automáticamente gracias a la
    #  tabla 'precedence' y a que cada operador se declara una vez.
    # ==========================================================

    # Operaciones binarias aritméticas y lógicas
    @_('expresion MAS expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '+', p.expresion1)

    @_('expresion MENOS expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '-', p.expresion1)

    @_('expresion POR expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '*', p.expresion1)

    @_('expresion ENTRE expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '/', p.expresion1)

    @_('expresion POTENCIA expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '^', p.expresion1)

    # Operaciones de comparación
    @_('expresion IGUAL_IGUAL expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '==', p.expresion1)

    @_('expresion DIFERENTE expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '!=', p.expresion1)

    @_('expresion MAYOR expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '>', p.expresion1)

    @_('expresion MENOR expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '<', p.expresion1)

    @_('expresion MAYOR_IGUAL expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '>=', p.expresion1)

    @_('expresion MENOR_IGUAL expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '<=', p.expresion1)

    # Operaciones lógicas
    @_('expresion Y expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '&&', p.expresion1)

    @_('expresion O expresion')
    def expresion(self, p):
        return NodoOperacion(p.expresion0, '||', p.expresion1)

    # Negación unaria: -num1  o  !condicion
    # El token especial UMENOS se usa para diferenciar el '-' binario
    # del '-' unario. SLY lo maneja con %prec UMENOS.
    @_('MENOS expresion %prec UMENOS')
    def expresion(self, p):
        return NodoNegacion('-', p.expresion)

    @_('NO expresion')
    def expresion(self, p):
        return NodoNegacion('!', p.expresion)

    # Agrupación con paréntesis
    @_('LPAREN expresion RPAREN')
    def expresion(self, p):
        return p.expresion

    # Literales y variables
    @_('NUMERO_ENTERO')
    def expresion(self, p):
        return NodoNumeroEntero(p.NUMERO_ENTERO)

    @_('NUMERO_REAL')
    def expresion(self, p):
        return NodoNumeroReal(p.NUMERO_REAL)

    @_('CADENA')
    def expresion(self, p):
        return NodoCadena(p.CADENA)

    @_('VERDADERO')
    def expresion(self, p):
        return NodoBooleano(True)

    @_('FALSO')
    def expresion(self, p):
        return NodoBooleano(False)

    @_('ID')
    def expresion(self, p):
        return NodoIdentificador(p.ID, p.lineno)

    # ==========================================================
    #  MANEJO DE ERRORES SINTÁCTICOS
    #  Cuando el parser encuentra un token que no encaja con
    #  ninguna regla, llama a este método.
    # ==========================================================

    def error(self, t):
        """
        Detector de chicharrones sintácticos.
        Reporta errores de sintaxis con mensaje costeño.
        Solo reporta un error por línea para no spamear.
        """
        if t:
            linea = t.lineno
            valor = t.value if isinstance(t.value, str) else str(t.type)

            # Deduplicar: solo un error por línea
            ya_reportada = any(
                f'linea {linea}' in e for e in self.errores
            )
            if not ya_reportada:
                msg = (f"  \U0001f6a8 Error sintactico en la linea {linea}: "
                       f"token inesperado '{valor}'. "
                       f"Revisa la sintaxis de esa instruccion, cuadro.")
                self.errores.append(msg)
                print(msg)
            # Recuperación: avanzar al siguiente punto y coma
            self.errok()
        else:
            msg = "  Barro, cuadro... el programa termino de forma inesperada."
            if msg not in self.errores:
                self.errores.append(msg)
                print(msg)

