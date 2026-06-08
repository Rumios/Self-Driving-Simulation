import pygame
import pygame.gfxdraw
import math
from config.settings import *

# sensor class
class Sensor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.angle = 0 # 센서의 초기 방향
        self.fov = 60 # 시야각
        self.max_range = RAY_MAX_RANGE # 최대 감지 범위 (임시값)
        self.angle_interval = 3 # Ray 간격 (임시값)
        
        # 색상 설정
        self.body_color = RED
        self.text_color = BLACK
        self.range_color = SENSOR_RANGE_COLOR
        self.ray_color = RAY_COLOR
        self.HIT_RAY_COLOR = HIT_RAY_COLOR
        
        self.point_cloud = [] # 감지된 점들의 상대적 좌표 리스트 (dx, dy)

    def draw(self, screen, font, is_active, obstacles, camera_x = 0, camera_y = 0):
        self.point_cloud.clear()
        
        screen_sensor_x = self.x - camera_x
        screen_sensor_y = self.y - camera_y
        
        # 감지 범위 렌더링
        surface_size = self.max_range * 2
        range_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        
        # 가상 surf 중심 (센서)
        center_x = self.max_range
        center_y = self.max_range
        
        points = [(center_x, center_y)]
        
        start_angle = self.angle - self.fov // 2
        end_angle = self.angle + self.fov // 2
        
        for angle in range(start_angle, end_angle + 1, 1):
            rad = math.radians(angle)
            px = center_x + self.max_range * math.cos(rad)
            py = center_y + self.max_range * math.sin(rad)
            points.append((px, py))
        
        if len(points) >= 3:
            # pygame.gfxdraw.filled_polygon alpha 오류 해결 -> RGB 변환, surf alpha 변경으로 해결
            pure_rgb = (self.range_color[0], self.range_color[1], self.range_color[2])
            pygame.gfxdraw.filled_polygon(range_surface, points, pure_rgb)
            
            alpha = self.range_color[3]
            range_surface.set_alpha(alpha)
        
        # 부채꼴 렌더링
        screen.blit(range_surface, (screen_sensor_x - self.max_range, screen_sensor_y - self.max_range))
        
        # Ray 렌더링
        # 방식
        # 1. 일정 간격으로 Ray 발사 (임시값: 5도 간격)
        # 2. 각 Ray를 각각 일정 간격마다 점검하여 오브젝트 충돌 여부 확인
        # 3. 충돌한다면 Raycasting 방식을 활용해 닿은 지점과 센서 사이의 거리를 도출
        # 4. 거리와 Ray 각도를 알고 있으므로 Lidar 3D 방식을 2D 방식으로 처리해서 sin, cos로 상대적 끝점 좌표 계산
        
        # 실제 Lidar 방식과의 차이점
        # Lidar에서는 돌아오는 시간과 빛의 속력으로 거리를 계산하지만 여기서는 단순히 충돌 지점까지의 거리를 계산하는 방식

        if is_active:
            for angle in range(start_angle, end_angle + 1, self.angle_interval):
                rad = math.radians(angle)
                
                # degree -> radian 변환
                relative_angle = (angle - self.angle) % 360
                relative_rad = math.radians(relative_angle)
                
                # hit = False
                final_r = self.max_range
                current_ray_color = self.ray_color
                
                for r in range(1, self.max_range + 1, 1):
                    check_x = self.x + r * math.cos(rad)
                    check_y = self.y + r * math.sin(rad)
                    
                    # 충돌 check
                    collision_detected = False
                    for obj in obstacles:
                        if obj.rect.collidepoint(check_x, check_y):
                            # hit = True
                            final_r = r
                            current_ray_color = self.HIT_RAY_COLOR
                            collision_detected = True
                            break
                            
                    if collision_detected:
                        break
                
                relative_angle = (angle - self.angle) % 360
                relative_rad = math.radians(relative_angle)
                
                # 상대적 끝점 좌표
                dx = final_r * math.cos(relative_rad)
                dy = final_r * math.sin(relative_rad)
                
                # 2D Lidar 실제 데이터 형태로 저장 (dx, dy, dist, rad)
                self.point_cloud.append((dx, dy, final_r, rad))
                
                # 절대 좌표 (월드 각도)
                end_x = self.x + final_r * math.cos(rad) - camera_x
                end_y = self.y + final_r * math.sin(rad) - camera_y
                
                pygame.draw.line(screen, current_ray_color, (screen_sensor_x, screen_sensor_y), (end_x, end_y), 2)
        
        # 본체 렌더링
        pygame.draw.circle(screen, BLACK, (screen_sensor_x, screen_sensor_y), self.radius + 2)
        pygame.draw.circle(screen, self.body_color, (screen_sensor_x, screen_sensor_y), self.radius)
        
        arrow_head_size = 8
        arrow_body_size = 3
        
        rad = math.radians(self.angle)
        
        start_x = screen_sensor_x - (self.radius - 5) * math.cos(rad)
        start_y = screen_sensor_y - (self.radius - 5) * math.sin(rad)
        
        end_x = screen_sensor_x + (self.radius - 5) * math.cos(rad)
        end_y = screen_sensor_y + (self.radius - 5) * math.sin(rad)
        
        pygame.draw.line(
            screen,
            BLACK,
            (start_x, start_y),
            (end_x, end_y),
            arrow_body_size
        )
        
        left_rad = rad + math.radians(150)
        right_rad = rad - math.radians(150)

        left_x = end_x + arrow_head_size * math.cos(left_rad)
        left_y = end_y + arrow_head_size * math.sin(left_rad)

        right_x = end_x + arrow_head_size * math.cos(right_rad)
        right_y = end_y + arrow_head_size * math.sin(right_rad)

        pygame.draw.line(
            screen,
            BLACK,
            (end_x, end_y),
            (left_x, left_y),
            4
        )

        pygame.draw.line(
            screen,
            BLACK,
            (end_x, end_y),
            (right_x, right_y),
            4
        )
    
    def handle_input(self, obstacles):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.angle -= ROT_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.angle += ROT_SPEED
        
        self.angle %= 360
        
        # 방향 벡터
        rad = math.radians(self.angle)
        move_x = SPEED * math.cos(rad)
        move_y = SPEED * math.sin(rad)
        
        # 이동 변위
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dx += move_x
            dy += move_y
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dx -= move_x
            dy -= move_y
            
        if dx != 0 or dy != 0:
            # 슬라이딩 충돌 판정
            # X, Y축 동시에 검사하면 벽에 부딫히는 순간 멈춰버림.
            # 그러나 따로 분리 검사 시, 열려있는 축으로 미끄러지도록 처리 가능
            
            # X축 검사
            next_x = self.x + dx
            can_move_x = True
            
            for obj in obstacles:
                if not hasattr(obj, "rect"):
                    continue
                
                # 원의 중심과 가장 가까운 점 찾기
                closest_x = max(obj.rect.left, min(next_x, obj.rect.right))
                closest_y = max(obj.rect.top, min(self.y, obj.rect.bottom))
                
                # 거리 계산
                dist = (next_x - closest_x) ** 2 + (self.y - closest_y) ** 2
                
                if dist < self.radius ** 2:
                    can_move_x = False
                    break
            
            if can_move_x:
               self.x = next_x 
            
            # Y축 검사
            next_y = self.y + dy
            can_move_y = True
            
            for obj in obstacles:
                if not hasattr(obj, "rect"):
                    continue
                
                # 원의 중심과 가장 가까운 점 찾기
                closest_x = max(obj.rect.left, min(self.x, obj.rect.right))
                closest_y = max(obj.rect.top, min(next_y, obj.rect.bottom))
                
                # 거리 계산
                dist = (self.x - closest_x) ** 2 + (next_y - closest_y) ** 2
                
                if dist < self.radius ** 2:
                    can_move_y = False
                    break
            
            if can_move_y:
                self.y = next_y