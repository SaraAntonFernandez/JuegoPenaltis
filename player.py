from multiprocessing.connection import Client
import traceback
import pygame
import sys, os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

FPS = 60

GOALKEEPER = 0
SHOOTER = 1

class Player():
    def __init__(self, tipo):
        self.size = size
        self.pos = None # Una se fija
        self.tipo = tipo
    
class Ball(): # solo se mueve en linea recta
    def __init__(self):
        self.speed = None

#class Game():
    


class Display():
    def __init__():
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load('fondo.jpeg')
        pygame.init()

    def analyze_events(self):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
            elif event.type == pygame.QUIT:
                events.append("quit")
        return events

    def tick(self):
        self.clock.tick(FPS)
    
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 11235), authkey=b'secret password') as conn:

            #side,gameinfo = conn.recv()

            print("I am playing")

            display = Display()
            while True:
                events = display.analyze_events()
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                
                message = conn.recv()
                print(f'Printing message: {message})
                
                #game.update(gameinfo)
                #display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
