# =============================================================
#  COSTEÑOL — Punto de Entrada Principal
#  costeñol.py
# =============================================================
#
#  ¿QUÉ ES ESTO?
#  El corazón del compilador. Desde aquí se orquesta todo:
#    1. Leer el archivo fuente (.cos)
#    2. Tokenizar con el Lexer del Malecón
#    3. Parsear con el Parser Bacano
#    4. Validar con el Analizador Sabroso
#    5. Ejecutar con el Ejecutor Costeño
#    6. Mostrar resultados en la Consola Costeña
#
#  USO:
#    py costeñol.py archivo.cos
#    py costeñol.py archivo.cos --arrebatao
#    py costeñol.py --ayuda
# =============================================================

import sys
import os
import io

# Reconfigurar stdout para soportar UTF-8 en terminales Windows
# Esto evita el UnicodeEncodeError con caracteres especiales
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio raíz al path para que Python encuentre 'src' y 'ui'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer      import LexerMalecon
from src.parser     import ParserBacano
from src.semantic   import AnalizadorSabroso
from src.interpreter import EjecutorCosteño
from ui.console     import (
    BANNER, AYUDA,
    titulo_seccion, separador,
    msg_ok, msg_error, msg_info,
    inicio_lexer, fin_lexer,
    inicio_parser, fin_parser,
    inicio_semantico, fin_semantico_ok,
    inicio_ejecucion, fin_ejecucion,
    exito_compilacion, error_compilacion, advertencias_compilacion,
    mostrar_tokens, banner_arrebatao
)


def compilar(codigo_fuente: str, modo_arrebatao: bool = False) -> bool:
    """
    Función principal del compilador Costeñol.
    Ejecuta todas las fases en orden y retorna True si tuvo éxito.

    Args:
        codigo_fuente  (str):  código Costeñol a compilar
        modo_arrebatao (bool): si True, muestra debug detallado

    Returns:
        bool: True si compiló y ejecutó sin errores
    """
    if modo_arrebatao:
        banner_arrebatao()

    # ==========================================================
    #  FASE 1: ANÁLISIS LÉXICO — Lexer del Malecón
    # ==========================================================
    inicio_lexer()

    lexer = LexerMalecon()

    # Generar lista de tokens (el lexer es un generador en SLY)
    tokens_list = list(lexer.tokenize(codigo_fuente))

    fin_lexer(len(tokens_list))

    # En modo arrebatao: mostrar la tabla completa de tokens
    if modo_arrebatao:
        mostrar_tokens(tokens_list)

    # Si no hay tokens, el programa está vacío
    if not tokens_list:
        msg_info("El programa está vacío, cuadro. ¿No ibas a escribir algo?")
        return True

    # ==========================================================
    #  FASE 2: ANÁLISIS SINTÁCTICO — Parser Bacano
    # ==========================================================
    inicio_parser()

    parser = ParserBacano()

    # Re-tokenizar para el parser (el generador ya fue consumido)
    ast = parser.parse(LexerMalecon().tokenize(codigo_fuente))

    if ast is None:
        ast = []

    n_nodos = len(ast) if ast else 0
    fin_parser(n_nodos)

    # Si hubo errores sintácticos, no seguir
    if parser.errores:
        error_compilacion(len(parser.errores))
        return False

    # ==========================================================
    #  FASE 3: ANÁLISIS SEMÁNTICO — Analizador Sabroso
    # ==========================================================
    inicio_semantico()

    semantico = AnalizadorSabroso()
    sem_ok = semantico.analizar(ast)

    if semantico.advertencias:
        advertencias_compilacion(len(semantico.advertencias))

    if not sem_ok:
        error_compilacion(len(semantico.errores))
        return False

    fin_semantico_ok()

    # Mostrar tabla de símbolos en modo arrebatao
    if modo_arrebatao:
        titulo_seccion("TABLA E' VAINAS (después del análisis semántico)")
        semantico.tabla.mostrar()

    # ==========================================================
    #  FASE 4: EJECUCIÓN — Ejecutor Costeño
    # ==========================================================
    inicio_ejecucion()

    ejecutor = EjecutorCosteño(semantico.tabla, modo_arrebatao)
    exec_ok  = ejecutor.ejecutar(ast)

    fin_ejecucion()

    # Mostrar tabla de símbolos final en modo arrebatao
    if modo_arrebatao:
        titulo_seccion("TABLA E' VAINAS (después de la ejecución)")
        ejecutor.tabla.mostrar()

    # ==========================================================
    #  RESULTADO FINAL
    # ==========================================================
    if exec_ok and not ejecutor.errores:
        exito_compilacion()
        return True
    else:
        error_compilacion(len(ejecutor.errores))
        return False


def main():
    """
    Punto de entrada del compilador Costeñol.
    Procesa los argumentos de línea de comandos.
    """
    print(BANNER)

    # Procesar argumentos
    args = sys.argv[1:]

    # Sin argumentos → mostrar ayuda
    if not args:
        print(AYUDA)
        return

    # Pedir ayuda
    if '--ayuda' in args or '--help' in args or '-h' in args:
        print(AYUDA)
        return

    # Detectar modo arrebatao
    modo_arrebatao = '--arrebatao' in args
    # Filtrar el flag para obtener solo el nombre de archivo
    archivos = [a for a in args if not a.startswith('--')]

    if not archivos:
        msg_error("Eche, cuadro, ¿dónde está el archivo .cos? "
                  "Usa: py costeñol.py mi_programa.cos")
        return

    archivo = archivos[0]

    # Verificar que el archivo existe
    if not os.path.isfile(archivo):
        msg_error(f"Barro, cuadro... el archivo '{archivo}' no existe. "
                  f"¿Lo escribiste bien?")
        return

    # Leer el código fuente
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            codigo_fuente = f.read()
    except Exception as e:
        msg_error(f"Chicharrón al leer '{archivo}': {e}")
        return

    titulo_seccion(f"Compilando: {archivo}")

    # Ejecutar el compilador
    compilar(codigo_fuente, modo_arrebatao)


if __name__ == '__main__':
    main()
