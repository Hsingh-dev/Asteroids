from objects.game_object import GameObject
from utils.constants import WIDTH, HEIGHT

class Asteroid(GameObject):
    def __init__(self, image, x, y, speed):
        super().__init__(image, x, y)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class BossAsteroid(Asteroid):
    def __init__(self, image, x, y):
        super().__init__(image, x, y, speed=1)
        self.health = 10
        self.direction = 1

    def update(self):
        super().update()
        self.rect.x += self.direction * 2
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1
