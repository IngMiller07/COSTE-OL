# =============================================================
#  COSTEÑOL — API del Compilador (interfaz programática)
#  src/compiler_api.py
# =============================================================
#
#  ¿QUÉ ES ESTO?
#  Una capa de abstracción sobre el compilador que devuelve
#  resultados estructurados (diccionarios Python) en vez de
#  imprimir directamente a la consola.
#
#  Esto es necesario para la IDE web: el servidor Flask llama
#  esta API, obtiene el resultado estructurado, y lo manda
#  al navegador como JSON.
# =============================================================

import io
import sys
import contextlib

from src.lexer       import LexerMalecon
from src.parser      import ParserBacano
from src.semantic    import AnalizadorSabroso
from src.interpreter import EjecutorCosteño


@contextlib.contextmanager
def capturar_stdout():
    """Captura todo lo que se imprima a stdout durante el bloque."""
    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        yield buffer
    finally:
        sys.stdout = old_stdout


def compilar_codigo(codigo_fuente: str, modo_arrebatao: bool = False) -> dict:
    """
    Compila y ejecuta código Costeñol.
    Retorna un diccionario con todos los resultados estructurados.

    Returns dict con:
        success       (bool):  True si compiló y ejecutó sin errores
        tokens        (list):  lista de dicts {tipo, valor, linea}
        ast_count     (int):   número de nodos en el AST
        errores       (list):  errores encontrados
        advertencias  (list):  advertencias encontradas
        tabla         (list):  lista de dicts {nombre, tipo, valor, linea}
        salida        (list):  líneas de salida del programa (Mensaje.Texto)
        fases         (dict):  estado de cada fase {lexer, parser, semantico, ejecutor}
    """
    resultado = {
        'success':      False,
        'tokens':       [],
        'ast_count':    0,
        'errores':      [],
        'advertencias': [],
        'tabla':        [],
        'salida':       [],
        'fases': {
            'lexer':     {'ok': False, 'msg': ''},
            'parser':    {'ok': False, 'msg': ''},
            'semantico': {'ok': False, 'msg': ''},
            'ejecutor':  {'ok': False, 'msg': ''},
        }
    }

    if not codigo_fuente or not codigo_fuente.strip():
        resultado['errores'].append('El programa está vacío, cuadro. ¿No ibas a escribir algo?')
        return resultado

    # ==========================================================
    #  FASE 1: LEXER
    # ==========================================================
    try:
        lexer = LexerMalecon()
        # Capturar stderr de SLY (donde imprime sus warnings)
        with capturar_stdout():
            tokens_gen = list(lexer.tokenize(codigo_fuente))

        for t in tokens_gen:
            resultado['tokens'].append({
                'tipo':  t.type,
                'valor': str(t.value),
                'linea': t.lineno,
            })

        n = len(tokens_gen)
        resultado['fases']['lexer'] = {
            'ok':  True,
            'msg': f'Tokenización completa: {n} token(s). ¡Calidad!'
        }
    except Exception as e:
        resultado['errores'].append(f'Chicharrón en el Lexer: {e}')
        resultado['fases']['lexer'] = {'ok': False, 'msg': str(e)}
        return resultado

    # ==========================================================
    #  FASE 2: PARSER
    # ==========================================================
    try:
        parser = ParserBacano()
        # Capturar errores que SLY imprime directamente
        with capturar_stdout():
            ast = parser.parse(LexerMalecon().tokenize(codigo_fuente))

        ast = ast or []
        resultado['ast_count'] = len(ast)

        if parser.errores:
            resultado['errores'].extend(parser.errores)
            resultado['fases']['parser'] = {
                'ok':  False,
                'msg': f'{len(parser.errores)} error(es) sintáctico(s)'
            }
            return resultado

        resultado['fases']['parser'] = {
            'ok':  True,
            'msg': f'Árbol sintáctico: {len(ast)} nodo(s). ¡Bacano!'
        }
    except Exception as e:
        resultado['errores'].append(f'Chicharrón en el Parser: {e}')
        resultado['fases']['parser'] = {'ok': False, 'msg': str(e)}
        return resultado

    # ==========================================================
    #  FASE 3: SEMÁNTICA
    # ==========================================================
    try:
        semantico = AnalizadorSabroso()
        with capturar_stdout():
            sem_ok = semantico.analizar(ast)

        resultado['advertencias'].extend(semantico.advertencias)

        # Construir tabla de símbolos para el frontend
        for nombre, entrada in semantico.tabla._tabla.items():
            resultado['tabla'].append({
                'nombre': entrada.nombre,
                'tipo':   entrada.tipo,
                'valor':  str(entrada.valor) if entrada.valor is not None else '—',
                'linea':  entrada.linea,
            })

        if not sem_ok:
            resultado['errores'].extend(semantico.errores)
            resultado['fases']['semantico'] = {
                'ok':  False,
                'msg': f'{len(semantico.errores)} error(es) semántico(s)'
            }
            return resultado

        resultado['fases']['semantico'] = {
            'ok':  True,
            'msg': 'Semántica aprobada. Sin chicharrones de tipos. ¡Chévere!'
        }
    except Exception as e:
        resultado['errores'].append(f'Chicharrón en el Analizador Sabroso: {e}')
        resultado['fases']['semantico'] = {'ok': False, 'msg': str(e)}
        return resultado

    # ==========================================================
    #  FASE 4: EJECUCIÓN
    # ==========================================================
    try:
        ejecutor = EjecutorCosteño(semantico.tabla, modo_arrebatao)

        # Capturar la salida del programa (Mensaje.Texto y debug)
        with capturar_stdout() as buf:
            exec_ok = ejecutor.ejecutar(ast)

        salida_raw = buf.getvalue()
        if salida_raw:
            resultado['salida'] = salida_raw.splitlines()

        # Actualizar tabla con valores post-ejecución
        resultado['tabla'] = []
        for nombre, entrada in ejecutor.tabla._tabla.items():
            resultado['tabla'].append({
                'nombre': entrada.nombre,
                'tipo':   entrada.tipo,
                'valor':  str(entrada.valor) if entrada.valor is not None else '—',
                'linea':  entrada.linea,
            })

        if ejecutor.errores:
            resultado['errores'].extend(ejecutor.errores)
            resultado['fases']['ejecutor'] = {
                'ok':  False,
                'msg': f'{len(ejecutor.errores)} error(es) en ejecución'
            }
        else:
            resultado['fases']['ejecutor'] = {
                'ok':  True,
                'msg': '¡Ejecución del carajo, cuadro!'
            }
            resultado['success'] = True

    except Exception as e:
        resultado['errores'].append(f'Chicharrón en el Ejecutor: {e}')
        resultado['fases']['ejecutor'] = {'ok': False, 'msg': str(e)}

    return resultado
