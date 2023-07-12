from pygame import Rect
from pygame.math import Vector2


class Collider:
    def __init__(self, rects, position=Vector2(0, 0)):
        if type(rects) == list:
            self.rects = rects
        else:
            self.rects = [rects]

        self.minx = min(rect.x for rect in self.rects)
        self.miny = min(rect.y for rect in self.rects)

        self.width = max(rect.x + rect.width for rect in self.rects) - self.minx
        self.height = max(rect.y + rect.height for rect in self.rects) - self.miny
        
        self.position = position
    
    def collides(self, other):
        
        rects = self.copy_to_pos()
        rects2 = other.copy_to_pos()

        for rect in rects:
            for rect2 in rects2:
                if rect.colliderect(rect2):
                    return True
                
        return False

    def collidespoint(self, point):

        rects = self.copy_to_pos()

        for rect in rects:
            if rect.collidepoint(point): return True

        return False
    
    def copy(self):
        return [rect.copy() for rect in self.rects]
    
    def copy_to_pos(self):
        
        rects = self.copy()
        for rect in rects:
            rect.center += self.position
            
        return rects
    
    @property
    def top(self):
        if self.position:
            return self.position.y + self.miny

    @property
    def bottom(self):
        if self.position:
            return self.position.y + self.height + self.miny
    
    @property
    def left(self):
        if self.position:
            return self.position.x + self.minx

    @property
    def right(self):
        if self.position:
            return self.position.x + self.width + self.minx
    
    @property
    def horizontal_center(self):
        if self.position:
            return (self.left + self.right) / 2
    
    @property
    def under(self):
        lower_rect = self.rects[0]
        for i in range(1, len(self.rects)):
            if self.rects[i].bottom < lower_rect.bottom:
                lower_rect = self.rects[i]
        if self.position:
            return Rect(self.position.x + lower_rect.x, self.position.y + lower_rect.bottom + 1, lower_rect.width, 1)
        else:
            return Rect(lower_rect.x, lower_rect.y + 1, lower_rect.width, 1)

    @top.setter
    def top(self, value):
        self.position.y = value - self.miny

    @bottom.setter
    def bottom(self, value):
        self.position.y = value - self.height - self.miny
    
    @left.setter
    def left(self, value):
        self.position.x = value - self.minx
    
    @right.setter
    def right(self, value):
        self.position.x = value - self.width - self.minx
    

def collides(rects1, rects2):
    if type(rects1) == Rect:
        if type(rects2) == Rect:
            return rects1.colliderect(rects2)
        else:
            return any(rect.colliderect(rects1) for rect in rects2)
    else:
        if type(rects2) == Rect:
            any(rect.colliderect(rects2) for rect in rects1)
        else:
            return any(rect.colliderect(rect2) for rect in rects1 for rect2 in rects2)