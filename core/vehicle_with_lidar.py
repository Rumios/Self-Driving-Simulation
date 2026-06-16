import pygame
import math
from config.settings import *

class Vehicle():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = 0.0
        self.angle = 0.0 
        self.steer_angle = 0.0 
        
        self.width = VEHICLE_WIDTH
        self.height = VEHICLE_HEIGHT
        self.wheelbase = VEHICLE_WHEELBASE 
        
        self.MAX_SPEED = VEHICLE_MAX_SPEED
        self.MAX_STEER = VEHICLE_MAX_STEER 
        self.ACCEL = VEHICLE_ACCEL 
        self.DECEL = DECEL        
        
        self.image = pygame.image.load("assets/vehicle.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        self.image = pygame.transform.rotate(self.image, 180)
        
        # [추가] 센서 감지 포인트 저장용
        self.sensor_points = []
    
    def get_vertices(self):
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
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
    
    # [추가] DQN 전용 8차원 State(상태) 추출 함수
    def get_state(self, obstacles, goal_x, goal_y):
        # 1. 목적지까지의 거리 및 상대 각도 계산
        dx = goal_x - self.x
        dy = goal_y - self.y
        goal_dist = math.hypot(dx, dy)
        
        target_angle = math.degrees(math.atan2(dy, dx)) - self.angle
        target_angle = (target_angle + 180) % 360 - 180 # -180 ~ 180 정규화
        
        # 2. 5방향 라이다(Lidar) 센서 레이캐스팅 (-60도, -30도, 0도, 30도, 60도)
        sensor_angles = [-60, -30, 0, 30, 60]
        max_sensor_range = 150.0
        sensor_inputs = []
        self.sensor_points = []
        
        for sa in sensor_angles:
            rad = math.radians(self.angle + sa)
            hit_dist = max_sensor_range
            
            # 10픽셀 단위로 전방 탐색
            for d in range(0, int(max_sensor_range), 10):
                sx = self.x + d * math.cos(rad)
                sy = self.y + d * math.sin(rad)
                
                # 장애물 충돌 check
                hit = False
                for obj in obstacles:
                    if obj.rect.collidepoint(sx, sy):
                        hit_dist = d
                        hit = True
                        break
                if hit: break
                
            sensor_inputs.append(hit_dist / max_sensor_range) # 0 ~ 1 정규화
            self.sensor_points.append((self.x + hit_dist * math.cos(rad), self.y + hit_dist * math.sin(rad)))
            
        # 총 8차원 벡터 반환
        state = [
            self.speed / self.MAX_SPEED,
            target_angle / 180.0,
            min(goal_dist / 1000.0, 1.0)
        ] + sensor_inputs
        return state

    # [추가] DQN의 Discrete Action(0~3)을 차량 제어로 변환
    def apply_action(self, action_idx):
        if action_idx == 0:   # 좌회전 + 가속
            self.steer_angle = -self.MAX_STEER
            self.speed = min(self.speed + self.ACCEL, self.MAX_SPEED)
        elif action_idx == 1: # 직진 + 가속
            self.steer_angle = 0.0
            self.speed = min(self.speed + self.ACCEL, self.MAX_SPEED)
        elif action_idx == 2: # 우회전 + 가속
            self.steer_angle = self.MAX_STEER
            self.speed = min(self.speed + self.ACCEL, self.MAX_SPEED)
        elif action_idx == 3: # 감속 / 브레이크
            self.steer_angle = 0.0
            self.speed = max(self.speed - self.ACCEL * 1.5, 0.0)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.steer_angle = -self.MAX_STEER
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.steer_angle = self.MAX_STEER
        else: self.steer_angle = 0.0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.speed = min(self.speed + self.ACCEL, self.MAX_SPEED)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]: self.speed = max(self.speed - self.ACCEL, -self.MAX_SPEED * 0.85)
        else:
            if self.speed > 0: self.speed = max(self.speed - self.DECEL, 0.0)
            elif self.speed < 0: self.speed = min(self.speed + self.DECEL, 0.0)
        
    def update(self):
        steer_rad = math.radians(self.steer_angle)
        if abs(steer_rad) > 0.001:            
            angular_velocity = (self.speed / self.wheelbase) * math.tan(steer_rad)
            self.angle += math.degrees(angular_velocity)
        
        self.angle %= 360
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        # [있어보이는 포인트 1] 라이다 센서 광선 시각화 (Cyan 색상 레이저 레이)
        for sx, sy in self.sensor_points:
            pygame.draw.line(screen, (0, 180, 255), (self.x - camera_x, self.y - camera_y), (sx - camera_x, sy - camera_y), 1)
            pygame.draw.circle(screen, (255, 50, 50), (int(sx - camera_x), int(sy - camera_y)), 3)

        world_vertices = self.get_vertices()
        screen_vertices = [(vx - camera_x, vy - camera_y) for vx, vy in world_vertices]
        pygame.draw.polygon(screen, (255, 0, 0), screen_vertices, 1)
        
        rotated_img = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated_img.get_rect(center=(self.x - camera_x, self.y - camera_y))
        screen.blit(rotated_img, rect)