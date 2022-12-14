from random import choice
from random import randint as rnd
import pygame
import math

pygame.font.init()
FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
ORANGE = (255, 128, 0)
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball
        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        r - радиус мяча
        color - цвет мяча
        vx - начальная скорость мяча по горизонтали
        vy - начальная скорость мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.stopped = False

    def move(self):
        """Переместить мяч по прошествии единицы времени.
        Метод описывает перемещение мяча за один кадр перерисовки.
        То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy,
        силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vy -= 1
        self.x += self.vx
        self.y -= self.vy

        if self.y+self.r*2 >= 600:
            self.vx = int(self.vx/1.4)
            self.vy = -int(self.vy/1.4)
        if self.y-self.r <= 0:
            self.vy = -self.vy
        if self.x-self.r <= 0 or self.x+self.r >= 800:
            self.vx = -self.vx
        if abs(self.vx) == 0 and abs(self.vx) == 0 and (self.y+self.r) >= 590:
            self.vy += 1

    def draw(self):
        ''' рисует шарик '''
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью,
        описываемой в обьекте obj.
        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели.
            В противном случае возвращает False.
        """
        x = self.x - obj.x
        y = self.y - obj.y
        if (x ** 2 + y ** 2) ** 0.5 <= self.r + obj.r:
            return True
        else:
            return False


class Gun:
    def __init__(self, screen):
        '''
        Конструктор класса gun
        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        f2_power - сила выстрела
        '''
        self.x = 20
        self.y = 450
        self.screen = screen
        self.f2_power = 10
        self.f2_on = False
        self.an = 0
        self.color = BLACK

    def fire2_start(self, event):
        self.f2_on = True

    def fire2_end(self, event):
        """Выстрел мячом.
        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy
        зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        new_ball.r += 5
        pos_x = event.pos[0]-new_ball.x
        pos_y = event.pos[1]-new_ball.y
        self.an = math.atan2(pos_y, pos_x)
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan((event.pos[1]-450) / (event.pos[0]-20))
        if self.f2_on:
            self.color = ORANGE
        else:
            self.color = BLACK

    def draw(self):
        '''рисует пушку'''
        pygame.draw.line(
            self.screen,
            self.color,
            (self.x, self.y),
            (self.x + max(self.f2_power, 20) * math.cos(self.an),
             self.y + max(self.f2_power, 20) * math.sin(self.an)),
            8
            )

    def power_up(self):
        '''увеличивает силу выстрела, до крит значения'''
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = ORANGE
        else:
            self.color = BLACK


class Target:
    def __init__(self, screen, points=0):
        '''
        Конструктор класса target
        Args:
        live - количество жизней у цели
        '''
        self.screen = screen
        self.points = points
        self.live = 1
        self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        self.x = rnd(600, 780)
        self.y = rnd(300, 550)
        self.r = rnd(2, 50)
        self.vx = rnd(-10, 10)
        self.vy = rnd(-10, 10)
        self.live = 1
        self.color = RED

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        '''рисует цель'''
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def move(self):
        """Переместить цель по прошествии единицы времени.
        Метод описывает перемещение цели за один кадр перерисовки.
        То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy,
        с учетом стен по краям окна (размер окна 800х600).
        """
        self.x += self.vx
        self.y += self.vy
        if self.y+self.r*2 >= 589:
            self.vx = self.vx
            self.vy = -self.vy
        if self.y-self.r <= 0:
            self.vy = -self.vy
        if self.x-self.r <= 0 or self.x+self.r >= 800:
            self.vx = -self.vx


class Strange_Target(Target):
    def move(self):
        """Переместить странную цель по прошествии единицы времени.
        Метод описывает перемещение странной цели за один кадр перерисовки.
        То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy,
        с учетом стен по краям окна (размер окна 800х600),
        меняет рандомно скорость мяча за один кадр
        """
        self.x += self.vx
        self.y += self.vy
        self.vx = rnd(-30, +30)
        self.vy = rnd(-30, +30)
        if self.y+self.r*2 >= 589:
            self.x = rnd(100, 700)
            self.y = rnd(100, 500)
        if self.y-self.r <= 0:
            self.x = rnd(100, 700)
            self.y = rnd(100, 500)
        if self.x-self.r <= 0 or self.x+self.r >= 800:
            self.x = rnd(100, 700)
            self.y = rnd(100, 500)

    def draw(self):
        ''' рисует странный шарик '''
        pygame.draw.circle(
            self.screen,
            BLACK,
            (self.x, self.y),
            self.r
        )
        pygame.draw.circle(
            self.screen,
            WHITE,
            (self.x, self.y),
            self.r/2
        )

    def hit(self, points=5):
        """Попадание шарика в цель"""
        self.points += points


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []
target = Target(screen)
clock = pygame.time.Clock()
gun = Gun(screen)
strange_target = Strange_Target(screen)
finished = False

f = pygame.font.Font(None, 24)

while not finished:
    screen.fill(WHITE)
    gun.draw()
    target.draw()
    target.move()
    strange_target.draw()
    strange_target.move()
    for b in balls:
        b.draw()
    text1 = str(target.points+strange_target.points) + ' ' + str(bullet)
    text = f.render(text1, True, BLACK)
    screen.blit(text, (10, 10))
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    for b in balls:
        b.move()
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit()
            target.new_target()
        if b.hittest(strange_target) and strange_target.live:
            strange_target.live = 0
            strange_target.hit()
            strange_target.new_target()
    gun.power_up()

pygame.quit()