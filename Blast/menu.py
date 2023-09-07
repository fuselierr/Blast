import pygame
import globals
import random
import math

pygame.init()

TILE_DENSITY = 20
PROJ_VEL = 5
TRAIL_LENGTH = 150
BUTTON_GRAV = 0.25

in_transition = False
title_y = 50

title_font = pygame.font.Font('fonts/GalacticaGrid.ttf', 100)
button_font = pygame.font.Font('fonts/GalacticaGrid.ttf', 52)

button_sprite = pygame.image.load('graphics/button.png')
button_sprite = pygame.transform.scale(button_sprite, (200, 75))

projectile_sprite = pygame.image.load('graphics/projectile.png')
tile_sprite = pygame.image.load('graphics/tile.png')
mine_sprite = pygame.image.load('graphics/mine.png')
stone_sprite = pygame.image.load('graphics/stone.png')

gradient = globals.CenteredGradient(globals.SCREENWIDTH, globals.SCREENHEIGHT, globals.BG2, globals.BG)
gradient.update()

class Projectile():
    def __init__(self, image):
        self.image = image
        self.particle_trail = []
        seed = random.randint(1, 8)
        match seed:
            case 1:
                self.x_vel = PROJ_VEL
                self.y_vel = 0
                self.x_pos = -10
                self.y_pos = random.randint(0, globals.SCREENHEIGHT / 30) * 30
            case 2:
                self.x_vel = PROJ_VEL
                self.y_vel = PROJ_VEL
                if random.randint(0, 1) == 0:
                    self.x_pos = -10
                    self.y_pos = random.randint(0, globals.SCREENHEIGHT / 30) * 30
                else:
                    self.x_pos = random.randint(0, globals.SCREENWIDTH / 30) * 30
                    self.y_pos = -10
            case 3:
                self.x_vel = 0
                self.y_vel = PROJ_VEL
                self.x_pos = random.randint(0, globals.SCREENWIDTH / 30) * 30
                self.y_pos = -10
            case 4:
                self.x_vel = PROJ_VEL * -1
                self.y_vel = PROJ_VEL
                if random.randint(0, 1) == 0:
                    self.x_pos = globals.SCREENWIDTH + 10
                    self.y_pos = random.randint(0, globals.SCREENHEIGHT / 30) * 30
                else:
                    self.x_pos = random.randint(0, globals.SCREENWIDTH / 30) * 30
                    self.y_pos = -10
            case 5:
                self.x_vel = PROJ_VEL * -1
                self.y_vel = 0
                self.x_pos = globals.SCREENWIDTH + 10
                self.y_pos = random.randint(0, globals.SCREENHEIGHT / 30) * 30
            case 6:
                self.x_vel = PROJ_VEL * -1
                self.y_vel = PROJ_VEL * -1
                if random.randint(0, 1) == 0:
                    self.x_pos = globals.SCREENWIDTH + 10
                    self.y_pos = random.randint(0, globals.SCREENHEIGHT / 30) * 30
                else:
                    self.x_pos = random.randint(0, globals.SCREENWIDTH / 30) * 30
                    self.y_pos = globals.SCREENHEIGHT + 10
            case 7:
                self.x_vel = 0
                self.y_vel = PROJ_VEL * -1
                self.x_pos = random.randint(0, globals.SCREENWIDTH / 30) * 30
                self.y_pos = globals.SCREENHEIGHT + 10
            case 8:
                self.x_vel = PROJ_VEL
                self.y_vel = PROJ_VEL * -1
                if random.randint(0, 1) == 0:
                    self.x_pos = -10
                    self.y_pos = random.randint(0, globals.SCREENHEIGHT / 30) * 30
                else:
                    self.x_pos = random.randint(0, globals.SCREENWIDTH / 30) * 30
                    self.y_pos = globals.SCREENHEIGHT + 10

    def update(self):
        self.x_pos += self.x_vel
        self.y_pos += self.y_vel
        self.particle_trail.append(globals.Particle((self.x_pos + 15, self.y_pos + 15), globals.LIGHT_ORANGE, 8, 0))
        for i in self.particle_trail:
            if i.radius <= 0:
                self.particle_trail.remove(i)
            else:
                i.update()

    def check_bounds(self):
        if self.x_pos < TRAIL_LENGTH * -1 or self.x_pos > globals.SCREENWIDTH + TRAIL_LENGTH or self.y_pos < TRAIL_LENGTH * -1 or self.y_pos > globals.SCREENHEIGHT + TRAIL_LENGTH:
            self.particle_trail = []
            return True
        else:
            return False
        
    def draw(self, win):
        for i in self.particle_trail:
            i.draw(win)
        win.blit(self.image, (self.x_pos, self.y_pos))

class FloatingTile():
    def __init__(self, image, x_pos, y_pos, gravity):
        self.original_image = image
        self.angle = random.randint(0, 359)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.y_vel = 0
        self.spin_speed = random.random() + 1
        if random.randint(0, 1) == 1:
            self.spin_speed *= -1
        self.gravity = gravity
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))

    def update(self):
        if self.gravity == True:
            self.y_vel += 0.3
            self.y_pos += self.y_vel

        self.angle += self.spin_speed
        self.angle %= 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))

    def check_for_impact(self):
        if self.y_pos > globals.SCREENHEIGHT + 200:
            return True
        else:
            return False
        
    def draw(self, win):
        win.blit(self.image, self.rect)
   
class Button():
    def __init__(self, image, x_pos, y_pos, offset, snap, text_input):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.offset = offset
        self.snap = snap
        self.y_offset = y_pos + offset
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        self.text_input = text_input
        self.text = button_font.render(self.text_input, False, globals.DARK_GREY)
        self.text_rect = self.text.get_rect(center = (self.x_pos, self.y_pos))
        self.y_vel = -5
        self.is_falling = False

    def clicked(self, mouse_pos):
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            return True

    def update(self, x_pos, y_pos):
        if self.is_falling == True:
            self.y_pos += self.y_vel
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center = (self.x_pos, self.y_pos))

    def hovered(self, mouse_pos):
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            self.text = button_font.render(self.text_input, False, globals.DARK_RED)
            self.y_pos += (self.y_offset - self.y_pos) * self.snap
            self.update(self.x_pos, self.y_pos)
        else:
            self.text = button_font.render(self.text_input, False, globals.DARK_GREY)
            self.y_pos += ((self.y_offset - self.offset) - self.y_pos) * self.snap
            self.update(self.x_pos, self.y_pos)
        
title = title_font.render("BLAST", False, globals.DARK_RED)
play_button = Button(button_sprite, globals.SCREENWIDTH / 2, globals.SCREENHEIGHT / 2 + 40, 20, 0.1, 'PLAY')

def find_tile_locations(screen_x, screen_y, width, height, num_tiles, depth, tile_arr):
    if depth == 0 or num_tiles == 1:
        for i in range(num_tiles):
            temp_x = random.randint(screen_x, screen_x + width)
            temp_y = random.randint(screen_y, screen_y + height)
            tile_arr.append((temp_x, temp_y))
    
    else:
        find_tile_locations(screen_x, screen_y, width / 2, height / 2, round(num_tiles / 4), depth - 1, tile_arr)
        find_tile_locations(screen_x + (width / 2), screen_y, width / 2, height / 2, round(num_tiles / 4), depth - 1, tile_arr)
        find_tile_locations(screen_x, screen_y + (height / 2), width / 2, height / 2, round(num_tiles / 4), depth - 1, tile_arr)
        find_tile_locations(screen_x + (width / 2), screen_y + height / 2, width / 2, height / 2, round(num_tiles / 4), depth - 1, tile_arr)

tile_locations = []
find_tile_locations(0, 0, globals.SCREENWIDTH, globals.SCREENHEIGHT, 32, 2, tile_locations)
floating_tiles = []
for i in range(len(tile_locations)):
    skin = random.randint(0, 2)
    match skin:
        case 0:
            floating_tiles.append(FloatingTile(tile_sprite.copy(), tile_locations[i][0], tile_locations[i][1], False))
        case 1:
            floating_tiles.append(FloatingTile(mine_sprite.copy(), tile_locations[i][0], tile_locations[i][1], False))
        case 2:
            floating_tiles.append(FloatingTile(stone_sprite.copy(), tile_locations[i][0], tile_locations[i][1], False))

projectile_array = []

def draw_menu(win, screen):
    global in_transition, title_y

    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    for i in floating_tiles:
        i.draw(win)
        i.update()
        if i.check_for_impact() == True:
            floating_tiles.remove(i)

    if random.randint(1, 30) == 1 and in_transition == False:
        projectile_array.append(Projectile(projectile_sprite))

    for i in projectile_array:
        i.draw(win)
        i.update()
        if i.check_bounds() == True:
            projectile_array.remove(i)
    
    gradient.draw(screen)

    win.blit(play_button.image, play_button.rect)
    win.blit(play_button.text, play_button.text_rect)

    win.blit(title, (globals.SCREENWIDTH / 2 - 150, title_y))

    if in_transition == True:
        play_button.y_vel += BUTTON_GRAV
        play_button.update(play_button.x_pos, play_button.y_pos)
        title_y -= 5
        if len(projectile_array) == 0 and len(floating_tiles) == 0 and play_button.y_pos > globals.SCREENHEIGHT + 50:
            globals.scene = 1
    else:
        play_button.hovered(mouse_pos)

    if mouse_buttons[0] == 1 and in_transition == False and play_button.clicked(mouse_pos):
        play_button.is_falling = True
        for i in floating_tiles:
            i.gravity = True
        for i in projectile_array:
            i.x_vel *= 5
            i.y_vel *= 5
        in_transition = True

def draw_game_over(win):
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()