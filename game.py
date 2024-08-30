import pygame
import random
import json
from objects.spaceship import Spaceship
from objects.asteroid import Asteroid, BossAsteroid
from objects.bullet import Bullet
from objects.point import Point
from objects.powerup import PowerUp
from objects.particle import Particle
from utils.constants import WIDTH, HEIGHT, FPS, COLORS
from utils.assets import load_assets, load_sounds

class AsteroidAvoidanceGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroid Avoidance Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.images = load_assets()
        self.sounds = load_sounds()
        self.load_high_score()
        self.reset_game()

    def load_high_score(self):
        try:
            with open("high_score.json", "r") as f:
                self.high_score = json.load(f)["high_score"]
        except FileNotFoundError:
            self.high_score = 0

    def save_high_score(self):
        with open("high_score.json", "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.points = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.spaceship = Spaceship(self.images['spaceship'], WIDTH // 2, HEIGHT - 60)
        self.all_sprites.add(self.spaceship)
        self.score = 0
        self.level = 1
        self.spawn_timer = 0
        self.boss_timer = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.main_menu = True
        self.difficulty = "normal"
        self.combo = 0
        self.combo_timer = 0
        self.game_time = 0
        self.particles = []
        self.achievements = {
            "first_point": False,
            "survive_1_minute": False,
            "reach_level_5": False
        }
        self.show_controls = False
        pygame.mixer.music.play(-1)

    def run(self):
        while True:
            if not self.handle_events():
                return
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
        return True

    def handle_keydown(self, key):
        if key == pygame.K_p:
            self.paused = not self.paused
        elif key == pygame.K_r and self.game_over:
            self.reset_game()
        elif key == pygame.K_RETURN and self.main_menu:
            self.main_menu = False
        elif key == pygame.K_1 and self.main_menu:
            self.difficulty = "easy"
        elif key == pygame.K_2 and self.main_menu:
            self.difficulty = "normal"
        elif key == pygame.K_3 and self.main_menu:
            self.difficulty = "hard"
        elif key == pygame.K_4 and self.main_menu:
            self.show_controls = not self.show_controls

    def update(self):
        if self.main_menu or self.paused or self.game_over:
            return

        self.game_time += 1
        self.all_sprites.update()
        self.bullets.update()
        self.handle_collisions()
        self.spawn_objects()
        self.move_spaceship()
        self.update_difficulty()
        self.update_combo()
        self.update_particles()
        self.check_achievements()
        self.handle_shooting()

    def handle_collisions(self):
        self.check_asteroid_collisions()
        self.check_point_collisions()
        self.check_powerup_collisions()
        self.check_bullet_collisions()

    def check_asteroid_collisions(self):
        for asteroid in pygame.sprite.spritecollide(self.spaceship, self.asteroids, True):
            if not self.spaceship.shield:
                self.lives -= 1
                self.sounds['explosion'].play()
                self.create_explosion(asteroid.rect.center)
                if self.lives <= 0:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
            else:
                self.sounds['explosion'].play()
                self.create_explosion(asteroid.rect.center)

    def check_point_collisions(self):
        for point in pygame.sprite.spritecollide(self.spaceship, self.points, True):
            self.score += 1
            self.combo += 1
            self.combo_timer = 60
            self.sounds['point'].play()
            self.create_sparkle(point.rect.center)

    def check_powerup_collisions(self):
        for powerup in pygame.sprite.spritecollide(self.spaceship, self.powerups, True):
            self.apply_powerup(powerup.type)
            self.sounds['powerup'].play()
            self.create_sparkle(powerup.rect.center)

    def check_bullet_collisions(self):
        for bullet in self.bullets:
            hit_asteroids = pygame.sprite.spritecollide(bullet, self.asteroids, True)
            for asteroid in hit_asteroids:
                self.score += 1
                self.combo += 1
                self.combo_timer = 60
                self.create_explosion(asteroid.rect.center)
                bullet.kill()

    def apply_powerup(self, type):
        if type == "shield":
            self.spaceship.shield = True
            self.spaceship.shield_timer = 300
        elif type == "life":
            self.lives = min(self.lives + 1, 5)
        elif type == "rapid_fire":
            self.spaceship.rapid_fire = True
            self.spaceship.rapid_fire_timer = 300

    def spawn_objects(self):
        self.spawn_timer += 1
        self.boss_timer += 1
        if self.spawn_timer >= 60 // self.level:
            self.spawn_timer = 0
            if random.random() < 0.7:
                self.spawn_asteroid()
            elif random.random() < 0.2:
                self.spawn_powerup()
            else:
                self.spawn_point()

        if self.boss_timer >= 1800:
            self.boss_timer = 0
            self.spawn_boss_asteroid()

    def spawn_asteroid(self):
        speed = random.randint(1, 5)
        if self.difficulty == "easy":
            speed = max(1, speed - 1)
        elif self.difficulty == "hard":
            speed = min(5, speed + 1)
        asteroid = Asteroid(self.images['asteroid'], random.randint(0, WIDTH - 50), -50, speed)
        self.all_sprites.add(asteroid)
        self.asteroids.add(asteroid)

    def spawn_boss_asteroid(self):
        boss = BossAsteroid(self.images['boss_asteroid'], random.randint(0, WIDTH - 100), -100)
        self.all_sprites.add(boss)
        self.asteroids.add(boss)

    def spawn_point(self):
        point = Point(self.images['point'], random.randint(0, WIDTH - 30), -30)
        self.all_sprites.add(point)
        self.points.add(point)

    def spawn_powerup(self):
        powerup_type = random.choice(["shield", "life", "rapid_fire"])
        image = self.images[powerup_type]
        powerup = PowerUp(image, random.randint(0, WIDTH - 50), -50, powerup_type)
        self.all_sprites.add(powerup)
        self.powerups.add(powerup)

    def move_spaceship(self):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        self.spaceship.move(dx, dy)

    def update_difficulty(self):
        self.level = min(10, 1 + self.score // 10)

    def update_combo(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def create_explosion(self, position):
        for _ in range(20):
            self.particles.append(Particle(position[0], position[1], COLORS['RED']))

    def create_sparkle(self, position):
        for _ in range(10):
            self.particles.append(Particle(position[0], position[1], COLORS['YELLOW']))

    def check_achievements(self):
        if not self.achievements["first_point"] and self.score > 0:
            self.achievements["first_point"] = True
            self.show_achievement("First Point!")
        if not self.achievements["survive_1_minute"] and self.game_time >= 3600:
            self.achievements["survive_1_minute"] = True
            self.show_achievement("Survived 1 Minute!")
        if not self.achievements["reach_level_5"] and self.level >= 5:
            self.achievements["reach_level_5"] = True
            self.show_achievement("Reached Level 5!")

    def show_achievement(self, text):
        self.achievement_text = text
        self.achievement_timer = 180  # Display for 3 seconds

    def handle_shooting(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            bullet = self.spaceship.shoot()
            if bullet:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                if self.spaceship.rapid_fire:
                    self.spaceship.shoot_delay = 10
                else:
                    self.spaceship.shoot_delay = 30

    def draw(self):
        self.screen.fill(COLORS['BLACK'])

        if self.main_menu:
            self.draw_main_menu()
        else:
            self.draw_game()

        pygame.display.flip()

    def draw_main_menu(self):
        if not self.show_controls:
            self.draw_menu_options()
        else:
            self.draw_controls()

    def draw_menu_options(self):
        line_spacing = 40
        self.draw_text("ASTEROID AVOIDANCE", WIDTH // 2, HEIGHT // 4, center=True, size=48)

        menu_start_y = HEIGHT // 2 - 80
        options = [
            "PRESS ENTER TO START",
            "1 - EASY",
            "2 - NORMAL",
            "3 - HARD",
            "4 - GAME CONTROLS"
        ]
        for i, option in enumerate(options):
            self.draw_text(option, WIDTH // 2, menu_start_y + i * line_spacing, center=True)

        info_start_y = HEIGHT * 3 // 4
        self.draw_text(f"HIGH SCORE: {self.high_score}", WIDTH // 2, info_start_y, center=True)
        self.draw_text(f"CURRENT DIFFICULTY: {self.difficulty.upper()}", WIDTH // 2, info_start_y + line_spacing, center=True)

    def draw_controls(self):
        line_spacing = 40
        self.draw_text("GAME CONTROLS", WIDTH // 2, HEIGHT // 4, center=True, size=48)

        controls_start_y = HEIGHT // 2 - 60
        controls = [
            "ARROW KEYS - MOVE SPACESHIP",
            "SPACE - SHOOT",
            "P - PAUSE GAME",
            "R - RESTART (WHEN GAME OVER)"
        ]
        for i, control in enumerate(controls):
            self.draw_text(control, WIDTH // 2, controls_start_y + i * line_spacing, center=True)

        self.draw_text("PRESS 4 TO RETURN TO MAIN MENU", WIDTH // 2, HEIGHT - 100, center=True)

    def draw_game(self):
        self.all_sprites.draw(self.screen)
        self.bullets.draw(self.screen)
        self.draw_ui()
        self.draw_particles()
        self.draw_powerups()
        self.draw_achievement()
        self.draw_game_state()

    def draw_ui(self):
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"Level: {self.level}", 10, 50)
        self.draw_text(f"High Score: {self.high_score}", WIDTH - 200, 10)
        self.draw_text(f"Combo: x{self.combo}", 10, 90)
        self.draw_lives()

    def draw_particles(self):
        for particle in self.particles:
            particle.draw(self.screen)

    def draw_powerups(self):
        if self.spaceship.shield:
            pygame.draw.circle(self.screen, COLORS['BLUE'], self.spaceship.rect.center, 40, 2)
        if self.spaceship.rapid_fire:
            pygame.draw.circle(self.screen, COLORS['YELLOW'], self.spaceship.rect.center, 35, 2)

    def draw_achievement(self):
        if hasattr(self, 'achievement_text') and hasattr(self, 'achievement_timer'):
            if self.achievement_timer > 0:
                self.draw_text(self.achievement_text, WIDTH // 2, 100, center=True, color=COLORS['GREEN'])
                self.achievement_timer -= 1

    def draw_game_state(self):
        if self.game_over:
            self.draw_text("Game Over! Press R to restart", WIDTH // 2, HEIGHT // 2, center=True)
        elif self.paused:
            self.draw_text("PAUSED", WIDTH // 2, HEIGHT // 2, center=True)

    def draw_text(self, text, x, y, color=COLORS['WHITE'], center=False, size=36):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_lives(self):
        for i in range(self.lives):
            self.screen.blit(self.images['life'], (WIDTH - 60 - i * 40, 60))
