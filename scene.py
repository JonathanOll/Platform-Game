import pygame
from time import time
from settings import *
from random import shuffle

class SceneTransition:
    def __init__(self, color=(0, 0, 0), delay=1, reverse=False):
        self.start = -1
        self.delay = delay
        self.reverse = reverse
        self.color = color

    def draw(self, screen):
        pass

    @property
    def finished(self):
        return time() - self.start > self.delay


class Rectangle(SceneTransition):
    def __init__(self, color=(0, 0, 0), delay=2.5, reverse=False):
        super().__init__(delay, reverse)

    def draw(self, screen):
        
        t = min(1, (time() - self.start) / self.delay)
        
        if self.reverse:
            t = 1 - (time() - self.start) / self.delay

        pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_width, screen_height * (1 / 2 - t)))
        
        pygame.draw.rect(screen, (0, 0, 0), (0, 1 + screen_height - screen_height * (1 / 2 - t) , screen_width, screen_height * (1 / 2 - t)))
    
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_width * (1 / 2 - t), screen_height))
        
        pygame.draw.rect(screen, (0, 0, 0), (1 + screen_width - screen_width * (1 / 2 - t), 0, screen_width * (1 / 2 - t), screen_width))
        
class Comb(SceneTransition):
    def __init__(self, color=(0, 0, 0), comb_count=6, delay=1, reverse=False):
        
        self.comb_count = comb_count
        super().__init__(color, delay, reverse)

    def draw(self, screen):

        t = min(1, (time() - self.start) / self.delay)
        
        if self.reverse:
            t = 1 - (time() - self.start) / self.delay

        comb_height = screen_height / self.comb_count
        if int(comb_height) != comb_height: comb_height += 1

        for i in range(self.comb_count):
            
            if i % 2 == 0:
                
                pygame.draw.rect(screen, (0, 0, 0), (0, i * comb_height, screen_width * t, comb_height))

            else:

                pygame.draw.rect(screen, (0, 0, 0), (screen_width * (1 - t), i * comb_height, 1 + screen_width * t, comb_height))

class Grid(SceneTransition):
    def __init__(self, color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False, order=None):
        
        self.cell_per_row = cell_per_row
        self.cell_size = round(screen_width / cell_per_row) + 1
        self.cell_per_column = round(screen_height / self.cell_size) + 1

        if order:
            self.order = order
        else:
            self.order = list(range(self.cell_per_row * self.cell_per_column))
            shuffle(self.order)
        
        super().__init__(color, delay, reverse)
    
    def draw(self, screen):
        
        t = min(1, (time() - self.start) / self.delay)
        
        if self.reverse:
            t = 1 - (time() - self.start) / self.delay

        for i in self.order[:int(t * self.cell_per_row * self.cell_per_column)]:
            x = i % self.cell_per_row
            y = i // self.cell_per_row
            
            pygame.draw.rect(screen, (0, 0, 0), (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

class GridNoShuffle(Grid):
    def __init__(self, color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False, order=None):
        
        super().__init__(color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False, order=None)

        self.order = list(range(self.cell_per_column * self.cell_per_row))

class GridSpiral(Grid):
    def __init__(self, color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False, order=None):
        
        super().__init__(color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False, order=None)

        self.order = [19, 20, 21, 13, 12, 11, 10, 18, 26, 27, 28, 29, 30, 22, 14, 6, 5, 4, 3, 2, 1, 9, 17, 25, 33, 34, 35, 36, 37, 38, 39, 31, 23, 15, 7, 0, 8, 16, 24, 32]

class GridGrow(Grid):
    def __init__(self, color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False):
        
        super().__init__(color=(0, 0, 0), cell_per_row=8, delay=1.5, reverse=False, order=None)

    def draw(self, screen):
        
        t = min(1, (time() - self.start) / self.delay)
        
        if self.reverse:
            t = 1 - (time() - self.start) / self.delay

        size = self.cell_size * t

        for i in range(self.cell_per_row * self.cell_per_column):
            x = i % self.cell_per_row
            y = i // self.cell_per_row
            
            pygame.draw.rect(screen, (0, 0, 0), ((x + 0.5) * self.cell_size - size // 2, (y + 0.5) * self.cell_size - size // 2, size, size))
    
class Fade(SceneTransition):
    def __init__(self, color=(0, 0, 0), delay=1, reverse=False):
        
        super().__init__(color, delay, reverse)

    def draw(self, screen):
        
        t = min(1, (time() - self.start) / self.delay)
        
        if self.reverse:
            t = 1 - (time() - self.start) / self.delay

        s = pygame.Surface((screen_width, screen_height))
        s.set_alpha(255 * t)
        s.fill(self.color)
        screen.blit(s, (0, 0))

class Scene:
    def __init__(self, in_anim=None, out_anim=None):
        self.request = None

        self.in_anim = in_anim
        self.out_anim = out_anim

    def paint(self, screen, camera=None):

        if self.in_anim and time() - self.in_anim.start < self.in_anim.delay :
            self.in_anim.draw(screen)
        
        if self.out_anim and time() - self.out_anim.start < self.out_anim.delay + DELAY_BETWEEN_SCENE:
            self.out_anim.draw(screen)

        pygame.display.flip()
    
    def update(self, dt):
        pass

    def handle_events(self, events):
        pass

    def load(self):
        if self.in_anim:
            self.in_anim.start = time()
            self.out_anim.start = -1

    def request_scene_change(self, scene):
        if self.out_anim:
            self.out_anim.start = time()
        self.request = scene
