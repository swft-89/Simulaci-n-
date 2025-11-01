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
from scipy.stats import norm
import math

#importar los algoritmos
try:
    from generadores import algoritmo_lineal, cuadrados_medios, algoritmo_cuadratico

    GENERADORES_DISPONIBLES = True
except ImportError as e:
    print(f"Error importando generadores: {e}")
    GENERADORES_DISPONIBLES = False


class VariablesAleatoriasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generación de Variables Aleatorias")
        self.root.geometry("1400x800")

        #Configurar estilo
        self.style = ttk.Style(theme="flatly")
        self.configure_styles()

        #Datos
        self.numeros_ri = []
        self.resultados = []
        self.num_muestras = 5
        self.current_method = "transformada_inversa"

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

        #Mostrar transformada inversa por defecto
        self.show_transformada_inversa()

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

        title_label = ttk.Label(self.left_frame, text="Variables Aleatorias", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        #Botones de métodos
        buttons_frame = ttk.Frame(self.left_frame)
        buttons_frame.pack(fill=X, pady=(0, 20))

        metodos = {
            "Transformada Inversa": self.show_transformada_inversa,
            "Distribución Exponencial": self.show_exponencial,
            "Distribución Poisson": self.show_poisson
        }

        for metodo_name, metodo_command in metodos.items():
            btn = ttk.Button(
                buttons_frame,
                text=metodo_name,
                command=metodo_command,
                style="Accent.TButton",
                width=20
            )
            btn.pack(fill=X, pady=5)

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
        self.results_title = ttk.Label(right_frame, text="Resultados - Transformada Inversa", style="Subtitle.TLabel")
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
                #Si no hay suficientes números generar más
                while len(numeros) < n:
                    ultimo_valor = int(procedimiento[-1][1])
                    nuevos_numeros, nuevo_procedimiento, _ = cuadrados_medios(ultimo_valor)
                    numeros.extend(nuevos_numeros)
                    procedimiento.extend(nuevo_procedimiento)

            elif self.algoritmo_actual == "congruencial_cuadratico":
                numeros, procedimiento, advertencias, m = algoritmo_cuadratico(
                    self.semilla, self.a, self.b, self.c, self.g
                )
                # Sino hay suficientes números generar más
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
            return [random.random() for _ in range(n)]

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

            ttk.Label(frame, text=label_text, width=15).pack(side=LEFT)
            entry = ttk.Entry(frame, width=10)
            entry.pack(side=RIGHT, padx=(10, 0))
            entry.insert(0, default)
            self.entries_generador[field] = entry

    def crear_campos_cuadrados(self):
        frame = ttk.Frame(self.param_frame)
        frame.pack(fill=X, pady=3)

        ttk.Label(frame, text="Semilla:", width=20).pack(side=LEFT)
        self.entries_generador = {}
        entry = ttk.Entry(frame, width=10)
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

            ttk.Label(frame, text=label_text, width=20).pack(side=LEFT)
            entry = ttk.Entry(frame, width=10)
            entry.pack(side=RIGHT, padx=(10, 0))
            entry.insert(0, default)
            self.entries_generador[field] = entry

    def obtener_parametros_generador(self):
        if not GENERADORES_DISPONIBLES:
            return True  #Nonecesita parámetros si usa random

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

    def show_transformada_inversa(self):
        self.clear_form_frame()
        self.current_method = "transformada_inversa"
        self.results_title.config(text="Resultados - Transformada Inversa Normal")

        title = ttk.Label(self.form_frame, text="Transformada Inversa Normal", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Frame del generador
        self.show_generador_frame(self.form_frame)

        #Configuración
        config_frame = ttk.LabelFrame(self.form_frame, text="Configuración", padding=10)
        config_frame.pack(fill=X, pady=(0, 15))

        #Parámetros
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=X, pady=5)

        #--- Media ---
        media_frame = ttk.Frame(params_frame)
        media_frame.pack(fill=X)
        ttk.Label(media_frame, text="Media calculada:").pack(anchor="w")
        self.label_media = ttk.Label(media_frame, text="—", width=10)
        self.label_media.pack(anchor="w", pady=(0, 5))

        #--- Desviación estándar ---
        desv_frame = ttk.Frame(params_frame)
        desv_frame.pack(fill=X)
        ttk.Label(desv_frame, text="Desv. Estándar:").pack(anchor="w")
        self.label_desv = ttk.Label(desv_frame, text="—", width=10)
        self.label_desv.pack(anchor="w")

        #Número de muestras
        muestras_frame = ttk.Frame(config_frame)
        muestras_frame.pack(fill=X, pady=5)

        ttk.Label(muestras_frame, text="N° Muestras:").pack(side=LEFT)
        self.entry_muestras = ttk.Entry(muestras_frame, width=10)
        self.entry_muestras.pack(side=LEFT, padx=(10, 0))
        self.entry_muestras.insert(0, "5")

        #Entrada de números ri
        ri_frame = ttk.LabelFrame(self.form_frame, text="Números Aleatorios (ri)", padding=10)
        ri_frame.pack(fill=X, pady=(0, 15))

        self.ri_text = scrolledtext.ScrolledText(ri_frame, height=6, width=50)
        self.ri_text.pack(fill=BOTH, expand=YES)

        #Valores por defecto
        valores_default = """0.6858864803874236
0.6765478325537848
0.8185288531947669
0.7605602605975517
0.3023922912988838"""
        self.ri_text.insert("1.0", valores_default)

        #Botones
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
            text="Calcular Transformada",
            command=self.calcular_transformada_inversa,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

    def show_exponencial(self):
        self.clear_form_frame()
        self.current_method = "exponencial"
        self.results_title.config(text="Resultados - Distribución Exponencial")

        title = ttk.Label(self.form_frame, text="Distribución Exponencial", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        # Frame del generador
        self.show_generador_frame(self.form_frame)

        #Configuración
        config_frame = ttk.LabelFrame(self.form_frame, text="Configuración", padding=10)
        config_frame.pack(fill=X, pady=(0, 15))

        #Parámetros
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=X, pady=5)

        ttk.Label(params_frame, text="Lambda (λ):").pack(side=LEFT)
        self.entry_lambda = ttk.Entry(params_frame, width=10)
        self.entry_lambda.pack(side=LEFT, padx=(10, 20))
        self.entry_lambda.insert(0, "0.1")

        #Número de muestras
        muestras_frame = ttk.Frame(config_frame)
        muestras_frame.pack(fill=X, pady=5)

        ttk.Label(muestras_frame, text="N° Muestras:").pack(side=LEFT)
        self.entry_muestras_exp = ttk.Entry(muestras_frame, width=10)
        self.entry_muestras_exp.pack(side=LEFT, padx=(10, 0))
        self.entry_muestras_exp.insert(0, "5")

        #Entrada de números ri
        ri_frame = ttk.LabelFrame(self.form_frame, text="Números Aleatorios (ri)", padding=10)
        ri_frame.pack(fill=X, pady=(0, 15))

        self.ri_text_exp = scrolledtext.ScrolledText(ri_frame, height=6, width=50)
        self.ri_text_exp.pack(fill=BOTH, expand=YES)

        #Valores por defecto
        valores_default = """0.685886480387424
0.6765478325537848
0.8185288531947669
0.7605602605975517
0.3023922912988838"""
        self.ri_text_exp.insert("1.0", valores_default)

        #Botones de acción
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(
            button_frame,
            text="Generar Números Aleatorios",
            command=self.generar_numeros_aleatorios_exp,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

        ttk.Button(
            button_frame,
            text="Calcular Exponencial",
            command=self.calcular_exponencial,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

    def show_poisson(self):
        self.clear_form_frame()
        self.current_method = "poisson"
        self.results_title.config(text="Resultados - Distribución Poisson")

        title = ttk.Label(self.form_frame, text="Distribución Poisson", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Frame del generador
        self.show_generador_frame(self.form_frame)

        #Configuración
        config_frame = ttk.LabelFrame(self.form_frame, text="Configuración", padding=10)
        config_frame.pack(fill=X, pady=(0, 15))

        #Lambda
        lambda_frame = ttk.Frame(config_frame)
        lambda_frame.pack(fill=X, pady=5)
        ttk.Label(lambda_frame, text="Lambda (λ):").pack(side=LEFT)
        self.entry_lambda_poisson = ttk.Entry(lambda_frame, width=10)
        self.entry_lambda_poisson.pack(side=LEFT, padx=(10, 0))
        self.entry_lambda_poisson.insert(0, "0.1")

        #N inicial
        n_frame = ttk.Frame(config_frame)
        n_frame.pack(fill=X, pady=5)
        ttk.Label(n_frame, text="N inicial:").pack(side=LEFT)
        self.entry_n_ini = ttk.Entry(n_frame, width=10)
        self.entry_n_ini.pack(side=LEFT, padx=(10, 0))
        self.entry_n_ini.insert(0, "0")

        #T inicial
        t_frame = ttk.Frame(config_frame)
        t_frame.pack(fill=X, pady=5)
        ttk.Label(t_frame, text="T inicial:").pack(side=LEFT)
        self.entry_t_ini = ttk.Entry(t_frame, width=10)
        self.entry_t_ini.pack(side=LEFT, padx=(10, 0))
        self.entry_t_ini.insert(0, "1")

        #Media calculada de ri
        media_frame = ttk.Frame(config_frame)
        media_frame.pack(fill=X, pady=5)
        ttk.Label(media_frame, text="Media calculada de ri:").pack(side=LEFT)
        self.label_media_ri_poisson = ttk.Label(media_frame, text="—", width=10)
        self.label_media_ri_poisson.pack(side=LEFT, padx=(10, 0))

        #Número de muestras
        muestras_frame = ttk.Frame(config_frame)
        muestras_frame.pack(fill=X, pady=5)

        ttk.Label(muestras_frame, text="N° Muestras:").pack(side=LEFT)
        self.entry_muestras_poisson = ttk.Entry(muestras_frame, width=10)
        self.entry_muestras_poisson.pack(side=LEFT, padx=(10, 0))
        self.entry_muestras_poisson.insert(0, "5")

        #Entrada de números ri
        ri_frame = ttk.LabelFrame(self.form_frame, text="Números Aleatorios (ri)", padding=10)
        ri_frame.pack(fill=X, pady=(0, 15))

        self.ri_text_poisson = scrolledtext.ScrolledText(ri_frame, height=6, width=50)
        self.ri_text_poisson.pack(fill=BOTH, expand=YES)

        #Valores por defecto
        valores_default = """0.685886480387424
0.6765478325537848
0.8185288531947669
0.7605602605975517
0.3023922912988838"""
        self.ri_text_poisson.insert("1.0", valores_default)

        #Botones de acción
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(
            button_frame,
            text="Generar Números Aleatorios",
            command=self.generar_numeros_aleatorios_poisson,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

        ttk.Button(
            button_frame,
            text="Calcular Poisson",
            command=self.calcular_poisson,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

    def generar_numeros_aleatorios(self):
        try:
            if not self.obtener_parametros_generador():
                return

            n = int(self.entry_muestras.get())
            numeros = self.generar_numeros_pseudoaleatorios(n)
            self.ri_text.delete("1.0", tk.END)
            self.ri_text.insert("1.0", "\n".join(map(str, numeros)))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido de muestras")

    def generar_numeros_aleatorios_exp(self):
        try:
            if not self.obtener_parametros_generador():
                return

            n = int(self.entry_muestras_exp.get())
            numeros = self.generar_numeros_pseudoaleatorios(n)
            self.ri_text_exp.delete("1.0", tk.END)
            self.ri_text_exp.insert("1.0", "\n".join(map(str, numeros)))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido de muestras")


    def generar_numeros_aleatorios_poisson(self):
            try:
                if not self.obtener_parametros_generador():
                    return

                n = int(self.entry_muestras_poisson.get())
                numeros = self.generar_numeros_pseudoaleatorios(n)
                self.ri_text_poisson.delete("1.0", tk.END)
                self.ri_text_poisson.insert("1.0", "\n".join(map(str, numeros)))
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número válido de muestras")


    def calcular_transformada_inversa(self):
            try:
                #Inicializar media y desviación estándar
                media = None
                desv_estandar = None

                #Obtener ri del cuadro de texto, si existen
                ri_text = self.ri_text.get("1.0", tk.END).strip().split()

                if len(ri_text) > 0:
                    try:
                        ri = [float(num) for num in ri_text]
                    except ValueError:
                        messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos para ri.")
                        return
                else:
                    #Si el cuadro está vacío, generar aleatorios con nuestro generador
                    n = int(self.entry_muestras.get())
                    if not self.obtener_parametros_generador():
                        return
                    ri = self.generar_numeros_pseudoaleatorios(n)

                #Calcular media y desviación estándar de los ri
                media = np.mean(ri)
                desv_estandar = np.std(ri)

                #Calcular los valores X usando la transformada inversa
                valores_x = [norm.ppf(r, loc=media, scale=desv_estandar) for r in ri]

                #Guardar los valores para uso posterior
                self.media_real = media
                self.desv_real = desv_estandar
                self.valores_x = valores_x

                #Construir self.resultados
                self.resultados = []
                for r, x in zip(ri, valores_x):
                    comparacion = "Mayor" if x > media else "Menor"
                    self.resultados.append({
                        'ri': r,
                        'x': x,
                        'comparacion': comparacion
                    })

                #Mostrar resultados en las etiquetas
                self.label_media.config(text=f"{media:.4f}")
                self.label_desv.config(text=f"{desv_estandar:.4f}")

                self.mostrar_resultados_transformada()
                self.generar_grafica_transformada()
                self.generar_conclusion_transformada()

            except ValueError as e:
                messagebox.showerror("Error", f"Por favor ingrese valores numéricos válidos: {str(e)}")
            except ImportError:
                messagebox.showerror("Error", "No se pudo importar scipy.stats.")

    def calcular_exponencial(self):
            try:
                #Obtener parámetros
                lambda_val = float(self.entry_lambda.get())

                #Obtener números ri
                ri_text = self.ri_text_exp.get("1.0", tk.END).strip()
                self.numeros_ri = [float(x.strip()) for x in ri_text.split('\n') if x.strip()]

                #Calcular media teórica
                media_teorica = 1 / lambda_val

                #Calcular distribución exponencial usando transformada inversa
                self.resultados = []
                for ri in self.numeros_ri:
                    x = -np.log(1 - ri) / lambda_val
                    comparacion = "Mayor" if x > media_teorica else "Menor"
                    self.resultados.append({
                        'ri': ri,
                        'x': x,
                        'comparacion': comparacion
                    })

                self.mostrar_resultados_exponencial()
                self.generar_grafica_exponencial()
                self.generar_conclusion_exponencial()

            except ValueError as e:
                messagebox.showerror("Error", f"Por favor ingrese valores numéricos válidos: {str(e)}")

    def calcular_poisson(self):
            try:
                #Obtener parámetros
                lambda_val = float(self.entry_lambda_poisson.get())
                n_inicial = int(self.entry_n_ini.get())
                t_inicial = float(self.entry_t_ini.get())

                #Obtener números ri
                ri_text = self.ri_text_poisson.get("1.0", tk.END).strip()
                self.numeros_ri = [float(x.strip()) for x in ri_text.split('\n') if x.strip()]

                if not self.numeros_ri:
                    messagebox.showerror("Error", "Ingrese al menos un número ri")
                    return

                #Calcular media final de ri
                media_ri_final = np.mean(self.numeros_ri)
                self.label_media_ri_poisson.config(text=f"{media_ri_final:.4f}")

                #Calcular -exp(lambda)
                e_lambda = -np.exp(lambda_val)

                #Inicializar variables para el proceso
                n_actual = n_inicial
                t_actual = t_inicial

                self.resultados = []

                for i, ri in enumerate(self.numeros_ri):
                    #Calcular T' = ri * T_actual
                    t_prima = ri * t_actual

                    #Determinar si hay evento (T' >= -exp(lambda))
                    if t_prima >= e_lambda:
                        n_nuevo = n_actual + 1
                        t_nuevo = t_prima
                    else:
                        n_nuevo = n_actual
                        t_nuevo = t_actual

                    #Comparación de T con la media final de todos los ri
                    comparacion = "Mayor" if t_nuevo > media_ri_final else "Menor"

                    #Guardar resultados
                    self.resultados.append({
                        'ri': ri,
                        't_prima': t_prima,
                        'n': n_nuevo,
                        't': t_nuevo,
                        'comparacion': comparacion
                    })

                    #Actualizar valores para la siguiente iteración
                    n_actual = n_nuevo
                    t_actual = t_nuevo

                #Mostrar resultados en tabla y gráficos
                self.mostrar_resultados_poisson()
                self.generar_grafica_poisson()
                self.generar_conclusion_poisson()

            except ValueError as e:
                messagebox.showerror("Error", f"Por favor ingrese valores numéricos válidos: {str(e)}")

    def mostrar_resultados_transformada(self):
            #Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            #Configurar columnas
            self.tree["columns"] = ("ri", "x", "comparacion")
            self.tree.heading("#0", text="No.")
            self.tree.column("#0", width=50, anchor="center")

            self.tree.heading("ri", text="ri", anchor="center")
            self.tree.column("ri", width=150, anchor="center")

            self.tree.heading("x", text="X", anchor="center")
            self.tree.column("x", width=150, anchor="center")

            self.tree.heading("comparacion", text="Comparación con Media", anchor="center")
            self.tree.column("comparacion", width=200, anchor="center")

            #Llenar tabla
            for i, resultado in enumerate(self.resultados):
                self.tree.insert("", "end", text=str(i + 1), values=(
                    f"{resultado['ri']:.6f}",
                    f"{resultado['x']:.6f}",
                    resultado['comparacion']
                ))

    def mostrar_resultados_exponencial(self):
            #Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            #Configurar columnas
            self.tree["columns"] = ("ri", "x", "comparacion")
            self.tree.heading("#0", text="No.")
            self.tree.column("#0", width=50, anchor="center")

            self.tree.heading("ri", text="ri", anchor="center")
            self.tree.column("ri", width=150, anchor="center")

            self.tree.heading("x", text="X", anchor="center")
            self.tree.column("x", width=150, anchor="center")

            self.tree.heading("comparacion", text="Comparación con Media", anchor="center")
            self.tree.column("comparacion", width=200, anchor="center")

            #Llenar tabla
            for i, resultado in enumerate(self.resultados):
                self.tree.insert("", "end", text=str(i + 1), values=(
                    f"{resultado['ri']:.6f}",
                    f"{resultado['x']:.6f}",
                    resultado['comparacion']
                ))

    def mostrar_resultados_poisson(self):
            #Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            #Configurar columnas
            self.tree["columns"] = ("ri", "t_prima", "n", "t", "comparacion")
            self.tree.heading("#0", text="No.")
            self.tree.column("#0", width=50, anchor="center")

            self.tree.heading("ri", text="ri", anchor="center")
            self.tree.column("ri", width=120, anchor="center")

            self.tree.heading("t_prima", text="T'", anchor="center")
            self.tree.column("t_prima", width=120, anchor="center")

            self.tree.heading("n", text="N", anchor="center")
            self.tree.column("n", width=80, anchor="center")

            self.tree.heading("t", text="T", anchor="center")
            self.tree.column("t", width=120, anchor="center")

            self.tree.heading("comparacion", text="Comparación con media", anchor="center")
            self.tree.column("comparacion", width=180, anchor="center")

            #Llenar tabla
            for i, resultado in enumerate(self.resultados):
                self.tree.insert("", "end", text=str(i + 1), values=(
                    f"{resultado['ri']:.6f}",
                    f"{resultado['t_prima']:.6f}",
                    resultado['n'],
                    f"{resultado['t']:.6f}",
                    resultado['comparacion']
                ))

    def generar_grafica_transformada(self):
            self.limpiar_graficas()

            #Limpiar controles
            for widget in self.controls_frame.winfo_children():
                widget.destroy()

            ttk.Button(self.controls_frame, text="Generar Gráficas",
                       command=self._generar_grafica_transformada).pack(side=LEFT)

    def _generar_grafica_transformada(self):
            if not self.resultados:
                return

            #Crear figura con dos subgráficas
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            #Extraer datos
            indices = range(1, len(self.resultados) + 1)
            valores_ri = [r['ri'] for r in self.resultados]
            valores_x = self.valores_x
            media_real = self.media_real

            #Gráfica 1: Distribución de números ri
            ax1.plot(indices, valores_ri, marker='o', linewidth=2, markersize=8,
                     color='blue', label='Números ri')
            ax1.axhline(y=media_real, color='red', linestyle='--', linewidth=2,
                        label=f'Media: {media_real:.4f}')
            ax1.set_xlabel('Número de Muestra')
            ax1.set_ylabel('Valor de ri')
            ax1.set_title('Distribución de Números Aleatorios (ri)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(indices)
            ax1.set_ylim(0, 1)

            #Gráfica 2: Distribución de valores X
            ax2.plot(indices, valores_x, marker='s', linewidth=2, markersize=8,
                     color='green', label='Valores X generados')

            #Calcular la media de los valores X generados
            media_x_real = np.mean(valores_x)

            #Línea de media de los valores X generados
            ax2.axhline(y=media_x_real, color='orange', linestyle='-.', linewidth=2,
                        label=f"Media (valores X): {media_x_real:.4f}")

            #Colorear puntos según comparación
            for i, resultado in enumerate(self.resultados):
                color = 'darkgreen' if resultado['comparacion'] == 'Mayor' else 'lightgreen'
                ax2.plot(i + 1, resultado['x'], 's', markersize=8, color=color)

            ax2.set_xlabel('Número de Muestra')
            ax2.set_ylabel('Valor de X')
            ax2.set_title('Transformada Inversa - Distribución de Valores X')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks(indices)

            plt.tight_layout()

            #Mostrar en interfaz
            canvas = FigureCanvasTkAgg(fig, self.graficas_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=5)

    def generar_grafica_exponencial(self):
            self.limpiar_graficas()

            #Limpiar controles
            for widget in self.controls_frame.winfo_children():
                widget.destroy()

            ttk.Button(self.controls_frame, text="Generar Gráfica",
                       command=self._generar_grafica_exponencial).pack(side=LEFT)

    def _generar_grafica_exponencial(self):
            if not self.resultados:
                return

            #Crear figura con dos subgráficas (ri y X)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

            #Extraer datos
            indices = range(1, len(self.resultados) + 1)
            valores_ri = [r['ri'] for r in self.resultados]
            valores_x = [r['x'] for r in self.resultados]

            lambda_val = float(self.entry_lambda.get())
            media_teorica = 1 / lambda_val
            media_ri = np.mean(valores_ri)
            media_x = np.mean(valores_x)

            #Distribución de números aleatorios (ri)
            ax1.plot(indices, valores_ri, marker='o', linewidth=2, markersize=8,
                     color='teal', label='Números aleatorios (ri)')

            #Línea de media de ri
            ax1.axhline(y=media_ri, color='orange', linestyle='-.', linewidth=2,
                        label=f'Media (ri): {media_ri:.4f}')

            ax1.set_xlabel('Número de muestra')
            ax1.set_ylabel('ri')
            ax1.set_title('Distribución de Números Aleatorios (ri)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(indices)

            #Distribución Exponencial - Tiempos entre llegadas
            ax2.plot(indices, valores_x, marker='o', linewidth=2, markersize=8,
                     color='purple', label='Tiempos entre llegadas (x)')

            #Línea de media teórica
            ax2.axhline(y=media_teorica, color='red', linestyle='--', linewidth=2,
                        label=f'Media teórica: {media_teorica:.4f}')

            #Línea de media real de los valores x
            ax2.axhline(y=media_x, color='orange', linestyle='-.', linewidth=2,
                        label=f'Media (valores x): {media_x:.4f}')

            #Colorear puntos según comparación
            for i, resultado in enumerate(self.resultados):
                color = 'orange' if resultado['comparacion'] == 'Mayor' else 'brown'
                ax2.plot(i + 1, resultado['x'], 'o', markersize=8, color=color)

            ax2.set_xlabel('Número de muestra')
            ax2.set_ylabel('Tiempo entre llegadas (x)')
            ax2.set_title('Distribución Exponencial - Comparación con Media')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks(indices)

            plt.tight_layout()

            #Mostrar en interfaz
            canvas = FigureCanvasTkAgg(fig, self.graficas_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=5)

    def generar_grafica_poisson(self):
            self.limpiar_graficas()

            #Limpiar controles
            for widget in self.controls_frame.winfo_children():
                widget.destroy()

            ttk.Button(self.controls_frame, text="Generar Gráfica",
                       command=self._generar_grafica_poisson).pack(side=LEFT)

    def _generar_grafica_poisson(self):
            if not self.resultados:
                return

            #Crear figura con dos subgráficas
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            #Extraer datos
            indices = range(1, len(self.resultados) + 1)
            valores_ri = [r['ri'] for r in self.resultados]
            valores_t = [r['t'] for r in self.resultados]

            #Calcular media final de ri y T
            media_ri_final = np.mean(valores_ri)
            media_t_final = np.mean(valores_t)

            #Gráfica 1: Distribución de números ri
            ax1.plot(indices, valores_ri, marker='o', linewidth=2, markersize=8,
                     color='blue', label='Números ri')
            ax1.axhline(y=media_ri_final, color='red', linestyle='--', linewidth=2,
                        label=f'Media ri: {media_ri_final:.4f}')
            ax1.set_xlabel('Número de Muestra')
            ax1.set_ylabel('Valor de ri')
            ax1.set_title('Distribución de Números Aleatorios (ri) - Poisson')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(indices)
            ax1.set_ylim(0, 1)

            #Gráfica 2: Distribución de valores T
            ax2.plot(indices, valores_t, marker='s', linewidth=2, markersize=8,
                     color='green', label='Valores T')

            #Línea de media de todos los ri para comparación
            ax2.axhline(y=media_ri_final, color='red', linestyle='--', linewidth=2,
                        label=f'Media ri (para comparación): {media_ri_final:.4f}')

            #Colorear puntos según comparación con media final de ri
            for i, resultado in enumerate(self.resultados):
                color = 'darkgreen' if resultado['comparacion'] == 'Mayor' else 'lightgreen'
                ax2.plot(i + 1, resultado['t'], 's', markersize=8, color=color)

            ax2.set_xlabel('Número de Muestra')
            ax2.set_ylabel('Valor de T')
            ax2.set_title('Distribución Poisson - Valores de T vs Media final de ri')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks(indices)

            plt.tight_layout()

            #Mostrar en interfaz
            canvas = FigureCanvasTkAgg(fig, self.graficas_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=5)

    def generar_conclusion_transformada(self):
            media = self.media_real
            desv_estandar = self.desv_real
            mayores = sum(1 for r in self.resultados if r['comparacion'] == 'Mayor')
            total = len(self.resultados)

            conclusion = f"""CONCLUSIÓN - TRANSFORMADA INVERSA NORMAL

    Estadísticas de los datos generados:
    - Media real: {self.media_real:.4f}
    - Desviación estándar real: {self.desv_real:.4f}
    - Total de muestras: {total}

    Distribución respecto a la media:
    - Valores mayores a la media: {mayores} ({mayores / total * 100:.1f}%)
    - Valores menores a la media: {total - mayores} ({(total - mayores) / total * 100:.1f}%)

    Análisis:
    """
            diferencia_media = abs(media - self.media_real)
            diferencia_desv = abs(desv_estandar - self.desv_real)

            if diferencia_media < 0.1 and diferencia_desv < 0.1:
                conclusion += "Los datos generados se ajustan bien a la distribución, con pequeñas diferencias en media y desviación estándar."
            else:
                conclusion += f"Existen diferencias notables entre los parámetros teóricos y los datos generados:\n"
                conclusion += f"- Diferencia en media: {diferencia_media:.4f}\n"
                conclusion += f"- Diferencia en desviación estándar: {diferencia_desv:.4f}"

            self.conclusion_text.delete("1.0", tk.END)
            self.conclusion_text.insert("1.0", conclusion)

    def generar_conclusion_exponencial(self):
            valores_ri = [r['ri'] for r in self.resultados]
            valores_x = [r['x'] for r in self.resultados]
            media_ri = np.mean(valores_ri)
            media_x = np.mean(valores_x)
            lambda_val = float(self.entry_lambda.get())
            #media_teorica = 1 / lambda_val
            mayores = sum(1 for r in self.resultados if r['comparacion'] == 'Mayor')
            total = len(self.resultados)

            conclusion = f"""CONCLUSIÓN - DISTRIBUCIÓN EXPONENCIAL
    """
            if mayores == total:
                conclusion += "Todos los tiempos entre eventos son superiores al promedio."
            elif mayores > total / 2:
                conclusion += "La mayoría de los tiempos entre eventos son superiores al promedio."
            else:
                conclusion += "La mayoría de los tiempos entre eventos son inferiores al promedio."

            conclusion += f"""

    Parámetros:
    - Lambda (λ): {lambda_val:.4f}
    - Media (ri): {media_ri:.4f}
    - Media (x): {media_x:.4f}
    - Total de muestras: {total}
    - Tiempos > media: {mayores} ({mayores / total * 100:.1f}%)
    - Tiempos < media: {total - mayores} ({(total - mayores) / total * 100:.1f}%)"""

            self.conclusion_text.delete("1.0", tk.END)
            self.conclusion_text.insert("1.0", conclusion)

    def generar_conclusion_poisson(self):
            lambda_val = float(self.entry_lambda_poisson.get())
            n_inicial = int(self.entry_n_ini.get())
            t_inicial = float(self.entry_t_ini.get())

            if not self.resultados:
                return

            total_eventos = self.resultados[-1]['n']
            total_muestras = len(self.resultados)

            #Calcular medias reales finales
            valores_ri = [r['ri'] for r in self.resultados]
            valores_t_prima = [r['t_prima'] for r in self.resultados]
            valores_t = [r['t'] for r in self.resultados]

            media_ri_final = np.mean(valores_ri)
            media_t_prima_final = np.mean(valores_t_prima)
            media_t_final = np.mean(valores_t)

            conclusion = f"""CONCLUSIÓN - DISTRIBUCIÓN POISSON
    Parámetros iniciales:
    - Lambda (λ): {lambda_val:.4f}
    - N inicial: {n_inicial}
    - T inicial: {t_inicial:.4f}

    Estadísticas reales calculadas:
    - Media final de ri: {media_ri_final:.6f}
    - Media final de T': {media_t_prima_final:.6f}
    - Media final de T: {media_t_final:.6f}

    Resultados de la simulación:
    - Total de eventos (N final): {total_eventos}
    - Total de muestras: {total_muestras}

    Análisis de comparaciones:
    - La columna "Comparación con media ri" muestra si cada ri es Mayor o Menor que la media acumulada de ri en ese momento
    - Total de ri mayores a su media acumulada: {sum(1 for r in self.resultados if r['comparacion'] == 'Mayor')}
    - Total de ri menores a su media acumulada: {sum(1 for r in self.resultados if r['comparacion'] == 'Menor')}
    """

            self.conclusion_text.delete("1.0", tk.END)
            self.conclusion_text.insert("1.0", conclusion)

    def limpiar_graficas(self):
            for widget in self.graficas_container.winfo_children():
                if widget != self.controls_frame:  #No eliminar el frame de controles
                    widget.destroy()

# if __name__ == "__main__":
#     root = ttk.Window(themename="flatly")
#     app = VariablesAleatoriasApp(root)
#     root.mainloop()

