# =============================================================
#  COSTEÑOL — Nodos del Árbol Sintáctico Abstracto (AST)
#  src/ast_nodes.py
# =============================================================
#
#  ¿QUÉ ES UN AST?
#  El Árbol Sintáctico Abstracto (Abstract Syntax Tree) es la
#  representación estructurada del programa después del análisis
#  sintáctico. Cada nodo representa una construcción del lenguaje.
#
#  Ejemplo para:  num1 Entero;
#    NodoDeclaracion(nombre='num1', tipo='Entero')
#
#  Ejemplo para:  suma = num1 + num2;
#    NodoAsignacion(
#      nombre='suma',
#      expresion=NodoOperacion(
#        izquierda=NodoIdentificador('num1'),
#        operador='+',
#        derecha=NodoIdentificador('num2')
#      )
#    )
#
#  ¿POR QUÉ USAR CLASES?
#  Cada tipo de instrucción del lenguaje tiene su propia clase.
#  Esto hace que el intérprete y el analizador semántico puedan
#  identificar qué tipo de nodo están procesando usando isinstance().
#
#  Flujo:
#    Tokens → ParserBacano → lista de nodos AST → Semántica/Ejecutor
# =============================================================


# =============================================================
#  NODO BASE
# =============================================================

class Nodo:
    """
    Clase base para todos los nodos del AST.
    Todos los nodos heredan de aquí.
    """
    pass


# =============================================================
#  NODOS DE DECLARACIÓN
# =============================================================

class NodoDeclaracion(Nodo):
    """
    Representa la declaración de una variable.
    Ejemplo: num1 Entero;

    Atributos:
        nombre (str): nombre de la variable → 'num1'
        tipo   (str): tipo de dato         → 'Entero'
        linea  (int): línea del código fuente (para errores)
    """
    def __init__(self, nombre, tipo, linea=0):
        self.nombre = nombre
        self.tipo   = tipo
        self.linea  = linea

    def __repr__(self):
        return f"Declaracion({self.nombre}: {self.tipo})"


# =============================================================
#  NODOS DE ASIGNACIÓN
# =============================================================

class NodoAsignacion(Nodo):
    """
    Representa la asignación de un valor a una variable.
    Ejemplo: suma = num1 + num2;
             nombre = "Alejandra";
             pi = 3.1416;

    Atributos:
        nombre    (str):  nombre de la variable destino
        expresion (Nodo): nodo con la expresión del lado derecho
        linea     (int):  línea del código fuente
    """
    def __init__(self, nombre, expresion, linea=0):
        self.nombre    = nombre
        self.expresion = expresion
        self.linea     = linea

    def __repr__(self):
        return f"Asignacion({self.nombre} = {self.expresion})"


# =============================================================
#  NODOS DE CAPTURA (entrada del usuario)
# =============================================================

class NodoCaptura(Nodo):
    """
    Representa la captura de datos del usuario.
    Ejemplo: nombre = Captura.Texto();
             n1 = Captura.Entero();

    Atributos:
        variable (str): variable donde se guarda el dato capturado
        tipo     (str): tipo de dato a capturar ('Texto', 'Entero', etc.)
        linea    (int): línea del código fuente
    """
    def __init__(self, variable, tipo, linea=0):
        self.variable = variable
        self.tipo     = tipo
        self.linea    = linea

    def __repr__(self):
        return f"Captura({self.variable} <- Captura.{self.tipo}())"


# =============================================================
#  NODOS DE SALIDA
# =============================================================

class NodoMensaje(Nodo):
    """
    Representa la instrucción de mostrar un mensaje o valor.
    Ejemplo: Mensaje.Texto("Esto es una prueba");
             Mensaje.Texto(nombre);

    Atributos:
        contenido (Nodo): expresión a mostrar (cadena, variable, etc.)
        linea     (int):  línea del código fuente
    """
    def __init__(self, contenido, linea=0):
        self.contenido = contenido
        self.linea     = linea

    def __repr__(self):
        return f"Mensaje({self.contenido})"


# =============================================================
#  NODOS DE EXPRESIÓN
# =============================================================

class NodoNumeroEntero(Nodo):
    """
    Representa un literal numérico entero.
    Ejemplo: 42, 100, 0

    Atributos:
        valor (int): el valor numérico
    """
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return f"Entero({self.valor})"


class NodoNumeroReal(Nodo):
    """
    Representa un literal numérico real (con decimales).
    Ejemplo: 3.14, 2.5, 0.001

    Atributos:
        valor (float): el valor numérico
    """
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return f"Real({self.valor})"


class NodoCadena(Nodo):
    """
    Representa un literal de texto entre comillas.
    Ejemplo: "Hola cuadro", "Alejandra"

    Atributos:
        valor (str): el texto sin comillas
    """
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return f'Cadena("{self.valor}")'


class NodoBooleano(Nodo):
    """
    Representa un literal booleano.
    Ejemplo: verdadero, falso

    Atributos:
        valor (bool): True o False de Python
    """
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return f"Booleano({self.valor})"


class NodoIdentificador(Nodo):
    """
    Representa el uso de una variable en una expresión.
    Ejemplo: num1, nombre, resultado

    Atributos:
        nombre (str): nombre de la variable
        linea  (int): línea del código fuente (para errores semánticos)
    """
    def __init__(self, nombre, linea=0):
        self.nombre = nombre
        self.linea  = linea

    def __repr__(self):
        return f"ID({self.nombre})"


class NodoOperacion(Nodo):
    """
    Representa una operación binaria (con dos operandos).
    Ejemplo: num1 + num2, x * y, a - b

    Atributos:
        izquierda (Nodo): operando izquierdo
        operador  (str):  símbolo del operador: '+', '-', '*', '/', '^'
        derecha   (Nodo): operando derecho
    """
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador  = operador
        self.derecha   = derecha

    def __repr__(self):
        return f"Op({self.izquierda} {self.operador} {self.derecha})"


class NodoNegacion(Nodo):
    """
    Representa la negación unaria (número negativo o NOT lógico).
    Ejemplo: -num1, !condicion

    Atributos:
        operador (str):  '-' o '!'
        operando (Nodo): expresión a negar
    """
    def __init__(self, operador, operando):
        self.operador = operador
        self.operando = operando

    def __repr__(self):
        return f"Neg({self.operador}{self.operando})"
