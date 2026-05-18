# =============================================================
#  COSTEÑOL — Tests del Parser Bacano y Semántica
#  tests/test_parser.py
# =============================================================
#
#  Para ejecutar:
#    py -m pytest tests/test_parser.py -v
# =============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer    import LexerMalecon
from src.parser   import ParserBacano
from src.semantic import AnalizadorSabroso
from src.ast_nodes import (
    NodoDeclaracion, NodoAsignacion, NodoCaptura,
    NodoMensaje, NodoNumeroEntero, NodoCadena
)


def parsear(codigo):
    """Helper: parsea código y retorna (ast, errores)."""
    parser = ParserBacano()
    ast = parser.parse(LexerMalecon().tokenize(codigo))
    return (ast or []), parser.errores


class TestParserBacano:

    def test_declaracion_entero(self):
        ast, errores = parsear("num1 Entero;")
        assert len(errores) == 0
        assert len(ast) == 1
        assert isinstance(ast[0], NodoDeclaracion)
        assert ast[0].nombre == 'num1'
        assert ast[0].tipo   == 'Entero'

    def test_declaracion_texto(self):
        ast, errores = parsear("nombre Texto;")
        assert len(errores) == 0
        assert isinstance(ast[0], NodoDeclaracion)
        assert ast[0].tipo == 'Texto'

    def test_asignacion_entero(self):
        ast, errores = parsear("num1 Entero;\nnum1 = 42;")
        assert len(errores) == 0
        assert len(ast) == 2
        assert isinstance(ast[1], NodoAsignacion)
        assert ast[1].nombre == 'num1'

    def test_asignacion_cadena(self):
        ast, errores = parsear('nombre Texto;\nnombre = "Alejandra";')
        assert len(errores) == 0
        asig = ast[1]
        assert isinstance(asig, NodoAsignacion)
        assert isinstance(asig.expresion, NodoCadena)
        assert asig.expresion.valor == 'Alejandra'

    def test_captura_texto(self):
        ast, errores = parsear("nombre Texto;\nnombre = Captura.Texto();")
        assert len(errores) == 0
        assert isinstance(ast[1], NodoCaptura)
        assert ast[1].tipo == 'Texto'

    def test_mensaje(self):
        ast, errores = parsear('Mensaje.Texto("Hola cuadro");')
        assert len(errores) == 0
        assert isinstance(ast[0], NodoMensaje)

    def test_programa_completo(self):
        codigo = """
        num1 Entero;
        num2 Entero;
        suma Entero;
        num1 = 10;
        num2 = 5;
        suma = num1 + num2;
        Mensaje.Texto(suma);
        """
        ast, errores = parsear(codigo)
        assert len(errores) == 0
        assert len(ast) == 7


class TestAnalizadorSabroso:

    def test_variable_declarada(self):
        ast, _ = parsear("num1 Entero;\nnum1 = 5;")
        sem = AnalizadorSabroso()
        ok = sem.analizar(ast)
        assert ok  # Sin errores semánticos

    def test_variable_no_declarada(self):
        ast, _ = parsear("num1 = 5;")
        sem = AnalizadorSabroso()
        ok = sem.analizar(ast)
        assert not ok  # Debe detectar error: num1 no declarada

    def test_tipos_incompatibles(self):
        ast, _ = parsear('nombre Texto;\nnombre = 42;')
        sem = AnalizadorSabroso()
        ok = sem.analizar(ast)
        assert not ok  # Texto no puede recibir Entero

    def test_tipos_numericos_compatibles(self):
        ast, _ = parsear("n1 Real;\nn1 = 3;")
        sem = AnalizadorSabroso()
        ok = sem.analizar(ast)
        assert ok  # Real puede recibir Entero (promoción)

    def test_tabla_simbolos_poblada(self):
        ast, _ = parsear("num1 Entero;\nnum2 Real;")
        sem = AnalizadorSabroso()
        sem.analizar(ast)
        assert sem.tabla.existe('num1')
        assert sem.tabla.obtener_tipo('num1') == 'Entero'
        assert sem.tabla.existe('num2')
        assert sem.tabla.obtener_tipo('num2') == 'Real'


if __name__ == '__main__':
    print("\n=== Tests Parser Bacano ===")
    t1 = TestParserBacano()
    tests1 = [m for m in dir(t1) if m.startswith('test_')]
    pasados = fallados = 0
    for nombre in tests1:
        try:
            getattr(t1, nombre)()
            print(f"  ✅ Parser::{nombre}")
            pasados += 1
        except AssertionError as e:
            print(f"  ❌ Parser::{nombre}: {e}")
            fallados += 1

    print("\n=== Tests Analizador Sabroso ===")
    t2 = TestAnalizadorSabroso()
    tests2 = [m for m in dir(t2) if m.startswith('test_')]
    for nombre in tests2:
        try:
            getattr(t2, nombre)()
            print(f"  ✅ Semantico::{nombre}")
            pasados += 1
        except AssertionError as e:
            print(f"  ❌ Semantico::{nombre}: {e}")
            fallados += 1

    print(f"\n  Resultado: {pasados} pasados, {fallados} fallados.")
