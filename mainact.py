from ursina import *
from random import choice, random
from math import sin

app = Ursina()
window.title = "Pac-Man 3D"
window.color = color.black

TAMANO_CELDA = 1.8
ALTURA_PARED = 2.6

# El mapa completo ahora sí
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

# Suelo
piso = Entity(
    model="cube",
    color=color.rgb(0, 0, 0),
    scale=(cantidad_columnas * TAMANO_CELDA + 2, 0.25, cantidad_filas * TAMANO_CELDA + 2),
    position=(0, -0.25, 0)
)

# Bucle para generar el escenario
for fila, linea in enumerate(mapa):
    for columna, simbolo in enumerate(linea):
        posicion = convertir_celda_a_mundo(fila, columna)

        if simbolo == "#":
            paredes.add((fila, columna))
            Entity(
                model="cube",
                color=color.rgb(0, 0, 255),
                scale=(TAMANO_CELDA * 0.95, ALTURA_PARED, TAMANO_CELDA * 0.95),
                position=posicion + Vec3(0, ALTURA_PARED / 2, 0)
            )
        elif simbolo == ".":
            bolita = Entity(
                model="sphere",
                color=color.yellow,
                scale=0.22,
                position=posicion + Vec3(0, 0.20, 0)
            )
            bolitas[(fila, columna)] = bolita