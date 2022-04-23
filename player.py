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

PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 25
PLAYER_WIDTH = 25

GOALKEEPER = 0
SHOOTER = 1
TYPE = ['goalkeeper', 'shooter']

class Player():
    def __init__(self, type):
        self.pos = [None, None]
        self.type = type
    
    def get_pos(self):
        return self.pos
    
    def get_type(self):
        return self.type
    
    def set_pos(self, pos):
        self.pos = pos
    
    def __str__(self):
        pass
    
class Ball(): # solo se mueve en linea recta
    def __init__(self):
        self.speed = None

class Game():
    def __init__(self):
        self.players = [Player(k) for k in range(2)]
        self.score = [0, 0]
        self.running = True

    def get_player(self, type):
        return self.players[type]

    def set_pos_player(self, type, pos):
        self.players[type].set_pos(pos)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def update(self, gameinfo):
        self.set_pos_player(GOALKEEPER, gameinfo['pos_goalkeeper'])
        self.set_pos_player(SHOOTER, gameinfo['pos_shooter'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def stop(self):
        self.running = False

    def __str__(self):
        pass

class Cube(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)
      self.player = player
      color = PLAYER_COLOR[self.player.get_type()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"

class Display():
    def __init__(self, game):
        self.game = game
        self.cube = [Cube(self.game.get_player(k)) for k in range(2)]
        
        self.cube_sprite = pygame.sprite.Group()
        for cube in self.cube:
            self.cube_sprite.add(cube)
                
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load('background.png')
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
    
    def refresh(self):
        self.cube_sprite.update()
        self.screen.blit(self.background, (0, 0))
        
        score = self.game.get_score()
        
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[GOALKEEPER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[SHOOTER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        
        self.cube_sprite.draw(self.screen)
        
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)
    
    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 11235), authkey=b'secret password') as conn:
            game = Game()
            type, gameinfo = conn.recv()
            print(f"I am playing {TYPE[type]}")
            game.update(gameinfo)
            
            display = Display(game)
            
            while game.running:
                events = display.analyze_events()
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                
                gameinfo = conn.recv()
                game.update(gameinfo)
                

                display.refresh()
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
