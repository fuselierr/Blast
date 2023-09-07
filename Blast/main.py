import pygame
import game
import menu
import globals
import random
from sys import exit

SCREENWIDTH = globals.SCREENWIDTH
SCREENHEIGHT = globals.SCREENHEIGHT
FPS = 60

WIN = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
pygame.display.set_caption('Blast')
clock = pygame.time.Clock()

surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
surface.fill(globals.BG)    

screen_x = 0
screen_y = 0

def screen_shake_update():
    global screen_x, screen_y
    if game.ticks % globals.shake_rate == 0:
        screen_x = random.randint(globals.shake * -1, globals.shake)
        screen_y = random.randint(globals.shake * -1, globals.shake)

        if random.randint(0, 100) < globals.shake_decline:
            globals.shake -= 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if globals.shake > 0:
        screen_shake_update()
    else:
        screen_x = 0
        screen_y = 0

    WIN.blit(surface, (screen_x, screen_y))

    match globals.scene:
        case 0:
            menu.draw_menu(WIN, surface)
        case 1:
            game.draw_game(WIN)
        case 2:
            menu.draw_game_over(WIN)

    pygame.display.update()
    clock.tick(FPS)