from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import math
from time import sleep

GOALKEEPER = 0
SHOOTER = 1
BALL_SIZE = 20
SIDESSTR = ["goalkeeper", "shooter"]
SIZE = (700, 700)  #la imagen es de 700x700

ALPHA = 1/60    # Variacion del angulo
DELTA = 5       # Variacion del paso del portero
SPEED = 3

class Player():
    def __init__(self):
        self.posx = SIZE[0]/2
    #lo paso a la clase hijo, voy a hacer uno diferente para shooter

    def move(self):
        pass
    
    def get_pos(self):
        return [self.posx, self.posy]

class Goalkeeper(Player):
    def __init__(self):
        super().__init__()
        #he cambiado la posicion
        self.posy = SIZE[1]/2 - 230
    
    def move(self, dir):
        sign = -1 if dir == "left" else 1
        self.posx = self.posx + sign*DELTA
        if self.posx < 0:
            self.posx = 0
        elif self.posx > SIZE[0]:
            self.posx = SIZE[0]
    
    def reset(self):
        self.posx = SIZE[0]/2
        self.posy = SIZE[1]/2 - 230

class Shooter(Player): #es el propio balon en si
    #NOTA: no se si hacer que rebote o no, pues es un poco irrelevante
    #lo dejare para despues
    def __init__(self):
        super().__init__()
        self.posy = SIZE[1]/2 + 250
        self.speed = SPEED #modulo de la velocidad
        self.angle = math.pi/2 #angulo del disparo NOTA: tipo float, pero creo que asi escrito esta muy feo
        self.velocity = [self.speed * math.cos(self.angle), -self.speed * math.sin(self.angle)]
    
    def get_angle(self):
        return self.angle
        
    def move(self, dir): #nombre anterior: adjust_angle, se pasa a llamar move, por reutilizar la funcion en game
        sign = -1 if dir == "left" else 1
        self.angle = self.angle - sign*ALPHA
        if self.angle < math.pi/8:          # Angulo minimo
            self.angle = math.pi/8
        elif self.angle > 7*math.pi/8:      # Angulo maximo
            self.angle = 7*math.pi/8
    
        #actualiza la velocidad(vector) lo hago asi para evitar calcular tantos cosenos y senos
    def update_velocity(self):
        self.velocity = [self.speed * math.cos(self.angle), -self.speed * math.sin(self.angle)]
    
    def update(self): #actualiza la posicion de la pelota
        self.posx += self.velocity[0]
        self.posy += self.velocity[1]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]
    
    def reset(self):
        self.posx = SIZE[0]/2
        self.posy = SIZE[1]/2 + 250
        self.speed = SPEED #modulo de la velocidad
        self.angle = math.pi/2 #angulo del disparo NOTA: tipo float, pero creo que asi escrito esta muy feo
        self.velocity = [self.speed * math.cos(self.angle), -self.speed * math.sin(self.angle)]
    
    def __str__(self):
        pass
       
class Game():
    def __init__(self, manager):
        self.manager = manager
        self.players = manager.list([Goalkeeper(), Shooter()])
        self.score = manager.list([0, 0])
        self.running = Value('i', 1)
        self.ball_moving = Value('i', 0)
        self.round_state = Value('i', 1)
        self.lock = Lock()
        
    def get_player(self, type):
        return self.players[type]
    
    def get_score(self):
        return list(self.score)
    
    def set_score(self, type):
        self.lock.acquire()
        self.score[type] += 1
        self.lock.release()
        
    def is_running(self):
        return self.running.value == 1
    
    def get_round_state(self):
        return self.round_state.value == 1
    
    def end_round(self):
        self.lock.acquire()
        self.round_state.value = 0
        self.lock.release()
    
    def is_ball_moving(self):
        return self.ball_moving.value == 1
    
    def stop_ball(self):
        self.lock.acquire()
        self.ball_moving.value = 0
        self.lock.release()

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
        pos = p.get_pos()
        if pos[0] < BALL_SIZE//2 or pos[0] > SIZE[0] - BALL_SIZE//2:
            p.bounce(0)
        self.players[SHOOTER] = p  
        self.lock.release()
    
    def reset(self):
        self.lock.acquire()
        self.round_state.value = 1
        p1 = self.players[GOALKEEPER]
        p2 = self.players[SHOOTER]
        p1.reset()
        p2.reset()
        self.players[GOALKEEPER] = p1
        self.players[SHOOTER] = p2
        self.lock.release()
    
        
    def get_info(self):
        info = {
            'pos_goalkeeper': self.players[GOALKEEPER].get_pos(),
            'pos_shooter': self.players[SHOOTER].get_pos(),
            'ball_angle': self.players[SHOOTER].get_angle(),
            'score': self.get_score(),
            'is_running': self.is_running(),
            'ball_moving': self.is_ball_moving(),
            'round_state': self.get_round_state()
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
                elif command == "goal":
                    game.end_round()
                    game.stop_ball()
                    game.set_score(SHOOTER)
                elif command == "out" or command == "catch":
                    game.end_round()
                    game.stop_ball()
                    game.set_score(GOALKEEPER)
                elif command == "quit":
                    game.stop()
            if game.is_ball_moving(): #mueve la pelota si se ha disparado
                game.move_ball()
            conn.send(game.get_info())

            if not game.get_round_state():
                game.reset()
                conn.send(game.get_info())
                
    except:
        traceback.print_exc()
        conn.close()

    finally:
        print(f"Game ended {game}")
    
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 11239), authkey=b'secret password') as listener:
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
