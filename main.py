import pygame
from time import time
from world import *
from entities import *
from menu import *
import world
import sys


# setup
pygame.init()
clock = pygame.time.Clock()

# game

class Game:

    def __init__(self, screen):
        self.scenes = {
            "main": Menu(),
            "world": World()
        }
        self.scene = self.scenes["main"]
        self.scene.in_anim.start = time()

        world.init(self.scenes["world"])

        self.screen = screen

        self.closing_request = False

    def paint(self):

        self.scene.paint(self.screen)

    def update(self, dt):

        if self.scene.request and (not self.scene.out_anim or (time() - self.scene.out_anim.start >= self.scene.out_anim.delay + DELAY_BETWEEN_SCENE - 0.05)):
            self.change_scene(self.scene.request)
        
        if self.closing_request and self.scene.out_anim.finished:
            pygame.quit()
            sys.exit()

        self.scene.update(dt)

    def handle_events(self, events):
        self.scene.handle_events(events)

    def close(self):
        self.closing_request = True
        self.scene.out_anim.delay = 1
        self.scene.out_anim.start = time()

    def change_scene(self, scene):

        self.scene.request = None

        self.scene = self.scenes[scene]

        self.scene.load()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jeu test")
if MUSIC_ENABLED:
    pygame.mixer.Sound("assets/sounds/level_music.wav").play()

game = Game(screen)

last_tick = time()

while True:

    dt = time() - last_tick
    last_tick = time()

    events = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            game.close()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                DEBUG = not DEBUG
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if DEBUG and pygame.key.get_pressed()[pygame.K_LALT]:
                main_camera = game.scenes['world'].main_camera
                print(main_camera.x + pygame.mouse.get_pos()[0], main_camera.y + pygame.mouse.get_pos()[1])
            else:
                pos = pygame.mouse.get_pos()
                events.append((event.button, pygame.math.Vector2(pos[0], pos[1])))
    
    if dt > 0.3:
        continue

    game.handle_events(events)
    game.update(dt)

    game.paint()

    clock.tick(TPS)
