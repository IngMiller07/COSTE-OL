# =============================================================
#  COSTEÑOL — Tests del Lexer del Malecón
#  tests/test_lexer.py
# =============================================================
#
#  Pruebas unitarias para verificar que el Lexer tokeniza
#  correctamente todos los casos del lenguaje Costeñol.
#
#  Para ejecutar:
#    py -m pytest tests/test_lexer.py -v
# =============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import LexerMalecon


def tokenizar(codigo):
    """Helper: tokeniza un string y retorna lista de (tipo, valor)."""
    lexer = LexerMalecon()
    return [(t.type, t.value) for t in lexer.tokenize(codigo)]


class TestLexerMalecon:

    def test_declaracion_entero(self):
        """num1 Entero; → ID, ENTERO, PUNTO_COMA"""
        tokens = tokenizar("num1 Entero;")
        assert tokens == [('ID', 'num1'), ('ENTERO', 'Entero'), ('PUNTO_COMA', ';')]

    def test_declaracion_texto(self):
        tokens = tokenizar("nombre Texto;")
        assert tokens == [('ID', 'nombre'), ('TEXTO', 'Texto'), ('PUNTO_COMA', ';')]

    def test_declaracion_real(self):
        tokens = tokenizar("n1 Real;")
        assert tokens == [('ID', 'n1'), ('REAL', 'Real'), ('PUNTO_COMA', ';')]

    def test_declaracion_logico(self):
        tokens = tokenizar("asis Logico;")
        assert tokens == [('ID', 'asis'), ('LOGICO', 'Logico'), ('PUNTO_COMA', ';')]

    def test_numero_entero(self):
        tokens = tokenizar("42")
        assert tokens == [('NUMERO_ENTERO', 42)]

    def test_numero_real(self):
        tokens = tokenizar("3.1416")
        assert tokens == [('NUMERO_REAL', 3.1416)]

    def test_cadena(self):
        tokens = tokenizar('"Hola cuadro"')
        assert tokens == [('CADENA', 'Hola cuadro')]

    def test_operadores_aritmeticos(self):
        tokens = tokenizar("+ - * / ^")
        tipos = [t for t, _ in tokens]
        assert tipos == ['MAS', 'MENOS', 'POR', 'ENTRE', 'POTENCIA']

    def test_operadores_comparacion(self):
        tokens = tokenizar("== != > < >= <=")
        tipos = [t for t, _ in tokens]
        assert tipos == ['IGUAL_IGUAL', 'DIFERENTE', 'MAYOR', 'MENOR',
                         'MAYOR_IGUAL', 'MENOR_IGUAL']

    def test_asignacion(self):
        tokens = tokenizar("A = b;")
        tipos = [t for t, _ in tokens]
        assert tipos == ['ID', 'IGUAL', 'ID', 'PUNTO_COMA']

    def test_captura(self):
        tokens = tokenizar("nombre = Captura.Texto();")
        tipos = [t for t, _ in tokens]
        assert tipos == ['ID', 'IGUAL', 'CAPTURA', 'PUNTO', 'TEXTO',
                         'LPAREN', 'RPAREN', 'PUNTO_COMA']

    def test_mensaje(self):
        tokens = tokenizar('Mensaje.Texto("Prueba");')
        tipos = [t for t, _ in tokens]
        assert tipos == ['MENSAJE', 'PUNTO', 'TEXTO', 'LPAREN',
                         'CADENA', 'RPAREN', 'PUNTO_COMA']

    def test_booleanos(self):
        tokens = tokenizar("verdadero falso")
        tipos = [t for t, _ in tokens]
        assert tipos == ['VERDADERO', 'FALSO']

    def test_comentario_ignorado(self):
        tokens = tokenizar("// Este es un comentario\nnum1 Entero;")
        tipos = [t for t, _ in tokens]
        assert tipos == ['ID', 'ENTERO', 'PUNTO_COMA']

    def test_expresion_aritmetica(self):
        tokens = tokenizar("num1 + (num2 * num3)")
        tipos = [t for t, _ in tokens]
        assert tipos == ['ID', 'MAS', 'LPAREN', 'ID', 'POR', 'ID', 'RPAREN']

    def test_programa_completo(self):
        codigo = """
        num1 Entero;
        nombre Texto;
        num1 = 42;
        nombre = "Alejandra";
        Mensaje.Texto("Hola");
        """
        tokens = tokenizar(codigo)
        # Verificar que se generaron tokens (no vacío)
        assert len(tokens) > 0
        # Verificar primer token
        assert tokens[0] == ('ID', 'num1')


if __name__ == '__main__':
    # Ejecutar tests manualmente sin pytest
    t = TestLexerMalecon()
    tests = [m for m in dir(t) if m.startswith('test_')]
    pasados = 0
    fallados = 0
    for nombre_test in tests:
        try:
            getattr(t, nombre_test)()
            print(f"  ✅ {nombre_test}")
            pasados += 1
        except AssertionError as e:
            print(f"  ❌ {nombre_test}: {e}")
            fallados += 1
    print(f"\n  Resultado: {pasados} pasados, {fallados} fallados.")
