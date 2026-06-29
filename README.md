# 🕹️ Pac-Man 3D - Computación Gráfica

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Ursina Engine](https://img.shields.io/badge/Engine-Ursina%203D-darkgreen.svg?style=for-the-badge)
![License](https://img.shields.io/badge/Licencia-MIT-purple.svg?style=for-the-badge)

Un videojuego clásico de **Pac-Man recreado completamente en un entorno tridimensional** utilizando el lenguaje de programación Python y el motor gráfico **Ursina Engine**. Este proyecto fue desarrollado como trabajo práctico para la asignatura de *Computación Gráfica*.

---

## 🚀 Características del Proyecto

* **Entorno 3D Completo:** Renderizado dinámico de un laberinto tridimensional a partir de una matriz de caracteres.
* **Animaciones Fluídas:** Pac-Man cuenta con una malla poligonal personalizada para simular la apertura y cierre de la boca al moverse, además de un efecto de flotación para los fantasmas.
* **Inteligencia Artificial (IA) de los Fantasmas:** Los enemigos calculan distancias Manhattan de manera autónoma para perseguir activamente al jugador o huir de él en situaciones de vulnerabilidad.
* **Modo Especial (Power-Pellet):** Al consumir las píldoras especiales blancas (`O`), los fantasmas cambian visualmente a un color azul y se vuelven vulnerables a las colisiones del jugador.
* **Interfaz de Usuario (UI):** Marcador de puntaje en tiempo real, contador de vidas con interfaz dinámica y estados de juego (*GAME OVER* y *¡¡GANASTE!!*).

---

## 🎮 Controles del Juego

El juego soporta múltiples esquemas de control para una mejor experiencia de usuario:

| Acción | Teclas Alternativas |
| :--- | :--- |
| **Mover hacia Arriba** | `W` / `Flecha Arriba` |
| **Mover hacia Abajo** | `S` / `Flecha Abajo` |
| **Mover hacia la Izquierda** | `A` / `Flecha Izquierda` |
| **Mover hacia la Derecha** | `D` / `Flecha Derecha` |
| **Salir del Juego** | `Esc` |
| **Cerrar al terminar (Win/Loss)** | `Enter` / `Espacio` |

---

## 🛠️ Requisitos e Instalación

Para ejecutar este proyecto de forma local en tu computadora, asegúrate de cumplir con los siguientes prerrequisitos.

### 1. Clonar el repositorio
```bash
git clone [https://github.com/gabrieleleleee/Computacion_Grafica.git](https://github.com/gabrieleleleee/Computacion_Grafica.git)
cd Computacion_Grafica