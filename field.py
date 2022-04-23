from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

GOALKEEPER = 0
SHOOTER = 1
SIDESSTR = ["goalkeeper", "shooter"]
SIZE = (700, 525)
DELTA = 10

class Player():
    def __init__(self):
        self.posx = SIZE[0]/2

    def move(self, dir):
        self.posx = (-1 if dir == "left" else 1)*DELTA
        if self.posx < 0:
            self.posx = 0
        elif self.posx > SIZE[0]:
            self.posx = SIZE[0]
    
    def get_pos(self):
        return [self.posx, self.posy]

class Goalkeeper(Player):
    def __init__(self):
        super().__init__()
        self.posy = SIZE[1]/2 - 50
        
class Shooter():
    def __init__(self):
        super().__init__()
        self.posy = SIZE[1] + 50
        
class Game():
    def __init__(self, manager):
        self.players = manager.list([Goalkeeper(), Shooter()])
        self.running = Value('i', 1)
        self.lock = Lock()
        
    def get_player(self, type):
        return self.players[type]
        
    def is_running(self):
        return self.running.value == 1

    def move(self, type, dir):
        self.lock.acquire()
        self.players[type].move(dir)
        self.lock.release()
        
    def stop(self):
        self.running.value = 0
        
    def get_info(self):
        info = {
            'pos_goalkeeper': self.players[0].get_pos(),
            'pos_shooter': self.players[1].get_pos(),
            'score': [0, 1],
            'is_running': self.is_running()
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
                if command != "quit":
                    game.move(type, command)
                else:
                    game.stop()
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