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
#  Incluye un PREPROCESADOR que normaliza el código antes de
#  enviarlo al lexer, soportando variaciones de sintaxis como:
#    - Mensaje.Texto(El resultado es:"variable")
#    - ID=Captura.Tipo() (sin espacios)
# =============================================================

import io
import re
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


# =============================================================
#  PREPROCESADOR
#  Normaliza variaciones sintácticas del lenguaje antes de
#  enviar al lexer/parser.
# =============================================================

def _preprocesar(codigo: str) -> tuple:
    """
    Pre-procesa el código fuente de Costeñol para normalizar
    variaciones de sintaxis.

    Transformaciones aplicadas:
      1. Normaliza comillas tipográficas (curly quotes) a rectas.
      2. Mensaje.Texto(texto libre:"var") →
         Mensaje.Texto("texto libre:" + var);

    Returns:
        (str, list): código transformado y lista de advertencias de preprocesado
    """
    advertencias_prep = []

    # Normalizar comillas tipográficas (curly quotes) a rectas
    codigo = codigo.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    # ----------------------------------------------------------
    # Transformación: Mensaje.Texto(template con variables)
    #
    # Ejemplo:
    #   Mensaje.Texto(El resultado es:"sum");
    # Se convierte a:
    #   Mensaje.Texto("El resultado es:" + sum);
    # ----------------------------------------------------------
    def reemplazar_template(m):
        contenido = m.group(1)

        # Si ya es una expresión válida simple (comienza con " o es sólo ID)
        # no tocamos nada
        contenido_strip = contenido.strip()
        if contenido_strip.startswith('"') or re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ_]\w*$', contenido_strip):
            return m.group(0)  # Sin cambios

        # Detectar si hay variables entre comillas ("nombre_var")
        if '"' not in contenido:
            return m.group(0)  # Sin variables → sin cambios

        # Construir la expresión de concatenación
        partes = re.split(r'"([^"]+)"', contenido)
        expresiones = []
        for i, parte in enumerate(partes):
            parte = parte.strip()
            if not parte:
                continue
            if i % 2 == 0:
                if parte:
                    expresiones.append(f'"{parte}"')
            else:
                expresiones.append(parte)

        if not expresiones:
            return m.group(0)

        expr_final = ' + '.join(expresiones)
        advertencias_prep.append(
            f"  [Preprocesador] Template convertido: Mensaje.Texto({contenido}) "
            f"→ Mensaje.Texto({expr_final})"
        )
        return f'Mensaje.Texto({expr_final})'

    # Aplicar la transformación de templates
    codigo_procesado = re.sub(
        r'Mensaje\.Texto\(([^)]+)\)',
        reemplazar_template,
        codigo
    )

    return codigo_procesado, advertencias_prep


def compilar_codigo(codigo_fuente: str, modo_arrebatao: bool = False, fn_input=None) -> dict:
    """
    Compila y ejecuta código Costeñol.
    Retorna un diccionario con todos los resultados estructurados.

    Args:
        codigo_fuente   (str):  el código fuente a compilar
        modo_arrebatao  (bool): obsoleto (se mantiene por compatibilidad de firma)
        fn_input    (callable): función para capturar datos (ej: simpledialog de Tkinter)

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
        resultado['errores'].append('El programa esta vacio, cuadro. No ibas a escribir algo?')
        return resultado

    # ==========================================================
    #  FASE 0: PREPROCESAMIENTO
    # ==========================================================
    codigo_procesado, advertencias_prep = _preprocesar(codigo_fuente)
    resultado['advertencias'].extend(advertencias_prep)

    # ==========================================================
    #  FASE 1: LEXER
    # ==========================================================
    try:
        lexer = LexerMalecon()
        with capturar_stdout():
            tokens_gen = list(lexer.tokenize(codigo_procesado))

        for t in tokens_gen:
            resultado['tokens'].append({
                'tipo':  t.type,
                'valor': str(t.value),
                'linea': t.lineno,
            })

        n = len(tokens_gen)
        resultado['fases']['lexer'] = {
            'ok':  True,
            'msg': f'Tokenizacion completa: {n} token(s). Calidad!'
        }
    except Exception as e:
        resultado['errores'].append(f'Chicharron en el Lexer: {e}')
        resultado['fases']['lexer'] = {'ok': False, 'msg': str(e)}
        return resultado

    # ==========================================================
    #  FASE 2: PARSER
    # ==========================================================
    try:
        parser = ParserBacano()
        with capturar_stdout():
            ast = parser.parse(LexerMalecon().tokenize(codigo_procesado))

        ast = ast or []
        resultado['ast_count'] = len(ast)

        if parser.errores:
            resultado['errores'].extend(parser.errores)
            resultado['fases']['parser'] = {
                'ok':  False,
                'msg': f'{len(parser.errores)} error(es) sintactico(s)'
            }
            return resultado

        resultado['fases']['parser'] = {
            'ok':  True,
            'msg': f'Arbol sintactico: {len(ast)} nodo(s). Bacano!'
        }
    except Exception as e:
        resultado['errores'].append(f'Chicharron en el Parser: {e}')
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
                'valor':  str(entrada.valor) if entrada.valor is not None else '-',
                'linea':  entrada.linea,
            })

        if not sem_ok:
            resultado['errores'].extend(semantico.errores)
            resultado['fases']['semantico'] = {
                'ok':  False,
                'msg': f'{len(semantico.errores)} error(es) semantico(s)'
            }
            return resultado

        resultado['fases']['semantico'] = {
            'ok':  True,
            'msg': 'Semantica aprobada. Sin chicharrones de tipos. Chevere!'
        }
    except Exception as e:
        resultado['errores'].append(f'Chicharron en el Analizador Sabroso: {e}')
        resultado['fases']['semantico'] = {'ok': False, 'msg': str(e)}
        return resultado

    # ==========================================================
    #  FASE 4: EJECUCIÓN
    # ==========================================================
    try:
        ejecutor = EjecutorCosteño(semantico.tabla, fn_input=fn_input)

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
                'valor':  str(entrada.valor) if entrada.valor is not None else '-',
                'linea':  entrada.linea,
            })

        if ejecutor.errores:
            resultado['errores'].extend(ejecutor.errores)
            resultado['fases']['ejecutor'] = {
                'ok':  False,
                'msg': f'{len(ejecutor.errores)} error(es) en ejecucion'
            }
        else:
            resultado['fases']['ejecutor'] = {
                'ok':  True,
                'msg': 'Ejecucion exitosa, cuadro!'
            }
            resultado['success'] = True

    except Exception as e:
        resultado['errores'].append(f'Chicharron en el Ejecutor: {e}')
        resultado['fases']['ejecutor'] = {'ok': False, 'msg': str(e)}

    return resultado
