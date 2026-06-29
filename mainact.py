from ursina import *
from random import choice, random
from math import sin

app = Ursina()
window.title = "Pac-Man 3D"
window.color = color.black

TAMANO_CELDA = 1.8
ALTURA_PARED = 2.6
TIEMPO_MOVIMIENTO_PACMAN = 0.11
TIEMPO_MOVIMIENTO_FANTASMA = 0.45
DISTANCIA_CAMARA = Vec3(0, 24, -18)
VELOCIDAD_CAMARA = 4.5

puntaje = 0
juego_terminado = False
modo_especial = False
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
fantasmas = []

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

def distancia_en_mapa(fila_1, columna_1, fila_2, columna_2):
    return abs(fila_1 - fila_2) + abs(columna_1 - columna_2)

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

def crear_fantasma(posicion, color_fantasma):
    fantasma = Entity(position=posicion)
    fantasma.color_original = color_fantasma
    fantasma.esta_vulnerable = False
    fantasma.esta_comido = False
    fantasma.partes = []
    
    parte_superior = Entity(parent=fantasma, model="sphere", color=color_fantasma, scale=(1.05, 1.18, 1.05), position=(0, 0.50, 0))
    cuerpo = Entity(parent=fantasma, model="cube", color=color_fantasma, scale=(1.05, 0.95, 1.05), position=(0, 0.02, 0))
    fantasma.partes.append(parte_superior)
    fantasma.partes.append(cuerpo)
    
    for i in range(3):
        onda = Entity(parent=fantasma, model="sphere", color=color_fantasma, scale=(0.34, 0.34, 0.34), position=(-0.34 + i * 0.34, -0.46, 0))
        fantasma.partes.append(onda)
        
    Entity(parent=fantasma, model="sphere", color=color.white, scale=(0.22, 0.22, 0.08), position=(-0.23, 0.62, -0.49))
    Entity(parent=fantasma, model="sphere", color=color.white, scale=(0.22, 0.22, 0.08), position=(0.23, 0.62, -0.49))
    return fantasma

def mover_fantasma(fantasma):
    if juego_terminado or fantasma.esta_comido: return
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    movimientos_validos = []
    for cambio_fila, cambio_columna in direcciones:
        nueva_fila = fantasma.fila + cambio_fila
        nueva_columna = fantasma.columna + cambio_columna
        if puede_moverse(nueva_fila, nueva_columna):
            movimientos_validos.append((cambio_fila, cambio_columna))
            
    if not movimientos_validos: return
    
    movimiento_elegido = None
    mejor_distancia = 999999
    for cambio_fila, cambio_columna in movimientos_validos:
        nueva_fila = fantasma.fila + cambio_fila
        nueva_columna = fantasma.columna + cambio_columna
        distancia = distancia_en_mapa(nueva_fila, nueva_columna, jugador.fila, jugador.columna)
        if distancia < mejor_distancia:
            mejor_distancia = distancia
            movimiento_elegido = (cambio_fila, cambio_columna)
            
    if random() < 0.20:
        movimiento_elegido = choice(movimientos_validos)
        
    fantasma.fila += movimiento_elegido[0]
    fantasma.columna += movimiento_elegido[1]
    fantasma.position = convertir_celda_a_mundo(fantasma.fila, fantasma.columna) + Vec3(0, fantasma.altura_base, 0)

def actualizar_camara():
    posicion_objetivo = jugador.position + DISTANCIA_CAMARA
    camera.position = lerp(camera.position, posicion_objetivo, time.dt * VELOCIDAD_CAMARA)
    camera.rotation_x = 55

def mover_pacman(cambio_fila, cambio_columna):
    global puntaje
    if juego_terminado: return
    nueva_fila = jugador.fila + cambio_fila
    nueva_columna = jugador.columna + cambio_columna
    if puede_moverse(nueva_fila, nueva_columna):
        jugador.fila = nueva_fila
        jugador.columna = nueva_columna
        jugador.position = convertir_celda_a_mundo(nueva_fila, nueva_columna) + Vec3(0, jugador.altura_base, 0)
        if (nueva_fila, nueva_columna) in bolitas:
            destroy(bolitas[(nueva_fila, nueva_columna)])
            del bolitas[(nueva_fila, nueva_columna)]
            puntaje += 10

piso = Entity(model="cube", color=color.rgb(0, 0, 0), scale=(cantidad_columnas * TAMANO_CELDA + 2, 0.25, cantidad_filas * TAMANO_CELDA + 2), position=(0, -0.25, 0))
jugador = None

colores_fantasmas = {"1": color.red, "2": color.magenta, "3": color.cyan, "4": color.orange}

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
        elif simbolo in colores_fantasmas:
            fantasma = crear_fantasma(posicion + Vec3(0, 0.72, 0), colores_fantasmas[simbolo])
            fantasma.fila = fila
            fantasma.columna = columna
            fantasma.altura_base = 0.72
            fantasma.temporizador_movimiento = 0
            fantasmas.append(fantasma)

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
        if held_keys["w"] or held_keys["up arrow"]: mover_pacman(-1, 0); jugador.temporizador_movimiento = 0
        elif held_keys["s"] or held_keys["down arrow"]: mover_pacman(1, 0); jugador.temporizador_movimiento = 0
        elif held_keys["a"] or held_keys["left arrow"]: mover_pacman(0, -1); jugador.temporizador_movimiento = 0
        elif held_keys["d"] or held_keys["right arrow"]: mover_pacman(0, 1); jugador.temporizador_movimiento = 0
        
    for indice, fantasma in enumerate(fantasmas):
        fantasma.temporizador_movimiento += time.dt
        if fantasma.temporizador_movimiento >= TIEMPO_MOVIMIENTO_FANTASMA:
            mover_fantasma(fantasma)
            fantasma.temporizador_movimiento = 0
        fantasma.y = fantasma.altura_base + sin(reloj_animacion * 4 + indice) * 0.08