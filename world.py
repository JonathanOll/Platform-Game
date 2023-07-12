import pygame
from entities import *
from settings import *
from utils import Collider
from scene import *

class Camera:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.following = None
    
    def paint_ui(self, screen, players):
        for a in range(len(players)):
            
            player = players[a]

            scale = 4
            
            img = pygame.image.load('assets/images/characters/ui/background.png')
            img = pygame.transform.scale(img, (img.get_width()*scale, img.get_height()*scale))
            
            icon = pygame.image.load('assets/images/characters/' + players[a].color + '_icon.png')
            icon = pygame.transform.scale(icon, (icon.get_width()*scale, icon.get_height()*scale))
            
            img_x = round(player.health / player.max_health * 49)

            healthbar = pygame.image.load('assets/images/characters/ui/healthbar.png').subsurface((49 - img_x, 0, img_x, 3))
            healthbar = pygame.transform.scale(healthbar, (healthbar.get_width()*scale, healthbar.get_height()*scale))

            x = int(screen_width / 2 - img.get_width()/2 - ((img.get_width()+30) * (len(players) - 1) / 2) + a * ((img.get_width()+30) * len(players) / 2))
            
            screen.blit(img, (x, 10))
            screen.blit(icon, (x + 20, 40))

            if time() < player.invicible_time:
                img_x = round((player.health) / player.max_health * 49)
                
                img_x += round(49 / player.max_health * (player.invicible_time - time()) * 2)
                healthbar_back = pygame.image.load('assets/images/characters/ui/healthbar_back.png').subsurface((49 - img_x, 0, img_x, 3))
                healthbar_back = pygame.transform.scale(healthbar_back, (healthbar_back.get_width()*scale, healthbar_back.get_height()*scale))
                
                screen.blit(healthbar_back, (x + 26 * scale, 10 + 3 * scale))

            screen.blit(healthbar, (x + 26 * scale, 10 + 3 * scale))

            


    def paint_debug(self, screen, *args):
        for arg in args:
            for element in arg.sprites():
                if not hasattr(element, "collider"):
                    break
                for rect in element.collider.copy_to_pos():
                    rect.center -= pygame.math.Vector2(self.x, self.y)
                    pygame.draw.rect(screen, (255, 0, 0), rect, width=2)

                # pygame.draw.rect(screen, (0, 255, 0), element.rect, width=2)

    def paint(self, screen, *args, players=None):
        screen.fill('black')
        for group in args:
            group.draw(screen)
        self.paint_ui(screen, players)
        if DEBUG:
            self.paint_debug(screen, *args)
    
    def update(self, dt):
        radius = 125 * RESIZE / 4
        x = self.following.position.x - screen_width / 2 - self.x
        if x > radius:
            self.x += x - radius
        elif x < - radius:
            self.x += x + radius
        if self.x < 0:
            self.x = 0
            return

class Background(pygame.sprite.Sprite):
    def __init__(self, src, x, y, offset):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(src), (screen_width, screen_height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.offset = offset
        self.x = x
    
    def update(self, camera):
        self.rect.x = self.x - (camera.x // self.offset % (320 * RESIZE))



class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, type, collectable=False, bounciness=0, frictional_coefficient=1):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("assets/images/tilesets/plain-tileset.png").subsurface(((type%7)*16, (type//7)*16, 16, 16)), (TILE_SIZE * RESIZE, TILE_SIZE * RESIZE))
        self.rect = self.image.get_rect(topleft=pygame.math.Vector2(x*TILE_SIZE*RESIZE, y*TILE_SIZE*RESIZE))
        self.position = pygame.math.Vector2(x*TILE_SIZE*RESIZE, y*TILE_SIZE*RESIZE)
        self.collider = Collider(pygame.Rect(0, 0, TILE_SIZE*RESIZE, TILE_SIZE*RESIZE), self.position)
        self.collectable = collectable
        self.bounciness = bounciness
        self.frictional_coefficient = frictional_coefficient

    def update(self, camera):
        self.rect.x = self.position.x - camera.x

class World(Scene):
    def __init__(self):
        self.entities = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        self.players = []
        
        self.collisions = []
        self.cameras = []

        self.main_camera = None

        super().__init__(Grid(reverse=True), Comb())

    def setup_background(self):
        self.background.add(Background("assets/images/back.png", 0, 0, 5))
        self.background.add(Background("assets/images/back.png", 320*RESIZE, 0, 5))
        self.background.add(Background("assets/images/middle.png", 0, 0, 3))
        self.background.add(Background("assets/images/middle.png", 320*RESIZE, 0, 3))
        self.background.add(Background("assets/images/near.png", 0, 0, 1.5))
        self.background.add(Background("assets/images/near.png", 320*RESIZE, 0, 1.5))
        for b in self.background.sprites():
            b.image = b.image.convert_alpha()

    def update(self, dt):

        super().update(dt)
        
        self.tiles.update(self.main_camera)

        self.entities.update(self.main_camera, dt)
        for entity in self.entities:
            if not entity.alive:
                self.entities.remove(entity)

        while len(PARTICLES) > 0:
            self.particles.add(PARTICLES.pop())

        self.background.update(self.main_camera)
        self.handle_collisions(dt)
        for camera in self.cameras:
            camera.update(dt)

        self.particles.update(self.main_camera, dt)
        for particle in self.particles:
            if not particle.animations[particle.animation].repeating and (time() - particle.animations[particle.animation].start) / particle.animations[particle.animation].delay >= len(particle.animations[particle.animation].images):
                self.particles.remove(particle)
                del particle
        

        for i in range(len(self.players)):
            if not self.main_camera.following.alive or (self.players[i].alive and self.players[i].position.x > self.main_camera.following.position.x):
                self.main_camera.following = self.players[i]

    def handle_collisions(self, dt):
        for entity in self.entities.sprites():

            if not entity.alive: continue

            entity.collisions = [ None, None, None, None ]

            entity.position.x += entity.velocity.x * dt

            for tile in self.collisions:
                if tile == entity or (isinstance(tile, Entity) and not tile.alive): continue
                if tile.collider.collides(entity.collider):
                    if entity.velocity.x > 0:
                        entity.collider.right = tile.collider.left
                        entity.collisions[1] = tile
                    else:
                        entity.collider.left = tile.collider.right
                        entity.collisions[3] = tile
                    
                    if isinstance(tile, Physics) and abs(entity.velocity.x) > 25 * RESIZE:
                        # choc élastique
                        v = entity.velocity.x - tile.velocity.x
                        entity.velocity.x = - tile.mass / (entity.mass + tile.mass) * v
                        tile.velocity.x = entity.mass / (entity.mass + tile.mass) * v
                        entity.animation_lock = time() + 0.75
                        tile.animation_lock = time() + 0.75
                        pygame.mixer.Sound("assets/sounds/effects/hit.wav").play()
                        """else:
                            # pousser
                            pass
                            entity.velocity.x = entity.mass / (entity.mass + tile.mass) * min(75, entity.velocity.x)
                            tile.velocity.x = entity.mass / (entity.mass + tile.mass) * min(75, entity.velocity.x)
                            
                            entity.position.x = tile.collider.left - entity.collider.width - entity.collider_rect.x"""
                    else:
                        entity.velocity.x = 0
                        
            entity.position.y += entity.velocity.y * dt

            for tile in self.collisions:
                if tile == entity or (isinstance(tile, Entity) and not tile.alive): continue
                if tile.collider.collides(entity.collider):
                    if entity.velocity.y > 0:
                        entity.collider.bottom = tile.collider.top
                        entity.collisions[2] = tile

                        # rebond
                        if tile.bounciness != 0 and RESIZE * abs(entity.velocity.y) / GRAVITY > 0.25 :
                            entity.velocity.y *= - tile.bounciness
                            pygame.mixer.Sound("assets/sounds/slimejump.wav").play()
                        else:
                            entity.velocity.y = 0

                    else:
                        entity.collider.top = tile.collider.bottom
                        entity.velocity.y = 0
                        entity.collisions[0] = tile
            
            point = Collider(entity.collider.under)
            for tile in self.collisions:
                if tile == entity: continue
                if tile.collider.collides(point):
                    entity.collisions[2] = tile
                    break
                """if tile.collider.collides(rect) and not tile.collider.collides(entity.collider):
                    entity.collisions[2] = tile
                    break"""


    def create_entity(self, entity, collision=True):
        self.entities.add(entity)
        if isinstance(entity, Player):
            self.players.append(entity)
        if collision:
            self.collisions.append(entity)
        return entity

    def create_camera(self, camera):
        self.cameras.append(camera)
        if not self.main_camera:
            self.main_camera = camera
        return camera

    def create_tile(self, tile, collision=True):
        self.tiles.add(tile)
        if collision:
            self.collisions.append(tile)
        return tile
    
    def create_particle(self, particle):
        self.particles.add(particle)
        return particle
    
    def paint(self, screen, camera=None):

        if camera:
            camera.paint(screen, self.background, self.tiles, self.entities, self.particles, players=self.players)
        else:
            self.main_camera.paint(screen, self.background, self.tiles, self.entities, self.particles, players=self.players)
        
        super().paint(screen)


def init(world):
    player = world.create_entity(Player({pygame.K_q: "left", pygame.K_d: "right", pygame.K_SPACE: "up", pygame.K_s: "down"}, pygame.Vector2(63, 135)))
    player2 = world.create_entity(Player({pygame.K_LEFT: "left", pygame.K_RIGHT: "right", pygame.K_UP: "up", pygame.K_DOWN: "down"}, pygame.Vector2(37, 135), color="red"))

    main_camera = world.create_camera(Camera())
    main_camera.following = player

    world.create_tile(Tile(14,10,40), False)
    world.create_tile(Tile(15,10,40), False)
    world.create_tile(Tile(16,10,40), False)
    world.create_tile(Tile(17,10,40), False)
    world.create_tile(Tile(18,10,40), False)
    world.create_tile(Tile(14,11,68), False)
    world.create_tile(Tile(15,11,68), False)
    world.create_tile(Tile(16,11,68), False)
    world.create_tile(Tile(17,11,68), False)
    world.create_tile(Tile(18,11,68), False)


    world.create_tile(Tile(1,10,0))
    world.create_tile(Tile(1,11,7))
    for a in range(12):
        world.create_tile(Tile(2+a,10,1))
        world.create_tile(Tile(2+a,11,8))
    world.create_tile(Tile(14,10,2))
    world.create_tile(Tile(14,11,9))

    world.create_tile(Tile(18,10,0))
    world.create_tile(Tile(18,11,7))
    for a in range(33):
        if a > 2: 
            world.create_tile(Tile(19+a,10,1))
            world.create_tile(Tile(19+a,11,8))
        else:
            world.create_tile(Tile(19+a,10,69, bounciness=1, frictional_coefficient=3))
            world.create_tile(Tile(19+a,11,8))

    world.create_tile(Tile(52,10,2))
    world.create_tile(Tile(52,11,9))

    world.create_tile(Tile(16,9,10))
    world.create_tile(Tile(16,10,12))
    world.create_tile(Tile(16,11,12))

    world.create_entity(Box(7,9))

    world.create_tile(Tile(10,8,17))
    world.create_tile(Tile(11,8,18))
    world.create_tile(Tile(12,8,18))
    world.create_tile(Tile(13,8,19))
    world.create_tile(Tile(10,9,24))
    world.create_tile(Tile(11,9,25))
    world.create_tile(Tile(12,9,25))
    world.create_tile(Tile(13,9,26))

    monkey = world.create_entity(Monkey(177, 90, 640, 700))
    monkey.reverse = True

    world.create_tile(Tile(11,6,62,True), False)
    world.create_tile(Tile(12,6,62,True), False)

    slime = world.create_entity(Slime(300, 150, 300, 375, 'green'))

    world.setup_background()