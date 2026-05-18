# =============================================================
#  COSTEÑOL — Analizador Sabroso (Analizador Semántico)
#  src/semantic.py
# =============================================================
#
#  ¿QUÉ ES EL ANÁLISIS SEMÁNTICO?
#  El análisis semántico es la tercera fase del compilador.
#  Mientras el lexer verifica los caracteres y el parser verifica
#  la estructura, la semántica verifica el SIGNIFICADO.
#
#  Ejemplos de errores semánticos (la sintaxis puede ser correcta
#  pero el significado no tiene sentido):
#    - Usar una variable sin declararla
#    - Declarar la misma variable dos veces
#    - Asignar un texto a una variable Entero
#
#  ¿CÓMO FUNCIONA?
#  El AnalizadorSabroso recorre el AST nodo por nodo usando
#  el patrón de diseño VISITOR (visitar cada tipo de nodo con
#  su propio método).
#
#  Flujo:
#    AST → AnalizadorSabroso → Tabla de símbolos + Lista de errores
# =============================================================

from src.ast_nodes import (
    NodoDeclaracion, NodoAsignacion, NodoCaptura, NodoMensaje,
    NodoNumeroEntero, NodoNumeroReal, NodoCadena, NodoBooleano,
    NodoIdentificador, NodoOperacion, NodoNegacion
)
from src.symbol_table import TablaEVainas


class AnalizadorSabroso:
    """
    El Analizador Sabroso — Analizador semántico del Compilador Costeñol.

    Recorre el AST y valida que el programa tenga sentido semántico:
    - Variables declaradas antes de usarse
    - No declarar la misma variable dos veces
    - Compatibilidad básica de tipos

    Nombre costeño: 'Sabroso' → porque analiza con fineza y sabor,
    como la gastronomía costeña: no todo vale, hay que saber.
    """

    # Mapeo de tipos del lenguaje a tipos de Python
    # Útil para verificar compatibilidad en asignaciones
    TIPO_PYTHON = {
        'Entero': int,
        'Real':   float,
        'Texto':  str,
        'Logico': bool,
    }

    def __init__(self):
        # La tabla de símbolos: se crea aquí y se comparte con el ejecutor
        self.tabla   = TablaEVainas()
        self.errores = []      # Lista de errores semánticos
        self.advertencias = [] # Lista de advertencias

    # ----------------------------------------------------------
    #  MÉTODO PRINCIPAL: analizar
    #  Recorre la lista de nodos del AST uno por uno.
    # ----------------------------------------------------------
    def analizar(self, nodos):
        """
        Punto de entrada del análisis semántico.

        Args:
            nodos (list): lista de nodos AST del parser

        Returns:
            bool: True si no hay errores, False si hay chicharrones
        """
        for nodo in nodos:
            self._visitar(nodo)

        return len(self.errores) == 0

    # ----------------------------------------------------------
    #  DISPATCHER: _visitar
    #  Redirige al método correcto según el tipo de nodo.
    #  Esto es el patrón Visitor simplificado con isinstance().
    # ----------------------------------------------------------
    def _visitar(self, nodo):
        """
        Determina el tipo de nodo y llama al método correspondiente.
        Si el nodo es None, simplemente retorna None.
        """
        if nodo is None:
            return None

        if isinstance(nodo, NodoDeclaracion):
            return self._visitar_declaracion(nodo)
        elif isinstance(nodo, NodoAsignacion):
            return self._visitar_asignacion(nodo)
        elif isinstance(nodo, NodoCaptura):
            return self._visitar_captura(nodo)
        elif isinstance(nodo, NodoMensaje):
            return self._visitar_mensaje(nodo)
        elif isinstance(nodo, NodoOperacion):
            return self._visitar_operacion(nodo)
        elif isinstance(nodo, NodoNegacion):
            return self._visitar_negacion(nodo)
        elif isinstance(nodo, NodoIdentificador):
            return self._visitar_identificador(nodo)
        elif isinstance(nodo, NodoNumeroEntero):
            return 'Entero'
        elif isinstance(nodo, NodoNumeroReal):
            return 'Real'
        elif isinstance(nodo, NodoCadena):
            return 'Texto'
        elif isinstance(nodo, NodoBooleano):
            return 'Logico'
        else:
            return None

    # ----------------------------------------------------------
    #  VISITAR DECLARACIÓN
    # ----------------------------------------------------------
    def _visitar_declaracion(self, nodo):
        """
        Verifica que una variable no haya sido declarada antes.
        Si ya existe → advertencia costeña.
        Si no → la registra en la tabla de símbolos.
        """
        exito = self.tabla.declarar(nodo.nombre, nodo.tipo, nodo.linea)
        if not exito:
            entrada_existente = self.tabla.obtener(nodo.nombre)
            msg = (f"  ⚠️  Ajá, cuadro... '{nodo.nombre}' ya fue declarada "
                   f"en la línea {entrada_existente.linea}. "
                   f"¿Qué estás haciendo ahí?")
            self.advertencias.append(msg)
            print(msg)

    # ----------------------------------------------------------
    #  VISITAR ASIGNACIÓN
    # ----------------------------------------------------------
    def _visitar_asignacion(self, nodo):
        """
        Verifica que:
        1. La variable destino haya sido declarada.
        2. El tipo de la expresión sea compatible con el tipo de la variable.
        """
        # 1. Verificar que la variable existe
        if not self.tabla.existe(nodo.nombre):
            msg = (f"  🚨 Eche, '{nodo.nombre}' no fue declarada, cuadro "
                   f"(línea {nodo.linea}). Esa vaina no existe en la Tabla e' Vainas.")
            self.errores.append(msg)
            print(msg)
            return

        # 2. Inferir el tipo de la expresión del lado derecho
        tipo_expresion = self._visitar(nodo.expresion)
        tipo_variable  = self.tabla.obtener_tipo(nodo.nombre)

        # 3. Verificar compatibilidad de tipos
        if tipo_expresion is not None and tipo_variable is not None:
            if not self._tipos_compatibles(tipo_variable, tipo_expresion):
                msg = (f"  🚨 Barro de tipos en la línea {nodo.linea}: "
                       f"'{nodo.nombre}' es {tipo_variable} "
                       f"pero le estás metiendo un {tipo_expresion}. "
                       f"Eso no cuadra, cuadro.")
                self.errores.append(msg)
                print(msg)

    # ----------------------------------------------------------
    #  VISITAR CAPTURA
    # ----------------------------------------------------------
    def _visitar_captura(self, nodo):
        """
        Verifica que la variable destino exista y que el tipo
        de captura sea compatible con el tipo de la variable.
        """
        if not self.tabla.existe(nodo.variable):
            msg = (f"  🚨 Eche, '{nodo.variable}' no fue declarada "
                   f"(línea {nodo.linea}). Declárala primero, cuadro.")
            self.errores.append(msg)
            print(msg)
            return

        tipo_variable = self.tabla.obtener_tipo(nodo.variable)
        if not self._tipos_compatibles(tipo_variable, nodo.tipo):
            msg = (f"  🚨 Chicharrón de tipos en la línea {nodo.linea}: "
                   f"'{nodo.variable}' es {tipo_variable} "
                   f"pero Captura.{nodo.tipo}() mete un {nodo.tipo}. "
                   f"Eso no pega, cuadro.")
            self.errores.append(msg)
            print(msg)

    # ----------------------------------------------------------
    #  VISITAR MENSAJE
    # ----------------------------------------------------------
    def _visitar_mensaje(self, nodo):
        """
        Verifica que la expresión del Mensaje sea válida.
        """
        self._visitar(nodo.contenido)

    # ----------------------------------------------------------
    #  VISITAR OPERACIÓN
    # ----------------------------------------------------------
    def _visitar_operacion(self, nodo):
        """
        Verifica los operandos de una operación y retorna
        el tipo resultante.

        Reglas de tipo para operaciones aritméticas:
          Entero op Entero  → Entero
          Real   op Real    → Real
          Entero op Real    → Real   (promoción automática)
          Real   op Entero  → Real

        Para operaciones de comparación y lógicas → Logico
        """
        tipo_izq = self._visitar(nodo.izquierda)
        tipo_der = self._visitar(nodo.derecha)

        # Operadores lógicos y de comparación → siempre retornan Logico
        if nodo.operador in ('==', '!=', '>', '<', '>=', '<=', '&&', '||'):
            return 'Logico'

        # Operadores aritméticos → respetar jerarquía de tipos
        if tipo_izq == 'Real' or tipo_der == 'Real':
            return 'Real'
        if tipo_izq == 'Entero' and tipo_der == 'Entero':
            return 'Entero'
        if tipo_izq == 'Texto' and nodo.operador == '+':
            return 'Texto'  # Concatenación de texto

        return tipo_izq  # Retorno por defecto

    # ----------------------------------------------------------
    #  VISITAR NEGACIÓN
    # ----------------------------------------------------------
    def _visitar_negacion(self, nodo):
        """
        Verifica la negación unaria.
        '-' aplica a Entero o Real → mismo tipo
        '!' aplica a Logico → Logico
        """
        tipo_operando = self._visitar(nodo.operando)
        if nodo.operador == '!':
            return 'Logico'
        return tipo_operando

    # ----------------------------------------------------------
    #  VISITAR IDENTIFICADOR
    # ----------------------------------------------------------
    def _visitar_identificador(self, nodo):
        """
        Verifica que la variable usada en una expresión
        haya sido declarada previamente.
        Retorna su tipo si existe.
        """
        if not self.tabla.existe(nodo.nombre):
            msg = (f"  🚨 Ajá... ¿y '{nodo.nombre}' de dónde salió? "
                   f"(línea {nodo.linea}) Esa variable no fue declarada, cuadro.")
            self.errores.append(msg)
            print(msg)
            return None
        return self.tabla.obtener_tipo(nodo.nombre)

    # ----------------------------------------------------------
    #  VERIFICAR COMPATIBILIDAD DE TIPOS
    # ----------------------------------------------------------
    def _tipos_compatibles(self, tipo_destino, tipo_origen):
        """
        Verifica si tipo_origen puede ser asignado a tipo_destino.

        Reglas de compatibilidad:
          - Mismo tipo         → siempre compatible
          - Entero ← Real     → compatible (por truncamiento)
          - Real   ← Entero   → compatible (promoción)
          - Texto  ← Entero   → incompatible
          - Logico ← Entero   → incompatible
        """
        if tipo_destino == tipo_origen:
            return True
        # Compatibilidad entre numéricos
        if tipo_destino in ('Entero', 'Real') and tipo_origen in ('Entero', 'Real'):
            return True
        return False
