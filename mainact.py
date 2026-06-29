from ursina import *
from random import choice, random
from math import sin


# =========================================================
# PROYECTO: PAC-MAN 3D EN PYTHON
# Librería usada: Ursina
# Descripción:
# Este código crea un juego tipo Pac-Man en 3D, con mapa,
# Pac-Man, fantasmas, bolitas normales, bolitas especiales,
# puntaje, cámara que sigue al jugador y modo especial.
# =========================================================


# =========================================================
# INICIO DEL JUEGO
# =========================================================

app = Ursina()

window.title = "Pac-Man 3D"
window.borderless = False
window.fullscreen = False
window.fps_counter.enabled = True
window.color = color.black


# =========================================================
# CONFIGURACIÓN GENERAL DEL JUEGO
# =========================================================

# Tamaño de cada casilla del mapa
TAMANO_CELDA = 1.8

# Altura de las paredes del laberinto
ALTURA_PARED = 2.6

# Velocidad de movimiento de Pac-Man
TIEMPO_MOVIMIENTO_PACMAN = 0.11

# Velocidad de movimiento de los fantasmas
TIEMPO_MOVIMIENTO_FANTASMA = 0.45
# Duración del modo especial al comer una bolita grande
DURACION_MODO_ESPECIAL = 30.0

# Tiempo que tarda un fantasma comido en reaparecer
TIEMPO_REAPARICION_FANTASMA = 30.0

# Configuración de cámara
DISTANCIA_CAMARA = Vec3(0, 24, -18)
VELOCIDAD_CAMARA = 4.5

# Variables principales del juego
puntaje = 0
vidas = 3
juego_terminado = False
modo_especial = False
tiempo_modo_especial = 0.0
reloj_animacion = 0.0


# =========================================================
# MAPA DEL JUEGO
#
# Significado de símbolos:
# # = pared
# . = bolita normal
# O = bolita especial
# P = Pac-Man
# 1,2,3,4 = fantasmas
# =========================================================

mapa = [
    "#########################",
    "#O.......#.....#.......O#",
    "#.###.###.#.#.#.###.###.#",
    "#.....#...#.#.#...#.....#",
    "###.#.#.###.#.###.#.#.###",
    "#...#.#...........#.#...#",
    "#.###.#.##.###.##.#.###.#",
    "#.......#.......#.......#",
    "#####.#.#.#####.#.#.#####",
    "#..........1234.........#",
    "#####.#.#.#####.#.#.#####",
    "#.......#.......#.......#",
    "#.###.#.##.###.##.#.###.#",
    "#...#.#...........#.#...#",
    "###.#.#.###.#.###.#.#.###",
    "#.....#...#.#.#...#.....#",
    "#.###.###.#.#.#.###.###.#",
    "#O.......#..P..#.......O#",
    "#########################",
]

# Se iguala el largo de todas las filas para evitar errores
columnas_maximas = max(len(fila) for fila in mapa)
mapa = [fila.ljust(columnas_maximas) for fila in mapa]

cantidad_filas = len(mapa)
cantidad_columnas = len(mapa[0])

# Estructuras donde se guardan los elementos del juego
paredes = set()
bolitas = {}
bolitas_especiales = {}
fantasmas = []


# =========================================================
# FUNCIONES PARA CONVERTIR POSICIONES
# =========================================================

def convertir_celda_a_mundo(fila, columna):
    """
    Convierte una posición del mapa por filas y columnas
    a una posición 3D dentro del mundo de Ursina.
    """
    x = (columna - cantidad_columnas / 2) * TAMANO_CELDA
    z = (cantidad_filas / 2 - fila) * TAMANO_CELDA
    return Vec3(x, 0, z)


def puede_moverse(fila, columna):
    """
    Verifica si Pac-Man o un fantasma pueden moverse
    hacia una casilla determinada.
    """
    if fila < 0 or fila >= cantidad_filas:
        return False

    if columna < 0 or columna >= cantidad_columnas:
        return False

    if (fila, columna) in paredes:
        return False

    return True


def distancia_en_mapa(fila_1, columna_1, fila_2, columna_2):
    """
    Calcula una distancia simple entre dos casillas.
    Se usa para que los fantasmas persigan o huyan.
    """
    return abs(fila_1 - fila_2) + abs(columna_1 - columna_2)


# =========================================================
# CREACIÓN DE PAC-MAN 3D
# =========================================================

def crear_malla_boca(apertura=0.30):
    """
    Crea la malla negra que simula la boca de Pac-Man.
    La variable apertura sirve para abrir y cerrar la boca.
    """
    ancho = 0.18 + apertura
    frente = 0.80
    fondo = 0.04
    y_superior = 0.18
    y_inferior = -0.18

    vertices = [
        Vec3(0, y_superior, fondo),
        Vec3(-ancho, y_superior, frente),
        Vec3(ancho, y_superior, frente),

        Vec3(0, y_inferior, fondo),
        Vec3(-ancho, y_inferior, frente),
        Vec3(ancho, y_inferior, frente),
    ]

    triangulos = [
        0, 1, 2,
        3, 5, 4,
        0, 3, 4,
        0, 4, 1,
        0, 2, 5,
        0, 5, 3,
        1, 4, 5,
        1, 5, 2
    ]

    return Mesh(vertices=vertices, triangles=triangulos, mode="triangle")


def crear_pacman(posicion):
    """
    Crea a Pac-Man usando una esfera amarilla,
    una boca negra y un ojo.
    """
    pacman = Entity(position=posicion)

    pacman.cuerpo = Entity(
        parent=pacman,
        model="sphere",
        color=color.yellow,
        scale=1.10
    )

    pacman.boca = Entity(
        parent=pacman,
        model=crear_malla_boca(0.30),
        color=color.black,
        scale=1.10
    )

    pacman.ojo = Entity(
        parent=pacman,
        model="sphere",
        color=color.black,
        scale=0.12,
        position=(0.28, 0.30, -0.28)
    )

    pacman.apertura_boca = 0.30
    pacman.direccion_boca = 1

    return pacman


def animar_pacman():
    """
    Anima la boca de Pac-Man abriendo y cerrando.
    También se le da un pequeño movimiento vertical.
    """
    if juego_terminado:
        return

    jugador.apertura_boca += jugador.direccion_boca * time.dt * 2.8

    if jugador.apertura_boca >= 0.42:
        jugador.apertura_boca = 0.42
        jugador.direccion_boca = -1

    if jugador.apertura_boca <= 0.08:
        jugador.apertura_boca = 0.08
        jugador.direccion_boca = 1

    jugador.boca.model = crear_malla_boca(jugador.apertura_boca)

    jugador.y = jugador.altura_base + sin(reloj_animacion * 8) * 0.03


# =========================================================
# CREACIÓN DE FANTASMAS 3D
# =========================================================

def crear_fantasma(posicion, color_fantasma):
    """
    Crea un fantasma 3D usando una esfera, un cubo,
    pequeñas ondas inferiores y ojos.
    """
    fantasma = Entity(position=posicion)

    fantasma.color_original = color_fantasma
    fantasma.esta_vulnerable = False
    fantasma.esta_comido = False
    fantasma.tiempo_reaparicion = 0.0
    fantasma.partes = []

    parte_superior = Entity(
        parent=fantasma,
        model="sphere",
        color=color_fantasma,
        scale=(1.05, 1.18, 1.05),
        position=(0, 0.50, 0)
    )

    cuerpo = Entity(
        parent=fantasma,
        model="cube",
        color=color_fantasma,
        scale=(1.05, 0.95, 1.05),
        position=(0, 0.02, 0)
    )

    fantasma.partes.append(parte_superior)
    fantasma.partes.append(cuerpo)

    # Ondas inferiores del fantasma
    for i in range(3):
        onda = Entity(
            parent=fantasma,
            model="sphere",
            color=color_fantasma,
            scale=(0.34, 0.34, 0.34),
            position=(-0.34 + i * 0.34, -0.46, 0)
        )
        fantasma.partes.append(onda)

    # Ojos blancos
    Entity(
        parent=fantasma,
        model="sphere",
        color=color.white,
        scale=(0.22, 0.22, 0.08),
        position=(-0.23, 0.62, -0.49)
    )

    Entity(
        parent=fantasma,
        model="sphere",
        color=color.white,
        scale=(0.22, 0.22, 0.08),
        position=(0.23, 0.62, -0.49)
    )

    # Pupilas negras
    Entity(
        parent=fantasma,
        model="sphere",
        color=color.black,
        scale=(0.09, 0.09, 0.04),
        position=(-0.23, 0.62, -0.56)
    )

    Entity(
        parent=fantasma,
        model="sphere",
        color=color.black,
        scale=(0.09, 0.09, 0.04),
        position=(0.23, 0.62, -0.56)
    )

    return fantasma


def cambiar_estado_visual_fantasma(fantasma, vulnerable):
    """
    Cambia el color del fantasma.
    Cuando es vulnerable, se vuelve azul.
    Cuando vuelve a la normalidad, recupera su color original.
    """
    fantasma.esta_vulnerable = vulnerable

    if fantasma.esta_comido:
        return

    if vulnerable:
        nuevo_color = color.rgb(40, 80, 255)
    else:
        nuevo_color = fantasma.color_original

    for parte in fantasma.partes:
        parte.color = nuevo_color


def comer_fantasma(fantasma):
    """
    Cuando Pac-Man come un fantasma, este desaparece
    y empieza un contador para reaparecer.
    """
    global puntaje

    fantasma.esta_comido = True
    fantasma.visible = False
    fantasma.tiempo_reaparicion = TIEMPO_REAPARICION_FANTASMA

    puntaje += 200
    texto_puntaje.text = f"Puntaje: {puntaje}"


def reaparecer_fantasma(fantasma):
    """
    Reaparece al fantasma en su punto inicial.
    """
    fantasma.esta_comido = False
    fantasma.visible = True

    fantasma.fila = fantasma.fila_inicial
    fantasma.columna = fantasma.columna_inicial

    fantasma.position = convertir_celda_a_mundo(
        fantasma.fila_inicial,
        fantasma.columna_inicial
    ) + Vec3(0, fantasma.altura_base, 0)

    if modo_especial:
        cambiar_estado_visual_fantasma(fantasma, True)
    else:
        cambiar_estado_visual_fantasma(fantasma, False)


# =========================================================
# CREACIÓN DEL PISO 3D
# =========================================================

piso = Entity(
    model="cube",
    color=color.rgb(0, 0, 0),
    scale=(cantidad_columnas * TAMANO_CELDA + 2, 0.25, cantidad_filas * TAMANO_CELDA + 2),
    position=(0, -0.25, 0)
)


# =========================================================
# CONSTRUCCIÓN DEL MAPA 3D
# =========================================================

jugador = None

colores_fantasmas = {
    "1": color.red,
    "2": color.magenta,
    "3": color.cyan,
    "4": color.orange
}

for fila, linea in enumerate(mapa):
    for columna, simbolo in enumerate(linea):
        posicion = convertir_celda_a_mundo(fila, columna)

        if simbolo == "#":
            paredes.add((fila, columna))

            # Cuerpo principal de la pared
            Entity(
                model="cube",
                color=color.rgb(0, 0, 255),
                scale=(TAMANO_CELDA * 0.95, ALTURA_PARED, TAMANO_CELDA * 0.95),
                position=posicion + Vec3(0, ALTURA_PARED / 2, 0)
            )

            # Tapa superior de la pared para darle mejor apariencia
            Entity(
                model="cube",
                color=color.rgb(0, 200, 255),
                scale=(TAMANO_CELDA * 0.80, 0.12, TAMANO_CELDA * 0.80),
                position=posicion + Vec3(0, ALTURA_PARED + 0.03, 0)
            )

        elif simbolo == ".":
            bolita = Entity(
                model="sphere",
                color=color.yellow,
                scale=0.22,
                position=posicion + Vec3(0, 0.20, 0)
            )

            bolitas[(fila, columna)] = bolita

        elif simbolo == "O":
            bolita_especial = Entity(
                model="sphere",
                color=color.white,
                scale=0.45,
                position=posicion + Vec3(0, 0.25, 0)
            )

            bolitas_especiales[(fila, columna)] = bolita_especial

        elif simbolo == "P":
            jugador = crear_pacman(
                posicion + Vec3(0, 0.65, 0)
            )

            jugador.fila = fila
            jugador.columna = columna
            jugador.altura_base = 0.65
            jugador.temporizador_movimiento = 0

        elif simbolo in colores_fantasmas:
            fantasma = crear_fantasma(
                posicion + Vec3(0, 0.72, 0),
                colores_fantasmas[simbolo]
            )

            fantasma.fila = fila
            fantasma.columna = columna
            fantasma.fila_inicial = fila
            fantasma.columna_inicial = columna
            fantasma.altura_base = 0.72
            fantasma.temporizador_movimiento = 0
            fantasma.ultima_direccion = None

            fantasmas.append(fantasma)


# =========================================================
# INTERFAZ DEL JUEGO
# =========================================================

texto_nivel = Text(
    text="NIVEL 1",
    position=(-0.82, 0.44),
    scale=1.8,
    color=color.yellow
)

texto_puntaje = Text(
    text="Puntaje: 0",
    position=(0.45, 0.44),
    scale=1.8,
    color=color.yellow
)

texto_vidas = Text(
    text="Vidas: 3",
    position=(0.45, 0.38),
    scale=1.5,
    color=color.red
)

texto_mensaje = Text(
    text="",
    origin=(0, 0),
    scale=2.7,
    color=color.white
)


# =========================================================
# CÁMARA Y LUCES
# =========================================================

camera.orthographic = False
camera.fov = 55
camera.position = jugador.position + DISTANCIA_CAMARA
camera.rotation_x = 55
camera.rotation_y = 0

AmbientLight(
    color=color.rgb(70, 70, 70)
)

DirectionalLight(
    position=(0, 20, -10),
    rotation=(45, -45, 0),
    color=color.white
)


def actualizar_camara():
    """
    La cámara sigue a Pac-Man suavemente.
    """
    posicion_objetivo = jugador.position + DISTANCIA_CAMARA

    camera.position = lerp(
        camera.position,
        posicion_objetivo,
        time.dt * VELOCIDAD_CAMARA
    )

    camera.rotation_x = 55
    camera.rotation_y = 0


# =========================================================
# MODO ESPECIAL
# =========================================================

def activar_modo_especial():
    """
    Se activa cuando Pac-Man come una bolita especial.
    Durante este tiempo los fantasmas pueden ser comidos.
    """
    global modo_especial, tiempo_modo_especial

    modo_especial = True
    tiempo_modo_especial = DURACION_MODO_ESPECIAL

    for fantasma in fantasmas:
        if not fantasma.esta_comido:
            cambiar_estado_visual_fantasma(fantasma, True)


def actualizar_modo_especial():
    """
    Actualiza el tiempo restante del modo especial.
    Ya no se muestra texto en pantalla, pero la lógica sigue funcionando.
    """
    global modo_especial, tiempo_modo_especial

    if not modo_especial:
        return

    tiempo_modo_especial -= time.dt

    if tiempo_modo_especial <= 0:
        modo_especial = False
        tiempo_modo_especial = 0

        for fantasma in fantasmas:
            if not fantasma.esta_comido:
                cambiar_estado_visual_fantasma(fantasma, False)


# =========================================================
# MOVIMIENTO DE PAC-MAN
# =========================================================

def mover_pacman(cambio_fila, cambio_columna):
    """
    Mueve a Pac-Man por casillas.
    Antes de moverse revisa si la casilla no es una pared.
    """
    global puntaje

    if juego_terminado:
        return

    nueva_fila = jugador.fila + cambio_fila
    nueva_columna = jugador.columna + cambio_columna

    if puede_moverse(nueva_fila, nueva_columna):
        jugador.fila = nueva_fila
        jugador.columna = nueva_columna

        jugador.position = convertir_celda_a_mundo(
            nueva_fila,
            nueva_columna
        ) + Vec3(0, jugador.altura_base, 0)

        # Rotación visual según la dirección de movimiento
        if cambio_fila == -1:
            jugador.rotation_y = 180
        elif cambio_fila == 1:
            jugador.rotation_y = 0
        elif cambio_columna == -1:
            jugador.rotation_y = 90
        elif cambio_columna == 1:
            jugador.rotation_y = -90

        # Comer bolita normal
        if (nueva_fila, nueva_columna) in bolitas:
            destroy(bolitas[(nueva_fila, nueva_columna)])
            del bolitas[(nueva_fila, nueva_columna)]

            puntaje += 10
            texto_puntaje.text = f"Puntaje: {puntaje}"

        # Comer bolita especial
        if (nueva_fila, nueva_columna) in bolitas_especiales:
            destroy(bolitas_especiales[(nueva_fila, nueva_columna)])
            del bolitas_especiales[(nueva_fila, nueva_columna)]

            puntaje += 50
            texto_puntaje.text = f"Puntaje: {puntaje}"

            activar_modo_especial()

        # Si ya no quedan bolitas, el jugador gana
        if len(bolitas) == 0 and len(bolitas_especiales) == 0:
            ganar_juego()
            return


# =========================================================
# MOVIMIENTO DE LOS FANTASMAS
# =========================================================

def mover_fantasma(fantasma):
    """
    Movimiento simple de los fantasmas.
    Si están normales, persiguen a Pac-Man.
    Si están vulnerables, intentan alejarse.
    """
    if juego_terminado or fantasma.esta_comido:
        return

    direcciones = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    movimientos_validos = []

    for cambio_fila, cambio_columna in direcciones:
        nueva_fila = fantasma.fila + cambio_fila
        nueva_columna = fantasma.columna + cambio_columna

        if puede_moverse(nueva_fila, nueva_columna):
            movimientos_validos.append((cambio_fila, cambio_columna))

    if not movimientos_validos:
        return

    # Evita que el fantasma regrese inmediatamente por donde vino
    if fantasma.ultima_direccion and len(movimientos_validos) > 1:
        direccion_contraria = (
            -fantasma.ultima_direccion[0],
            -fantasma.ultima_direccion[1]
        )

        if direccion_contraria in movimientos_validos:
            movimientos_validos.remove(direccion_contraria)

    movimiento_elegido = None

    if fantasma.esta_vulnerable:
        # Si está vulnerable, intenta alejarse de Pac-Man
        mejor_distancia = -1

        for cambio_fila, cambio_columna in movimientos_validos:
            nueva_fila = fantasma.fila + cambio_fila
            nueva_columna = fantasma.columna + cambio_columna

            distancia = distancia_en_mapa(
                nueva_fila,
                nueva_columna,
                jugador.fila,
                jugador.columna
            )

            if distancia > mejor_distancia:
                mejor_distancia = distancia
                movimiento_elegido = (cambio_fila, cambio_columna)

        # Pequeña probabilidad de movimiento aleatorio
        if random() < 0.25:
            movimiento_elegido = choice(movimientos_validos)

    else:
        # Si está normal, intenta acercarse a Pac-Man
        mejor_distancia = 999999

        for cambio_fila, cambio_columna in movimientos_validos:
            nueva_fila = fantasma.fila + cambio_fila
            nueva_columna = fantasma.columna + cambio_columna

            distancia = distancia_en_mapa(
                nueva_fila,
                nueva_columna,
                jugador.fila,
                jugador.columna
            )

            if distancia < mejor_distancia:
                mejor_distancia = distancia
                movimiento_elegido = (cambio_fila, cambio_columna)

        # Pequeña probabilidad de movimiento aleatorio
        if random() < 0.20:
            movimiento_elegido = choice(movimientos_validos)

    if movimiento_elegido is None:
        movimiento_elegido = choice(movimientos_validos)

    fantasma.ultima_direccion = movimiento_elegido
    fantasma.fila += movimiento_elegido[0]
    fantasma.columna += movimiento_elegido[1]

    fantasma.position = convertir_celda_a_mundo(
        fantasma.fila,
        fantasma.columna
    ) + Vec3(0, fantasma.altura_base, 0)


def actualizar_reaparicion_fantasmas():
    """
    Controla el tiempo de reaparición de los fantasmas comidos.
    """
    for fantasma in fantasmas:
        if fantasma.esta_comido:
            fantasma.tiempo_reaparicion -= time.dt

            if fantasma.tiempo_reaparicion <= 0:
                reaparecer_fantasma(fantasma)


# =========================================================
# COLISIONES
# =========================================================

def revisar_colision_con_fantasmas():
    """
    Revisa si Pac-Man está en la misma casilla que un fantasma.
    """
    for fantasma in fantasmas:
        if fantasma.esta_comido:
            continue

        if fantasma.fila == jugador.fila and fantasma.columna == jugador.columna:
            if fantasma.esta_vulnerable:
                comer_fantasma(fantasma)
            else:
                perder_juego()


def perder_juego():
    """
    Resta una vida y reinicia posiciones.
    """
    global juego_terminado, vidas

    vidas -= 1
    texto_vidas.text = f"Vidas: {vidas}"

    # Si ya no quedan vidas
    if vidas <= 0:
        juego_terminado = True
        texto_mensaje.text = "GAME OVER"
        texto_mensaje.color = color.red
        return

    # Reiniciar posición de Pac-Man
    jugador.fila = 17
    jugador.columna = 13

    jugador.position = convertir_celda_a_mundo(
        jugador.fila,
        jugador.columna
    ) + Vec3(0, jugador.altura_base, 0)

    # Reiniciar fantasmas
    for fantasma in fantasmas:
        fantasma.fila = fantasma.fila_inicial
        fantasma.columna = fantasma.columna_inicial

        fantasma.position = convertir_celda_a_mundo(
            fantasma.fila,
            fantasma.columna
        ) + Vec3(0, fantasma.altura_base, 0)


def ganar_juego():
    """
    Muestra mensaje de victoria.
    """
    global juego_terminado

    juego_terminado = True

    texto_mensaje.text = "¡¡GANASTE!!"
    texto_mensaje.color = color.lime
    texto_mensaje.scale = 4

# =========================================================
# ENTRADA DEL TECLADO
# =========================================================

def input(tecla):
    """
    Detecta teclas especiales.
    """
    if tecla == "escape":
        application.quit()

    # Cerrar juego después de ganar o perder
    if juego_terminado:
        if tecla == "enter" or tecla == "space":
            application.quit()


# =========================================================
# ACTUALIZACIÓN PRINCIPAL DEL JUEGO
# =========================================================

def update():
    """
    Esta función se ejecuta muchas veces por segundo.
    Aquí se actualiza todo el juego.
    """
    global reloj_animacion

    if juego_terminado:
        return

    reloj_animacion += time.dt

    animar_pacman()
    actualizar_modo_especial()
    actualizar_reaparicion_fantasmas()
    actualizar_camara()

    # Movimiento de Pac-Man
    jugador.temporizador_movimiento += time.dt

    if jugador.temporizador_movimiento >= TIEMPO_MOVIMIENTO_PACMAN:
        if held_keys["w"] or held_keys["up arrow"]:
            mover_pacman(-1, 0)
            jugador.temporizador_movimiento = 0

        elif held_keys["s"] or held_keys["down arrow"]:
            mover_pacman(1, 0)
            jugador.temporizador_movimiento = 0

        elif held_keys["a"] or held_keys["left arrow"]:
            mover_pacman(0, -1)
            jugador.temporizador_movimiento = 0

        elif held_keys["d"] or held_keys["right arrow"]:
            mover_pacman(0, 1)
            jugador.temporizador_movimiento = 0

    # Movimiento y animación de los fantasmas
    for indice, fantasma in enumerate(fantasmas):
        if fantasma.esta_comido:
            continue

        fantasma.temporizador_movimiento += time.dt

        if fantasma.temporizador_movimiento >= TIEMPO_MOVIMIENTO_FANTASMA:
            mover_fantasma(fantasma)
            fantasma.temporizador_movimiento = 0

        # Pequeña animación para que parezcan flotar
        fantasma.y = fantasma.altura_base + sin(reloj_animacion * 4 + indice) * 0.08

    # Animación de las bolitas especiales
    for indice, bolita_especial in enumerate(bolitas_especiales.values()):
        bolita_especial.scale = 0.45 + sin(reloj_animacion * 5 + indice) * 0.06

    revisar_colision_con_fantasmas()


# =========================================================
# EJECUTAR EL JUEGO
# =========================================================

app.run()