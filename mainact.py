from ursina import *
from random import choice, random
from math import sin

app = Ursina()
window.title = "Pac-Man 3D"
window.color = color.black

TAMANO_CELDA = 1.8
ALTURA_PARED = 2.6
TIEMPO_MOVIMIENTO_PACMAN = 0.11
DISTANCIA_CAMARA = Vec3(0, 24, -18)
VELOCIDAD_CAMARA = 4.5

puntaje = 0
juego_terminado = False
reloj_animacion = 0.0

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

columnas_maximas = max(len(fila) for fila in mapa)
mapa = [fila.ljust(columnas_maximas) for fila in mapa]

cantidad_filas = len(mapa)
cantidad_columnas = len(mapa[0])

paredes = set()
bolitas = {}
bolitas_especiales = {}

def convertir_celda_a_mundo(fila, columna):
    x = (columna - cantidad_columnas / 2) * TAMANO_CELDA
    z = (cantidad_filas / 2 - fila) * TAMANO_CELDA
    return Vec3(x, 0, z)

def puede_moverse(fila, columna):
    if fila < 0 or fila >= cantidad_filas or columna < 0 or columna >= cantidad_columnas:
        return False
    if (fila, columna) in paredes:
        return False
    return True

def crear_malla_boca(apertura=0.30):
    ancho = 0.18 + apertura
    frente = 0.80
    fondo = 0.04
    y_superior = 0.18
    y_inferior = -0.18
    vertices = [
        Vec3(0, y_superior, fondo), Vec3(-ancho, y_superior, frente), Vec3(ancho, y_superior, frente),
        Vec3(0, y_inferior, fondo), Vec3(-ancho, y_inferior, frente), Vec3(ancho, y_inferior, frente),
    ]
    triangulos = [0, 1, 2, 3, 5, 4, 0, 3, 4, 0, 4, 1, 0, 2, 5, 0, 5, 3, 1, 4, 5, 1, 5, 2]
    return Mesh(vertices=vertices, triangles=triangulos, mode="triangle")

def crear_pacman(posicion):
    pacman = Entity(position=posicion)
    pacman.cuerpo = Entity(parent=pacman, model="sphere", color=color.yellow, scale=1.10)
    pacman.boca = Entity(parent=pacman, model=crear_malla_boca(0.30), color=color.black, scale=1.10)
    pacman.ojo = Entity(parent=pacman, model="sphere", color=color.black, scale=0.12, position=(0.28, 0.30, -0.28))
    pacman.apertura_boca = 0.30
    pacman.direccion_boca = 1
    return pacman

def animar_pacman():
    if juego_terminado: return
    jugador.apertura_boca += jugador.direccion_boca * time.dt * 2.8
    if jugador.apertura_boca >= 0.42:
        jugador.apertura_boca = 0.42
        jugador.direccion_boca = -1
    if jugador.apertura_boca <= 0.08:
        jugador.apertura_boca = 0.08
        jugador.direccion_boca = 1
    jugador.boca.model = crear_malla_boca(jugador.apertura_boca)
    jugador.y = jugador.altura_base + sin(reloj_animacion * 8) * 0.03

def actualizar_camara():
    posicion_objetivo = jugador.position + DISTANCIA_CAMARA
    camera.position = lerp(camera.position, posicion_objetivo, time.dt * VELOCIDAD_CAMARA)
    camera.rotation_x = 55
    camera.rotation_y = 0

def mover_pacman(cambio_fila, cambio_columna):
    global puntaje
    if juego_terminado: return
    nueva_fila = jugador.fila + cambio_fila
    nueva_columna = jugador.columna + cambio_columna
    if puede_moverse(nueva_fila, nueva_columna):
        jugador.fila = nueva_fila
        jugador.columna = nueva_columna
        jugador.position = convertir_celda_a_mundo(nueva_fila, nueva_columna) + Vec3(0, jugador.altura_base, 0)
        if cambio_fila == -1: jugador.rotation_y = 180
        elif cambio_fila == 1: jugador.rotation_y = 0
        elif cambio_columna == -1: jugador.rotation_y = 90
        elif cambio_columna == 1: jugador.rotation_y = -90

        if (nueva_fila, nueva_columna) in bolitas:
            destroy(bolitas[(nueva_fila, nueva_columna)])
            del bolitas[(nueva_fila, nueva_columna)]
            puntaje += 10

# Construir escenario básico con Pacman
piso = Entity(model="cube", color=color.rgb(0, 0, 0), scale=(cantidad_columnas * TAMANO_CELDA + 2, 0.25, cantidad_filas * TAMANO_CELDA + 2), position=(0, -0.25, 0))
jugador = None

for fila, linea in enumerate(mapa):
    for columna, simbolo in enumerate(linea):
        posicion = convertir_celda_a_mundo(fila, columna)
        if simbolo == "#":
            paredes.add((fila, columna))
            Entity(model="cube", color=color.rgb(0, 0, 255), scale=(TAMANO_CELDA * 0.95, ALTURA_PARED, TAMANO_CELDA * 0.95), position=posicion + Vec3(0, ALTURA_PARED / 2, 0))
        elif simbolo == ".":
            bolitas[(fila, columna)] = Entity(model="sphere", color=color.yellow, scale=0.22, position=posicion + Vec3(0, 0.20, 0))
        elif simbolo == "P":
            jugador = crear_pacman(posicion + Vec3(0, 0.65, 0))
            jugador.fila = fila
            jugador.columna = columna
            jugador.altura_base = 0.65
            jugador.temporizador_movimiento = 0

camera.orthographic = False
camera.fov = 55
camera.position = jugador.position + DISTANCIA_CAMARA
camera.rotation_x = 55

def update():
    global reloj_animacion
    if juego_terminado: return
    reloj_animacion += time.dt
    animar_pacman()
    actualizar_camara()
    
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