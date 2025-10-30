import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

from prueba import GeneradorApp
from estudiosTM import EstudioTiemposApp
from variablesAleatorias import VariablesAleatoriasApp
from composicion import ComposicionApp
class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal - Simulación")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        #estilo
        self.style = ttk.Style(theme="flatly")
        self.configure_styles()

        #contenedor principal
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        title = ttk.Label(frame, text="Menú Principal", style="Title.TLabel")
        title.pack(pady=(10, 20))

        subtitle = ttk.Label(
            frame,
            text="Selecciona una sección del programa:",
            style="Subtitle.TLabel"
        )
        subtitle.pack(pady=(0, 30))

        #frame para los botones
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=10)

        opciones = [
            ("Generadores de Números Pseudoaleatorios", self.abrir_generadores),
            ("Estudio de Tiempos y Medición de Piezas", self.abrir_tiempos),
            ("Variables Aleatorias", self.abrir_variables),
            ("Composición", self.abrir_composicion),
            ("Sugerencias y Guía", self.mostrar_sugerencias),
            ("Salir", self.root.quit)
        ]

        for texto, comando in opciones:
            btn = ttk.Button(
                buttons_frame,
                text=texto,
                command=comando,
                style="Accent.TButton",
                width=40
            )
            btn.pack(pady=10)

        #Pie de página
        footer = ttk.Label(frame, text="Proyecto de Simulación - Los Tres Caballeros", font=("Helvetica", 9, "italic"))
        footer.pack(side=BOTTOM, pady=(20, 0))

    def configure_styles(self):
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12))
        self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))

    #Funciones para abrir ventanas
    def abrir_generadores(self):
        ventana = tk.Toplevel(self.root)
        GeneradorApp(ventana)

    def abrir_tiempos(self):
        ventana = tk.Toplevel(self.root)
        EstudioTiemposApp(ventana)

    def abrir_variables(self):
        ventana = tk.Toplevel(self.root)
        VariablesAleatoriasApp(ventana)

    def abrir_composicion(self):
        ventana = tk.Toplevel(self.root)
        ComposicionApp(ventana)

    def mostrar_sugerencias(self):
        #Crea ventana de sugerencias
        sugerencias_window = tk.Toplevel(self.root)
        sugerencias_window.title("Sugerencias")
        sugerencias_window.geometry("900x700")
        sugerencias_window.resizable(False, False)
        sugerencias_window.transient(self.root)
        sugerencias_window.grab_set()

        #Frame principal con scroll
        main_frame = ttk.Frame(sugerencias_window, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        #Título
        title = ttk.Label(main_frame, text="Guía de Secciones",
                         style="Title.TLabel")
        title.pack(pady=(0, 20))

        #Texto con scroll
        texto_frame = ttk.Frame(main_frame)
        texto_frame.pack(fill=BOTH, expand=YES)

        texto_sugerencias = scrolledtext.ScrolledText(
            texto_frame,
            width=80,
            height=25,
            font=("Helvetica", 10),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        texto_sugerencias.pack(fill=BOTH, expand=YES)

        # Contenido de las sugerencias
        contenido = """GUÍA DE SECCIONES – ¿QUÉ HERRAMIENTA NECESITAS?

        ESTUDIO DE TIEMPOS Y MEDICIÓN DE PIEZAS
        ----------------------------------------
        ESTUDIO DE TIEMPOS:  
        Ideal para analizar procesos de producción, medir tiempos de operación y calcular la eficiencia de las actividades.  
        Úsalo cuando necesites:  
        - Cronometrar tareas dentro de una línea de producción.  
        - Calcular tiempos estándar de operación.  
        - Analizar la variabilidad en procesos manuales.  
        - Determinar factores de ritmo y tolerancia.  

        MEDICIÓN DE PIEZAS:  
        Pensado para el control de calidad y el análisis dimensional.  
        Úsalo cuando necesites:  
        - Medir dimensiones de piezas (diámetros, largos, anchos, etc.).  
        - Calcular promedios, varianzas o desviaciones estándar.  
        - Analizar la consistencia de las piezas fabricadas.  
        - Comparar mediciones repetidas de una misma característica.  

        VARIABLES ALEATORIAS – DISTRIBUCIONES
        ---------------------------------------
        TRANSFORMADA INVERSA NORMAL:  
        Ideal para modelar fenómenos que siguen una distribución normal (la clásica “campana de Gauss”).  
        Algunos ejemplos de uso:  
        - Tiempos de llegada de clientes.  
        - Errores o variaciones en mediciones.  
        - Altura, peso u otras características físicas.  
        - Cualquier variable con comportamiento simétrico alrededor de una media.  

        DISTRIBUCIÓN EXPONENCIAL:  
        Perfecta para modelar el tiempo que transcurre entre eventos independientes.  
        Ejemplos:  
        - Tiempos entre llegadas de clientes a un sistema.  
        - Duración de llamadas telefónicas.  
        - Tiempo hasta que ocurre una falla.  
        - Procesos sin memoria (donde el futuro no depende del pasado).  

        DISTRIBUCIÓN POISSON:  
        Se utiliza para contar cuántos eventos ocurren dentro de un intervalo de tiempo.  
        Ejemplos:  
        - Número de clientes que llegan en una hora.  
        - Cantidad de defectos en un lote de producción.  
        - Número de accidentes en un periodo.  
        - Llegadas a un sistema de colas.  

        COMPOSICIÓN – DISTRIBUCIÓN TRIANGULAR
        ---------------------------------------
        Úsala cuando tienes poca información, pero conoces tres valores clave:  
        - El valor mínimo posible.  
        - El valor más probable (moda).  
        - El valor máximo posible.  

        Aplicaciones:  
        - Estimación de duraciones en proyectos.  
        - Cálculo de costos con incertidumbre.  
        - Tiempos de proceso con datos limitados.  
        - Análisis de riesgos con tres puntos de estimación.  

        GENERADORES DE NÚMEROS PSEUDOALEATORIOS
        -----------------------------------------
        Estas herramientas permiten generar secuencias de números aleatorios mediante diferentes métodos.  
        - Congruencial Lineal: Algoritmo básico y eficiente.  
        - Cuadrados Medios: Método histórico y sencillo.  
        - Congruencial Cuadrático: Ofrece mayor período y mejor aleatoriedad.  

        Son la base para todas las simulaciones anteriores.  

        CONSEJOS PARA ELEGIR
        ----------------------
        - Si tienes datos históricos usa la distribución que mejor se ajuste.  
        - Si solo tienes estimaciones usa la distribución Triangular.  
        - Si vas a contar eventos elige Poisson.  
        - Si mides tiempos entre eventos elige Exponencial.  
        - Si trabajas con variables continuas simétricas usa la Normal.  
        - Si analizas procesos productivos aplica Estudio de Tiempos.  
        - Si haces control dimensional utiliza Medición de Piezas.  
        """

        texto_sugerencias.insert("1.0", contenido)
        texto_sugerencias.config(state=tk.DISABLED)  #Hace el texto de solo lectura

        #Botón cerrar
        ttk.Button(
            main_frame,
            text="Cerrar Guía",
            command=sugerencias_window.destroy,
            style="Accent.TButton"
        ).pack(pady=(15, 0))


if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = MenuPrincipal(root)
    root.mainloop()