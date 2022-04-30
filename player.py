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
        self.angle = None

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
        self.round_state = True

    def get_player(self):
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
        self.round_state = gameinfo['round_state']

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

class Line(pygame.sprite.Sprite):
    def __init__(self, width, height, color, pos):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos

class Circle(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.image = pygame.Surface([BALL_SIZE, BALL_SIZE])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.ball = ball
        pygame.draw.circle(self.image, BALL_COLOR, [BALL_SIZE//2, BALL_SIZE//2], BALL_SIZE//2)
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos
    
    def __str__(self):
        return f"S<{self.ball}>"

class Arrow(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.image = pygame.Surface([BALL_SIZE, 3*BALL_SIZE])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.ball = ball
        pygame.draw.polygon(self.image, RED, points = [(BALL_SIZE//2, 0), (BALL_SIZE//4, BALL_SIZE//2), (3*BALL_SIZE//4, BALL_SIZE//2)]) # Comprobar
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.ball.get_pos()
        self.update()

    def update(self):
        # angle = self.angle - self.ball.get_angle()
        angle = self.ball.get_angle()
        self.image = pygame.transform.rotate(self.orig_image, 180*angle/math.pi - 90)
        self.rect = self.image.get_rect(center=self.ball.get_pos())
    
    def __str__(self):
        return f"S<{self.ball}>"

class Display():
    def __init__(self, game, type):
        self.game = game
        self.type = type
        self.square = Square(self.game.get_player())
        self.circle = Circle(self.game.get_ball())
        self.line_red = Line(400, 10, RED, [SIZE[0]/2, SIZE[1]/2 - 260])   # LINEAS DEL CAMPO
        self.lineR = Line(10, 1220, WHITE, [0, SIZE[1]])
        self.lineL = Line(10, 1220, WHITE, [SIZE[0], SIZE[1]])
        self.lineUR = Line(300, 5, WHITE, [0, SIZE[1]/2 - 260])
        self.lineUL = Line(300, 5, WHITE, [SIZE[0], SIZE[1]/2 - 260])
        self.all_sprites = pygame.sprite.Group()
        self.fixed_sprites = pygame.sprite.Group()
        
        self.all_sprites.add(self.square)
        self.all_sprites.add(self.circle)
        self.fixed_sprites.add(self.lineR)
        self.fixed_sprites.add(self.lineL)
        self.fixed_sprites.add(self.lineUR)
        self.fixed_sprites.add(self.lineUL)
        self.fixed_sprites.add(self.line_red)

        self.add_arrow()

        self.screen = pygame.display.set_mode(SIZE)
        
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load('field_background2.jpeg')
        pygame.init()
        
    def collision(self, type, object):
        r = type == SHOOTER and self.game.ball_moving
        p = False
        for k in object:
            p = p or pygame.sprite.collide_rect(self.circle, k)
        return r and p

    def analyze_events(self, type):
        events = []

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT] and self.game.round_state:
            events.append("left")
        if pressed[pygame.K_RIGHT] and self.game.round_state:
            events.append("right")
        if pressed[pygame.K_SPACE] and type == SHOOTER and not self.game.ball_moving and self.game.round_state:
            self.arrow.kill()       # Hace desaparecer la flecha al disparar
            events.append("shoot")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append("quit")

        if self.collision(type, [self.square]):
            events.append("catch")
        elif self.collision(type, [self.lineUL, self.lineUR]):
            events.append("out")
        elif self.collision(type, [self.line_red]):
            events.append("goal")
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[GOALKEEPER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[SHOOTER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprites.draw(self.screen)
        self.fixed_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    def add_arrow(self):
        if self.type == SHOOTER:     # Se muestra la flecha unicamente si el jugador es el que dispara
            print("hola")
            self.arrow = Arrow(self.game.get_ball())
            self.all_sprites.add(self.arrow)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 11239), authkey=b'secret password') as conn:
            game = Game()
            type, gameinfo = conn.recv()
            print(f"I am playing {TYPE[type]}")
            game.update(gameinfo)
            display = Display(game, type)
            while game.running:
                events = display.analyze_events(type)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                print(game.round_state)
                if not game.round_state:
                    display.add_arrow()
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
