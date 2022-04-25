from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 700) #la imagen es de 700x700

FPS = 60

PLAYER_COLOR = [BLUE, YELLOW]
PLAYER_HEIGHT = 30
PLAYER_WIDTH = 30

BALL_SIZE = 20
BALL_COLOR = YELLOW

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

#lo voy a hacer como subclase de Player
class Ball(Player): # solo se mueve en linea recta
    def __init__(self):
        super().__init__(SHOOTER)
        #self.speed = None
        self.angle = None
        #self.pos = [None, None] ya lo hereda de Player(class)

    def set_angle(self, angle):
        self.angle = angle

    def get_angle(self):
        return self.angle

    def __str__(self):
        pass

class Game():
    def __init__(self):
        self.player = Player(GOALKEEPER)
        self.ball = Ball()
        self.score = [0, 0]
        self.running = True
        self.ball_moving = False

    def get_player(self, type):
        return self.player
    
    def get_ball(self):
        return self.ball

    def set_pos_player(self, pos):
        self.player.set_pos(pos)
    
    def set_pos_ball(self, pos):
        self.ball.set_pos(pos)
    
    def set_angle_ball(self, angle):
        self.ball.set_angle(angle)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def update(self, gameinfo):
        self.set_pos_player(gameinfo['pos_goalkeeper'])
        
        self.set_pos_ball(gameinfo['pos_shooter'])
        
        self.set_angle_ball(gameinfo['ball_angle'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
        self.ball_moving = gameinfo['ball_moving']

    def stop(self):
        self.running = False

    def __str__(self):
        pass

class Square(pygame.sprite.Sprite):
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

class Circle(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.image = pygame.Surface([BALL_SIZE, BALL_SIZE])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.ball = ball
        pygame.draw.circle(self.image, BALL_COLOR, [0,0], BALL_SIZE//2)
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.ball.get_pos()
        #print(pos)
        self.rect.centerx, self.rect.centery = pos
    
    def __str__(self):
        return f"S<{self.ball}>"

class Display():
    def __init__(self, game):
        self.game = game
        self.square = Square(self.game.get_player(GOALKEEPER))
        self.circle = Circle(self.game.ball)
        self.all_sprite = pygame.sprite.Group()
        
        self.all_sprite.add(self.square)
        self.all_sprite.add(self.circle)
        
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load('fondo.jpeg')
        pygame.init()

    def analyze_events(self, type):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
                elif event.key == pygame.K_SPACE and type == SHOOTER and not self.game.ball_moving:
                    events.append("shoot")
            elif event.type == pygame.QUIT:
                events.append("quit")
        return events

    def refresh(self):
        self.all_sprite.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[GOALKEEPER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[SHOOTER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprite.draw(self.screen)
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
                events = display.analyze_events(type)
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
