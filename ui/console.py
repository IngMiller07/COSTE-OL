# =============================================================
#  COSTEÑOL — Consola Costeña (UI)
#  ui/console.py
# =============================================================
#
#  ¿QUÉ ES ESTO?
#  El módulo de interfaz visual del compilador Costeñol.
#  Maneja todos los colores, mensajes, banner y presentación
#  de la terminal con identidad costeña.
#
#  Usa 'colorama' para colorear la salida en la terminal de Windows.
#  colorama.init() normaliza los códigos ANSI para que funcionen
#  correctamente en PowerShell y CMD.
# =============================================================

from colorama import init, Fore, Back, Style
init(autoreset=True, strip=False)  # strip=False → no quitar ANSI en Windows


# =============================================================
#  BANNER PRINCIPAL
# =============================================================

BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}
   ===================================================
   =   C O S T E N O L   -   Compilador del Malecon =
   ===================================================
{Style.RESET_ALL}
{Fore.YELLOW}  El Compilador del Malecon  |  Barranquilla, Colombia
{Fore.WHITE}  -----------------------------------------------------
{Fore.CYAN}  Lexer del Malecon  |  Parser Bacano  |  Tabla e' Vainas
{Fore.CYAN}  Analizador Sabroso  |  Ejecutor Costeno  |  Modo Arrebatao
{Fore.WHITE}  -----------------------------------------------------
{Fore.GREEN}  Version 1.0  |  Python + SLY  |  Aja, arrancamos, cuadro!
{Style.RESET_ALL}"""


# =============================================================
#  SEPARADORES Y SECCIONES
# =============================================================

def separador():
    print(f"{Fore.WHITE}  {'-' * 60}")

def titulo_seccion(texto):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}  >> {texto}")
    separador()


# =============================================================
#  MENSAJES DE ESTADO
# =============================================================

def msg_ok(texto):
    """Mensaje de éxito — color verde."""
    print(f"{Fore.GREEN}  ✅ {texto}")

def msg_error(texto):
    """Mensaje de error — color rojo."""
    print(f"{Fore.RED}  ❌ {texto}")

def msg_advertencia(texto):
    """Mensaje de advertencia — color amarillo."""
    print(f"{Fore.YELLOW}  ⚠️  {texto}")

def msg_info(texto):
    """Mensaje informativo — color cyan."""
    print(f"{Fore.CYAN}  ℹ️  {texto}")

def msg_debug(texto):
    """Mensaje de debug (modo arrebatao) — color magenta."""
    print(f"{Fore.MAGENTA}  🔍 [Arrebatao] {texto}")


# =============================================================
#  MENSAJES COSTEÑOS DE COMPILACIÓN
# =============================================================

def exito_compilacion():
    print(f"\n{Fore.GREEN}{Style.BRIGHT}  🎉 ¡Bacano, cuadro! El código corrió sin chicharrones.")
    print(f"{Fore.GREEN}     Compilación del carajo. Ajá, todo chévere por aquí. 🌴")

def error_compilacion(n_errores):
    print(f"\n{Fore.RED}{Style.BRIGHT}  💥 Eche, cuadro... salieron {n_errores} chicharrón(es).")
    print(f"{Fore.RED}     Revisa los errores arriba y vuelve a intentarlo, no te achicopales.")

def advertencias_compilacion(n_adv):
    print(f"\n{Fore.YELLOW}  ⚡ Salieron {n_adv} advertencia(s), cuadro.")
    print(f"{Fore.YELLOW}    No son errores fatales, pero tenlas en cuenta.")

def inicio_lexer():
    print(f"\n{Fore.CYAN}  🔤 Lexer del Malecón arrancando...")

def fin_lexer(n_tokens):
    print(f"{Fore.GREEN}  ✅ Tokenización completa: {n_tokens} token(s) encontrado(s). ¡Calidad!")

def inicio_parser():
    print(f"\n{Fore.CYAN}  🌳 Parser Bacano analizando la estructura...")

def fin_parser(n_nodos):
    print(f"{Fore.GREEN}  ✅ Árbol sintáctico construido: {n_nodos} nodo(s). ¡Bacano!")

def inicio_semantico():
    print(f"\n{Fore.CYAN}  🧠 Analizador Sabroso verificando el sentido...")

def fin_semantico_ok():
    print(f"{Fore.GREEN}  ✅ Semántica aprobada. Sin chicharrones de tipos. ¡Chévere!")

def inicio_ejecucion():
    print(f"\n{Fore.CYAN}  ▶️  Ejecutor Costeño en acción...")
    separador()

def fin_ejecucion():
    separador()
    print(f"{Fore.GREEN}  ✅ Ejecución terminada. ¡Del carajo, cuadro!")


# =============================================================
#  VISUALIZACIÓN DE TOKENS (para debug o modo arrebatao)
# =============================================================

def mostrar_tokens(tokens):
    """
    Imprime la lista de tokens en formato tabla.
    Útil para el modo arrebatao o para explicar el lexer.
    """
    titulo_seccion("TOKENS DEL LEXER DEL MALECÓN")
    print(f"  {'#':<5} {'TIPO':<18} {'VALOR':<20} {'LÍNEA'}")
    print(f"  {'─'*5} {'─'*18} {'─'*20} {'─'*6}")
    for i, tok in enumerate(tokens, 1):
        print(f"  {i:<5} {tok.type:<18} {str(tok.value):<20} {tok.lineno}")
    separador()


# =============================================================
#  MODO ARREBATAO (debug verboso)
# =============================================================

def banner_arrebatao():
    print(f"""
{Fore.MAGENTA}{Style.BRIGHT}
  ╔══════════════════════════════════════╗
  ║   🔥  MODO ARREBATAO ACTIVADO  🔥   ║
  ║   Debug completo. Todo lo que pasa  ║
  ║   adentro va a quedar expuesto.     ║
  ╚══════════════════════════════════════╝
{Style.RESET_ALL}""")


# =============================================================
#  AYUDA DEL COMPILADOR
# =============================================================

AYUDA = f"""
{Fore.CYAN}{Style.BRIGHT}  COSTEÑOL — Compilador del Malecón
{Fore.WHITE}  ──────────────────────────────────

  USO:
    py costeñol.py [archivo.cos]
    py costeñol.py [archivo.cos] --arrebatao
    py costeñol.py --ayuda

  OPCIONES:
    archivo.cos     Archivo fuente Costeñol a compilar
    --arrebatao     Modo debug verboso (muestra tokens, AST y tabla)
    --ayuda         Muestra este mensaje de ayuda

  EJEMPLO:
    py costeñol.py examples/hola_cuadro.cos
    py costeñol.py examples/calculadora.cos --arrebatao

  TIPOS DE DATO SOPORTADOS:
    Entero    → Números enteros (42, -5, 0)
    Real      → Números decimales (3.14, 2.5)
    Texto     → Cadenas de texto ("Hola cuadro")
    Logico    → Booleanos (verdadero, falso)

  SINTAXIS BÁSICA:
    num1 Entero;                    ← Declaración
    num1 = 42;                      ← Asignación
    num1 = Captura.Entero();        ← Captura de usuario
    Mensaje.Texto("Hola cuadro");   ← Salida
    Mensaje.Texto(num1);            ← Salida de variable

  ¡Que no te dé chicharrón, cuadro! 🌴
{Style.RESET_ALL}"""
