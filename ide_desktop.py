# =============================================================
#  COSTEÑOL — IDE de Escritorio (Tkinter)
#  ide_desktop.py
#  Uso: py ide_desktop.py
# =============================================================
import sys, os, io, tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.compiler_api import compilar_codigo

# ── Paleta de colores (tema oscuro) ─────────────────────────
BG       = '#1e1e2e'
BG2      = '#181825'
BG3      = '#24243e'
BORDER   = '#313244'
ACCENT   = '#cba6f7'
GREEN    = '#a6e3a1'
RED      = '#f38ba8'
YELLOW   = '#f9e2af'
BLUE     = '#89b4fa'
CYAN     = '#89dceb'
TEXT     = '#cdd6f4'
MUTED    = '#6c7086'

KEYWORDS  = ('Entero','Texto','Real','Logico','Captura','Mensaje','verdadero','falso')


class CosteñolIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('🌊 Costeñol IDE — Compilador del Malecón')
        self.configure(bg=BG)
        self.geometry('1200x700')
        self.minsize(900, 550)

        # Fuentes
        self.font_code = tkfont.Font(family='Consolas', size=12)
        self.font_out  = tkfont.Font(family='Consolas', size=11)
        self.font_ui   = tkfont.Font(family='Segoe UI',  size=10)
        self.font_bold = tkfont.Font(family='Segoe UI',  size=10, weight='bold')

        self.archivo_actual = None
        self._build_ui()
        self._cargar_ejemplo_bienvenida()

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_topbar()
        self._build_main()
        self._build_statusbar()

    def _build_topbar(self):
        bar = tk.Frame(self, bg=BG2, height=44)
        bar.pack(fill='x', side='top')
        bar.pack_propagate(False)

        tk.Label(bar, text='🌊 Costeñol IDE', bg=BG2, fg=ACCENT,
                 font=self.font_bold).pack(side='left', padx=(14,6), pady=8)
        tk.Label(bar, text='v1.0 · Barranquilla', bg=BG2, fg=MUTED,
                 font=self.font_ui).pack(side='left')

        # Botones derecha
        btn_cfg = dict(bg=BG3, fg=TEXT, activebackground=BORDER,
                       activeforeground=TEXT, bd=0, padx=12, pady=5,
                       font=self.font_ui, cursor='hand2')

        self.btn_run = tk.Button(bar, text='▶  Compilar y Ejecutar',
                                 bg=GREEN, fg=BG, activebackground='#7fc98a',
                                 activeforeground=BG, bd=0, padx=14, pady=5,
                                 font=self.font_bold, cursor='hand2',
                                 command=self.compilar)
        self.btn_run.pack(side='right', padx=(4,14), pady=6)

        tk.Button(bar, text='Guardar', command=self.guardar, **btn_cfg).pack(side='right', padx=2, pady=6)
        tk.Button(bar, text='Abrir',   command=self.abrir,   **btn_cfg).pack(side='right', padx=2, pady=6)
        tk.Button(bar, text='Nuevo',   command=self.nuevo,   **btn_cfg).pack(side='right', padx=2, pady=6)

        # Modo arrebatao
        self.arrebatao = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text='🔥 Modo Arrebatao', variable=self.arrebatao,
                       bg=BG2, fg=MUTED, selectcolor=BG2, activebackground=BG2,
                       activeforeground=ACCENT, font=self.font_ui,
                       cursor='hand2').pack(side='right', padx=8)

    def _build_main(self):
        paned = tk.PanedWindow(self, orient='horizontal', bg=BORDER,
                               sashwidth=4, sashrelief='flat')
        paned.pack(fill='both', expand=True)

        # ── IZQUIERDA: ejemplos + editor ─────────────────────
        left = tk.Frame(paned, bg=BG)
        paned.add(left, minsize=300)

        # Panel ejemplos
        sidebar = tk.Frame(left, bg=BG2, width=170)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text='EJEMPLOS', bg=BG2, fg=MUTED,
                 font=tkfont.Font(family='Segoe UI', size=9),
                 pady=8).pack(fill='x', padx=8)
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill='x')

        for nombre, codigo in self._ejemplos():
            tk.Button(sidebar, text=f'📄 {nombre}', anchor='w',
                      bg=BG2, fg=TEXT, activebackground=BG3, activeforeground=ACCENT,
                      bd=0, padx=10, pady=6, font=self.font_ui, cursor='hand2',
                      command=lambda c=codigo, n=nombre: self._abrir_ejemplo(n, c)
                      ).pack(fill='x')

        # Editor
        ed_frame = tk.Frame(left, bg=BG)
        ed_frame.pack(side='left', fill='both', expand=True)

        tk.Label(ed_frame, text=' EDITOR  ·  Costeñol', bg=BG3, fg=MUTED,
                 anchor='w', font=tkfont.Font(family='Segoe UI', size=9),
                 pady=4).pack(fill='x')

        # Frame editor + números de línea
        editor_area = tk.Frame(ed_frame, bg=BG)
        editor_area.pack(fill='both', expand=True)

        self.ln = tk.Text(editor_area, width=4, bg=BG2, fg=MUTED, bd=0,
                          font=self.font_code, state='disabled',
                          cursor='arrow', wrap='none', pady=4)
        self.ln.pack(side='left', fill='y')

        scroll_y = tk.Scrollbar(editor_area, orient='vertical', bg=BG2)
        scroll_y.pack(side='right', fill='y')
        scroll_x = tk.Scrollbar(ed_frame, orient='horizontal', bg=BG2)
        scroll_x.pack(fill='x')

        self.editor = tk.Text(editor_area, bg=BG, fg=TEXT, insertbackground=ACCENT,
                              selectbackground=BORDER, font=self.font_code,
                              bd=0, padx=8, pady=4, wrap='none', undo=True,
                              yscrollcommand=self._sync_scroll_y,
                              xscrollcommand=scroll_x.set)
        self.editor.pack(side='left', fill='both', expand=True)
        scroll_y.config(command=self._scroll_both_y)
        scroll_x.config(command=self.editor.xview)

        self.editor.bind('<KeyRelease>', self._on_key)
        self.editor.bind('<Return>',     self._on_key)
        self.editor.bind('<Control-Return>', lambda e: self.compilar())
        self.editor.bind('<Tab>', self._tab_to_spaces)

        self._setup_highlighting()

        # ── DERECHA: output ───────────────────────────────────
        right = tk.Frame(paned, bg=BG)
        paned.add(right, minsize=340)

        # Indicadores de fases
        fases_frame = tk.Frame(right, bg=BG2, pady=6)
        fases_frame.pack(fill='x')
        self.fase_dots = {}
        self.fase_msgs = {}
        fases = [
            ('lexer',     '🔤 Lexer del Malecón'),
            ('parser',    '🌳 Parser Bacano'),
            ('semantico', '🧠 Analizador Sabroso'),
            ('ejecutor',  '▶️  Ejecutor Costeño'),
        ]
        for key, label in fases:
            row = tk.Frame(fases_frame, bg=BG2)
            row.pack(fill='x', padx=10, pady=1)
            dot = tk.Label(row, text='●', bg=BG2, fg=MUTED, font=self.font_ui)
            dot.pack(side='left')
            tk.Label(row, text=label, bg=BG2, fg=MUTED, width=20, anchor='w',
                     font=tkfont.Font(family='Segoe UI', size=9)).pack(side='left', padx=4)
            msg = tk.Label(row, text='En espera...', bg=BG2, fg=MUTED, anchor='w',
                           font=tkfont.Font(family='Segoe UI', size=9))
            msg.pack(side='left', fill='x', expand=True)
            self.fase_dots[key] = dot
            self.fase_msgs[key] = msg

        tk.Frame(right, bg=BORDER, height=1).pack(fill='x')

        # Notebook tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('C.TNotebook',           background=BG2, borderwidth=0)
        style.configure('C.TNotebook.Tab',        background=BG2, foreground=MUTED,
                         padding=[12,5], font=('Segoe UI', 9))
        style.map('C.TNotebook.Tab',
                  background=[('selected', BG3)],
                  foreground=[('selected', ACCENT)])

        nb = ttk.Notebook(right, style='C.TNotebook')
        nb.pack(fill='both', expand=True)

        # Tab Consola
        tab_con = tk.Frame(nb, bg=BG)
        nb.add(tab_con, text='💬 Consola')
        self.consola = scrolledtext.ScrolledText(tab_con, bg=BG, fg=TEXT,
                                                  font=self.font_out, bd=0,
                                                  padx=10, pady=8, state='disabled',
                                                  wrap='word')
        self.consola.pack(fill='both', expand=True)
        for tag, color in [('ok',GREEN),('err',RED),('warn',YELLOW),
                            ('info',BLUE),('banner',CYAN),('muted',MUTED),('accent',ACCENT)]:
            self.consola.tag_config(tag, foreground=color)

        # Tab Tabla
        tab_tab = tk.Frame(nb, bg=BG)
        nb.add(tab_tab, text="📋 Tabla e' Vainas")
        cols = ('Nombre','Tipo','Valor','Línea')
        style.configure('C.Treeview', background=BG, foreground=TEXT,
                        fieldbackground=BG, rowheight=24,
                        font=('Consolas', 10), borderwidth=0)
        style.configure('C.Treeview.Heading', background=BG2, foreground=MUTED,
                        font=('Segoe UI', 9, 'bold'))
        style.map('C.Treeview', background=[('selected', BORDER)])
        self.tabla_tree = ttk.Treeview(tab_tab, columns=cols, show='headings',
                                        style='C.Treeview')
        for c, w in zip(cols, [120,80,120,60]):
            self.tabla_tree.heading(c, text=c)
            self.tabla_tree.column(c, width=w, anchor='w')
        self.tabla_tree.pack(fill='both', expand=True)

        # Tab Tokens
        tab_tok = tk.Frame(nb, bg=BG)
        nb.add(tab_tok, text='🔤 Tokens')
        self.tok_text = scrolledtext.ScrolledText(tab_tok, bg=BG, fg=TEXT,
                                                   font=self.font_out, bd=0,
                                                   padx=10, pady=8, state='disabled')
        self.tok_text.pack(fill='both', expand=True)
        self.tok_text.tag_config('tipo',  foreground=ACCENT)
        self.tok_text.tag_config('valor', foreground=TEXT)
        self.tok_text.tag_config('linea', foreground=MUTED)
        self.tok_text.tag_config('num',   foreground=BORDER)

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG2, height=24)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)
        self.st_status  = tk.Label(bar, text='Listo', bg=BG2, fg=GREEN,
                                    font=tkfont.Font(family='Segoe UI', size=9), padx=10)
        self.st_status.pack(side='left')
        self.st_tokens  = tk.Label(bar, text='0 tokens', bg=BG2, fg=MUTED,
                                    font=tkfont.Font(family='Segoe UI', size=9))
        self.st_tokens.pack(side='left', padx=8)
        self.st_nodos   = tk.Label(bar, text='0 nodos', bg=BG2, fg=MUTED,
                                    font=tkfont.Font(family='Segoe UI', size=9))
        self.st_nodos.pack(side='left', padx=8)
        self.st_errores = tk.Label(bar, text='0 errores', bg=BG2, fg=MUTED,
                                    font=tkfont.Font(family='Segoe UI', size=9))
        self.st_errores.pack(side='left', padx=8)
        self.st_file    = tk.Label(bar, text='sin_titulo.cos', bg=BG2, fg=MUTED,
                                    font=tkfont.Font(family='Segoe UI', size=9))
        self.st_file.pack(side='right', padx=10)
        tk.Label(bar, text='Python + SLY · Costeñol v1.0 · Barranquilla 🌊',
                 bg=BG2, fg=MUTED, font=tkfont.Font(family='Segoe UI', size=9)
                 ).pack(side='right', padx=10)

    # ── EDITOR ────────────────────────────────────────────────
    def _setup_highlighting(self):
        self.editor.tag_config('kw',      foreground=ACCENT)
        self.editor.tag_config('string',  foreground=YELLOW)
        self.editor.tag_config('comment', foreground=MUTED)
        self.editor.tag_config('number',  foreground=BLUE)
        self.editor.tag_config('paren',   foreground=CYAN)

    def _highlight(self):
        for tag in ('kw','string','comment','number','paren'):
            self.editor.tag_remove(tag, '1.0', 'end')
        content = self.editor.get('1.0', 'end')
        import re
        # Comentarios
        for m in re.finditer(r'//[^\n]*', content):
            self.editor.tag_add('comment', f'1.0+{m.start()}c', f'1.0+{m.end()}c')
        # Strings
        for m in re.finditer(r'"[^"]*"', content):
            self.editor.tag_add('string', f'1.0+{m.start()}c', f'1.0+{m.end()}c')
        # Keywords
        for kw in KEYWORDS:
            for m in re.finditer(r'\b' + kw + r'\b', content):
                self.editor.tag_add('kw', f'1.0+{m.start()}c', f'1.0+{m.end()}c')
        # Números
        for m in re.finditer(r'\b\d+\.?\d*\b', content):
            self.editor.tag_add('number', f'1.0+{m.start()}c', f'1.0+{m.end()}c')
        # Paréntesis/puntuación
        for m in re.finditer(r'[()\.;=]', content):
            self.editor.tag_add('paren', f'1.0+{m.start()}c', f'1.0+{m.end()}c')

    def _on_key(self, event=None):
        self._highlight()
        self._update_linenos()

    def _update_linenos(self):
        lines = self.editor.get('1.0', 'end').count('\n')
        nums = '\n'.join(str(i) for i in range(1, lines + 2))
        self.ln.config(state='normal')
        self.ln.delete('1.0', 'end')
        self.ln.insert('1.0', nums)
        self.ln.config(state='disabled')

    def _sync_scroll_y(self, *args):
        self.ln.yview_moveto(args[0])

    def _scroll_both_y(self, *args):
        self.editor.yview(*args)
        self.ln.yview(*args)

    def _tab_to_spaces(self, event):
        self.editor.insert('insert', '  ')
        return 'break'

    # ── ARCHIVOS ──────────────────────────────────────────────
    def nuevo(self):
        self.editor.delete('1.0', 'end')
        self.archivo_actual = None
        self.st_file.config(text='sin_titulo.cos')
        self._on_key()

    def abrir(self):
        ruta = filedialog.askopenfilename(
            title='Abrir archivo Costeñol',
            filetypes=[('Costeñol', '*.cos'), ('Todos', '*.*')])
        if ruta:
            with open(ruta, 'r', encoding='utf-8') as f:
                self.editor.delete('1.0', 'end')
                self.editor.insert('1.0', f.read())
            self.archivo_actual = ruta
            self.st_file.config(text=os.path.basename(ruta))
            self._on_key()

    def guardar(self):
        if not self.archivo_actual:
            ruta = filedialog.asksaveasfilename(
                defaultextension='.cos',
                filetypes=[('Costeñol', '*.cos'), ('Todos', '*.*')])
            if not ruta: return
            self.archivo_actual = ruta
        with open(self.archivo_actual, 'w', encoding='utf-8') as f:
            f.write(self.editor.get('1.0', 'end'))
        self.st_file.config(text=os.path.basename(self.archivo_actual))
        self.st_status.config(text='Guardado ✓', fg=GREEN)

    def _abrir_ejemplo(self, nombre, codigo):
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', codigo)
        self.st_file.config(text=nombre + '.cos')
        self._on_key()

    # ── COMPILAR ──────────────────────────────────────────────
    def compilar(self):
        codigo = self.editor.get('1.0', 'end').strip()
        arrebatao = self.arrebatao.get()

        self.btn_run.config(text='⏳ Compilando...', state='disabled')
        self.update()

        self._reset_fases()
        self._limpiar_consola()

        try:
            data = compilar_codigo(codigo, arrebatao)
        except Exception as e:
            self._escribir('❌ Error interno: ' + str(e) + '\n', 'err')
            self.btn_run.config(text='▶  Compilar y Ejecutar', state='normal')
            return

        self._mostrar_resultado(data)
        self.btn_run.config(text='▶  Compilar y Ejecutar', state='normal')

    def _mostrar_resultado(self, data):
        # Fases
        fases_map = {'lexer':'lexer','parser':'parser',
                     'semantico':'semantico','ejecutor':'ejecutor'}
        for k, v in (data.get('fases') or {}).items():
            dot = self.fase_dots.get(k)
            msg = self.fase_msgs.get(k)
            if dot and msg:
                color = GREEN if v.get('ok') else RED
                dot.config(fg=color)
                msg.config(text=v.get('msg',''), fg=color)

        # Consola
        self._escribir('═' * 45 + '\n', 'muted')
        self._escribir(' 🌊  COSTEÑOL — Resultado\n', 'banner')
        self._escribir('═' * 45 + '\n', 'muted')

        if data.get('advertencias'):
            for a in data['advertencias']:
                self._escribir('⚠️  ' + a + '\n', 'warn')

        if data.get('errores'):
            self._escribir('\n── CHICHARRONES ──\n', 'warn')
            for e in data['errores']:
                self._escribir(e + '\n', 'err')

        if data.get('salida'):
            self._escribir('\n── SALIDA ──\n', 'info')
            for linea in data['salida']:
                tag = 'accent' if '[Arrebatao]' in linea else 'ok'
                self._escribir(linea + '\n', tag)

        self._escribir('\n', 'muted')
        if data.get('success'):
            self._escribir('🎉 ¡Bacano! El código corrió sin chicharrones. 🌴\n', 'ok')
            self.st_status.config(text='✅ Compilado', fg=GREEN)
        else:
            self._escribir('💥 Hay chicharrones. Revisa los errores arriba.\n', 'err')
            self.st_status.config(text='❌ Con errores', fg=RED)

        # Status bar
        self.st_tokens.config(text=f"{len(data.get('tokens',[]))} tokens")
        self.st_nodos.config(text=f"{data.get('ast_count',0)} nodos")
        n_err = len(data.get('errores',[]))
        self.st_errores.config(text=f'{n_err} error(es)',
                               fg=RED if n_err > 0 else GREEN)

        # Tabla
        for row in self.tabla_tree.get_children():
            self.tabla_tree.delete(row)
        for fila in data.get('tabla', []):
            self.tabla_tree.insert('', 'end',
                values=(fila['nombre'], fila['tipo'], fila['valor'], fila['linea']))

        # Tokens
        self.tok_text.config(state='normal')
        self.tok_text.delete('1.0', 'end')
        for i, t in enumerate(data.get('tokens', []), 1):
            self.tok_text.insert('end', f'{i:>4}  ', 'num')
            self.tok_text.insert('end', f'{t["tipo"]:<18}', 'tipo')
            self.tok_text.insert('end', f'{t["valor"]:<20}', 'valor')
            self.tok_text.insert('end', f':{t["linea"]}\n', 'linea')
        self.tok_text.config(state='disabled')

    def _limpiar_consola(self):
        self.consola.config(state='normal')
        self.consola.delete('1.0', 'end')
        self.consola.config(state='disabled')

    def _escribir(self, texto, tag='ok'):
        self.consola.config(state='normal')
        self.consola.insert('end', texto, tag)
        self.consola.see('end')
        self.consola.config(state='disabled')

    def _reset_fases(self):
        for dot in self.fase_dots.values():
            dot.config(fg=MUTED)
        for msg in self.fase_msgs.values():
            msg.config(text='En espera...', fg=MUTED)

    # ── EJEMPLOS ─────────────────────────────────────────────
    def _cargar_ejemplo_bienvenida(self):
        _, codigo = self._ejemplos()[0]
        self.editor.insert('1.0', codigo)
        self._on_key()

    def _ejemplos(self):
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')
        ejemplos = []
        if os.path.isdir(base):
            for f in sorted(os.listdir(base)):
                if f.endswith('.cos'):
                    with open(os.path.join(base, f), 'r', encoding='utf-8') as fh:
                        ejemplos.append((f.replace('.cos',''), fh.read()))
        if not ejemplos:
            ejemplos = [('hola_cuadro', '// Hola cuadro!\nnombre Texto;\nnombre = "Bacano";\nMensaje.Texto(nombre);\n')]
        return ejemplos


if __name__ == '__main__':
    app = CosteñolIDE()
    app.mainloop()
