import pygame
from objects.game_object import GameObject
from utils.constants import COLORS

class Bullet(GameObject):
    def __init__(self, x, y):
        image = pygame.Surface((5, 10))
        image.fill(COLORS['YELLOW'])
        super().__init__(image, x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
