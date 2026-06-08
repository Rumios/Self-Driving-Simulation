import pygame
import config.settings as settings

class Object:
    def __init__(self, x, y, width, height, color = settings.OBJECT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    
    def draw(self, screen, camera_x = 0, camera_y = 0):
        # 카메라 위치만큼 빼서 배치
        screen_rect = self.rect.move(-camera_x, -camera_y)
        
        pygame.draw.rect(screen, self.color, screen_rect)
        # 객체 경계선
        pygame.draw.rect(screen, settings.BORDER_COLOR, screen_rect, 2)