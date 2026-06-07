import pygame
import pygame.gfxdraw
import math
import config.settings as settings

# sensor class
class Sensor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.angle = 0 # 센서의 초기 방향
        self.fov = 60 # 시야각
        self.max_range = settings.RAY_MAX_RANGE # 최대 감지 범위 (임시값)
        
        # 색상 설정
        self.body_color = settings.RED
        self.text_color = settings.BLACK
        self.range_color = settings.SENSOR_RANGE_COLOR
        self.ray_color = settings.RAY_COLOR
        self.HIT_RAY_COLOR = settings.HIT_RAY_COLOR
        
        self.point_cloud = [] # 감지된 점들의 상대적 좌표 리스트 (dx, dy)

    def draw(self, screen, font, is_active, obstacles):
        self.point_cloud.clear()
        
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
        screen.blit(range_surface, (self.x - self.max_range, self.y - self.max_range))
        
        # Ray 렌더링
        # 방식
        # 1. 일정 간격으로 Ray 발사 (임시값: 5도 간격)
        # 2. 각 Ray를 각각 일정 간격마다 점검하여 오브젝트 충돌 여부 확인
        # 3. 충돌한다면 Raycasting 방식을 활용해 닿은 지점과 센서 사이의 거리를 도출
        # 4. 거리와 Ray 각도를 알고 있으므로 Lidar 3D 방식을 2D 방식으로 처리해서 sin, cos로 상대적 끝점 좌표 계산
        
        # 실제 Lidar 방식과의 차이점
        # Lidar에서는 돌아오는 시간과 빛의 속력으로 거리를 계산하지만 여기서는 단순히 충돌 지점까지의 거리를 계산하는 방식

        angle_interval = 4 # Ray 간격 (임시값)
        if is_active:
            for angle in range(start_angle, end_angle + 1, angle_interval):
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
                end_x = self.x + final_r * math.cos(rad)
                end_y = self.y + final_r * math.sin(rad)
                
                pygame.draw.line(screen, current_ray_color, (self.x, self.y), (end_x, end_y), 2)
        
        # 본체 렌더링
        pygame.draw.circle(screen, self.body_color, (self.x, self.y), self.radius)
        text_surface = font.render("S", True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x, self.y + (self.radius * 0.1)))
        screen.blit(text_surface, text_rect)
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.angle -= settings.ROT_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.angle += settings.ROT_SPEED
        
        self.angle %= 360
        
        # 방향 벡터
        rad = math.radians(self.angle)
        move_x = settings.SPEED * math.cos(rad)
        move_y = settings.SPEED * math.sin(rad)
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.x += move_x
            self.y += move_y
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.x -= move_x
            self.y -= move_y