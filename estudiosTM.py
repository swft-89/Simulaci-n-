import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class EstudioTiemposApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estudio de Tiempos y Mediciones")
        self.root.geometry("1400x800")

        #Configurar estilo
        self.style = ttk.Style(theme="flatly")
        self.configure_styles()

        #Datos del estudio de tiempos
        self.datos = {}
        self.elementos = []
        self.tiempos_observados = []
        self.num_elementos = 0
        self.num_iteraciones = 0
        self.factor_valoracion = 1.0
        self.factor_tolerancia = 1.0

        #Datos de medición de piezas
        self.dimensiones_pieza = []
        self.mediciones_pieza = []
        self.num_dimensiones = 0
        self.num_mediciones = 0

        #Campos información del estudio
        self.area_departamento = ""
        self.numero_estudio = ""
        self.fecha_estudio = ""
        self.operacion = ""
        self.termino_estudio = ""
        self.comenzo_estudio = ""
        self.producto_pieza = ""
        self.operadores = []
        self.herramientas = ""
        self.observado_por = ""
        self.comprobado_por = ""
        self.material = ""

        #Lista para almacenar gráficas
        self.graficas_canvas_list = []

        #Crear marco principal
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=YES)

        #Crear paneles
        self.create_left_panel()
        self.create_right_panel()

        #Mostrar estudio de tiempos por defecto
        self.show_estudio_tiempos()

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

        title_label = ttk.Label(self.left_frame, text="Sistema de Medición", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        #Botones de módulos
        buttons_frame = ttk.Frame(self.left_frame)
        buttons_frame.pack(fill=X, pady=(0, 20))

        modulos = {
            "Estudio de Tiempos": self.show_estudio_tiempos,
            "Medición de Piezas": self.show_medicion_piezas
        }

        for modulo_name, modulo_command in modulos.items():
            btn = ttk.Button(
                buttons_frame,
                text=modulo_name,
                command=modulo_command,
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
        self.results_title = ttk.Label(right_frame, text="Resultados del Estudio", style="Subtitle.TLabel")
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

    def show_estudio_tiempos(self):
        self.clear_form_frame()
        self.current_module = "Estudio de Tiempos"
        self.results_title.config(text="Resultados del Estudio de Tiempos")

        title = ttk.Label(self.form_frame, text="Estudio de Tiempos", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Campos de información general del estudio
        info_frame = ttk.LabelFrame(self.form_frame, text="Información General del Estudio", padding=10)
        info_frame.pack(fill=X, pady=(0, 15))

        campos_info = [
            ("Área/Departamento:", "area_departamento"),
            ("N° Estudio:", "numero_estudio"),
            ("Fecha:", "fecha_estudio"),
            ("Operación:", "operacion"),
            ("Comenzó:", "comenzo_estudio"),
            ("Terminó:", "termino_estudio"),
            ("Producto/Pieza:", "producto_pieza"),
            ("Herramientas:", "herramientas"),
            ("Material:", "material"),
            ("Observado por:", "observado_por"),
            ("Comprobado por:", "comprobado_por")
        ]

        self.entries_info = {}
        for label_text, field_name in campos_info:
            frame = ttk.Frame(info_frame)
            frame.pack(fill=X, pady=2)

            label = ttk.Label(frame, text=label_text, width=15)
            label.pack(side=LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
            self.entries_info[field_name] = entry

        #Frame para operadores
        operadores_frame = ttk.Frame(info_frame)
        operadores_frame.pack(fill=X, pady=2)

        ttk.Label(operadores_frame, text="Operadores:", width=15).pack(side=LEFT)
        self.operadores_text = scrolledtext.ScrolledText(operadores_frame, height=3, width=40)
        self.operadores_text.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))

        #Configuración de estudio
        estudio_frame = ttk.LabelFrame(self.form_frame, text="Configuración del Estudio", padding=10)
        estudio_frame.pack(fill=X, pady=(0, 15))

        campos_estudio = [
            ("N° Elementos:", "num_elementos"),
            ("N° Iteraciones:", "num_iteraciones"),
            ("Factor Valoración:", "factor_valoracion"),
            ("Factor Tolerancia:", "factor_tolerancia")
        ]

        self.entries_estudio = {}
        for label_text, field_name in campos_estudio:
            frame = ttk.Frame(estudio_frame)
            frame.pack(fill=X, pady=2)

            label = ttk.Label(frame, text=label_text, width=15)
            label.pack(side=LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
            self.entries_estudio[field_name] = entry

        # Botones de acción
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(
            button_frame,
            text="Configurar Estudio",
            command=self.configurar_estudio,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

        ttk.Button(
            button_frame,
            text="Registrar Tiempos",
            command=self.registrar_tiempos_interfaz,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

    def show_medicion_piezas(self):
        self.clear_form_frame()
        self.current_module = "Medición de Piezas"
        self.results_title.config(text="Resultados de Medición de Piezas")

        title = ttk.Label(self.form_frame, text="Medición de Piezas", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        # Campos de información general del estudio
        info_frame = ttk.LabelFrame(self.form_frame, text="Información General del Estudio", padding=10)
        info_frame.pack(fill=X, pady=(0, 15))

        campos_info = [
            ("Área/Departamento:", "area_departamento"),
            ("N° Estudio:", "numero_estudio"),
            ("Fecha:", "fecha_estudio"),
            ("Operación:", "operacion"),
            ("Comenzó:", "comenzo_estudio"),
            ("Terminó:", "termino_estudio"),
            ("Producto/Pieza:", "producto_pieza"),
            ("Herramientas:", "herramientas"),
            ("Material:", "material"),
            ("Observado por:", "observado_por"),
            ("Comprobado por:", "comprobado_por")
        ]

        self.entries_info_medicion = {}
        for label_text, field_name in campos_info:
            frame = ttk.Frame(info_frame)
            frame.pack(fill=X, pady=2)

            label = ttk.Label(frame, text=label_text, width=15)
            label.pack(side=LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
            self.entries_info_medicion[field_name] = entry

        #Frame para operadores
        operadores_frame = ttk.Frame(info_frame)
        operadores_frame.pack(fill=X, pady=2)

        ttk.Label(operadores_frame, text="Operadores:", width=15).pack(side=LEFT)
        self.operadores_text_medicion = scrolledtext.ScrolledText(operadores_frame, height=3, width=40)
        self.operadores_text_medicion.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))

        #Configuración de medición de piezas
        medicion_frame = ttk.LabelFrame(self.form_frame, text="Configuración de Medición", padding=10)
        medicion_frame.pack(fill=X, pady=(0, 15))

        campos_medicion = [
            ("N° Dimensiones:", "num_dimensiones"),
            ("N° Mediciones:", "num_mediciones")
        ]

        self.entries_medicion = {}
        for label_text, field_name in campos_medicion:
            frame = ttk.Frame(medicion_frame)
            frame.pack(fill=X, pady=2)

            label = ttk.Label(frame, text=label_text, width=15)
            label.pack(side=LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
            self.entries_medicion[field_name] = entry

        #botones
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(
            button_frame,
            text="Configurar Medición",
            command=self.configurar_medicion,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

        ttk.Button(
            button_frame,
            text="Registrar Mediciones",
            command=self.registrar_mediciones_interfaz,
            style="Accent.TButton"
        ).pack(fill=X, pady=5)

    def configurar_estudio(self):
        try:
            #Guardar información general
            self.area_departamento = self.entries_info["area_departamento"].get()
            self.numero_estudio = self.entries_info["numero_estudio"].get()
            self.fecha_estudio = self.entries_info["fecha_estudio"].get()
            self.operacion = self.entries_info["operacion"].get()
            self.comenzo_estudio = self.entries_info["comenzo_estudio"].get()
            self.termino_estudio = self.entries_info["termino_estudio"].get()
            self.producto_pieza = self.entries_info["producto_pieza"].get()
            self.herramientas = self.entries_info["herramientas"].get()
            self.material = self.entries_info["material"].get()
            self.observado_por = self.entries_info["observado_por"].get()
            self.comprobado_por = self.entries_info["comprobado_por"].get()

            #Obtener operadores del texto
            operadores_text = self.operadores_text.get("1.0", tk.END).strip()
            self.operadores = [op.strip() for op in operadores_text.split('\n') if op.strip()]

            #Obtener valores de configuración
            self.num_elementos = int(self.entries_estudio["num_elementos"].get())
            self.num_iteraciones = int(self.entries_estudio["num_iteraciones"].get())
            self.factor_valoracion = float(self.entries_estudio["factor_valoracion"].get())  # Cambiado
            self.factor_tolerancia = float(self.entries_estudio["factor_tolerancia"].get())

            if self.num_elementos <= 0 or self.num_iteraciones <= 0:
                messagebox.showerror("Error", "El número de elementos e iteraciones debe ser mayor a 0")
                return

            messagebox.showinfo("Configuración",
                                f"Estudio configurado:\n{self.num_elementos} elementos\n{self.num_iteraciones} iteraciones")

        except ValueError as e:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")

    def configurar_medicion(self):
        try:
            #Guardar información general
            self.area_departamento = self.entries_info_medicion["area_departamento"].get()
            self.numero_estudio = self.entries_info_medicion["numero_estudio"].get()
            self.fecha_estudio = self.entries_info_medicion["fecha_estudio"].get()
            self.operacion = self.entries_info_medicion["operacion"].get()
            self.comenzo_estudio = self.entries_info_medicion["comenzo_estudio"].get()
            self.termino_estudio = self.entries_info_medicion["termino_estudio"].get()
            self.producto_pieza = self.entries_info_medicion["producto_pieza"].get()
            self.herramientas = self.entries_info_medicion["herramientas"].get()
            self.material = self.entries_info_medicion["material"].get()
            self.observado_por = self.entries_info_medicion["observado_por"].get()
            self.comprobado_por = self.entries_info_medicion["comprobado_por"].get()

            #Obtener operadores del texto
            operadores_text = self.operadores_text_medicion.get("1.0", tk.END).strip()
            self.operadores = [op.strip() for op in operadores_text.split('\n') if op.strip()]

            #Obtener valores de los campos
            self.num_dimensiones = int(self.entries_medicion["num_dimensiones"].get())
            self.num_mediciones = int(self.entries_medicion["num_mediciones"].get())

            if self.num_dimensiones <= 0 or self.num_mediciones <= 0:
                messagebox.showerror("Error", "El número de dimensiones y mediciones debe ser mayor a 0")
                return

            messagebox.showinfo("Configuración",
                                f"Medición configurada:\n{self.num_dimensiones} dimensiones\n{self.num_mediciones} mediciones")

        except ValueError as e:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")

    def registrar_tiempos_interfaz(self):
        if self.num_elementos <= 0 or self.num_iteraciones <= 0:
            messagebox.showwarning("Configuración", "Primero configure el estudio")
            return

        #Crear ventana para registro de tiempos
        registro_window = tk.Toplevel(self.root)
        registro_window.title("Registro de Tiempos")
        registro_window.geometry("800x600")
        registro_window.transient(self.root)
        registro_window.grab_set()

        #Frame principal
        main_container = ttk.Frame(registro_window)
        main_container.pack(fill=BOTH, expand=YES)

        #Canvas
        canvas = tk.Canvas(main_container)
        v_scrollbar = ttk.Scrollbar(main_container, orient=VERTICAL, command=canvas.yview)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        #Frame dentro del canvas
        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        #Configurar el scroll
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        self.entries_tiempos = []

        for i in range(self.num_elementos):
            #Frame para cada elemento
            elemento_frame = ttk.LabelFrame(scrollable_frame, text=f"Elemento {i + 1}", padding=10)
            elemento_frame.pack(fill=X, pady=5, padx=10)

            #Nombre del elemento
            nombre_frame = ttk.Frame(elemento_frame)
            nombre_frame.pack(fill=X, pady=(0, 10))

            ttk.Label(nombre_frame, text="Descripción:").pack(side=LEFT)
            entry_nombre = ttk.Entry(nombre_frame)
            entry_nombre.pack(side=LEFT, fill=X, expand=YES, padx=(10, 0))

            #Tiempos por iteración
            tiempos_frame = ttk.Frame(elemento_frame)
            tiempos_frame.pack(fill=X, pady=5)

            ttk.Label(tiempos_frame, text="Tiempos (segundos):").pack(side=LEFT)

            #Frame para los campos de tiempo con grid
            tiempos_grid_frame = ttk.Frame(tiempos_frame)
            tiempos_grid_frame.pack(side=LEFT, fill=X, expand=YES, padx=(10, 0))

            entries_tiempo_elemento = []
            #Crear filas de 5 columnas para los tiempos
            for j in range(self.num_iteraciones):
                if j % 5 == 0:
                    row_frame = ttk.Frame(tiempos_grid_frame)
                    row_frame.pack(fill=X, pady=2)

                cell_frame = ttk.Frame(row_frame)
                cell_frame.pack(side=LEFT, padx=5)

                label = ttk.Label(cell_frame, text=f"Iter {j + 1}:")
                label.pack()

                entry_tiempo = ttk.Entry(cell_frame, width=8)
                entry_tiempo.pack()
                entry_tiempo.insert(0, "0.0")
                entries_tiempo_elemento.append(entry_tiempo)

            self.entries_tiempos.append((entry_nombre, entries_tiempo_elemento))

        #Botón de guardar
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=X, pady=20, padx=10)

        ttk.Button(
            button_frame,
            text="Guardar y Calcular",
            command=lambda: self.guardar_tiempos(registro_window),
            style="Accent.TButton"
        ).pack(fill=X)

    def registrar_mediciones_interfaz(self):
        if self.num_dimensiones <= 0 or self.num_mediciones <= 0:
            messagebox.showwarning("Configuración", "Primero configure la medición")
            return

        #Crear ventana para registro de dimensiones
        dim_window = tk.Toplevel(self.root)
        dim_window.title("Nombres de Dimensiones")
        dim_window.geometry("500x400")
        dim_window.transient(self.root)
        dim_window.grab_set()

        #Frame principal
        main_container = ttk.Frame(dim_window)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        ttk.Label(main_container, text="Ingrese los nombres de las dimensiones:",
                  style="Subtitle.TLabel").pack(pady=(0, 15))

        self.entries_dimensiones = []

        for i in range(self.num_dimensiones):
            frame = ttk.Frame(main_container)
            frame.pack(fill=X, pady=5)

            ttk.Label(frame, text=f"Dimensión {i + 1}:").pack(side=LEFT)
            entry_dim = ttk.Entry(frame)
            entry_dim.pack(side=LEFT, fill=X, expand=YES, padx=(10, 0))
            entry_dim.insert(0, f"Dimensión {i + 1}")
            self.entries_dimensiones.append(entry_dim)

        #Botón para continuar
        ttk.Button(
            main_container,
            text="Continuar a Mediciones",
            command=lambda: self.continuar_a_mediciones(dim_window),
            style="Accent.TButton"
        ).pack(pady=20)

    def continuar_a_mediciones(self, dim_window):
        #Obtener nombres de dimensiones
        self.dimensiones_pieza = []
        for entry in self.entries_dimensiones:
            nombre = entry.get().strip()
            if not nombre:
                nombre = "Dimensión"
            self.dimensiones_pieza.append(nombre)

        dim_window.destroy()
        self.mostrar_ventana_mediciones()

    def mostrar_ventana_mediciones(self):
        #Crea ventana para registro de mediciones
        medicion_window = tk.Toplevel(self.root)
        medicion_window.title("Registro de Mediciones")
        medicion_window.geometry("900x700")
        medicion_window.transient(self.root)
        medicion_window.grab_set()

        #Frame principal
        main_container = ttk.Frame(medicion_window)
        main_container.pack(fill=BOTH, expand=YES)

        #Canvas
        canvas = tk.Canvas(main_container)
        v_scrollbar = ttk.Scrollbar(main_container, orient=VERTICAL, command=canvas.yview)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        #Frame dentro del canvas
        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        #Configurar el scroll
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        #Título
        ttk.Label(scrollable_frame, text="Mediciones de Pieza",
                  style="Subtitle.TLabel").pack(pady=(10, 15))

        self.entries_mediciones = []

        #Crear tabla de mediciones
        for i in range(self.num_mediciones):
            #Frame para cada medición
            medicion_frame = ttk.LabelFrame(scrollable_frame, text=f"Medición {i + 1}", padding=10)
            medicion_frame.pack(fill=X, pady=5, padx=10)

            entries_medicion = []
            for j, dim_nombre in enumerate(self.dimensiones_pieza):
                frame = ttk.Frame(medicion_frame)
                frame.pack(fill=X, pady=2)

                ttk.Label(frame, text=f"{dim_nombre}:").pack(side=LEFT)
                entry_med = ttk.Entry(frame, width=10)
                entry_med.pack(side=RIGHT)
                entry_med.insert(0, "0.0")
                entries_medicion.append(entry_med)

            self.entries_mediciones.append(entries_medicion)

        #Botón de guardar
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=X, pady=20, padx=10)

        ttk.Button(
            button_frame,
            text="Guardar y Calcular",
            command=lambda: self.guardar_mediciones(medicion_window),
            style="Accent.TButton"
        ).pack(fill=X)

    def guardar_tiempos(self, ventana):
        try:
            self.elementos = []
            self.tiempos_observados = []

            for i, (entry_nombre, entries_tiempo) in enumerate(self.entries_tiempos):
                #Nombre del elemento
                nombre = entry_nombre.get()
                if not nombre.strip():
                    nombre = f"Elemento {i + 1}"
                self.elementos.append(nombre)

                #Tiempos
                tiempos_elemento = []
                for entry_tiempo in entries_tiempo:
                    tiempo = float(entry_tiempo.get())
                    tiempos_elemento.append(tiempo)
                self.tiempos_observados.append(tiempos_elemento)

            ventana.destroy()
            self.calcular_estadisticas()
            self.mostrar_resultados()
            self.generar_conclusion_estudio_tiempos()

        except ValueError as e:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para los tiempos")

    def guardar_mediciones(self, ventana):
        try:
            self.mediciones_pieza = []

            for entries_medicion in self.entries_mediciones:
                medicion = []
                for entry_med in entries_medicion:
                    valor = float(entry_med.get())
                    medicion.append(valor)
                self.mediciones_pieza.append(medicion)

            ventana.destroy()
            self.calcular_estadisticas_medicion()
            self.mostrar_resultados_medicion()
            self.generar_conclusion_medicion_piezas()

        except ValueError as e:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para las mediciones")

    def calcular_estadisticas(self):
        self.sumas = []
        self.tiempos_observados_promedio = []
        self.tiempos_normales = []
        self.tiempos_estandar = []
        self.varianzas = []
        self.desviaciones_estandar = []

        for tiempos in self.tiempos_observados:
            #Suma de tiempos
            suma = sum(tiempos)
            self.sumas.append(suma)

            #Tiempo observado promedio
            to_promedio = suma / self.num_iteraciones
            self.tiempos_observados_promedio.append(to_promedio)

            #Tiempo normal
            tn = to_promedio * self.factor_valoracion
            self.tiempos_normales.append(tn)

            #Tiempo estándar
            ts = tn * self.factor_tolerancia
            self.tiempos_estandar.append(ts)

            #Varianza y desviación estándar
            varianza = np.var(tiempos, ddof=1)
            desviacion_estandar = np.std(tiempos, ddof=1)
            self.varianzas.append(varianza)
            self.desviaciones_estandar.append(desviacion_estandar)

        #Promedios por iteración
        self.promedios_iteraciones = []
        self.varianzas_iteraciones = []
        self.desviaciones_iteraciones = []

        for i in range(self.num_iteraciones):
            #Tiempos de todos los elementos en esta iteración
            tiempos_iteracion = [tiempos[i] for tiempos in self.tiempos_observados]
            promedio_iter = sum(tiempos_iteracion) / self.num_elementos
            varianza_iter = np.var(tiempos_iteracion, ddof=1)
            desviacion_iter = np.std(tiempos_iteracion, ddof=1)

            self.promedios_iteraciones.append(promedio_iter)
            self.varianzas_iteraciones.append(varianza_iter)
            self.desviaciones_iteraciones.append(desviacion_iter)

        #Varianza de los promedios
        self.varianza_promedios = np.var(self.promedios_iteraciones, ddof=1) if len(
            self.promedios_iteraciones) > 1 else 0

    def calcular_estadisticas_medicion(self):
        #Calcular estadísticas para cada dimensión
        self.medias_dimensiones = []
        self.varianzas_dimensiones = []
        self.desviaciones_dimensiones = []

        #Transponer los datos para agrupar por dimensión
        mediciones_por_dimension = list(zip(*self.mediciones_pieza))

        for mediciones_dim in mediciones_por_dimension:
            media = np.mean(mediciones_dim)
            varianza = np.var(mediciones_dim, ddof=1)
            desviacion = np.std(mediciones_dim, ddof=1)

            self.medias_dimensiones.append(media)
            self.varianzas_dimensiones.append(varianza)
            self.desviaciones_dimensiones.append(desviacion)

    def mostrar_resultados(self):
        #Limpiar controles de gráfica
        self.limpiar_controles_graficas()

        #Agregar botones específicos para estudio de tiempos
        ttk.Button(self.controls_frame, text="Generar Gráficas por Iteración",
                   command=self.generar_graficas_iteraciones).pack(side=LEFT, padx=(0, 10))
        ttk.Button(self.controls_frame, text="Limpiar Gráficas", command=self.limpiar_graficas).pack(side=LEFT)

        #Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        #Configurar columnas de la tabla
        columns = ["No.", "Descripción"]
        columns.extend([f"Iter {i + 1}" for i in range(self.num_iteraciones)])
        columns.extend(["Ʃ", "T.O", "F.V", "T.N", "F.T", "T.S", "VAR"])

        self.tree["columns"] = columns[1:]
        self.tree.heading("#0", text="No.")
        self.tree.column("#0", width=50, anchor="center")

        for col in columns[1:]:
            self.tree.heading(col, text=col, anchor="center")
            if col.startswith("Iter"):
                self.tree.column(col, width=70, anchor="center")
            else:
                self.tree.column(col, width=80, anchor="center")

        #Llenar tabla con datos de elementos
        for i in range(self.num_elementos):
            valores = [self.elementos[i]]
            valores.extend([f"{t:.2f}" for t in self.tiempos_observados[i]])
            valores.extend([
                f"{self.sumas[i]:.2f}",
                f"{self.tiempos_observados_promedio[i]:.2f}",
                f"{self.factor_valoracion:.2f}",
                f"{self.tiempos_normales[i]:.2f}",
                f"{self.factor_tolerancia:.2f}",
                f"{self.tiempos_estandar[i]:.2f}",
                f"{self.varianzas[i]:.2f}"
            ])

            self.tree.insert("", "end", text=str(i + 1), values=valores)

        #Agregar fila de promedios por iteración
        valores_promedio = ["PROMEDIO"]
        valores_promedio.extend([f"{p:.2f}" for p in self.promedios_iteraciones])
        #Dejar vacíos los demás campos
        valores_promedio.extend([""] * 7)

        self.tree.insert("", "end", text="", values=valores_promedio)

    def mostrar_resultados_medicion(self):
        #Limpiar controles de gráficas
        self.limpiar_controles_graficas()

        #Agregar botones para medición de piezas
        ttk.Button(self.controls_frame, text="Generar Gráficas por Dimensión",
                   command=self.generar_graficas_dimensiones).pack(side=LEFT, padx=(0, 10))
        ttk.Button(self.controls_frame, text="Limpiar Gráficas",
                   command=self.limpiar_graficas).pack(side=LEFT)

        #Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        #Configurar columnas de la tabla
        columnas = ["No."] + self.dimensiones_pieza
        self.tree["columns"] = columnas[1:]
        self.tree.heading("#0", text="No.")
        self.tree.column("#0", width=60, anchor="center")

        for col in columnas[1:]:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=100, anchor="center")

        #Llenar tabla con las mediciones individuales
        for i in range(self.num_mediciones):
            valores = [f"{med:.3f}" for med in self.mediciones_pieza[i]]
            self.tree.insert("", "end", text=str(i + 1), values=valores)

        #Agregar filas con estadísticas
        #Media
        fila_media = [f"{self.medias_dimensiones[i]:.3f}" for i in range(self.num_dimensiones)]
        self.tree.insert("", "end", text="Media", values=fila_media)

        #Varianza
        fila_varianza = [f"{self.varianzas_dimensiones[i]:.5f}" for i in range(self.num_dimensiones)]
        self.tree.insert("", "end", text="Varianza", values=fila_varianza)

        #Desviación estándar
        fila_desv = [f"{self.desviaciones_dimensiones[i]:.5f}" for i in range(self.num_dimensiones)]
        self.tree.insert("", "end", text="Desv. Estándar", values=fila_desv)

    def generar_conclusion_estudio_tiempos(self):
        if not self.elementos:
            return

        conclusion = f"""CONCLUSIÓN - ESTUDIO DE TIEMPOS

INFORMACIÓN DEL ESTUDIO:
Área/Departamento: {self.area_departamento}
N° Estudio: {self.numero_estudio}
Fecha: {self.fecha_estudio}
Operación: {self.operacion}
Horario: {self.comenzo_estudio} - {self.termino_estudio}
Producto/Pieza: {self.producto_pieza}
Material: {self.material}
Herramientas: {self.herramientas}
Operadores: {', '.join(self.operadores)}
Observado por: {self.observado_por}
Comprobado por: {self.comprobado_por}

ANÁLISIS POR ELEMENTO:
"""

        #Análisis detallado por elemento
        for i, elemento in enumerate(self.elementos):
            conclusion += f"""
{elemento}:
Tiempo Observado: {self.tiempos_observados_promedio[i]:.2f}s
Tiempo Normal: {self.tiempos_normales[i]:.2f}s
Tiempo Estándar: {self.tiempos_estandar[i]:.2f}s
Varianza: {self.varianzas[i]:.4f}
Desviación Estándar: {self.desviaciones_estandar[i]:.4f}s
Coeficiente de Variación: {(self.desviaciones_estandar[i] / self.tiempos_observados_promedio[i]) * 100:.1f}%
"""

        elemento_mayor_varianza = self.elementos[np.argmax(self.varianzas)]
        mayor_varianza = max(self.varianzas)
        elemento_menor_varianza = self.elementos[np.argmin(self.varianzas)]
        menor_varianza = min(self.varianzas)

        elemento_mayor_desviacion = self.elementos[np.argmax(self.desviaciones_estandar)]
        mayor_desviacion = max(self.desviaciones_estandar)
        elemento_menor_desviacion = self.elementos[np.argmin(self.desviaciones_estandar)]
        menor_desviacion = min(self.desviaciones_estandar)

        #Calcular rango de variabilidad
        rango_varianza = mayor_varianza - menor_varianza
        rango_desviacion = mayor_desviacion - menor_desviacion

        conclusion += f"""
ANÁLISIS DE VARIABILIDAD:

ELEMENTO CON MAYOR VARIABILIDAD:
 {elemento_mayor_varianza} - Varianza: {mayor_varianza:.4f}, Desviación: {mayor_desviacion:.4f}s

ELEMENTO CON MENOR VARIABILIDAD:
 {elemento_menor_varianza} - Varianza: {menor_varianza:.4f}, Desviación: {menor_desviacion:.4f}s

RANGO DE VARIABILIDAD:
 Varianza: {rango_varianza:.4f} (de {menor_varianza:.4f} a {mayor_varianza:.4f})
 Desviación Estándar: {rango_desviacion:.4f}s (de {menor_desviacion:.4f}s a {mayor_desviacion:.4f}s)

NIVEL DE VARIABILIDAD:
"""

        #Clasificar la variabilidad general
        desviacion_promedio = np.mean(self.desviaciones_estandar)
        if desviacion_promedio < 2.0:
            conclusion += "BAJA variabilidad entre elementos (proceso consistente)"
        elif desviacion_promedio < 5.0:
            conclusion += "MODERADA variabilidad entre elementos"
        else:
            conclusion += "ALTA variabilidad entre elementos (revisar consistencia del proceso)"

        #Resumen general
        conclusion += f"""

RESUMEN GENERAL:
 Total elementos analizados: {self.num_elementos}
 Iteraciones por elemento: {self.num_iteraciones}
 Factor de Valoración aplicado: {self.factor_valoracion:.2f} 
 Factor de Tolerancia aplicado: {self.factor_tolerancia:.2f}
 Tiempo estándar total: {sum(self.tiempos_estandar):.2f}s
 Varianza promedio: {np.mean(self.varianzas):.4f}
 Desviación estándar promedio: {desviacion_promedio:.4f}s
"""

        self.conclusion_text.delete("1.0", tk.END)
        self.conclusion_text.insert("1.0", conclusion)

    def generar_conclusion_medicion_piezas(self):
        if not self.dimensiones_pieza:
            return

        conclusion = f"""CONCLUSIÓN - MEDICIÓN DE PIEZAS

INFORMACIÓN DEL ESTUDIO:
Área/Departamento: {self.area_departamento}
N° Estudio: {self.numero_estudio}
Fecha: {self.fecha_estudio}
Operación: {self.operacion}
Horario: {self.comenzo_estudio} - {self.termino_estudio}
Producto/Pieza: {self.producto_pieza}
Material: {self.material}
Herramientas: {self.herramientas}
Operadores: {', '.join(self.operadores)}
Observado por: {self.observado_por}
Comprobado por: {self.comprobado_por}

ANÁLISIS POR DIMENSIÓN:
"""

        #Análisis detallado por dimensión
        for i, dimension in enumerate(self.dimensiones_pieza):
            cv = (self.desviaciones_dimensiones[i] / self.medias_dimensiones[i]) * 100 if self.medias_dimensiones[
                                                                                              i] != 0 else 0
            conclusion += f"""
{dimension}:
 Media: {self.medias_dimensiones[i]:.4f}
 Varianza: {self.varianzas_dimensiones[i]:.6f}
 Desviación Estándar: {self.desviaciones_dimensiones[i]:.6f}
 Coeficiente de Variación: {cv:.2f}%
"""

        dimension_mayor_varianza = self.dimensiones_pieza[np.argmax(self.varianzas_dimensiones)]
        mayor_varianza = max(self.varianzas_dimensiones)
        dimension_menor_varianza = self.dimensiones_pieza[np.argmin(self.varianzas_dimensiones)]
        menor_varianza = min(self.varianzas_dimensiones)

        dimension_mayor_desviacion = self.dimensiones_pieza[np.argmax(self.desviaciones_dimensiones)]
        mayor_desviacion = max(self.desviaciones_dimensiones)
        dimension_menor_desviacion = self.dimensiones_pieza[np.argmin(self.desviaciones_dimensiones)]
        menor_desviacion = min(self.desviaciones_dimensiones)

        #Calcular rango de variabilidad
        rango_varianza = mayor_varianza - menor_varianza
        rango_desviacion = mayor_desviacion - menor_desviacion

        conclusion += f"""
ANÁLISIS DE VARIABILIDAD:

DIMENSIÓN CON MAYOR VARIABILIDAD:
 {dimension_mayor_varianza} - Varianza: {mayor_varianza:.6f}, Desviación: {mayor_desviacion:.6f}

DIMENSIÓN CON MENOR VARIABILIDAD:
 {dimension_menor_varianza} - Varianza: {menor_varianza:.6f}, Desviación: {menor_desviacion:.6f}

RANGO DE VARIABILIDAD:
 Varianza: {rango_varianza:.6f} (de {menor_varianza:.6f} a {mayor_varianza:.6f})
 Desviación Estándar: {rango_desviacion:.6f} (de {menor_desviacion:.6f} a {mayor_desviacion:.6f})

NIVEL DE VARIABILIDAD GENERAL:
"""

        #Clasificar la variabilidad general
        desviacion_promedio = np.mean(self.desviaciones_dimensiones)
        if desviacion_promedio < 0.01:
            conclusion += "BAJA variabilidad dimensional (proceso de manufactura consistente)"
        elif desviacion_promedio < 0.05:
            conclusion += "MODERADA variabilidad dimensional"
        else:
            conclusion += "ALTA variabilidad dimensional (revisar proceso de fabricación)"

        #Resumen general
        conclusion += f"""

RESUMEN GENERAL:
 Dimensiones medidas: {self.num_dimensiones}
 Mediciones realizadas: {self.num_mediciones}
 Varianza promedio: {np.mean(self.varianzas_dimensiones):.6f}
 Desviación estándar promedio: {desviacion_promedio:.6f}
"""

        self.conclusion_text.delete("1.0", tk.END)
        self.conclusion_text.insert("1.0", conclusion)

    def limpiar_controles_graficas(self):
        try:
            #Verificar si el frame de controles existe y es accesible
            if hasattr(self, 'controls_frame') and self.controls_frame.winfo_exists():
                for widget in self.controls_frame.winfo_children():
                    widget.destroy()
        except tk.TclError:
            #Si hay error, recrear el frame de controles
            self.recrear_controles_graficas()

    def recrear_controles_graficas(self):
        if hasattr(self, 'controls_frame') and not self.controls_frame.winfo_exists():
            self.controls_frame = ttk.Frame(self.graficas_container)
            self.controls_frame.pack(fill=X, pady=(0, 10))

    def generar_graficas_iteraciones(self):
        #Limpiar gráficas anteriores
        self.limpiar_graficas()

        if not self.elementos:
            messagebox.showwarning("Datos", "No hay datos para graficar")
            return

        #Crear gráficas para cada iteración
        for i in range(self.num_iteraciones):
            self.crear_grafica_iteracion(i)

    def crear_grafica_iteracion(self, iteracion):
        #Obtener tiempos de todos los elementos para esta iteración
        tiempos_iteracion = [tiempos[iteracion] for tiempos in self.tiempos_observados]
        promedio = self.promedios_iteraciones[iteracion]
        desviacion = self.desviaciones_iteraciones[iteracion]

        #Crear figura
        fig, ax = plt.subplots(figsize=(10, 5))
        elementos_range = range(1, self.num_elementos + 1)
        linea = ax.plot(elementos_range, tiempos_iteracion, marker='o', linewidth=2, markersize=6,
                        color='blue', label='Tiempos por elemento')

        #Línea del promedio
        ax.axhline(y=promedio, color='red', linestyle='--', linewidth=2, label=f'Promedio: {promedio:.2f}s')

        #Área de desviación estándar
        ax.fill_between([0.5, self.num_elementos + 0.5],
                        promedio - desviacion, promedio + desviacion,
                        alpha=0.2, color='red', label=f'Desv. Estándar: ±{desviacion:.2f}s')

        #Valores en los puntos
        for j, tiempo in enumerate(tiempos_iteracion):
            ax.annotate(f'{tiempo:.2f}s',
                        xy=(j + 1, tiempo),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        ax.set_xlabel('Elementos')
        ax.set_ylabel('Tiempo (segundos)')
        ax.set_title(
            f'Iteración {iteracion + 1} - Distribución de Tiempos\nPromedio: {promedio:.2f}s, Varianza: {self.varianzas_iteraciones[iteracion]:.2f}')
        ax.set_xticks(elementos_range)
        ax.set_xticklabels([f'Elem {i + 1}' for i in range(self.num_elementos)])
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.graficas_container)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=BOTH, expand=YES, pady=5)

        self.graficas_canvas_list.append(canvas)

    def generar_graficas_dimensiones(self):
        #Limpiar gráficas anteriores
        self.limpiar_graficas()

        if not self.dimensiones_pieza:
            messagebox.showwarning("Datos", "No hay datos para graficar")
            return

        #Crear gráficas para cada dimensión
        for i in range(self.num_dimensiones):
            self.crear_grafica_dimension(i)

    def crear_grafica_dimension(self, indice_dimension):
        #Obtener mediciones para esta dimensión
        mediciones_dim = [med[indice_dimension] for med in self.mediciones_pieza]
        nombre_dim = self.dimensiones_pieza[indice_dimension]
        media = self.medias_dimensiones[indice_dimension]
        desviacion = self.desviaciones_dimensiones[indice_dimension]

        #Crear figura
        fig, ax = plt.subplots(figsize=(10, 5))
        mediciones_range = range(1, self.num_mediciones + 1)
        linea = ax.plot(mediciones_range, mediciones_dim, marker='o', linewidth=2, markersize=6,
                        color='green', label=f'Mediciones de {nombre_dim}')

        #Línea de la media
        ax.axhline(y=media, color='red', linestyle='--', linewidth=2, label=f'Media: {media:.3f}')

        #Área de desviación estándar
        ax.fill_between([0.5, self.num_mediciones + 0.5],
                        media - desviacion, media + desviacion,
                        alpha=0.2, color='red', label=f'Desv. Estándar: ±{desviacion:.3f}')

        #Valores en los puntos
        for j, medicion in enumerate(mediciones_dim):
            ax.annotate(f'{medicion:.3f}',
                        xy=(j + 1, medicion),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        ax.set_xlabel('Número de Medición')
        ax.set_ylabel('Valor de Medición')
        ax.set_title(
            f'{nombre_dim} - Distribución de Mediciones\nMedia: {media:.3f}, Varianza: {self.varianzas_dimensiones[indice_dimension]:.3f}')
        ax.set_xticks(mediciones_range)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.graficas_container)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=BOTH, expand=YES, pady=5)

        self.graficas_canvas_list.append(canvas)

    def limpiar_graficas(self):
        #Limpiar la lista de canvas de gráficas
        for canvas in self.graficas_canvas_list:
            try:
                if canvas.get_tk_widget().winfo_exists():
                    canvas.get_tk_widget().destroy()
            except tk.TclError:
                continue  #El widget ya no existe, continuar

        self.graficas_canvas_list = []

        #Limpiar otros widgets en el contenedor de gráficas
        try:
            for widget in self.graficas_container.winfo_children():
                if widget != self.controls_frame and widget.winfo_exists():
                    widget.destroy()
        except tk.TclError:
            pass  #Ignorar errores de widgets que ya no existen

# if __name__ == "__main__":
#     root = ttk.Window(themename="flatly")
#     app = EstudioTiemposApp(root)
#     root.mainloop()