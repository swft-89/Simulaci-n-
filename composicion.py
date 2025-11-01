import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import random
import math

#Importar los algoritmos
try:
    from generadores import algoritmo_lineal, cuadrados_medios, algoritmo_cuadratico

    GENERADORES_DISPONIBLES = True
except ImportError as e:
    print(f"Error importando generadores: {e}")
    GENERADORES_DISPONIBLES = False


class ComposicionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Composición - Distribución Triangular")
        self.root.geometry("1400x800")

        #Configurar estilo
        self.style = ttk.Style(theme="flatly")
        self.configure_styles()

        #Datos
        self.numeros_rj = []
        self.numeros_ri = []
        self.resultados = []
        self.num_muestras = 5

        #Parámetros por defecto para generadores
        self.algoritmo_actual = "congruencial_lineal"
        self.semilla = 17
        self.a = 21
        self.c = 32
        self.m = 100
        self.b = 3
        self.g = 4

        #Crear marco principal
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=YES)

        #Crear paneles
        self.create_left_panel()
        self.create_right_panel()

        #Mostrar distribución triangular por defecto
        self.show_triangular()

    def configure_styles(self):
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))

    def create_left_panel(self):
        #Panel izquierdo
        left_container = ttk.Frame(self.main_frame, width=450)
        left_container.pack(side=LEFT, fill=Y, padx=(0, 10))
        left_container.pack_propagate(False)

        #Canvas
        self.left_canvas = tk.Canvas(left_container)
        v_scrollbar_left = ttk.Scrollbar(left_container, orient=VERTICAL, command=self.left_canvas.yview)
        v_scrollbar_left.pack(side=RIGHT, fill=Y)
        self.left_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.left_canvas.configure(yscrollcommand=v_scrollbar_left.set)

        #Frame dentro del canvas
        self.left_frame = ttk.Frame(self.left_canvas)
        self.left_canvas_window = self.left_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")

        #Configurar el scroll
        self.left_frame.bind("<Configure>", self.on_left_frame_configure)
        self.left_canvas.bind("<Configure>", self.on_left_canvas_configure)

        title_label = ttk.Label(self.left_frame, text="Composición - Distribución Triangular", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        #Frame para formularios
        self.form_frame = ttk.Frame(self.left_frame)
        self.form_frame.pack(fill=BOTH, expand=YES)

    def on_left_frame_configure(self, event):
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

    def on_left_canvas_configure(self, event):
        self.left_canvas.itemconfig(self.left_canvas_window, width=event.width)

    def create_right_panel(self):
        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        #Título
        self.results_title = ttk.Label(right_frame, text="Resultados - Distribución Triangular",
                                       style="Subtitle.TLabel")
        self.results_title.pack(pady=(0, 10))

        #Notebook para pestañas
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=BOTH, expand=YES)

        #Pestaña de tabla de resultados
        self.tabla_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tabla_frame, text="Tabla de Resultados")

        #Pestaña de gráficas
        self.graficas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graficas_frame, text="Gráficas")

        #Pestaña de conclusión
        self.conclusion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.conclusion_frame, text="Conclusión")

        #Configurar tabla
        self.setup_tabla()

        #Configurar área de gráficas
        self.setup_graficas()

        #Configurar área de conclusión
        self.setup_conclusion()

    def setup_tabla(self):
        #Crear frame con scrollbar para la tabla
        table_container = ttk.Frame(self.tabla_frame)
        table_container.pack(fill=BOTH, expand=YES)

        #Scrollbar vertical
        v_scrollbar = ttk.Scrollbar(table_container)
        v_scrollbar.pack(side=RIGHT, fill=Y)

        #Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(table_container, orient=HORIZONTAL)
        h_scrollbar.pack(side=BOTTOM, fill=X)

        #Crear treeview
        self.tree = ttk.Treeview(
            table_container,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=20
        )
        self.tree.pack(fill=BOTH, expand=YES)

        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

    def setup_graficas(self):
        #Contenedor principal
        graficas_main_container = ttk.Frame(self.graficas_frame)
        graficas_main_container.pack(fill=BOTH, expand=YES)

        #Canvas
        self.graficas_canvas = tk.Canvas(graficas_main_container)
        v_scrollbar_graficas = ttk.Scrollbar(graficas_main_container, orient=VERTICAL,
                                             command=self.graficas_canvas.yview)
        v_scrollbar_graficas.pack(side=RIGHT, fill=Y)
        self.graficas_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.graficas_canvas.configure(yscrollcommand=v_scrollbar_graficas.set)

        #Frame dentro del canvas para gráficas
        self.graficas_container = ttk.Frame(self.graficas_canvas)
        self.graficas_canvas_window = self.graficas_canvas.create_window((0, 0), window=self.graficas_container,
                                                                         anchor="nw")

        #Configurar el scroll
        self.graficas_container.bind("<Configure>", self.on_graficas_container_configure)
        self.graficas_canvas.bind("<Configure>", self.on_graficas_canvas_configure)

        #Frame para controles de gráficas
        self.controls_frame = ttk.Frame(self.graficas_container)
        self.controls_frame.pack(fill=X, pady=(0, 10))

    def setup_conclusion(self):
        #Área de texto para conclusión
        self.conclusion_text = scrolledtext.ScrolledText(
            self.conclusion_frame,
            width=80,
            height=20,
            font=("Helvetica", 11),
            wrap=tk.WORD
        )
        self.conclusion_text.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def on_graficas_container_configure(self, event):
        self.graficas_canvas.configure(scrollregion=self.graficas_canvas.bbox("all"))

    def on_graficas_canvas_configure(self, event):
        self.graficas_canvas.itemconfig(self.graficas_canvas_window, width=event.width)

    def clear_form_frame(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def generar_numeros_pseudoaleatorios(self, n):
        if not GENERADORES_DISPONIBLES:
            return [round(random.random(), 6) for _ in range(n)]

        try:
            if self.algoritmo_actual == "congruencial_lineal":
                numeros, procedimiento, advertencias = algoritmo_lineal(
                    self.semilla, self.a, self.c, self.m
                )
                #Si no hay suficientes números generar más
                while len(numeros) < n:
                    ultimo_valor = int(procedimiento[-1][1])
                    nuevos_numeros, nuevo_procedimiento, _ = algoritmo_lineal(
                        ultimo_valor, self.a, self.c, self.m
                    )
                    numeros.extend(nuevos_numeros)
                    procedimiento.extend(nuevo_procedimiento)

            elif self.algoritmo_actual == "cuadrados_medios":
                numeros, procedimiento, advertencias = cuadrados_medios(self.semilla)
                #Si no hay suficientes número generar más
                while len(numeros) < n:
                    ultimo_valor = int(procedimiento[-1][1])
                    nuevos_numeros, nuevo_procedimiento, _ = cuadrados_medios(ultimo_valor)
                    numeros.extend(nuevos_numeros)
                    procedimiento.extend(nuevo_procedimiento)

            elif self.algoritmo_actual == "congruencial_cuadratico":
                numeros, procedimiento, advertencias, m = algoritmo_cuadratico(
                    self.semilla, self.a, self.b, self.c, self.g
                )
                #Si no hay suficientes números generar más
                while len(numeros) < n:
                    ultimo_valor = int(procedimiento[-1][1])
                    nuevos_numeros, nuevo_procedimiento, _, _ = algoritmo_cuadratico(
                        ultimo_valor, self.a, self.b, self.c, self.g
                    )
                    numeros.extend(nuevos_numeros)
                    procedimiento.extend(nuevo_procedimiento)

            return numeros[:n]  #Retornar solo la cantidad necesaria

        except Exception as e:
            messagebox.showerror("Error", f"Error generando números: {str(e)}")
            return [random.random() for _ in range(n)]  # Fallback a random

    def show_generador_frame(self, parent_frame):
        generador_frame = ttk.LabelFrame(parent_frame, text="Generador de Números Pseudoaleatorios", padding=10)
        generador_frame.pack(fill=X, pady=(0, 15))

        if not GENERADORES_DISPONIBLES:
            ttk.Label(generador_frame, text="Generadores no disponibles. Usando random.random()",
                      foreground="orange").pack(fill=X, pady=5)
            return generador_frame

        algo_frame = ttk.Frame(generador_frame)
        algo_frame.pack(fill=X, pady=5)

        ttk.Label(algo_frame, text="Algoritmo:").pack(anchor="w")

        self.algoritmo_var = tk.StringVar(value="congruencial_lineal")
        algoritmos = [
            ("Congruencial Lineal", "congruencial_lineal"),
            ("Cuadrados Medios", "cuadrados_medios"),
            ("Congruencial Cuadrático", "congruencial_cuadratico")
        ]

        for text, value in algoritmos:
            radio_btn = ttk.Radiobutton(
                algo_frame,
                text=text,
                variable=self.algoritmo_var,
                value=value,
                command=self.actualizar_parametros_generador
            )
            radio_btn.pack(anchor="w", pady=2)

        #Frame para parámetros
        self.param_frame = ttk.Frame(generador_frame)
        self.param_frame.pack(fill=X, pady=5)

        self.actualizar_parametros_generador()

        return generador_frame

    def actualizar_parametros_generador(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        if not GENERADORES_DISPONIBLES:
            return

        algoritmo = self.algoritmo_var.get()
        self.algoritmo_actual = algoritmo

        if algoritmo == "congruencial_lineal":
            self.crear_campos_lineal()
        elif algoritmo == "cuadrados_medios":
            self.crear_campos_cuadrados()
        elif algoritmo == "congruencial_cuadratico":
            self.crear_campos_cuadratico()

    def crear_campos_lineal(self):
        campos = [
            ("Semilla (X0):", "semilla", "17"),
            ("Multiplicador (a):", "a", "21"),
            ("Incremento (c):", "c", "32"),
            ("Módulo (m):", "m", "100")
        ]

        self.entries_generador = {}
        for label_text, field, default in campos:
            frame = ttk.Frame(self.param_frame)
            frame.pack(fill=X, pady=3)

            ttk.Label(frame, text=label_text, width=20).pack(side=LEFT, anchor="w")
            entry = ttk.Entry(frame, width=12)
            entry.pack(side=RIGHT, padx=(10, 0))
            entry.insert(0, default)
            self.entries_generador[field] = entry

    def crear_campos_cuadrados(self):
        frame = ttk.Frame(self.param_frame)
        frame.pack(fill=X, pady=3)

        ttk.Label(frame, text="Semilla:", width=20).pack(side=LEFT, anchor="w")
        self.entries_generador = {}
        entry = ttk.Entry(frame, width=12)
        entry.pack(side=RIGHT, padx=(10, 0))
        entry.insert(0, "5735")
        self.entries_generador["semilla"] = entry

    def crear_campos_cuadratico(self):
        campos = [
            ("Semilla (X0):", "semilla", "1"),
            ("Multiplicador (a):", "a", "2"),
            ("Coeficiente (b):", "b", "3"),
            ("Constante (c):", "c", "1"),
            ("Exponente (g):", "g", "4")
        ]

        self.entries_generador = {}
        for label_text, field, default in campos:
            frame = ttk.Frame(self.param_frame)
            frame.pack(fill=X, pady=3)

            ttk.Label(frame, text=label_text, width=20).pack(side=LEFT, anchor="w")
            entry = ttk.Entry(frame, width=12)
            entry.pack(side=RIGHT, padx=(10, 0))
            entry.insert(0, default)
            self.entries_generador[field] = entry

    def obtener_parametros_generador(self):
        if not GENERADORES_DISPONIBLES:
            return True  #No necesita parámetros si usa random

        try:
            algoritmo = self.algoritmo_var.get()

            if algoritmo == "congruencial_lineal":
                self.semilla = int(self.entries_generador["semilla"].get())
                self.a = int(self.entries_generador["a"].get())
                self.c = int(self.entries_generador["c"].get())
                self.m = int(self.entries_generador["m"].get())

            elif algoritmo == "cuadrados_medios":
                self.semilla = int(self.entries_generador["semilla"].get())

            elif algoritmo == "congruencial_cuadratico":
                self.semilla = int(self.entries_generador["semilla"].get())
                self.a = int(self.entries_generador["a"].get())
                self.b = int(self.entries_generador["b"].get())
                self.c = int(self.entries_generador["c"].get())
                self.g = int(self.entries_generador["g"].get())

            return True

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para los parámetros")
            return False

    def show_triangular(self):
        self.clear_form_frame()
        self.results_title.config(text="Resultados - Distribución Triangular")

        title = ttk.Label(self.form_frame, text="Distribución Triangular", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Frame del generador
        self.show_generador_frame(self.form_frame)

        #Configuración de parámetros
        config_frame = ttk.LabelFrame(self.form_frame, text="Parámetros de la Distribución", padding=10)
        config_frame.pack(fill=X, pady=(0, 15))

        #Valor mínimo (a)
        min_frame = ttk.Frame(config_frame)
        min_frame.pack(fill=X, pady=5)
        ttk.Label(min_frame, text="Valor mínimo (a):").pack(side=LEFT)
        self.entry_min = ttk.Entry(min_frame, width=10)
        self.entry_min.pack(side=LEFT, padx=(10, 0))
        self.entry_min.insert(0, "5")

        #Moda (c)
        moda_frame = ttk.Frame(config_frame)
        moda_frame.pack(fill=X, pady=5)
        ttk.Label(moda_frame, text="Moda (c):").pack(side=LEFT)
        self.entry_moda = ttk.Entry(moda_frame, width=10)
        self.entry_moda.pack(side=LEFT, padx=(10, 0))
        self.entry_moda.insert(0, "10")

        #Valor máximo (b)
        max_frame = ttk.Frame(config_frame)
        max_frame.pack(fill=X, pady=5)
        ttk.Label(max_frame, text="Valor máximo (b):").pack(side=LEFT)
        self.entry_max = ttk.Entry(max_frame, width=10)
        self.entry_max.pack(side=LEFT, padx=(10, 0))
        self.entry_max.insert(0, "20")

        #Número de muestras
        muestras_frame = ttk.Frame(config_frame)
        muestras_frame.pack(fill=X, pady=5)
        ttk.Label(muestras_frame, text="N° Muestras:").pack(side=LEFT)
        self.entry_muestras = ttk.Entry(muestras_frame, width=10)
        self.entry_muestras.pack(side=LEFT, padx=(10, 0))
        self.entry_muestras.insert(0, "5")

        #Entrada de números rj (1er bloque)
        rj_frame = ttk.LabelFrame(self.form_frame, text="1er Bloque Aleatorios (rj)", padding=10)
        rj_frame.pack(fill=X, pady=(0, 15))

        self.rj_text = scrolledtext.ScrolledText(rj_frame, height=4, width=50)
        self.rj_text.pack(fill=BOTH, expand=YES)

        #Entrada de números ri (2do bloque)
        ri_frame = ttk.LabelFrame(self.form_frame, text="2do Bloque Aleatorios (ri)", padding=10)
        ri_frame.pack(fill=X, pady=(0, 15))

        self.ri_text = scrolledtext.ScrolledText(ri_frame, height=4, width=50)
        self.ri_text.pack(fill=BOTH, expand=YES)

        #Valores por defecto
        rj_default = """0.685886480387424
0.6765478325537848
0.8185288531947669
0.7605602605975517
0.3023922912988838"""

        ri_default = """0.6468997558157173
0.5290185841090674
0.5052305994219917
0.18974918830302023
0.8279108409251827"""

        self.rj_text.insert("1.0", rj_default)
        self.ri_text.insert("1.0", ri_default)

        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(
            button_frame,
            text="Generar Números Aleatorios",
            command=self.generar_numeros_aleatorios,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

        ttk.Button(
            button_frame,
            text="Calcular Distribución Triangular",
            command=self.calcular_triangular,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

    def generar_numeros_aleatorios(self):
        try:
            if not self.obtener_parametros_generador():
                return

            n = int(self.entry_muestras.get())
            rj_numeros = self.generar_numeros_pseudoaleatorios(n)
            ri_numeros = self.generar_numeros_pseudoaleatorios(n)

            self.rj_text.delete("1.0", tk.END)
            self.rj_text.insert("1.0", "\n".join(map(str, rj_numeros)))

            self.ri_text.delete("1.0", tk.END)
            self.ri_text.insert("1.0", "\n".join(map(str, ri_numeros)))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido de muestras")

    def calcular_triangular(self):
        try:
            #Obtener parámetros
            a = float(self.entry_min.get())
            c = float(self.entry_moda.get())
            b = float(self.entry_max.get())

            #Validar parámetros
            if not (a <= c <= b):
                messagebox.showerror("Error", "Los parámetros deben cumplir: a ≤ c ≤ b")
                return

            #Obtener números rj y ri
            rj_text = self.rj_text.get("1.0", tk.END).strip()
            ri_text = self.ri_text.get("1.0", tk.END).strip()

            self.numeros_rj = [float(x.strip()) for x in rj_text.split('\n') if x.strip()]
            self.numeros_ri = [float(x.strip()) for x in ri_text.split('\n') if x.strip()]

            #Verificar que tengan la misma cantidad
            if len(self.numeros_rj) != len(self.numeros_ri):
                messagebox.showerror("Error", "Los bloques rj y ri deben tener la misma cantidad de números")
                return

            #Calcular umbral
            umbral = (c - a) / (b - a)

            #Calcular distribución triangular
            self.resultados = []
            valores_x = []

            for i, (rj, ri) in enumerate(zip(self.numeros_rj, self.numeros_ri)):
                if rj <= umbral:
                    #Lado ascendente del triángulo
                    x = a + ((c - a) * math.sqrt(ri))
                    lado = "Ascendente"
                else:
                    #Lado descendente del triángulo
                    x = b - ((b - c) * math.sqrt(1 - ri))
                    lado = "Descendente"

                #Verificar si está por encima o por debajo de la moda
                comparacion = "Por encima" if x > c else "Por debajo"

                self.resultados.append({
                    'rj': rj,
                    'ri': ri,
                    'x': x,
                    'lado': lado,
                    'comparacion': comparacion
                })
                valores_x.append(x)

            self.valores_x = valores_x
            self.a = a
            self.c = c
            self.b = b

            self.mostrar_resultados_triangular()
            self.generar_grafica_triangular()
            self.generar_conclusion_triangular()

        except ValueError as e:
            messagebox.showerror("Error", f"Por favor ingrese valores numéricos válidos: {str(e)}")

    def mostrar_resultados_triangular(self):
        #Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        #Configurar columnas
        self.tree["columns"] = ("rj", "ri", "x", "lado", "comparacion")
        self.tree.heading("#0", text="No.")
        self.tree.column("#0", width=50, anchor="center")

        self.tree.heading("rj", text="rj", anchor="center")
        self.tree.column("rj", width=120, anchor="center")

        self.tree.heading("ri", text="ri", anchor="center")
        self.tree.column("ri", width=120, anchor="center")

        self.tree.heading("x", text="X", anchor="center")
        self.tree.column("x", width=120, anchor="center")

        self.tree.heading("lado", text="Lado del Triángulo", anchor="center")
        self.tree.column("lado", width=150, anchor="center")

        self.tree.heading("comparacion", text="Comparación con Moda", anchor="center")
        self.tree.column("comparacion", width=180, anchor="center")

        #Llenar tabla
        for i, resultado in enumerate(self.resultados):
            self.tree.insert("", "end", text=str(i + 1), values=(
                f"{resultado['rj']:.6f}",
                f"{resultado['ri']:.6f}",
                f"{resultado['x']:.6f}",
                resultado['lado'],
                resultado['comparacion']
            ))

    def generar_grafica_triangular(self):
        self.limpiar_graficas()

        #Limpiar controles
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

        ttk.Button(self.controls_frame, text="Generar Gráficas",
                   command=self._generar_grafica_triangular).pack(side=LEFT)

    def _generar_grafica_triangular(self):
        if not self.resultados:
            return

        #Crear figura con dos subgráficas
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        #Extraer datos
        indices = range(1, len(self.resultados) + 1)
        valores_x = self.valores_x
        valores_rj = [r['rj'] for r in self.resultados]
        valores_ri = [r['ri'] for r in self.resultados]

        #Gráfica 1: Distribución de valores X
        ax1.plot(indices, valores_x, marker='o', linewidth=2, markersize=8,
                 color='blue', label='Valores X generados')

        #Líneas de referencia para a, c, b
        ax1.axhline(y=self.a, color='red', linestyle='--', linewidth=2,
                    label=f'Valor mínimo (a): {self.a}')
        ax1.axhline(y=self.c, color='green', linestyle='--', linewidth=2,
                    label=f'Moda (c): {self.c}')
        ax1.axhline(y=self.b, color='orange', linestyle='--', linewidth=2,
                    label=f'Valor máximo (b): {self.b}')

        #Colorear puntos según el lado del triángulo
        for i, resultado in enumerate(self.resultados):
            color = 'darkblue' if resultado['lado'] == 'Ascendente' else 'lightblue'
            ax1.plot(i + 1, resultado['x'], 'o', markersize=8, color=color)

        ax1.set_xlabel('Número de Muestra')
        ax1.set_ylabel('Valor de X')
        ax1.set_title('Distribución Triangular - Valores Generados')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(indices)

        #Gráfica 2: Distribución de números aleatorios
        ax2.plot(indices, valores_rj, marker='s', linewidth=2, markersize=6,
                 color='purple', label='Números rj (1er bloque)')
        ax2.plot(indices, valores_ri, marker='^', linewidth=2, markersize=6,
                 color='teal', label='Números ri (2do bloque)')

        #Línea de umbral
        umbral = (self.c - self.a) / (self.b - self.a)
        ax2.axhline(y=umbral, color='red', linestyle='--', linewidth=2,
                    label=f'Umbral: {umbral:.4f}')

        ax2.set_xlabel('Número de Muestra')
        ax2.set_ylabel('Valor Aleatorio')
        ax2.set_title('Distribución Triangular - Números Aleatorios')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(indices)
        ax2.set_ylim(0, 1)

        plt.tight_layout()

        #Mostrar en interfaz
        canvas = FigureCanvasTkAgg(fig, self.graficas_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=5)

    def generar_conclusion_triangular(self):
        if not self.resultados:
            return

        #Calcular estadísticas
        total = len(self.resultados)
        ascendentes = sum(1 for r in self.resultados if r['lado'] == 'Ascendente')
        descendentes = total - ascendentes
        encima_moda = sum(1 for r in self.resultados if r['comparacion'] == 'Por encima')
        debajo_moda = total - encima_moda

        valores_x = [r['x'] for r in self.resultados]
        media_x = np.mean(valores_x)
        min_x = min(valores_x)
        max_x = max(valores_x)

        conclusion = f"""CONCLUSIÓN - DISTRIBUCIÓN TRIANGULAR

Parámetros de la distribución:
- Valor mínimo (a): {self.a}
- Moda (c): {self.c}
- Valor máximo (b): {self.b}

Estadísticas de los datos generados:
- Total de muestras: {total}
- Media de los valores X: {media_x:.4f}
- Mínimo generado: {min_x:.4f}
- Máximo generado: {max_x:.4f}

Distribución en el triángulo:
- Valores en lado ascendente: {ascendentes} ({ascendentes / total * 100:.1f}%)
- Valores en lado descendente: {descendentes} ({descendentes / total * 100:.1f}%)
- Valores por encima de la moda: {encima_moda} ({encima_moda / total * 100:.1f}%)
- Valores por debajo de la moda: {debajo_moda} ({debajo_moda / total * 100:.1f}%)

Análisis:
"""
        #Análisis adicional basado en la distribución
        if encima_moda > debajo_moda:
            conclusion += "La mayoría de los valores se ubican por encima de la moda, lo que indica una distribución sesgada hacia la derecha."
        else:
            conclusion += "La mayoría de los valores se ubican por debajo de la moda, lo que indica una distribución sesgada hacia la izquierda."

        conclusion += f"\n\nTodos los valores generados se mantienen dentro del rango esperado [{self.a}, {self.b}]."

        self.conclusion_text.delete("1.0", tk.END)
        self.conclusion_text.insert("1.0", conclusion)

    def limpiar_graficas(self):
        for widget in self.graficas_container.winfo_children():
            if widget != self.controls_frame:  #No eliminar el frame de controles
                widget.destroy()

# if __name__ == "__main__":
#     root = ttk.Window(themename="flatly")
#     app = ComposicionApp(root)
#     root.mainloop()