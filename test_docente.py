import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.compiler_api import compilar_codigo

print("=== PROBANDO CÓDIGO CON ERROR (DEL DOCENTE) ===")
# Codigo del docente (con los errores que trae)
codigo_err = """num1 Entero;
num2 Entero;
num1=Captura.Texto();
num2=Captura.Entero();
sum=num1+num2);
Mensaje.Texto(El resultado es:"sum");
"""

data = compilar_codigo(codigo_err)
print('SUCCESS:', data['success'])
print('ERRORES:')
for e in data['errores']:
    print(' ', e)
print('ADVERTENCIAS:')
for a in data['advertencias']:
    print(' ', a)

print("\n=== PROBANDO CÓDIGO CORREGIDO ===")
# Codigo corregido (removiendo el parentesis extra)
codigo_ok = """num1 Entero;
num2 Entero;
num1=Captura.Texto();
num2=Captura.Entero();
sum=num1+num2;
Mensaje.Texto(El resultado es:"sum");
"""

# Simularemos la entrada de datos en stdin para Captura
# En Python, sys.stdin puede ser mockeado o podemos pasar valores por defecto de EOFError.
# Como compilar_codigo usa input(), si sys.stdin no tiene lineas, dara EOFError y usara los defaults (0).
# Vamos a mockear sys.stdin con '10\n5\n' para simular num1=10 y num2=5
sys.stdin = io.StringIO("10\n5\n")

data_ok = compilar_codigo(codigo_ok)
print('SUCCESS:', data_ok['success'])
print('ERRORES:', data_ok['errores'])
print('ADVERTENCIAS:')
for a in data_ok['advertencias']:
    print(' ', a)
print('SALIDA DEL PROGRAMA:')
for s in data_ok['salida']:
    print(' ', s)
print('TABLA DE SÍMBOLOS:')
for t in data_ok['tabla']:
    print(' ', t)
