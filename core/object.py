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
        
class DynamicObject(Object):
    def __init__(self, x, y, width, height, speed, move_range, axis='y', color=settings.RED):
        super().__init__(x, y, width, height, color)
        # 시작 좌표도 실수형(float)으로 저장
        self.start_x = float(x)
        self.start_y = float(y)
        
        # [핵심] 소수점 단위의 미세한 움직임을 누적할 실제 좌표 변수
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.speed = float(speed)
        self.move_range = move_range  
        self.axis = axis              
        self.direction = 1            
    
    def update(self):
        # 지정된 축을 따라 이동 (실수형 변수에 누적)
        if self.axis == 'x':
            self.float_x += self.speed * self.direction
            self.rect.x = int(self.float_x) # 화면(rect)에는 정수로 변환해서 덮어씌움
            
            if abs(self.float_x - self.start_x) >= self.move_range:
                self.direction *= -1
                
        elif self.axis == 'y':
            self.float_y += self.speed * self.direction
            self.rect.y = int(self.float_y) # 화면(rect)에는 정수로 변환해서 덮어씌움
            
            if abs(self.float_y - self.start_y) >= self.move_range:
                self.direction *= -1