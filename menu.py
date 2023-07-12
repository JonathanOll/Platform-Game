from scene import *
import pygame
from settings import *
from entities import Animation

class Menu(Scene):
    def __init__(self):
        self.buttons_img = pygame.image.load("assets/images/menus/main.png")
        self.buttons_img = pygame.transform.scale(self.buttons_img, (self.buttons_img.get_width()*RESIZE, self.buttons_img.get_height()*RESIZE))

        self.buttons = {
            "play": pygame.Rect(130*RESIZE, 71*RESIZE, 60*RESIZE, 28*RESIZE),
            "options": pygame.Rect(130*RESIZE, 103*RESIZE, 60*RESIZE, 28*RESIZE),
            "exit": pygame.Rect(130*RESIZE, 135*RESIZE, 60*RESIZE, 28*RESIZE)
        }

        self.planet = Animation("assets/images/planet.png", [pygame.Rect(180*i, 0, 180, 180) for i in range(50)], 0.1, randomize=True)

        super().__init__(Rectangle(reverse=True), GridSpiral())

    def paint(self, screen, camera=None):

        screen.fill((0, 30, 101))

        # screen.blit(self.background, (0, 0))

        planet = self.planet.image()

        screen.blit(planet, (screen_width // 2 - planet.get_rect().width // 2, screen_height // 2 - planet.get_rect().height // 2))

        screen.blit(self.buttons_img, (0, 0))

        super().paint(screen)

    def update(self, dt):
        pass
    
    def click(self, button):
        if button == "play":
            self.request_scene_change("world")
        elif button == "options":
            pass
        elif button == "exit":
            self.request_scene_change("exit")

    def handle_events(self, events):
        for click, pos in events:
            if click != 1: continue
            for button, rect in self.buttons.items():
                if rect.collidepoint(pos):
                    self.click(button)
