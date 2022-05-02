from multiprocessing.connection import Client
import pygame

from config import *

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


class Ball(Player):
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

    def stop(self):
        self.running = False

    def __str__(self):
        pass

class Square(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(BLACK)
        self.player = player
        self.image = pygame.transform.scale(pygame.image.load('gloves-square.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))

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
        self.image = pygame.transform.scale(pygame.image.load('football-ball.png'), (BALL_SIZE, BALL_SIZE))
        self.ball = ball
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
        self.image = pygame.Surface([BALL_SIZE, 4*BALL_SIZE])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.ball = ball
        pygame.draw.polygon(self.image, RED, points = [(BALL_SIZE//2, 0), (0, BALL_SIZE), (BALL_SIZE, BALL_SIZE)])
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.ball.get_pos()
        self.update()

    def update(self):
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
        self.line_red = Line(3*SIZE[0]/5, 10, RED, [SIZE[0]/2, SIZE[1]/5])
        self.end_line = Line(SIZE[0], 5, WHITE, [SIZE[0]/2, SIZE[1]/5 - 10])

        self.all_sprites = pygame.sprite.Group()
        self.fixed_sprites = pygame.sprite.Group()
        self.arrow_group = pygame.sprite.Group()
        
        self.all_sprites.add(self.square)
        self.all_sprites.add(self.circle)
        self.fixed_sprites.add(self.end_line)
        self.fixed_sprites.add(self.line_red)

        self.add_arrow()

        self.screen = pygame.display.set_mode(SIZE)
        
        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(pygame.image.load('field_background.jpeg'), tuple(SIZE))
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
        if pressed[pygame.K_LEFT]:
            events.append("left")
        if pressed[pygame.K_RIGHT]:
            events.append("right")
        if pressed[pygame.K_SPACE] and type == SHOOTER and not self.game.ball_moving:
            events.append("shoot")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append("quit")

        if self.collision(type, [self.square]):
            events.append("catch")
        elif self.collision(type, [self.end_line]):
            events.append("out")
        elif self.collision(type, [self.line_red]):
            events.append("goal")
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()

        score_font = pygame.font.Font(None, 50)
        score_text = score_font.render(f"{score[GOALKEEPER]}  -  {score[SHOOTER]}", 1, WHITE)
        score_text_rect = score_text.get_rect(center=(SIZE[0]/2, SIZE[1]/10))
        self.screen.blit(score_text, score_text_rect)

        gk_font = pygame.font.Font(None, 50)
        gk_text = gk_font.render("GOALKEEPER", 1, WHITE)
        gk_text_rect = gk_text.get_rect(center=(SIZE[0]/4, SIZE[1]/10))
        self.screen.blit(gk_text, gk_text_rect)

        shooter_font = pygame.font.Font(None, 50)
        shooter_text = shooter_font.render("SHOOTER", 1, WHITE)
        shooter_text_rect = shooter_text.get_rect(center=(3*SIZE[0]/4, SIZE[1]/10))
        self.screen.blit(shooter_text, shooter_text_rect)

        self.all_sprites.draw(self.screen)

        if not self.game.ball_moving:
            self.arrow_group.update()
            self.arrow_group.draw(self.screen)

        self.fixed_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    def add_arrow(self):
        if self.type == SHOOTER:     # Se muestra la flecha unicamente si el jugador es el que dispara
            self.arrow = Arrow(self.game.get_ball())
            self.arrow_group.add(self.arrow)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address, port):
    try:
        with Client((ip_address, port), authkey=b'secret password') as conn:
            game = Game()
            type, gameinfo = conn.recv()
            print(f"I am playing {TYPES[type]}")
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
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        ip_address = "147.96.81.245"  #ip por defecto de simba
        port = 11239                #puerto por defecto
        print(f"Cargando {sys.argv[0]} {ip_address} {port}")
    elif len(sys.argv) == 2:
        ip_address = sys.argv[1]
    elif len(sys.argv) == 3:
        ip_address = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print(f"Uso: {sys.argv[0]} <ip_address> <port>")
        exit(1)
    main(ip_address, port)
