# 🌊 Compilador Costeñol

> *"Bacano, cuadro. El compilador del Malecón."*

Compilador académico inspirado en la jerga caribeña colombiana (Barranquilla).
Desarrollado en **Python** con **SLY** para la asignatura de Compiladores.

---

## 🚀 Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone https://github.com/IngMiller07/COSTE-OL.git
cd COSTE-OL
```

### 2. Instalar dependencias

```bash
py -m pip install sly colorama
```

> **Nota:** `tkinter` ya viene incluido con Python — no necesitas instalarlo.

### 3. Abrir la IDE de escritorio

```bash
py -X utf8 ide_desktop.py
```

¡Listo! Se abre la ventana del IDE. Escribe código Costeñol y presiona **▶ Compilar y Ejecutar** o `Ctrl + Enter`.

---

## 🖥️ IDE de Escritorio

La IDE tiene:

| Sección | Función |
|---------|---------|
| **Panel izquierdo** | Ejemplos precargados — clic para abrir |
| **Editor** | Escribe tu código `.cos` con syntax highlighting |
| **Fases** | Indicadores verdes/rojos de Lexer, Parser, Semántica y Ejecutor |
| **💬 Consola** | Salida del programa y errores costeños |
| **📋 Tabla e' Vainas** | Variables con nombre, tipo, valor y línea |
| **🔤 Tokens** | Todos los tokens del Lexer del Malecón |
| **Modo Arrebatao 🔥** | Debug completo y verboso |

**Atajos de teclado:**
- `Ctrl + Enter` → Compilar y ejecutar
- `Ctrl + Z` / `Ctrl + Y` → Deshacer / Rehacer

---

## 📝 Sintaxis del Lenguaje Costeñol

### Tipos de dato
```
Entero   → Números enteros:   num1 Entero;
Texto    → Cadenas de texto:  nombre Texto;
Real     → Decimales:         pi Real;
Logico   → Booleanos:         activo Logico;
```

### Declaración
```
num1 Entero;
nombre Texto;
```

### Asignación
```
num1 = 42;
nombre = "Alejandra";
pi = 3.1416;
activo = verdadero;
suma = num1 + num2;
```

### Captura (input del usuario)
```
nombre = Captura.Texto();
num1   = Captura.Entero();
pi     = Captura.Real();
activo = Captura.Logico();
```

### Salida
```
Mensaje.Texto("Hola cuadro");
Mensaje.Texto(nombre);
```

### Operadores
```
+  -  *  /  ^          ← Aritméticos
== != > < >= <=        ← Comparación
&& ||                  ← Lógicos
```

### Comentarios
```
// Esto es un comentario, se ignora al compilar
```

---

## 🏗️ Estructura del Proyecto

```
COSTE-OL/
├── ide_desktop.py       ← ⭐ PUNTO DE ENTRADA PRINCIPAL (IDE)
├── costeñol.py          ← Compilador por línea de comandos
├── requirements.txt     ← Dependencias
│
├── src/
│   ├── lexer.py         ← Lexer del Malecón (tokenización)
│   ├── parser.py        ← Parser Bacano (sintaxis + AST)
│   ├── ast_nodes.py     ← Nodos del Árbol Sintáctico
│   ├── symbol_table.py  ← Tabla e' Vainas (variables)
│   ├── semantic.py      ← Analizador Sabroso (semántica)
│   ├── interpreter.py   ← Ejecutor Costeño (intérprete)
│   └── compiler_api.py  ← API programática del compilador
│
├── examples/
│   ├── hola_cuadro.cos  ← Hola Mundo costeño
│   ├── calculadora.cos  ← Operaciones aritméticas
│   └── variables.cos    ← Todos los tipos + captura
│
└── tests/
    ├── test_lexer.py    ← Tests del Lexer (16 pruebas)
    └── test_parser.py   ← Tests del Parser y Semántica (12 pruebas)
```

---

## 💻 Uso por Línea de Comandos (alternativo)

```bash
# Compilar un archivo
py -X utf8 costeñol.py examples/hola_cuadro.cos

# Modo debug completo
py -X utf8 costeñol.py examples/calculadora.cos --arrebatao

# Ayuda
py -X utf8 costeñol.py --ayuda
```

---

## 🧪 Ejecutar Tests

```bash
# Tests del Lexer (16 pruebas)
py -X utf8 tests/test_lexer.py

# Tests del Parser y Semántica (12 pruebas)
py -X utf8 tests/test_parser.py
```

---

## 🏛️ Fases del Compilador

| # | Fase | Módulo | Qué hace |
|---|------|--------|----------|
| 1 | **Lexer del Malecón** | `lexer.py` | Convierte código → tokens |
| 2 | **Parser Bacano** | `parser.py` | Verifica gramática → construye AST |
| 3 | **Tabla e' Vainas** | `symbol_table.py` | Almacena variables |
| 3 | **Analizador Sabroso** | `semantic.py` | Valida tipos y variables |
| 4 | **Ejecutor Costeño** | `interpreter.py` | Ejecuta el AST |

---

## 📦 Exportar para Compañeros

Para que tus compañeros usen el proyecto en su PC:

### Opción A — Clonar desde GitHub (recomendado)

```bash
git clone https://github.com/IngMiller07/COSTE-OL.git
cd COSTE-OL
py -m pip install sly colorama
py -X utf8 ide_desktop.py
```

### Opción B — Descargar ZIP desde GitHub

1. Ir a `https://github.com/IngMiller07/COSTE-OL`
2. Clic en **Code → Download ZIP**
3. Descomprimir la carpeta
4. Abrir terminal en la carpeta descomprimida
5. Ejecutar:
   ```bash
   py -m pip install sly colorama
   py -X utf8 ide_desktop.py
   ```

### Requisitos del sistema

- Python 3.8 o superior (recomendado 3.10+)
- Windows, macOS o Linux
- Verificar Python instalado: `py --version`
- Si no tienen `py`, usar `python` o `python3`

---

## 🌴 Glosario Costeño

| Término | Significado técnico |
|---------|---------------------|
| Chicharrón | Error de compilación |
| Bacano | Éxito / Correcto |
| Tabla e' Vainas | Tabla de símbolos |
| Modo Arrebatao | Modo debug verboso |
| Lexer del Malecón | Analizador léxico |
| Parser Bacano | Analizador sintáctico |
| Analizador Sabroso | Analizador semántico |
| Ejecutor Costeño | Intérprete de árbol |

---

> *"Sin chicharrones y con calidad. Así se compila en el Malecón."* 🌊
