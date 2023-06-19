import pygame
from settings import *
from support import *
from timer import Timer
from sprites import *

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        #setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        
        self.z = LAYERS['main']
        #movement attributes
        self.directions = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 250
        #collisions
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

        #timer
        self.timers = {
            'tool use': Timer(350,self.use_tool),
            'switch tools': Timer(200),
            'seeds use': Timer(350,self.use_seed),
            'switch seeds': Timer(200)

        }
        #tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index] 

        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        #inventory
        self.item_invent = {
            'wood':   0,
            'apple':  0,
            'corn':   0,
            'tomato': 0
        }
        self.seed_invent = {
            'corn': 5,
            'tomato': 5
        }
        self.money = 500

        #interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop

        # sound
        self.watering = pygame.mixer.Sound('s2 - basic player/audio/water.mp3')

    def use_tool(self):
        # print('tool use')
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.watering.play()
        # print(self.selected_tool)

    def get_tar_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def use_seed(self):
        if self.seed_invent[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_invent[self.selected_seed] -= 1

    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [],'down_idle': [], 
            'right_hoe': [], 'left_hoe': [], 'up_hoe': [],'down_hoe': [],
            'right_axe': [], 'left_axe': [], 'up_axe': [],'down_axe': [],
            'right_water': [], 'left_water': [], 'up_water': [],'down_water':[]}

        for animation in self.animations.keys():
            full_path = 'C:/Users/ernes/pythonProject/deweyValley/s2 - basic player/graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers['tool use'].active and not self.sleep:
            if keys[pygame.K_UP]:
                self.directions.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.directions.y = 1
                self.status = 'down'
            else:
                self.directions.y = 0

            if keys[pygame.K_RIGHT]:
                self.directions.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.directions.x = -1
                self.status = 'left'
            else:
                self.directions.x = 0

            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.directions = pygame.math.Vector2()
                self.frame_index = 0 #random animation from first index

            if keys[pygame.K_TAB] and not self.timers['switch tools'].active:
                self.timers['switch tools'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]
            #seeds use and change seeds
            if keys[pygame.K_c]:
                self.timers['seeds use'].activate()
                self.directions = pygame.math.Vector2()
                self.frame_index = 0 #random animation from first index

            if keys[pygame.K_l] and not self.timers['switch seeds'].active:
                self.timers['switch seeds'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]

            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    else:
                        self.status = 'left_idle'
                        self.sleep = True
               
    def get_status(self):
    #character not moving
        if self.directions.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.directions.x > 0: # move to rigth
                            self.hitbox.right = sprite.hitbox.left
                        if self.directions.x < 0: # move to left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.directions.y > 0: # move to down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.directions.y < 0: # move to up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
    
    def move(self, dt):
        if self.directions.magnitude() > 0:
            self.directions = self.directions.normalize() #normalizing vector
        
        self.pos.x += self.directions.x * self.speed * dt #horizontal movement
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.directions.y * self.speed * dt #vertical movement
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_tar_pos()
        self.move(dt)
        self.animate(dt)
        