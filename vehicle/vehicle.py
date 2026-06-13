# 차량 전반적인 기능
import pygame
import math
from config.settings import *

class Vehicle():
    def __init__(self, x, y):
        # 위치, 물리 변수 
        self.x = float(x)
        self.y = float(y)
        self.speed = 0.0
        self.angle = 0.0 # 차량 바라보는 방향 (0도 = 우측)
        self.steer_angle = 0.0 # 바퀴 조향각
        
        # 차량 크기
        self.width = VEHICLE_WIDTH
        self.height = VEHICLE_HEIGHT
        self.wheelbase = VEHICLE_WHEELBASE # 바퀴 축거
        
        # 물리 제한 상수
        self.MAX_SPEED = VEHICLE_MAX_SPEED
        self.MAX_STEER = VEHICLE_MAX_STEER # 최대 조향각
        
        self.ACCEL = VEHICLE_ACCEL # 가속도
        self.DECEL = DECEL # 자연 감속도       
        
        self.STEER_SPEED = VEHICLE_STEER_SPEED
        self.STEER_DECEL = VEHICLE_STEER_DECEL
        
        # img
        self.image = pygame.image.load("assets/vehicle.png").convert_alpha()
        self.image = pygame.transform.smoothscale(
            self.image,
            (self.width, self.height)
        )
        self.image = pygame.transform.rotate(self.image, 180)
    
    def get_vertices(self):
        rad = math.radians(self.angle)
        
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # 앞우, 앞좌, 뒤좌, 뒤우
        local_points = [
            (self.width / 2, self.height / 2),
            (self.width / 2, -self.height / 2),
            (-self.width / 2, -self.height / 2),
            (-self.width / 2, self.height / 2),
        ]
        
        vertices = []
        
        for lx, ly in local_points:
            wx = self.x + (lx * cos_a - ly * sin_a)
            wy = self.y + (lx * sin_a + ly * cos_a)
            vertices.append((wx, wy))
        
        return vertices
    
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        accel_input = 0.0
        steer_input = 0.0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            accel_input += 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            accel_input -= 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            steer_input -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            steer_input += 1.0
        
        # 속도 처리  
        if accel_input != 0.0:
            self.speed += accel_input * self.ACCEL * dt
        else:
            if self.speed > 0:
                self.speed = max(self.speed - self.DECEL * dt, 0.0)
            elif self.speed < 0:
                self.speed = min(self.speed + self.DECEL * dt, 0.0)
        
        # 속도 범위 처리
        self.speed = max(-self.MAX_SPEED * 0.75, min(self.speed, self.MAX_SPEED))
        
        # 조향각 처리
        if steer_input != 0:
            self.steer_angle += steer_input * self.STEER_SPEED * dt
        else:
            # 자연 감속
            if self.steer_angle > 0:
                self.steer_angle = max(self.steer_angle - self.STEER_DECEL * dt, 0.0)
            elif self.steer_angle < 0:
                self.steer_angle = min(self.steer_angle + self.STEER_DECEL * dt, 0.0)
                
        # 조향각 범위 처리
        self.steer_angle = max(
            -self.MAX_STEER,
            min(self.steer_angle, self.MAX_STEER)
        )
        
    def update(self, dt):
        # 현재 구조
        # 다른 곳에서 speed와 steer을 다룸
        # 여기선 현재의 speed와 steer 기반 다음 위치 계산하는 함수
        
        steer_rad = math.radians(self.steer_angle)
        
        # Bicycle Kinematic Model 참고
        if abs(self.speed) > 1e-3 and abs(steer_rad) > 1e-6:
            # 각속도 계산
            angular_velocity = (self.speed / self.wheelbase) * math.tan(steer_rad)
            
            self.angle += math.degrees(angular_velocity * dt)
        
        self.angle %= 360
        
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad) * dt
        self.y += self.speed * math.sin(rad) * dt
    
    def draw(self, screen, camera_x = 0, camera_y = 0):
        
        world_vertices = self.get_vertices()
        screen_vertices = [(vx - camera_x, vy - camera_y) for vx, vy in world_vertices]
        
        pygame.draw.polygon(
            screen,
            (255, 0, 0),
            screen_vertices,
            1
        )
        
        # img 설정
        rotated_img = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated_img.get_rect(
            center=(self.x - camera_x, self.y - camera_y)
        )
        
        screen.blit(rotated_img, rect)