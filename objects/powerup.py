from objects.game_object import GameObject
from utils.constants import HEIGHT

class PowerUp(GameObject):
    def __init__(self, image, x, y, type):
        super().__init__(image, x, y)
        self.speed = 1
        self.type = type

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
