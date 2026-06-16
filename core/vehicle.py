# 차량 전반적인 기능

"""
DQN 접목 방식

목적지까지의 최소 waypoint를 만들어서 그곳으로 가는 최소한의 경로를 짜는 방식

이 waypoint를 찍는 방식을 생각해봐야함.

todo_list
1. 맵 전체를 데이터화
2. 최소 경로 알고리즘(A* algorithm 사용)
3. DQN 접목

1. state
State = [
    speed,
    steer_angle,
    wp_dist,
    wp_angle
]
"""


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
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # 조향각 제어
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.steer_angle = -self.MAX_STEER
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.steer_angle = self.MAX_STEER
        else:
            self.steer_angle = 0.0 # 키 때야 조정
        
        # 속도 제어
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.speed = min(self.speed + self.ACCEL, self.MAX_SPEED)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.ACCEL, -self.MAX_SPEED * 0.85) # 후진 속도 제한
        else:
            # 최소 속도
            if self.speed > 0:
                self.speed = max(self.speed - self.DECEL, 0.0) # 매 프레임마다 감속
            elif self.speed < 0:
                self.speed = min(self.speed + self.DECEL, 0.0)
        
    def update(self):
        # 현재 구조
        # 다른 곳에서 speed와 steer을 다룸
        # 여기선 현재의 speed와 steer 기반 다음 위치 계산하는 함수
        
        # Bicycle Kinematic Model 참고
        steer_rad = math.radians(self.steer_angle)
        # 한 프레임 동안 회전할 각도 변량
        if abs(steer_rad) > 0.001:            
            angular_velocity = (self.speed / self.wheelbase) * math.tan(steer_rad)
        
            self.angle += math.degrees(angular_velocity)
        
        self.angle %= 360
        
        # 실제 연산
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
    
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