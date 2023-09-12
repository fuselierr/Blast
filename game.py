import pygame
from array import *
import globals
import random
import math

pygame.init()

TILE_SIZE = 32
DETONATOR_X = globals.SCREENWIDTH / 2 + 150
PROJ_RADIUS = 3
PROJ_VEL = 4
PARTICLE_LIFESPAN = 180
GUI_LOAD_SPEED = 2

game_width = 38
game_height = 7
mines = 4
timer = 300
ticks = 0
difficulty = 4
remaining_mines = mines
mouse_down = False
gui_ypos = -300

streak = 0
score = 0

load_gui = False
game_start = False
exploded = False
projectiles_generated = False
done_exploding = False
won = False

FINAL_Y = ((globals.SCREENHEIGHT - (game_height * TILE_SIZE)) / 2) - 15
FINAL_X = ((globals.SCREENWIDTH - (game_width * TILE_SIZE)) / 2) - 15
horizontal_label_y = -50
vertical_label_x = -50

tile_sprite = pygame.image.load('graphics/tile.png')
mine_sprite = pygame.image.load('graphics/mine.png')
stone_sprite = pygame.image.load('graphics/stone.png')
mine_falling_sprite = pygame.image.load('graphics/mine_transparent.png')
selector_sprite = pygame.image.load('graphics/selector.png')
detonator_sprite = pygame.image.load('graphics/detonator.png')
projectile_sprite = pygame.image.load('graphics/projectile.png')
stone_falling_sprite = pygame.image.load('graphics/stone_transparent.png')
display_sprite = pygame.image.load('graphics/display.png')

font = pygame.font.Font('fonts/GalacticaGrid.ttf', 32)
mine_font = pygame.font.Font("fonts/GalacticaGrid.ttf", 15)
grid_label_font = pygame.font.Font('fonts/GalacticaGrid.ttf', 11)

class Tile():
    def __init__(self, image, x_pos, y_pos, state):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.tile_size = TILE_SIZE
        self.state = state
        self.rect = self.image.get_rect(topleft = (self.x_pos, self.y_pos))
        self.y_vel = 0
        self.is_falling = False

    def clicked(self, mouse_pos):
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            if self.state == 0:
                return 1
            elif self.state == 1:
                return 2
            else:
                return 3
        else:
            return 0
        
    def update_state(self, image, state):
        self.state = state
        self.image = image

    def hovered(self, mouse_pos):
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            if self.state < 2:
                return True
            else:
                return False
        else:
            return False
        
    def fall(self):
        self.y_vel *= 1.1
        self.y_pos += self.y_vel

class Projectile():

    def __init__(self, image, x_pos, y_pos, direction):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.direction = direction
        self.collided = False

        # if self.direction == 1:
        #         self.x_vel = 1
        #         self.y_vel = 0
        # elif self.direction == 2:
        #         self.x_vel = 1
        #         self.y_vel = 1
        # elif self.direction == 3:
        #         self.x_vel = 0
        #         self.y_vel = 1
        # elif self.direction == 4:
        #         self.x_vel = -1
        #         self.y_vel = 1
        # elif self.direction == 5:
        #         self.x_vel = -1
        #         self.y_vel = 0
        # elif self.direction == 6:
        #         self.x_vel = -1
        #         self.y_vel = -1
        # elif self.direction == 7:
        #         self.x_vel = 0
        #         self.y_vel = -1
        # elif self.direction == 8:
        #         self.x_vel = 1
        #         self.y_vel = -1

        match self.direction:
            case 1:
                self.x_vel = PROJ_VEL
                self.y_vel = 0
            case 2:
                self.x_vel = PROJ_VEL
                self.y_vel = PROJ_VEL
            case 3:
                self.x_vel = 0
                self.y_vel = PROJ_VEL
            case 4:
                self.x_vel = PROJ_VEL * -1
                self.y_vel = PROJ_VEL
            case 5:
                self.x_vel = PROJ_VEL * -1
                self.y_vel = 0
            case 6:
                self.x_vel = PROJ_VEL * -1
                self.y_vel = PROJ_VEL * -1
            case 7:
                self.x_vel = 0
                self.y_vel = PROJ_VEL * -1
            case 8:
                self.x_vel = PROJ_VEL
                self.y_vel = PROJ_VEL * -1

    def update_pos(self):
        self.x_pos += self.x_vel
        self.y_pos += self.y_vel

    def check_for_impact(self, tile_rect):
        temp_rect = self.image.get_rect(topleft = (self.x_pos, self.y_pos))
        if temp_rect.colliderect(tile_rect):
            self.collided = True
            return True
        if self.x_pos < -5 or self.x_pos > globals.SCREENWIDTH + 5 or self.y_pos < -5 or self.y_pos > globals.SCREENHEIGHT + 5:
            self.collided = True
        
        return False

class Num():
    def __init__(self, digit, font, font_size, colour, x_pos, y_pos):
        self.digit = digit
        self.font_size = font_size
        self.colour = colour
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.font = pygame.font.Font(font, font_size)
        self.num = self.font.render(str(digit), False, self.colour)

    def update_pos(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos

    def draw(self, win):
        win.blit(self.num, (self.x_pos, self.y_pos))

class Num_Display():
    def __init__(self, digit_count, number):
        self.digit_count = digit_count
        self.number = number

    def update(self, number):
        self.number = number


center_x = (globals.SCREENWIDTH - (game_width * TILE_SIZE)) / 2
center_y = (globals.SCREENHEIGHT - (game_height * TILE_SIZE)) / 2
tile_grid = [[Tile(tile_sprite.copy(), x * TILE_SIZE + center_x, y * TILE_SIZE - (game_height * TILE_SIZE), 0) for y in range(game_height)] for x in range(game_width)]

pseudo_mine_x = [random.randint(0, game_width - 1) for _ in range(mines)]
pseudo_mine_y = [random.randint(0, game_height - 1) for _ in range(mines)]

stone_array_x = []
stone_array_y = []

# # Random number generator 2
# directions = [1, 2, 3, 4, 5, 6, 7, 8]
# for _ in range(difficulty):
    
#     for x in pseudo_mine_x:
#         seed = random.choice(directions)
#         match seed:
#             case 1:



# Random number generator
# 1: horizontal offset
# 2: vertical offset
# 3: same number diagonal offset
# 4: different number diagonal offset
for _ in range(difficulty):
    for i, x in enumerate(pseudo_mine_x):
        seed = random.randint(1, 4)
        match seed:
            case 1:
                new_pos = random.randint(0, game_width - 1)
                while new_pos == pseudo_mine_x[i]:
                    new_pos = random.randint(0, game_width - 1)
                tile_grid[new_pos][pseudo_mine_y[i]].image = stone_sprite.copy()
                tile_grid[new_pos][pseudo_mine_y[i]].state = 2
                stone_array_x.append(new_pos)
                stone_array_y.append(pseudo_mine_y[i])
            case 2:
                new_pos = random.randint(0, game_height - 1)
                while new_pos == pseudo_mine_y[i]:
                    new_pos = random.randint(0, game_height - 1)
                tile_grid[pseudo_mine_x[i]][new_pos].image = stone_sprite.copy()
                tile_grid[pseudo_mine_x[i]][new_pos].state = 2
                stone_array_x.append(pseudo_mine_x[i])
                stone_array_y.append(new_pos)
            case 3:
                up_left = min(pseudo_mine_y[i], pseudo_mine_x[i])
                down_right = min((game_height - 1) - pseudo_mine_y[i], (game_width - 1) - pseudo_mine_x[i])
                offset = random.randint(0 - up_left, down_right)
                if offset != 0:
                    while offset == 0:
                        offset = random.randint(0 - up_left, down_right)
                    tile_grid[pseudo_mine_x[i] + offset][pseudo_mine_y[i] + offset].image = stone_sprite.copy()
                    tile_grid[pseudo_mine_x[i] + offset][pseudo_mine_y[i] + offset].state = 2
                    stone_array_x.append(pseudo_mine_x[i] + offset)
                    stone_array_y.append(pseudo_mine_y[i] + offset)
            case 4:
                up_right = min(pseudo_mine_y[i], (game_width - 1) - pseudo_mine_x[i])
                down_left = min((game_height - 1) - pseudo_mine_y[i], pseudo_mine_x[i])
                offset = random.randint(0 - up_right, down_left)
                if offset != 0:
                    while offset == 0:
                        offset = random.randint(0 - up_right, down_left)
                    tile_grid[pseudo_mine_x[i] - offset][pseudo_mine_y[i] + offset].image = stone_sprite.copy()
                    tile_grid[pseudo_mine_x[i] - offset][pseudo_mine_y[i] + offset].state = 2
                    stone_array_x.append(pseudo_mine_x[i] + offset)
                    stone_array_y.append(pseudo_mine_y[i] + offset)


columns = [game_height - 1] * game_width
desired_y = [i * TILE_SIZE + center_y for i in range(game_height)]

mines_x = []
mines_y = []
projectile_array = []
mines_gone = []
projectiles_gone = []

def draw_game(win):
    global ticks, timer, remaining_mines, mouse_down, game_start, exploded, done_exploding, projectiles_generated, won, load_gui, gui_ypos, horizontal_label_y, vertical_label_x

    for x in range(game_width):
        for y in range(game_height):
            win.blit(tile_grid[x][y].image, (tile_grid[x][y].x_pos, tile_grid[x][y].y_pos))

    if game_start == True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        mouse_flag = False
        for x in range(game_width):
            for y in range(game_height):

                if exploded == True and tile_grid[x][y].state == 1:
                    tile_grid[x][y].state = 0
                    tile_grid[x][y].image = tile_sprite.copy()

                if mouse_buttons[0] == 1 and mouse_down == False and exploded == False:

                    click_react = tile_grid[x][y].clicked(mouse_pos)

                    if click_react == 1 and remaining_mines > 0:
                        remaining_mines -= 1
                        tile_grid[x][y].update_state(mine_sprite.copy(), 1)
                        mines_x.append(x)
                        mines_y.append(y)
                    elif click_react == 2:
                        remaining_mines += 1
                        tile_grid[x][y].update_state(tile_sprite.copy(), 0)
                        for i in range(len(mines_x)):
                            altered = False

                            for j in range(len(mines_y)):
                                if x == mines_x[i] and y == mines_y[j]:
                                    mines_x.pop(i)
                                    mines_y.pop(j)
                                    altered = True
                                    break

                            if altered == True:
                                break

                    mouse_flag = True

        if exploded == False:
            for x in range(game_width):
                for y in range(game_height):
                    if tile_grid[x][y].hovered(mouse_pos):
                        win.blit(selector_sprite, (tile_grid[x][y].x_pos, tile_grid[x][y].y_pos))

        x_label = 1
        for x in range(game_width):
            x_display = grid_label_font.render(str(x_label), False, globals.WHITE)
            win.blit(x_display, ((globals.SCREENWIDTH - (game_width * TILE_SIZE)) / 2 + (x_label - 1) * TILE_SIZE + TILE_SIZE / 2 - 6, ((globals.SCREENHEIGHT - (game_height * TILE_SIZE)) / 2) - 15))
            x_label += 1

        y_label = 'A'
        for y in range(game_height):
            y_display = grid_label_font.render(y_label, False, globals.WHITE)
            win.blit(y_display, (((globals.SCREENWIDTH - (game_width * TILE_SIZE)) / 2) - 15, (((globals.SCREENHEIGHT - (game_height * TILE_SIZE)) / 2 + y * TILE_SIZE + TILE_SIZE / 2 - 6))))
            y_label = chr(ord(y_label) + 1)

        if mouse_flag == True:
            mouse_down = True

        if mouse_buttons[0] == 0:
            mouse_down = False

        if exploded == True and done_exploding == False:
            if projectiles_generated == False:
                for x in range(len(mines_x)):
                    for i in range(8):
                        projectile_array.append(Projectile(projectile_sprite, mines_x[x] * TILE_SIZE + center_x, mines_y[x] * TILE_SIZE + center_y, i + 1))
                
                projectiles_generated = True

            if len(projectile_array) == len(projectiles_gone):
                done_exploding = True

            for i in range(len(projectile_array)):
                if projectile_array[i].collided == False:
                    projectile_array[i].update_pos()
                    win.blit(projectile_array[i].image, (projectile_array[i].x_pos, projectile_array[i].y_pos))
                    for j in range(len(stone_array_x)):
                        if projectile_array[i].check_for_impact(tile_grid[stone_array_x[j]][stone_array_y[j]].rect) == True:
                            tile_grid[stone_array_x[j]][stone_array_y[j]].state = 0
                            tile_grid[stone_array_x[j]][stone_array_y[j]].image = tile_sprite.copy()
                            mines_gone.append(j)
                            projectiles_gone.append(projectile_array[i])
        elif done_exploding == True:
            if len(mines_gone) == len(mines_x):
                won = True
                print('W in the bag')
                pygame.quit()
            else:
                print('L lmao')
                pygame.quit()

        if rect_clicked(detonator_sprite.get_rect(topleft = (DETONATOR_X, gui_ypos + 10)), mouse_pos, mouse_down):
            exploded = True

        if timer > 0 and ticks == 59 and done_exploding == False:
            timer -= 1

    elif load_gui == False:
        if not(all(element == -1 for element in columns)):
            fall_index = random.randint(0, game_width - 1)
            fall_index2 = random.randint(0, game_width - 1)
            while columns[fall_index] == -1:
                fall_index = random.randint(0, game_width - 1)
            tile_grid[fall_index][columns[fall_index]].is_falling = True
            tile_grid[fall_index][columns[fall_index]].y_vel = 1
            columns[fall_index] -= 1

        done_falling = True
        for x in range(game_width):
            for y in range (game_height):
                if tile_grid[x][y].is_falling == True:
                    done_falling = False
                    tile_grid[x][y].fall()
                    if tile_grid[x][y].y_pos >= desired_y[y]:
                        tile_grid[x][y].y_pos = desired_y[y]
                        tile_grid[x][y].is_falling = False
                        tile_grid[x][y].rect = tile_grid[x][y].image.get_rect(topleft = (tile_grid[x][y].x_pos, tile_grid[x][y].y_pos))

        if done_falling == True:
            load_gui = True
    else:
        if gui_ypos == 0:
            game_start = True
        elif gui_ypos > 0:
            gui_ypos = 0
        else:
            gui_ypos += GUI_LOAD_SPEED
        
        x_label = 1
        for x in range(game_width):
            x_display = grid_label_font.render(str(x_label), False, globals.WHITE)
            win.blit(x_display, ((globals.SCREENWIDTH - (game_width * TILE_SIZE)) / 2 + (x_label - 1) * TILE_SIZE + TILE_SIZE / 2 - 6, horizontal_label_y))
            x_label += 1

        horizontal_label_y += (FINAL_Y - horizontal_label_y) * 0.05

        y_label = 'A'
        for y in range(game_height):
            y_display = grid_label_font.render(y_label, False, globals.WHITE)
            win.blit(y_display, (vertical_label_x, (((globals.SCREENHEIGHT - (game_height * TILE_SIZE)) / 2 + y * TILE_SIZE + TILE_SIZE / 2 - 6))))
            y_label = chr(ord(y_label) + 1)

        vertical_label_x += (FINAL_X - vertical_label_x) * 0.05

    minutes_left = math.floor(timer / 60)
    seconds_left = timer - (minutes_left * 60)
    time_display_text = f"{minutes_left}:{seconds_left:02}"

    win.blit(display_sprite.copy(), (globals.SCREENWIDTH / 2 + 120, gui_ypos))
    win.blit(display_sprite.copy(), (globals.SCREENWIDTH / 2 - 40, gui_ypos))
    win.blit(display_sprite.copy(), (globals.SCREENWIDTH / 2 - 200, gui_ypos))
    win.blit(display_sprite.copy(), (globals.SCREENWIDTH / 2 - 350, gui_ypos))

    time_display = font.render(time_display_text, False, globals.DARK_GREY)
    win.blit(time_display, ((globals.SCREENWIDTH / 2) + 3, gui_ypos + 23))
    time_display = font.render(time_display_text, False, globals.DARK_RED)
    win.blit(time_display, (globals.SCREENWIDTH / 2, gui_ypos + 23))

    mine_display_text = f"mines: {remaining_mines}"
    mine_display = mine_font.render(mine_display_text, False, globals.DARK_RED)
    win.blit(mine_display, (globals.SCREENWIDTH / 2, gui_ypos + 50))

    win.blit(detonator_sprite, (DETONATOR_X, gui_ypos + 10))

    if ticks == 59:
        ticks = 0
    else:
        ticks += 1

def rect_clicked(image_rect, mouse_pos, mouse_down):
    if mouse_pos[0] in range(image_rect.left, image_rect.right) and mouse_pos[1] in range(image_rect.top, image_rect.bottom) and mouse_down == True:
        return True
    else:
        return False