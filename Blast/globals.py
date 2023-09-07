import pygame
import random
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = (10, 30, 60)
BG2 = (50, 70, 130)
DARK_RED = (150, 0, 0)
DARK_GREY = (50, 50, 50)
LIGHT_ORANGE = (255, 150, 50)

SCREENWIDTH = 1260
SCREENHEIGHT = 600

scene = 0
shake = 20
shake_rate = 10
shake_decline = 30

class Particle:
    def __init__(self, pos, colour, radius, offset):
        self.x_pos, self.y_pos = pos
        self.offset = offset
        self.x_vel, self.y_vel = random.randint(self.offset * -1, self.offset), random.randint(self.offset * -5, 0) * 0.1
        self.radius = radius
        self.colour = colour

    def draw(self, win):
        pygame.draw.circle(win, self.colour, (self.x_pos, self.y_pos), self.radius)

    def update(self):
        self.x_pos += self.x_vel
        self.y_pos += self.y_vel
        if random.randint(0, 100) < 20 and self.radius > 0:
            self.radius -= 1

class Dust:
    def __init__(self, pos, quantity):
        self.pos = pos
        self.particles = []
        self.quantity = quantity
        for i in range(self.quantity):
            self.particles.append(Particle(self.pos))

    def update(self):
        for i in self.particles:
            i.update()
            self.particles = [particle for particle in self.particles if particle.radius > 0]

    def draw(self, win):
        for i in self.particles:
            i.draw(win)

def screen_shake(surface, intensity, rate, decline):
    screen_shake = max(screen_shake, intensity)
    shake_rate = max(rate, shake_rate)
    shake_decline = min(shake_decline, decline)

class CenteredGradient:
    def __init__(self, width, height, center_color, edge_color):
        self.width = width
        self.height = height
        self.center_color = center_color
        self.edge_color = edge_color
        self.center_x = width // 2
        self.center_y = height // 2
        self.max_distance = math.sqrt(self.center_x ** 2 + self.center_y ** 2)
        self.surface = pygame.Surface((width, height))

    def update(self):
        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - self.center_x) ** 2 + (y - self.center_y) ** 2)
                gradient_value = 1 - (distance / self.max_distance)
                r = int(self.center_color[0] * gradient_value + self.edge_color[0] * (1 - gradient_value))
                g = int(self.center_color[1] * gradient_value + self.edge_color[1] * (1 - gradient_value))
                b = int(self.center_color[2] * gradient_value + self.edge_color[2] * (1 - gradient_value))
                self.surface.set_at((x, y), (r, g, b))

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))