import pygame
from time import time
from settings import *
from random import uniform, randint
from math import sqrt
from utils import Collider


PARTICLES = []


class Physics:
    def __init__(self, x, y, mass=1, bounciness=0, frictional_coefficient=1):

        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        self.mass = mass
        self.bounciness = bounciness
        self.frictional_coefficient = frictional_coefficient
    
    def handle_controller(self):
        pass

    def apply_forces(self, dt):

        # mouvements 
        if hasattr(self, "controller"):
            self.handle_controller()

        # gravité
        self.acceleration += pygame.math.Vector2(0, GRAVITY)

        # frottements & friction de l'air
        
        total_friction = pygame.math.Vector2(0, 0)

        if self.collisions[2] and self.velocity.magnitude() != 0:
            total_friction += - 12 * self.collisions[2].frictional_coefficient * (self.acceleration.y / 100) * self.velocity.normalize()

        Cx = 0.5
        rho = 0.5
        if self.velocity.magnitude() != 0:
            total_friction += - 1 /2 * Cx * rho * sqrt(self.rect.width*self.rect.height) * (self.velocity.magnitude() / 100) ** 2 * self.velocity.normalize()

        if self.velocity.x * (self.velocity.x + (self.acceleration.x + total_friction.x) * dt) < 0:
            self.velocity.x = 0
        else:
            self.acceleration += total_friction

        """# friction de l'air
        if self.collisions[2]:
            if not "left" in self.controller.pressing and not "right" in self.controller.pressing:
                self.velocity.x *= 0.2 ** dt
            else:
                self.velocity.x *= 0.5 ** dt
            if abs(self.velocity.x) < 20 and abs(self.acceleration.x) < 5:
                self.velocity.x = 0
        else:
            self.velocity.x *= 0.9 ** dt"""

        self.acceleration *= RESIZE / 4
        
class Animation:
    def __init__(self, src, rects, delay, repeating=True, randomize=False, alternate=False, resize=1):
        
        self.img = pygame.image.load(src)
        self.img = pygame.transform.scale(self.img, (self.img.get_width() * RESIZE, self.img.get_height() * RESIZE))
        
        self.images = []
        self.reverse_images = []
        self.repeating = repeating
        self.alternate = alternate

        for rect in rects:
            img = self.img.subsurface(rect.x * RESIZE, rect.y * RESIZE, rect.width * RESIZE, rect.height * RESIZE)
            self.images.append(img)
            self.reverse_images.append(pygame.transform.flip(img, True, False))
        
        if randomize:
            self.start = time() + uniform(0, delay * len(self.images))
        else:
            self.start = time()
        self.delay = delay
    
    def image(self, reverse=False):
        index = int((time() - self.start) // self.delay)
        if index >= len(self.images) and not self.repeating:
            index = len(self.images) - 1
        if reverse:
            return self.reverse_images[index % len(self.images)]
        else:
            return self.images[index % len(self.images)]

    def reset(self):
        self.start = time()
        
class Controller:
    def __init__(self, keys={}):

        self.keys = keys

        self.pressed = []
        self.pressing = []
        self.released = []
    
    def update(self, dt):
        self.pressed.clear()
        self.released.clear()

        for key in self.keys.keys():
            if pygame.key.get_pressed()[key]:
                if self.keys[key] in self.pressing:
                    pass
                else:
                    self.pressed.append(self.keys[key])
                    self.pressing.append(self.keys[key])
            else:
                if self.keys[key] in self.pressing:
                    self.pressing.remove(self.keys[key])
                    self.released.append(self.keys[key])


class Entity(pygame.sprite.Sprite, Physics):
    def __init__(self, controller, img_src, animations, position, rect=None, mass=1):
        
        pygame.sprite.Sprite.__init__(self)

        self.controller = controller
        self.alive = True
        self.invicible_time = -1

        self.images = pygame.image.load(img_src)
        self.animation_state = 0
        self.animations = animations
        self.animation_lock = -1
        if animations:
            self.animation = list(animations.keys())[0]
        else:
            self.animation = 'none'
        self.reverse = False

        self.collisions = [ None, None, None, None ]  # top right bottom left
        Physics.__init__(self, position.x * RESIZE, position.y * RESIZE, mass)

        self.animate()

        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
        if type(rect) == pygame.Rect:
            rect.x *= RESIZE
            rect.y *= RESIZE
            rect.width *= RESIZE
            rect.height *= RESIZE
        else:
            for r in rect:
                r.x *= RESIZE
                r.y *= RESIZE
                r.width *= RESIZE
                r.height *= RESIZE
        
        self.collider = Collider(rect, self.position)

    """@property
    def collider(self):
        if self.reverse:
            # return pygame.Rect(self.position.x + (self.rect.width - self.collider_rect.x) - self.collider_rect.width - 1, self.position.y + self.collider_rect.y, self.collider_rect.width, self.collider_rect.height)
            return [pygame.Rect(self.position.x + self.collider_rect.x, self.position.y + self.collider_rect.y, self.collider_rect.width, self.collider_rect.height)]
        else:
            return [pygame.Rect(self.position.x + self.collider_rect.x, self.position.y + self.collider_rect.y, self.collider_rect.width, self.collider_rect.height)]
    """

    def update(self, camera, dt):
        if self.alive:
            self.acceleration *= 0

            self.controller.update(dt)
            self.check_alive()
            self.apply_forces(dt)
            self.animate()
            self.velocity += self.acceleration * dt
            
            self.rect.x = self.position.x - camera.x
            self.rect.y = self.position.y - camera.y

    def die(self):
        if self.alive:
            self.alive = False
            pygame.mixer.Sound("assets/sounds/effects/stomp.wav").play()
            self.acceleration *= 0
            self.velocity *= 0

        if hasattr(self, "health"):
            self.health = 0
    
    def check_alive(self):
        if self.rect.top > 180 * RESIZE:
            self.die()
    
    def animate(self):
        if self.animations:
            self.image = self.animations[self.animation].image(self.reverse)
    
    def reset_animation(self):
        if self.animations:
            self.animations[self.animation].start = time()

class Player(Entity):
    animations = {
        'idle': [pygame.Rect(4, 4, 17, 17), pygame.Rect(28, 4, 17, 17), pygame.Rect(52, 4, 17, 17), pygame.Rect(76, 4, 17, 17)],
        'walk': [pygame.Rect(76, 4, 17, 17),pygame.Rect(100, 4, 17, 16),pygame.Rect(124, 5, 17, 16),pygame.Rect(148, 4, 17, 17),pygame.Rect(172, 4, 17, 16),pygame.Rect(196, 5, 17, 16),pygame.Rect(220, 4, 17, 17)],
        'run': [17,18,19,20,21,22,23],
        'damage': [pygame.Rect(340, 3, 15, 18), pygame.Rect(362, 4, 15, 18), pygame.Rect(386, 4, 15, 17)]
    }

    def __init__(self, keys, pos=pygame.Vector2(50, 142), color='blue'):
        
        idle = Animation("assets/images/characters/" + color + ".png", Player.animations["idle"], 0.25, randomize=True)
        walk = Animation("assets/images/characters/" + color + ".png", Player.animations["walk"], 0.10)
        run = Animation("assets/images/characters/" + color + ".png", list(pygame.Rect((4+24*Player.animations["run"][i], 4, 20, 17)) for i in range(len(Player.animations["run"]))), 0.1)
        damage = Animation("assets/images/characters/" + color + ".png", Player.animations["damage"], 0.15, repeating=False)
        animations = {"idle": idle, "walk": walk, "run": run, "damage": damage}
        
        self.max_health = 5
        self.health = 5

        self.particles_delay = -1

        self.color = color

        rect = [pygame.Rect(4, 0, 8, 17)]
        super().__init__(Controller(keys), "assets/images/characters/" + color + ".png", animations, pos, rect=rect, mass=10)

    def update(self, camera, dt):
        
        if isinstance(self.collisions[2], Slime):
            self.collisions[2].die()
            self.velocity.y -= 100

        super().update(camera, dt)

    def animate(self):
        if not (self.animation == "damage" and time() - self.animations[self.animation].start < 0.6):
            if isinstance(self.collisions[2], Entity) and "right" not in self.controller.pressing and "left" not in self.controller.pressing:
                self.animation = 'idle'
            elif abs(self.velocity.x) > 5 * RESIZE:
                if "down" in self.controller.pressing and abs(self.velocity.x) > 25 * RESIZE:
                    self.animation = 'run'
                else:
                    self.animation = 'walk'
            else:
                self.animation = 'idle'
            if self.velocity.x < 0 and time() > self.animation_lock:
                self.reverse = True
            elif self.velocity.x > 0 and time() > self.animation_lock:
                self.reverse = False

        super().animate()

    def check_alive(self):
        Entity.check_alive(self)
    
    def damage(self):

        if time() > self.invicible_time:

            self.animation = "damage"
            self.reset_animation()
            self.velocity += pygame.Vector2(0, -75 * RESIZE)
            pygame.mixer.Sound("assets/sounds/effects/hit.wav").play()
            self.health -= 1

            self.invicible_time = time() + 0.5

            if self.health <= 0:
                
                self.die()
    
    def handle_controller(self):
        if "right" in self.controller.pressing:
            if self.collisions[2]:
                if "down" in self.controller.pressing:
                    if self.velocity.x < -100:
                        self.acceleration.x += PLAYER_SPEED * 3
                        
                    else:
                        self.acceleration.x += PLAYER_SPEED * 1.5
                else:
                    if self.velocity.x < -100:
                        self.acceleration.x += PLAYER_SPEED * 3
                    else:
                        self.acceleration.x += PLAYER_SPEED
            else:
                self.acceleration.x += PLAYER_SPEED / 3
        elif "left" in self.controller.pressing:
            if self.collisions[2]:
                if "down" in self.controller.pressing:
                    if self.velocity.x > 100:
                        self.acceleration.x += - PLAYER_SPEED * 3
                    else:
                        self.acceleration.x += - PLAYER_SPEED * 1.5
                else:
                    if self.velocity.x > 100:
                        self.acceleration.x += - PLAYER_SPEED * 3
                    else:
                        self.acceleration.x += - PLAYER_SPEED
            else:
                self.acceleration.x += - PLAYER_SPEED / 3

        if "up" in self.controller.pressed and self.collisions[2]:
            self.velocity.y = - GRAVITY / 2 * RESIZE / 4
            pygame.mixer.Sound("assets/sounds/effects/jump.wav").play()


class Slime(Entity):
    type = {
        'red_slime': (1,10,18,10),
        'blue_slime': (1,30,18,10),
        'green_slime': (1,50,18,10),
        'yellow_slime': (1,70,18,10)
    }
    animations = {
        'red_slime': {
            'left': [0,0,0,0,0,1,1,1,1,1],
            'right': [2,2,2,2,2,3,3,3,3,3]
        },
        'blue_slime': {
            'left': [0,0,0,0,0,1,1,1,1,1],
            'right': [2,2,2,2,2,3,3,3,3,3]
        },'green_slime': {
            'left': [0,0,0,0,0,1,1,1,1,1],
            'right': [2,2,2,2,2,3,3,3,3,3]
        },'yellow_slime': {
            'left': [0,0,0,0,0,1,1,1,1,1],
            'right': [2,2,2,2,2,3,3,3,3,3]
        }
    }
    def __init__(self, x, y, min_x=-999999, max_x=999999, type='red'):
        self.speed = 12.5 * RESIZE
        self.type = type + '_slime'
        idle = Animation("assets/images/enemies/enemies.png", list(pygame.Rect(Slime.type[self.type][0]+20*Slime.animations[self.type]["right"][i], Slime.type[self.type][1], Slime.type[self.type][2], Slime.type[self.type][3]) for i in range(len(Slime.animations[self.type]["right"]))), 0.05)
        animations = {"idle": idle}
        
        super().__init__(Controller(), "assets/images/enemies/enemies.png", animations, pygame.math.Vector2(x, y), pygame.Rect(0, 0, Slime.type[self.type][2], Slime.type[self.type][3]), 1)
        
        self.min_x = min_x * RESIZE
        self.max_x = max_x * RESIZE

        self.controller.pressing = ["left"]

    def update(self, camera, dt):
        if isinstance(self.collisions[1], Player):
            self.collisions[1].damage()
        if isinstance(self.collisions[3], Player):
            self.collisions[3].damage()

        if (self.collisions[3] or self.position.x < self.min_x) and "left" in self.controller.pressing:
            self.controller.pressing = ["right"]
        if (self.collisions[1] or self.position.x > self.max_x) and "right" in self.controller.pressing:
            self.controller.pressing = ["left"]

        super().update(camera, dt)

    def handle_controller(self):
        if "right" in self.controller.pressing:
            self.velocity.x = self.speed
        elif "left" in self.controller.pressing:
            self.velocity.x = - self.speed

    def animate(self):
        if not hasattr(self, "velocity"):
            super().animate()
            return
        if self.velocity.x > 0:
            self.reverse = False
        elif self.velocity.x < 0:
            self.reverse = True
        super().animate()


class Monkey(Entity):
    def __init__(self, x, y, min_x, max_x):
        
        idle = Animation("assets/images/enemies/monkey.png", [pygame.Rect(32*i, 0, 32, 32) for i in range(18)], 0.15, randomize=True)
        run = Animation("assets/images/enemies/monkey.png", [pygame.Rect(32*i, 32, 32, 32) for i in range(8)], 0.07)
        jump = Animation("assets/images/enemies/monkey.png", [pygame.Rect(32*i, 64, 32, 32) for i in range(4)], 0.3, repeating=False)
        damage = Animation("assets/images/enemies/monkey.png", [pygame.Rect(32*i, 96, 32, 32) for i in range(2)], 0.25, repeating=False)
        die = Animation("assets/images/enemies/monkey.png", [pygame.Rect(32*i, 128, 32, 32) for i in range(8)], 0.2, repeating=False)
        
        animations = { "idle": idle, "run": run,"jump": jump, "damage": damage, "die": die }
        
        self.max_health = 5
        self.health = 5

        self.next_jump = -1
        self.start_follow_x = -1
        self.start_follow_time = -1
        self.follow = None

        self.min_x = min_x
        self.max_x = max_x

        super().__init__(Controller(), "assets/images/enemies/enemies.png", animations, pygame.math.Vector2(x, y), [pygame.Rect(8, 3, 19, 29)], mass=25)
        

    def update(self, camera, dt):
        if isinstance(self.collisions[1], Player):
            self.collisions[1].damage()
        if isinstance(self.collisions[3], Player):
            self.collisions[3].damage()

        if self.animation != "jump":
            if self.next_jump != -1:
                if time() > self.next_jump:
                    self.velocity.y = -500
                    self.velocity.x = randint(-100, 100)
                    self.animation = "jump"
                    self.reset_move()
            else:
                self.next_jump = time() + uniform(2, 5)
            if not self.follow:
                self.rand_move()
            else:
                self.velocity.x = (self.follow - self.start_follow_x) / (self.next_jump - self.start_follow_time)


        super().update(camera, dt)

    def rand_move(self):

        self.follow = randint(self.min_x, self.max_x)
        self.start_follow_time = time()
        self.start_follow_x = self.position.x

    def reset_move(self):
        self.start_follow_x = -1
        self.start_follow_time = -1
        self.follow = None
        self.next_jump = -1

    def handle_controller(self):
        pass

    def damage(self):
        if self.health > 0:

            self.animation = "damage"
            self.animations["damage"].start = time()
            self.health -= 1

            if self.health <= 0:
                
                self.die()
                self.animation = "die"

    def animate(self):

        """if self.velocity.x > 0:
            self.reverse = False
        elif self.velocity.x < 0:
            self.reverse = True"""

        if not self.collisions[2] and self.animation != "jump":
            self.animation = "jump"
            self.animations["jump"].start = time()
        elif self.collisions[2]:
            if abs(self.velocity.x) > 1:
                self.animation = "run"
            else:
                self.animation = "idle"
        super().animate()

class Box(Entity):
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("assets/images/tilesets/plain-tileset.png").subsurface(((50%7)*16, (50//7)*16, 16, 16)), (TILE_SIZE * RESIZE, TILE_SIZE * RESIZE))
        super().__init__(Controller(), "assets/images/enemies/enemies.png", None, pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), mass=5)

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, type, moving=False):

        explosion = Animation("assets/images/particles/explosion/particles.png", [pygame.Rect(100 * i, 0, 100, 100) for i in range(56)], 0.03, repeating=False)
        fire_sparks = Animation("assets/images/particles/fire_sparks/particles.png", [pygame.Rect(96 * i, 0, 96, 96) for i in range(19)], 0.05)
        fire_top = Animation("assets/images/particles/fire_top/particles.png", [pygame.Rect(45 * i, 0, 45, 90) for i in range(14)], 0.1, repeating=False)
        gravity = Animation("assets/images/particles/gravity/particles.png", [pygame.Rect(96 * i, 0, 96, 80) for i in range(20)], 0.1, )
        leaves = Animation("assets/images/particles/leaves/particles.png", [pygame.Rect(150 * i, 0, 150, 150) for i in range(19)], 0.075, )
        poison_cloud = Animation("assets/images/particles/poison_cloud/particles.png", [pygame.Rect(144 * i, 0, 144, 144) for i in range(19)], 0.075, resize=0.75)
        smoke = Animation("assets/images/particles/smoke/particles.png", [pygame.Rect(0, 0, 16, 16), pygame.Rect(16, 0, 16, 16), pygame.Rect(32, 0, 16, 16), pygame.Rect(48, 0, 16, 16), pygame.Rect(0, 16, 16, 16), pygame.Rect(16, 16, 16, 16), pygame.Rect(32, 16, 16, 16), pygame.Rect(48, 16, 16, 16), pygame.Rect(0, 0, 1, 1)], 0.15, repeating=False)
        fire_smoke = Animation("assets/images/particles/smoke/particles.png", [pygame.Rect(0, 32, 16, 16), pygame.Rect(16, 32, 16, 16), pygame.Rect(32, 32, 16, 16), pygame.Rect(48, 32, 16, 16), pygame.Rect(0, 48, 16, 16), pygame.Rect(16, 48, 16, 16), pygame.Rect(32, 48, 16, 16), pygame.Rect(48, 48, 16, 16), pygame.Rect(0, 0, 1, 1)], 0.15, repeating=False)

        animations = { 'smoke': smoke, 'explosion': explosion, 'fire_smoke': fire_smoke, 
                       'fire_sparks': fire_sparks, 'fire_top': fire_top, 'gravity': gravity,
                        'leaves': leaves, 'poison_cloud': poison_cloud }
        
        self.animations = animations
        self.animation = type
        self.reverse = False
        self.moving = moving

        super().__init__()
        self.animate()

        self.rect = pygame.Rect(x - self.image.get_width() // 2, y - self.image.get_height() // 2, self.image.get_width(), self.image.get_height())
        self.position = pygame.Vector2(x, y)


    
    def animate(self):
        self.image = self.animations[self.animation].image(self.reverse)
    
    def update(self, camera, dt):

        self.animate()

        if self.moving:

            self.position += pygame.Vector2(uniform(-50, 50), - uniform(25, 50)) * dt
        
        self.rect = pygame.Rect(self.position.x - camera.x, self.position.y  - camera.y, 16, 16)
