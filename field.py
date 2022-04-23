from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

GOALKEEPER = 0
SHOOTER = 1
SIDESSTR = ["goalkeeper", "shooter"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 30

class Goalkeeper():
	def __init__(self):
		self.pos = # Completar, va arriba
	
	def getpos(self):
		return self.pos
	
	def moveLeft(self):
		self.pos[X] -= DELTA
		if self.pos[X] # Completar, ¿que pasa si se sale del campo?
		
	def moveRight(self):
		self.pos[X] += DELTA
		if self.pos[X] # Completar, ¿que pasa si se sale del campo?
		
	def __str__(self):
		# Completar
		
class Shooter():
	def __init__(self):
		# Completar
		
	def move  # Mover el balón
		# Completar
		
	def shoot(self):
		# Completar
	
	def __str__(self):
		# Completar
	
class Ball():
	def __init__(self, velocity):
		self.pos = # Completar, poner en la línea de tiro
		self.velocity = velocity
	
	def getpos(self):
		return self.pos
		
	def update(self):
		self.pos[X] += self.velocity[X]
		self.pos[Y] += self.velocity[Y]
	
	# ¿Hace falta alguna función más? Si el balón choca con el portero significa que este le ha parado = No hay función rebote ni colisión
		
	def __str__(self):
		# Completar
		
class Game():
	def __init__(self, manager):
		self.players = manager.list( [Goalkeeper, Shooter] )
		self.ball = manager.list( [Ball (#Velocidad#)] )
		self.goals = manager.list( [0] )
		self.running = Value('i', 1)
		self.lock = Lock()
		
	def getPlayer(self, typ):
		return self.players[typ]
		
	def getBall(self);
		return self.ball[0]
		
	def isRunning(self):
		return self.running.value == 1
		
	def moveRight(self, player): # Portero
		#Completar
	def moveLeft(self, player):
		#Completar
		
	def shoot(self, player): # Lanzador
		#Completar
	def move # Mover el balón
		#Completar
		
	def stopGame(self):
		self.running.value = 0
		
	def getinfo(self):
		#Completar
	
	def moveBall(self):
		self.lock.acquire()
		ball = self.ball[0]
		ball.update()
		pos = ball.getpos()
		# CASOS:
			# Gol = el balón toca la línea roja
			# Fuera
			# Lo para el portero
		# Al final de la jugada el balón vuelve a la línea de penáltis
		self.ball[0] = ball
		self.lock.release()
	
	def __str__(self)
		#Completar
		
def player(typ, conn, game):
	#Completar para cada tipo de jugador (typ)
	
def main(ip_address):
	manager = Manager()
	try:
		with Listener((ip_address, 11235), authkey=b'secret password') as listener
			numPlayers = 0
			players = [None, None]
			game = Game(manager)
			while True:
				print(f"accepting connection {numPlayers}")
				conn = listener.accept()
				players[numPlayers] = Process(target = player, args=(numPlayers, conn, game))
				numPlayers += 1
				if numPlayers == 2:
					players[0].start()
					players[1].start()
					numPlayers = 0
					players = [None, None]
					game = Game(manager)
	except Exception as e:
		traceback.print_exc()
		
if __name__ == '__main__':
	ip_address = sys.argv[1]
	main(ip_address)
	


