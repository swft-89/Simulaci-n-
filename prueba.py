import tkinter as tk
from tkinter import ttk, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import csv
from tkinter import filedialog, messagebox
import math

def algoritmo_lineal(semilla, a, c, m):
    if m <= 0:
        raise ValueError("El módulo (m) debe ser mayor que 0")

    numeros_generados = []
    semillas_vistas = set()
    x_actual = semilla
    ciclo_detectado = False

    #Lista con el procedimiento paso a paso
    procedimiento = []

    #Advertencias
    advertencias = []
    if not (0 <= semilla < m):
        advertencias.append("ADVERTENCIA: La semilla debe estar entre 0 y m-1.")
    if math.gcd(c, m) != 1:
        advertencias.append("ADVERTENCIA: 'c' y 'm' no son coprimos, el periodo no será máximo.")
    #Verificar factores primos de m
    factores_primos = set()
    temp = m
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factores_primos.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factores_primos.add(temp)

    for p in factores_primos:
        if (a - 1) % p != 0:
            advertencias.append(f"ADVERTENCIA: (a-1) no es múltiplo de {p}, no se garantiza periodo máximo.")
    if m % 4 == 0 and (a - 1) % 4 != 0:
        advertencias.append("ADVERTENCIA: Como m es divisible entre 4, (a-1) también debe ser divisible entre 4.")


    while not ciclo_detectado:
        if x_actual in semillas_vistas:
            ciclo_detectado = True
            messagebox.showinfo("Semilla repetida", f"La semilla {x_actual} se ha repetido. El ciclo ha terminado.")
            break

        semillas_vistas.add(x_actual)

        #calcular siguiente semilla
        x_siguiente = (a * x_actual + c) % m
        ri = x_siguiente / (m - 1)

        numeros_generados.append(ri)

        #guardar en tabla (X actual, X siguiente, número aleatorio)
        procedimiento.append((x_actual, x_siguiente, f"{ri:.4f}"))

        x_actual = x_siguiente

    return numeros_generados, procedimiento, advertencias


def cuadrados_medios(semilla):
    digitos = 4
    semillas_vistas = set()
    semilla_actual = semilla
    procedimiento = []
    numeros = []

    advertencias = []
    if len(str(semilla)) < digitos:
        advertencias.append("ADVERTENCIA: La semilla es muy corta, la secuencia puede degenerarse rápido.")
    if str(semilla).count("0") > len(str(semilla)) // 2:
        advertencias.append("ADVERTENCIA: La semilla tiene demasiados ceros, la secuencia puede ser de baja calidad.")

    while semilla_actual not in semillas_vistas:
        semillas_vistas.add(semilla_actual)

        cuadrado = semilla_actual ** 2
        str_cuadrado = str(cuadrado)

        #Agregar ceros a la izquierda si es necesario
        while len(str_cuadrado) < digitos * 2:
            str_cuadrado = '0' + str_cuadrado

        #Extraer dígitos del medio
        inicio = (len(str_cuadrado) - digitos) // 2
        fin = inicio + digitos
        semilla_str = str_cuadrado[inicio:fin]

        siguiente_semilla = int(semilla_str)
        ri = siguiente_semilla / (10 ** digitos)

        #Guardar resultados
        numeros.append(ri)
        procedimiento.append((semilla_actual, siguiente_semilla, f"{ri:.6f}"))

        semilla_actual = siguiente_semilla
    messagebox.showinfo("Semilla repetida", f"La semilla {semilla_actual} se ha repetido. El ciclo ha terminado.")

    return numeros, procedimiento, advertencias

def algoritmo_cuadratico(semilla, a, b, c, g):
    #Calcular m
    m = 2 ** g

    numeros_generados = []
    semillas_vistas = set()
    x_actual = semilla
    ciclo_detectado = False

    #Guardar advertencias si no cumplen condiciones
    advertencias = []
    if a % 2 != 0:
        advertencias.append("ADVERTENCIA: 'a' debe ser par para periodo máximo.")
    if c % 2 == 0:
        advertencias.append("ADVERTENCIA: 'c' debe ser impar para periodo máximo.")
    if (b - a) % 4 != 1:
        advertencias.append("ADVERTENCIA: '(b-a) mod 4 debe ser 1 para periodo máximo.")

    procedimiento = []

    while not ciclo_detectado:
        if x_actual in semillas_vistas:
            ciclo_detectado = True
            messagebox.showinfo("Semilla repetida", f"La semilla {x_actual} se ha repetido. El ciclo ha terminado.")
            break

        semillas_vistas.add(x_actual)

        #Fórmula cuadrática
        x_siguiente = (a * (x_actual ** 2) + b * x_actual + c) % m
        ri = x_siguiente / (m - 1)
        numeros_generados.append(ri)

        procedimiento.append((x_actual, x_siguiente, f"{ri:.6f}"))

        x_actual = x_siguiente

    return numeros_generados, procedimiento, advertencias, m



class GeneradorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generadores de Números Pseudoaleatorios")
        self.root.geometry("1200x700")

        #Configurar estilo
        self.style = ttk.Style(theme="flatly")
        self.configure_styles()

        #Algoritmos
        self.algoritmos = {
            "Congruencial Lineal": self.show_congruencial_lineal,
            "Cuadrados Medios": self.show_cuadrados_medios,
            "Congruencial Cuadrático": self.show_congruencial_cuadratico
        }
        self.params = {}

        #Crear marco principal
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=YES)

        #Crear paneles
        self.create_left_panel()
        self.create_right_panel()

        #Mostrar el primer algoritmo por defecto
        self.show_congruencial_lineal()

    def configure_styles(self):
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))

    def create_left_panel(self):
        #Panel izquierdo
        left_frame = ttk.Frame(self.main_frame, width=400)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        title_label = ttk.Label(left_frame, text="Generadores", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        #Botones de algoritmos
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill=X, pady=(0, 20))

        for algo_name in self.algoritmos.keys():
            btn = ttk.Button(
                buttons_frame,
                text=algo_name,
                command=lambda name=algo_name: self.algoritmos[name](),
                style="Accent.TButton",
                width=20
            )
            btn.pack(fill=X, pady=5)

        #Frame para formularios
        self.form_frame = ttk.Frame(left_frame)
        self.form_frame.pack(fill=BOTH, expand=YES)

    def create_right_panel(self):
        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        #Título
        results_title = ttk.Label(right_frame, text="Procedimiento y Resultados", style="Subtitle.TLabel")
        results_title.pack(pady=(0, 10))

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="center")
        style.configure("Treeview", rowheight=25, borderwidth=4, relief="solid")
        style.map("Treeview", background=[("selected", "#cce5ff")])

        #Tabla de resultados
        self.tree = ttk.Treeview(right_frame, columns=("i","X", "X_siguiente", "ri"), show="headings", height=20)
        self.tree.heading("i", text="Iteración", anchor="center")
        self.tree.heading("X", text="X actual", anchor="center")
        self.tree.heading("X_siguiente", text="X siguiente", anchor="center")
        self.tree.heading("ri", text="Número aleatorio (ri)", anchor="center")

        self.tree.column("i", anchor="center", width=90)
        self.tree.column("X", anchor="center", width=120)
        self.tree.column("X_siguiente", anchor="center", width=120)
        self.tree.column("ri", anchor="center", width=160)

        self.tree.pack(fill=BOTH, expand=YES)

        #Área de texto
        self.results_text = scrolledtext.ScrolledText(
            right_frame,
            width=70,
            height=10,
            font=("Consolas", 10)
        )
        self.results_text.pack(fill=BOTH, expand=YES, pady=(10, 0))

        #Botones de acción
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(action_frame, text="Limpiar", command=self.clear_results).pack(side=LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Exportar", command=self.export_results).pack(side=LEFT)

    def clear_form_frame(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def show_congruencial_lineal(self):
        self.clear_form_frame()
        self.clear_results()

        title = ttk.Label(self.form_frame, text="Congruencial Lineal", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Campos del formulario
        form_fields = [
            ("Semilla (X0)", "semilla"),
            ("Multiplicador (a)", "a"),
            ("Incremento (c)", "c"),
            ("Módulo (m)", "m")
        ]

        self.entries = {}
        for label_text, field_name in form_fields:
            frame = ttk.Frame(self.form_frame)
            frame.pack(fill=X, pady=5)

            label = ttk.Label(frame, text=label_text, width=15)
            label.pack(side=LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
            self.entries[field_name] = entry

        #Valores por defecto
        self.entries["semilla"].insert(0, "17")
        self.entries["a"].insert(0, "21")
        self.entries["c"].insert(0, "32")
        self.entries["m"].insert(0, "100")

        #Botón de ejecución
        ttk.Button(
            self.form_frame,
            text="Generar Números",
            command=self.execute_congruencial_lineal,
            style="Accent.TButton"
        ).pack(pady=20)

    def show_cuadrados_medios(self):
        #Mostrar formulario para cuadrados medios
        self.clear_form_frame()
        self.clear_results()

        title = ttk.Label(self.form_frame, text="Cuadrados Medios", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Campo del formulario
        frame = ttk.Frame(self.form_frame)
        frame.pack(fill=X, pady=5)

        label = ttk.Label(frame, text="Semilla", width=15)
        label.pack(side=LEFT)

        self.semilla_entry = ttk.Entry(frame)
        self.semilla_entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
        self.semilla_entry.insert(0, "5735")

        #Botón de ejecución
        ttk.Button(
            self.form_frame,
            text="Generar Números",
            command=self.execute_cuadrados_medios,
            style="Accent.TButton"
        ).pack(pady=20)

    def show_congruencial_cuadratico(self):
        #Mostrar formulario para congruencial cuadrático
        self.clear_form_frame()
        self.clear_results()

        title = ttk.Label(self.form_frame, text="Congruencial Cuadrático", style="Subtitle.TLabel")
        title.pack(pady=(0, 15))

        #Campos del formulario
        form_fields = [
            ("Semilla (X0)", "semilla"),
            ("Multiplicador (a)", "a"),
            ("Coeficiente (b)", "b"),
            ("Constante (c)", "c"),
            ("Exponente (g)", "g")
        ]

        self.entries_q = {}
        for label_text, field_name in form_fields:
            frame = ttk.Frame(self.form_frame)
            frame.pack(fill=X, pady=5)

            label = ttk.Label(frame, text=label_text, width=15)
            label.pack(side=LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, fill=X, expand=YES, padx=(10, 0))
            self.entries_q[field_name] = entry

        #Valores por defecto
        self.entries_q["semilla"].insert(0, "1")
        self.entries_q["a"].insert(0, "2")
        self.entries_q["b"].insert(0, "3")
        self.entries_q["c"].insert(0, "1")
        self.entries_q["g"].insert(0, "4")

        #Botón de ejecución
        ttk.Button(
            self.form_frame,
            text="Generar Números",
            command=self.execute_congruencial_cuadratico,
            style="Accent.TButton"
        ).pack(pady=20)

    def execute_congruencial_lineal(self):
        try:
            semilla = int(self.entries["semilla"].get())
            a = int(self.entries["a"].get())
            c = int(self.entries["c"].get())
            m = int(self.entries["m"].get())

            self.clear_results()

            numeros, procedimiento, advertencias = algoritmo_lineal(semilla, a, c, m)

            #Guardar parámetros
            self.params = {
                "Algoritmo": "Congruencial Lineal",
                "Semilla (X0)": semilla,
                "a (multiplicador)": a,
                "c (incremento)": c,
                "m (módulo)": m
            }

            #Llenar tabla
            for i, (x, x_sig, ri) in enumerate(procedimiento, start=1):
                self.tree.insert("", "end", values=(i, x, x_sig, ri))

            #Mensajes en el área de texto
            self.results_text.insert(END, f"Algoritmo: Congruencial Lineal\n")
            self.results_text.insert(END, f"Parámetros: X0={semilla}, a={a}, c={c}, m={m}\n")
            self.results_text.insert(END, "=" * 50 + "\n\n")
            self.results_text.insert(END, "Fórmula: X_{n+1} = (a * X_n + c) mod m\n")
            self.results_text.insert(END, "Número aleatorio: ri = X_{n+1} / (m-1)\n\n")
            for i, (x, x_sig, ri) in enumerate(procedimiento, start=1):
                self.results_text.insert(
                    END,
                    f"Iteración {i}: X_{i} = ({a}*{x} + {c}) mod {m} = {x_sig},  ri = {x_sig}/({m}-1) = {ri}\n"
                )
            self.results_text.insert(END, "=" * 50 + "\n\n")
            if advertencias:
                self.results_text.insert(END, "Advertencias:\n")
                for adv in advertencias:
                    self.results_text.insert(END, f"- {adv}\n")
                self.results_text.insert(END, "\n")
            self.results_text.insert(END, f"Total de números generados: {len(numeros)}\n")

        except ValueError as e:
            self.results_text.insert(END, f"Error: {str(e)}\n")

    def execute_cuadrados_medios(self):
        try:
            semilla = int(self.semilla_entry.get())

            self.clear_results()
            numeros, procedimiento, advertencias = cuadrados_medios(semilla)

            #Guardar parámetros
            self.params = {
                "Algoritmo": "Cuadrados Medios",
                "Semilla": semilla
            }

            #Llenar tabla
            for i, (x, x_sig, ri) in enumerate(procedimiento, start=1):
                self.tree.insert("", "end", values=(i, x, x_sig, ri))

            #Mensajes finales en el área de texto
            self.results_text.insert(END, f"Algoritmo: Cuadrados Medios\n")
            self.results_text.insert(END, f"Semilla: {semilla}\n")
            self.results_text.insert(END, "=" * 50 + "\n\n")
            for i, (x, x_sig, ri) in enumerate(procedimiento, start=1):
                self.results_text.insert(
                    END,
                    f"Iteración {i}: X_{i} = ({x}^2)[centro] = {x_sig},  ri = {x_sig}/10^{4} = {ri}\n"
                )
            self.results_text.insert(END, "=" * 50 + "\n\n")
            if advertencias:
                self.results_text.insert(END, "Advertencias:\n")
                for adv in advertencias:
                    self.results_text.insert(END, f"- {adv}\n")
                self.results_text.insert(END, "\n")
            self.results_text.insert(END, f"Total de números generados: {len(numeros)}\n")

        except ValueError as e:
            self.results_text.insert(END, f"Error: {str(e)}\n")

    def execute_congruencial_cuadratico(self):
        try:
            semilla = int(self.entries_q["semilla"].get())
            a = int(self.entries_q["a"].get())
            b = int(self.entries_q["b"].get())
            c = int(self.entries_q["c"].get())
            g = int(self.entries_q["g"].get())

            self.clear_results()
            numeros, procedimiento, advertencias, m = algoritmo_cuadratico(semilla, a, b, c, g)

            #Guardar parámetros
            self.params = {
                "Algoritmo": "Congruencial Cuadrático",
                "Semilla (X0)": semilla,
                "a (multiplicador)": a,
                "b (coeficiente)": b,
                "c (término constante)": c,
                "g (exponente)": g,
                "m (2^g)": m
            }

            #Llenar tabla
            for i, (x, x_sig, ri) in enumerate(procedimiento, start=1):
                self.tree.insert("", "end", values=(i, x, x_sig, ri))

            #Mensajes finales en el área de texto
            self.results_text.insert(END, f"Algoritmo: Congruencial Cuadrático\n")
            self.results_text.insert(END, f"Parámetros: X0={semilla}, a={a}, b={b}, c={c}, g={g}\n")
            self.results_text.insert(END, f"Módulo m = 2^{g} = {m}\n")
            self.results_text.insert(END, "=" * 50 + "\n\n")
            self.results_text.insert(END, "Fórmula: X_{n+1} = (a*X_n^2 + b*X_n + c) mod (2^g)\n")
            self.results_text.insert(END, "Número aleatorio: ri = X_{n+1} / (m-1)\n\n")

            for i, (x, x_sig, ri) in enumerate(procedimiento, start=1):
                self.results_text.insert(
                    END,
                    f"Iteración {i}: X_{i} = ({a}*{x}^2 + {b}*{x} + {c}) mod {m} = {x_sig},  ri = {x_sig}/({m}-1) = {ri}\n"
                )
            self.results_text.insert(END, "=" * 50 + "\n\n")
            if advertencias:
                self.results_text.insert(END, "Advertencias:\n")
                for adv in advertencias:
                    self.results_text.insert(END, f"- {adv}\n")
                self.results_text.insert(END, "\n")

            self.results_text.insert(END, f"Total de números generados: {len(numeros)}\n")

        except ValueError as e:
            self.results_text.insert(END, f"Error: {str(e)}\n")

    def clear_results(self):
        #Limpiar el cuadro de texto
        self.results_text.delete(1.0, END)

        #Limpiar la tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

    def export_results(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                #Guardar parámetros si existen
                if self.params:
                    writer.writerow(["Parámetros del algoritmo"])
                    for key, value in self.params.items():
                        writer.writerow([f"{key}: {value}"])
                    writer.writerow([])

                #Encabezados de la tabla
                headers = ["Iteración", "X actual", "X siguiente", "Número aleatorio (ri)"]
                writer.writerow(headers)

                #Guardar filas de la tabla
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])

            messagebox.showinfo("Éxito", f"Resultados exportados correctamente a:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo:\n{e}")


if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = GeneradorApp(root)
    root.mainloop()