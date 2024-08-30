import pygame
import os

# Get the current directory of the assets.py file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the game folder
game_dir = os.path.dirname(current_dir)
# Define paths to asset folders
images_dir = os.path.join(game_dir, 'assets', 'images')
sounds_dir = os.path.join(game_dir, 'assets', 'sounds')

def load_and_scale(path, width, height):
    return pygame.transform.scale(pygame.image.load(path), (width, height))

def load_assets():
    images = {
        'spaceship': load_and_scale(os.path.join(images_dir, "spaceship.png"), 60, 60),
        'asteroid': load_and_scale(os.path.join(images_dir, "asteroid.png"), 50, 50),
        'point': load_and_scale(os.path.join(images_dir, "point.png"), 50, 50),
        'shield': load_and_scale(os.path.join(images_dir, "shield.png"), 50, 50),
        'life': load_and_scale(os.path.join(images_dir, "life.png"), 50, 50),
        'rapid_fire': load_and_scale(os.path.join(images_dir, "rapid_fire.png"), 50, 50)
    }
    images['boss_asteroid'] = pygame.transform.scale(images['asteroid'], (100, 100))
    return images

def load_sounds():
    sounds = {
        'explosion': pygame.mixer.Sound(os.path.join(sounds_dir, "explosion.mp3")),
        'point': pygame.mixer.Sound(os.path.join(sounds_dir, "point.mp3")),
        'powerup': pygame.mixer.Sound(os.path.join(sounds_dir, "powerup.mp3"))
    }
    pygame.mixer.music.load(os.path.join(sounds_dir, "background_music.mp3"))
    return sounds
