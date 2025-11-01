import math


def algoritmo_lineal(semilla, a, c, m):
    if m <= 0:
        raise ValueError("El módulo (m) debe ser mayor que 0")

    numeros_generados = []
    semillas_vistas = set()
    x_actual = semilla
    ciclo_detectado = False

    procedimiento = []
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
            break

        semillas_vistas.add(x_actual)

        #Calcular siguiente semilla
        x_siguiente = (a * x_actual + c) % m
        ri = x_siguiente / (m - 1)

        numeros_generados.append(ri)
        procedimiento.append((x_actual, x_siguiente, f"{ri:.6f}"))
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
            break

        semillas_vistas.add(x_actual)

        #Fórmula cuadrática
        x_siguiente = (a * (x_actual ** 2) + b * x_actual + c) % m
        ri = x_siguiente / (m - 1)
        numeros_generados.append(ri)

        procedimiento.append((x_actual, x_siguiente, f"{ri:.6f}"))
        x_actual = x_siguiente

    return numeros_generados, procedimiento, advertencias, m