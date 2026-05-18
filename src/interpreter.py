# =============================================================
#  COSTEÑOL — Ejecutor Costeño (Intérprete)
#  src/interpreter.py
# =============================================================
#
#  ¿QUÉ ES EL INTÉRPRETE?
#  Es la última fase del compilador: toma el AST (ya validado
#  léxica, sintáctica y semánticamente) y LO EJECUTA.
#
#  Para Costeñol usamos un INTÉRPRETE DE ÁRBOL (tree-walking
#  interpreter): recorre el AST nodo por nodo y ejecuta
#  las operaciones directamente en Python.
#
#  Esto es más simple que generar bytecode o ensamblador,
#  y es perfecto para un compilador académico como este.
#
#  ¿POR QUÉ NO COMPILAR A CÓDIGO MÁQUINA?
#  Porque el objetivo es académico: queremos entender cómo
#  funciona un compilador, no hacer optimizaciones de bajo nivel.
#  Un intérprete de árbol es equivalente funcionalmente.
#
#  Flujo:
#    AST validado + TablaEVainas → EjecutorCosteño → Resultados
# =============================================================

from src.ast_nodes import (
    NodoDeclaracion, NodoAsignacion, NodoCaptura, NodoMensaje,
    NodoNumeroEntero, NodoNumeroReal, NodoCadena, NodoBooleano,
    NodoIdentificador, NodoOperacion, NodoNegacion
)
from src.symbol_table import TablaEVainas


class EjecutorCosteño:
    """
    El Ejecutor Costeño — Intérprete de árbol del Compilador Costeñol.

    Recorre el AST y ejecuta cada instrucción.
    Usa la tabla de símbolos para leer y escribir variables.

    Nombre costeño: porque ejecuta con sabor y sin chicharrones.
    """

    def __init__(self, tabla: TablaEVainas, modo_arrebatao=False):
        """
        Args:
            tabla          (TablaEVainas): tabla de símbolos del análisis semántico
            modo_arrebatao (bool):         si True, imprime debug detallado
        """
        self.tabla          = tabla
        self.modo_arrebatao = modo_arrebatao  # Modo debug verboso costeño
        self.errores        = []

    # ----------------------------------------------------------
    #  MÉTODO PRINCIPAL: ejecutar
    # ----------------------------------------------------------
    def ejecutar(self, nodos):
        """
        Ejecuta una lista de nodos AST secuencialmente.

        Args:
            nodos (list): lista de nodos del programa

        Returns:
            bool: True si terminó sin errores
        """
        for nodo in nodos:
            self._ejecutar_nodo(nodo)
        return len(self.errores) == 0

    # ----------------------------------------------------------
    #  DISPATCHER: _ejecutar_nodo
    # ----------------------------------------------------------
    def _ejecutar_nodo(self, nodo):
        """
        Redirige la ejecución al método adecuado según el tipo de nodo.
        """
        if nodo is None:
            return None

        if isinstance(nodo, NodoDeclaracion):
            return self._exec_declaracion(nodo)
        elif isinstance(nodo, NodoAsignacion):
            return self._exec_asignacion(nodo)
        elif isinstance(nodo, NodoCaptura):
            return self._exec_captura(nodo)
        elif isinstance(nodo, NodoMensaje):
            return self._exec_mensaje(nodo)
        elif isinstance(nodo, NodoOperacion):
            return self._eval_operacion(nodo)
        elif isinstance(nodo, NodoNegacion):
            return self._eval_negacion(nodo)
        elif isinstance(nodo, NodoIdentificador):
            return self._eval_identificador(nodo)
        elif isinstance(nodo, NodoNumeroEntero):
            return nodo.valor
        elif isinstance(nodo, NodoNumeroReal):
            return nodo.valor
        elif isinstance(nodo, NodoCadena):
            return nodo.valor
        elif isinstance(nodo, NodoBooleano):
            return nodo.valor
        return None

    # ----------------------------------------------------------
    #  EJECUTAR DECLARACIÓN
    # ----------------------------------------------------------
    def _exec_declaracion(self, nodo):
        """
        La declaración ya fue procesada por el semántico.
        Aquí solo registramos en modo arrebatao.
        """
        if self.modo_arrebatao:
            print(f"  🔍 [Arrebatao] Declarando '{nodo.nombre}' "
                  f"como {nodo.tipo} — chévere.")

    # ----------------------------------------------------------
    #  EJECUTAR ASIGNACIÓN
    # ----------------------------------------------------------
    def _exec_asignacion(self, nodo):
        """
        Evalúa la expresión del lado derecho y guarda el resultado
        en la tabla de símbolos.
        """
        valor = self._ejecutar_nodo(nodo.expresion)
        tipo  = self.tabla.obtener_tipo(nodo.nombre)

        # Conversión de tipo si es necesaria
        valor = self._convertir(valor, tipo)

        self.tabla.asignar(nodo.nombre, valor)

        if self.modo_arrebatao:
            print(f"  🔍 [Arrebatao] Asignando {nodo.nombre} = {valor} ({tipo})")

    # ----------------------------------------------------------
    #  EJECUTAR CAPTURA
    # ----------------------------------------------------------
    def _exec_captura(self, nodo):
        """
        Solicita al usuario que ingrese un valor por consola.
        Convierte el input al tipo esperado.
        """
        tipo = nodo.tipo
        prompt = f"  📥 Ingresa un valor {tipo} para '{nodo.variable}': "

        try:
            entrada = input(prompt)

            # Convertir según el tipo esperado
            if tipo == 'Entero':
                valor = int(entrada)
            elif tipo == 'Real':
                valor = float(entrada)
            elif tipo == 'Logico':
                valor = entrada.lower() in ('verdadero', 'true', '1', 'si', 'sí')
            else:  # Texto
                valor = entrada

            self.tabla.asignar(nodo.variable, valor)

            if self.modo_arrebatao:
                print(f"  🔍 [Arrebatao] Capturado '{nodo.variable}' = {valor}")

        except ValueError:
            msg = (f"  🚨 Barro en captura de '{nodo.variable}': "
                   f"eso no es un {tipo}, cuadro.")
            self.errores.append(msg)
            print(msg)

    # ----------------------------------------------------------
    #  EJECUTAR MENSAJE (salida)
    # ----------------------------------------------------------
    def _exec_mensaje(self, nodo):
        """
        Evalúa la expresión del mensaje y la imprime en consola.
        """
        valor = self._ejecutar_nodo(nodo.contenido)
        # Formatear booleanos al estilo costeño
        if isinstance(valor, bool):
            valor = "verdadero" if valor else "falso"
        print(f"  💬 {valor}")

    # ----------------------------------------------------------
    #  EVALUAR OPERACIÓN BINARIA
    # ----------------------------------------------------------
    def _eval_operacion(self, nodo):
        """
        Evalúa una operación binaria (+, -, *, /, ^, ==, etc.).
        Retorna el resultado calculado.
        """
        izq = self._ejecutar_nodo(nodo.izquierda)
        der = self._ejecutar_nodo(nodo.derecha)

        try:
            op = nodo.operador
            if op == '+':
                # Concatenación si alguno es string
                if isinstance(izq, str) or isinstance(der, str):
                    return str(izq) + str(der)
                return izq + der
            elif op == '-':
                return izq - der
            elif op == '*':
                return izq * der
            elif op == '/':
                if der == 0:
                    msg = "  🚨 Chicharrón matemático: no puedes dividir por cero, cuadro."
                    self.errores.append(msg)
                    print(msg)
                    return None
                return izq / der
            elif op == '^':
                return izq ** der
            elif op == '==':
                return izq == der
            elif op == '!=':
                return izq != der
            elif op == '>':
                return izq > der
            elif op == '<':
                return izq < der
            elif op == '>=':
                return izq >= der
            elif op == '<=':
                return izq <= der
            elif op == '&&':
                return bool(izq) and bool(der)
            elif op == '||':
                return bool(izq) or bool(der)
        except TypeError as e:
            msg = f"  🚨 Barro en operación '{nodo.operador}': tipos incompatibles."
            self.errores.append(msg)
            print(msg)
            return None

    # ----------------------------------------------------------
    #  EVALUAR NEGACIÓN UNARIA
    # ----------------------------------------------------------
    def _eval_negacion(self, nodo):
        """
        Evalúa la negación unaria: -valor o !valor
        """
        val = self._ejecutar_nodo(nodo.operando)
        if nodo.operador == '-':
            return -val
        elif nodo.operador == '!':
            return not val

    # ----------------------------------------------------------
    #  EVALUAR IDENTIFICADOR (leer variable)
    # ----------------------------------------------------------
    def _eval_identificador(self, nodo):
        """
        Lee el valor actual de una variable desde la tabla de símbolos.
        """
        valor = self.tabla.obtener_valor(nodo.nombre)
        if valor is None:
            # Puede ser None legítimamente (no asignada aún)
            if self.modo_arrebatao:
                print(f"  ⚠️  [Arrebatao] '{nodo.nombre}' no tiene valor aún.")
        return valor

    # ----------------------------------------------------------
    #  CONVERSIÓN DE TIPOS
    # ----------------------------------------------------------
    def _convertir(self, valor, tipo_destino):
        """
        Convierte un valor al tipo de dato correcto del lenguaje.
        Evita errores de tipo al guardar en la tabla.
        """
        if valor is None:
            return None
        try:
            if tipo_destino == 'Entero':
                return int(valor)
            elif tipo_destino == 'Real':
                return float(valor)
            elif tipo_destino == 'Texto':
                return str(valor)
            elif tipo_destino == 'Logico':
                return bool(valor)
        except (ValueError, TypeError):
            return valor  # Devolver tal como está si falla la conversión
        return valor
