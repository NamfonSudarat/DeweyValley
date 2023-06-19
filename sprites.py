import pygame
from settings import *
from random import randint, choice
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name

class Water(Generic):
    def __init__(self, pos, frames, groups):
        #frame animation
        self.frames = frames
        self.frame_index = 0

        super().__init__(
            pos = pos, 
            surf = self.frames[self.frame_index], 
            groups  = groups, 
            z = LAYERS['water'])
        
    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)

class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, self.rect.height * 0.9)

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        #mask
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0,0,0))
        self.image = new_surf

    def update(self, dt):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.start_time > self.duration: 
            self.kill()
    
class Tree(Generic):
    def __init__(self, pos, surf, groups, name, player_add):
        super().__init__(pos, surf, groups)

        #tree attribute
        self.heart = 6
        self.alive = True
        stump_pic = f'C:/Users/ernes/pythonProject/deweyValley/s2 - basic player/graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_pic).convert_alpha()
        #apple
        self.apples = pygame.image.load('C:/Users/ernes/pythonProject/deweyValley/s2 - basic player/graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

        # sounds
        self.axe_sound = pygame.mixer.Sound('s2 - basic player/audio/axe.mp3')

    def damage(self):
        #distroy tree
        self.heart -= 1
        # axe sound
        self.axe_sound.play()
        #cut apple
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                pos = random_apple.rect.topleft, 
                surf = random_apple.image, 
                groups = self.groups()[0], 
                z = LAYERS['fruit'])
            self.player_add('apple')
            random_apple.kill()

    def check_die(self):
        if self.heart <= 0:
            Particle(
                pos=self.rect.topleft, 
                surf=self.image, 
                groups=self.groups()[0], 
                z=LAYERS['fruit'], 
                duration=200)
            self.player_add('wood')
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False

    def update(self, dt):
        if self.alive:
            self.check_die()

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0,10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic(
                    pos = (x,y), 
                    surf = self.apples, 
                    groups = [self.apple_sprites, self.groups()[0]],
                    z = LAYERS['fruit'])
    