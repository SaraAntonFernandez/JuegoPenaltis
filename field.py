from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import math

GOALKEEPER = 0
SHOOTER = 1
SIDESSTR = ["goalkeeper", "shooter"]
SIZE = (700, 700)  #la imagen es de 700x700
GAMMA = 2*math.pi/30 #variacion del angulo
DELTA = 10

class Player():
    def __init__(self):
        self.posx = SIZE[0]/2
    #lo paso a la clase hijo, voy a hacer uno diferente para shooter
    """ 
    def move(self, dir):
        sign = -1 if dir == "left" else 1
        self.posx = self.posx + sign*DELTA
        if self.posx < 0:
            self.posx = 0
        elif self.posx > SIZE[0]:
            self.posx = SIZE[0]
    """
    
    def get_pos(self):
        return [self.posx, self.posy]

class Goalkeeper(Player):
    def __init__(self):
        super().__init__()
        #he cambiado la posicion
        self.posy = SIZE[1]/2 + 300
    
    def move(self, dir):
        sign = -1 if dir == "left" else 1
        self.posx = self.posx + sign*DELTA
        if self.posx < 0:
            self.posx = 0
        elif self.posx > SIZE[0]:
            self.posx = SIZE[0]
        
class Shooter(Player): #es el propio balon en si
    #NOTA: no se si hacer que rebote o no, pues es un poco irrelevante
    #lo dejare para despues
    def __init__(self, speed):
        super().__init__()
        self.posy = SIZE[1]/2 - 300
        self.speed = speed #modulo de la velocidad
        self.angle = 0.0 #angulo del disparo NOTA: tipo float, pero creo que asi escrito esta muy feo
        self.velocity = [int(self.speed * math.cos(self.angle)), int(self.speed * math.sin(self.angle))]
    
    def get_angle(self):
        return self.angle
        
    def move(self, dir): #nombre anterior: adjust_angle, se pasa a llamar move, por reutilizar la funcion en game
        sign = -1 if dir == "left" else 1
        self.angle = self.angle + sign*GAMMA
        if self.angle < -math.pi:
            self.angle = -math.pi
        elif self.angle > math.pi:
            self.angle = math.pi
    
        #actualiza la velocidad(vector) lo hago asi para evitar calcular tantos cosenos y senos
    def update_velocity(self):
        self.velocity = [int(self.speed * math.cos(self.angle)), int(self.speed * math.sin(self.angle))]
    
    def update(self): #actualiza la posicion de la pelota
        self.posx += self.velocity[0]
        self.posy += self.velocity[1]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]
    
    def __str__(self):
        pass

#incluida en clase Shooter
"""
class Ball():
    def __init__(self, speed):
		self.speed = speed
		self.posx = SIZE[0]/2
		self.posy = SIZE[1]/2 + 180
	
	def get_pos(self):
		return [self.posx, self.posy]
	
	def shoot(self):
		self.posx += 3*self.speed
"""


class Game():
    def __init__(self, manager):
        self.players = manager.list([Goalkeeper(), Shooter(speed=2)])
        self.score = manager.list([0, 0])
        self.running = Value('i', 1)
        self.ball_moving = Value('i', 0)
        #self.ball = manager.list( [Ball(2)] )
        self.lock = Lock()
        
    def get_player(self, type):
        return self.players[type]
    
    def get_score(self):
        return list(self.score)
        
    def is_running(self):
        return self.running.value == 1
    
    def is_ball_moving(self):
        return self.ball_moving.value == 1

    def move(self, type, dir):
        self.lock.acquire()
        p = self.players[type]
        p.move(dir)
        self.players[type] = p
        self.lock.release()
        
    def stop(self):
        self.running.value = 0
    
    def shoot_ball(self):
        self.lock.acquire()
        self.ball_moving.value = 1
        p = self.players[SHOOTER]
        p.update_velocity()
        self.players[SHOOTER] = p
        self.lock.release()
    
    def move_ball(self):
        self.lock.acquire()
        p = self.players[SHOOTER]
        p.update()
        #controlar la puntuacion aqui con condicionales
        self.players[SHOOTER] = p
        self.lock.release()
        
    def get_info(self):
        info = {
            'pos_goalkeeper': self.players[GOALKEEPER].get_pos(),
            'pos_shooter': self.players[SHOOTER].get_pos(),
            'ball_angle': self.players[SHOOTER].get_angle(),
            'score': [0, 0],
            'is_running': self.is_running(),
            'ball_moving': self.is_ball_moving()
        }
        return info

    def __str__(self):
        pass
        
def player(type, conn, game):
    try:
        print(f"starting player {SIDESSTR[type]}: {game.get_info()}")
        conn.send((type, game.get_info()))
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "left" or command == "right":
                    game.move(type, command)
                elif command == "shoot": #comando nuevo
                    game.shoot_ball()
                elif command == "quit":
                    game.stop()
            if game.is_ball_moving(): #mueve la pelota si se ha disparado
                game.move_ball()
            conn.send(game.get_info())

    except:
        traceback.print_exc()
        conn.close()

    finally:
        print(f"Game ended {game}")
    
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 11235), authkey=b'secret password') as listener:
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
