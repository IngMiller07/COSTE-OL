# =============================================================
#  COSTEÑOL — Tabla e' Vainas (Tabla de Símbolos)
#  src/symbol_table.py
# =============================================================
#
#  ¿QUÉ ES LA TABLA DE SÍMBOLOS?
#  Es una estructura de datos que guarda información sobre
#  cada variable declarada en el programa:
#    - Nombre
#    - Tipo de dato (Entero, Texto, Real, Logico)
#    - Valor actual (si ya fue asignada)
#    - Línea donde fue declarada
#
#  ¿PARA QUÉ SIRVE?
#  1. Semántica: verificar que una variable fue declarada antes
#     de usarla, y que los tipos son compatibles.
#  2. Ejecución: guardar y recuperar valores de variables
#     durante la interpretación del programa.
#
#  Analogía costeña: es como la libreta del tendero del barrio
#  donde anota quién debe qué, de qué tipo y cuánto.
#
#  Nombre costeño: 'Tabla e' Vainas' → porque guarda "las vainas"
#  (cosas) del programa: variables, tipos, valores.
# =============================================================


class EntradaSimbolo:
    """
    Representa una entrada en la tabla de símbolos.
    Cada variable declarada tiene su propia entrada.

    Atributos:
        nombre (str):   nombre de la variable → 'num1'
        tipo   (str):   tipo de dato         → 'Entero'
        valor  (any):   valor actual          → 42, None si no asignada
        linea  (int):   línea de declaración  → 3
    """
    def __init__(self, nombre, tipo, valor=None, linea=0):
        self.nombre = nombre
        self.tipo   = tipo
        self.valor  = valor
        self.linea  = linea

    def __repr__(self):
        return (f"[{self.nombre} | tipo:{self.tipo} | "
                f"valor:{self.valor} | línea:{self.linea}]")


class TablaEVainas:
    """
    La Tabla e' Vainas — Tabla de símbolos del Compilador Costeñol.

    Almacena todas las variables declaradas en el programa.
    Permite consultar, agregar y actualizar variables.

    Implementación: diccionario Python → O(1) para búsqueda.
    """

    def __init__(self):
        # El diccionario principal: { nombre_variable → EntradaSimbolo }
        self._tabla = {}

    # ----------------------------------------------------------
    #  DECLARAR una variable nueva
    # ----------------------------------------------------------
    def declarar(self, nombre, tipo, linea=0):
        """
        Registra una nueva variable en la tabla.

        Args:
            nombre (str): identificador de la variable
            tipo   (str): tipo de dato ('Entero', 'Texto', 'Real', 'Logico')
            linea  (int): línea del código fuente

        Returns:
            bool: True si se declaró bien, False si ya existía (redeclaración)
        """
        if nombre in self._tabla:
            # Ya existe → advertencia de redeclaración
            return False
        self._tabla[nombre] = EntradaSimbolo(nombre, tipo, None, linea)
        return True

    # ----------------------------------------------------------
    #  VERIFICAR si una variable existe
    # ----------------------------------------------------------
    def existe(self, nombre):
        """
        Verifica si una variable fue declarada previamente.

        Returns:
            bool: True si existe en la tabla, False si no
        """
        return nombre in self._tabla

    # ----------------------------------------------------------
    #  OBTENER el tipo de una variable
    # ----------------------------------------------------------
    def obtener_tipo(self, nombre):
        """
        Retorna el tipo de dato de una variable.

        Returns:
            str:  tipo de dato ('Entero', 'Texto', etc.)
            None: si la variable no existe
        """
        if nombre in self._tabla:
            return self._tabla[nombre].tipo
        return None

    # ----------------------------------------------------------
    #  OBTENER el valor de una variable
    # ----------------------------------------------------------
    def obtener_valor(self, nombre):
        """
        Retorna el valor actual de una variable.

        Returns:
            any:  valor actual (int, float, str, bool)
            None: si no tiene valor asignado o no existe
        """
        if nombre in self._tabla:
            return self._tabla[nombre].valor
        return None

    # ----------------------------------------------------------
    #  ASIGNAR un valor a una variable
    # ----------------------------------------------------------
    def asignar(self, nombre, valor):
        """
        Actualiza el valor de una variable ya declarada.

        Args:
            nombre (str): identificador de la variable
            valor  (any): nuevo valor a guardar

        Returns:
            bool: True si se asignó bien, False si la variable no existe
        """
        if nombre not in self._tabla:
            return False
        self._tabla[nombre].valor = valor
        return True

    # ----------------------------------------------------------
    #  OBTENER la entrada completa
    # ----------------------------------------------------------
    def obtener(self, nombre):
        """
        Retorna la entrada completa de una variable.

        Returns:
            EntradaSimbolo: la entrada completa
            None: si no existe
        """
        return self._tabla.get(nombre, None)

    # ----------------------------------------------------------
    #  MOSTRAR la tabla completa (para debugging costeño)
    # ----------------------------------------------------------
    def mostrar(self):
        """
        Imprime la tabla de símbolos completa.
        Útil para el 'Modo Arrebatao' (debug verboso).
        """
        if not self._tabla:
            print("  📋 La Tabla e' Vainas está vacía, cuadro.")
            return

        print("\n  ╔══════════════════════════════════════════════════╗")
        print("  ║           📋 TABLA E' VAINAS                    ║")
        print("  ╠══════════╦══════════╦══════════════╦═══════════╣")
        print("  ║ Nombre   ║ Tipo     ║ Valor        ║ Línea     ║")
        print("  ╠══════════╬══════════╬══════════════╬═══════════╣")
        for entrada in self._tabla.values():
            nombre = str(entrada.nombre)[:8].ljust(8)
            tipo   = str(entrada.tipo)[:8].ljust(8)
            valor  = str(entrada.valor)[:12].ljust(12)
            linea  = str(entrada.linea)[:7].ljust(7)
            print(f"  ║ {nombre} ║ {tipo} ║ {valor} ║ {linea} ║")
        print("  ╚══════════╩══════════╩══════════════╩═══════════╝\n")
