import pygame
import config.settings as settings

class Object:
    def __init__(self, x, y, width, height, color = settings.OBJECT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # 객체 경계선
        pygame.draw.rect(screen, settings.BORDER_COLOR, self.rect, 2)