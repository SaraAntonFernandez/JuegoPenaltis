# Importacion de librerias
import traceback
import sys
import math

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

# Varios
FPS = 60
TYPES = ['goalkeeper', 'shooter']

# Tamaños
SIZE = (1000, 1000)

PLAYER_HEIGHT = 50
PLAYER_WIDTH = 50

BALL_SIZE = 40

GOALKEEPER = 0
SHOOTER = 1

# Paso de movimiento
ALPHA = 1/30
DELTA = 5
SPEED = 6