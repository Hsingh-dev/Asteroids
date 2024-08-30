import pygame
from game import AsteroidAvoidanceGame

if __name__ == "__main__":
    try:
        pygame.init()
        pygame.mixer.init()
        game = AsteroidAvoidanceGame()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()
