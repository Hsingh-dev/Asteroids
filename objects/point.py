from objects.game_object import GameObject
from utils.constants import HEIGHT

class Point(GameObject):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
