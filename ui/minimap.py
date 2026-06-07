import pygame
import config.settings as settings
import math

class Minimap:
    def __init__(self):
        self.width = settings.MINIMAP_WIDTH
        self.height = settings.MINIMAP_HEIGHT
        self.pos_x = 10
        self.pos_y = 10
        
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        self.mini_font = pygame.font.SysFont("malgungothic", 12)
        self.btn_font = pygame.font.SysFont("arial", 14, bold=True)
        
        # 중복 방지 절대 좌표 map
        self.global_map = set()
        
        # LOCAL / GLOBAL
        self.view_mode = "LOCAL"
        
        self.btn_rect_in_surf = pygame.Rect(165, 165, 25, 25)
        
        self.btn_rect = pygame.Rect(
            self.pos_x + self.btn_rect_in_surf.x,
            self.pos_y + self.btn_rect_in_surf.y,
            self.btn_rect_in_surf.width,
            self.btn_rect_in_surf.height
        )        
    
    def check_click(self, mouse_pos):
        if self.btn_rect.collidepoint(mouse_pos):
            if self.view_mode == "LOCAL":
                self.view_mode = "GLOBAL"
            else:
                self.view_mode = "LOCAL"
    
    def draw(self, screen, sensor):
        surface = pygame.Surface((self.width, self.height))
        surface.fill(settings.MINIMAP_BG_COLOR)
        
        # 축적 배율 적용
        scale = getattr(settings, 'MINIMAP_SCALE', 0.5)
        
        pygame.draw.rect(surface, (70, 70, 70), (0, 0, self.width, self.height), 1)
        
        for dx, dy, r, abs_rad in sensor.point_cloud:
            # 최대 사정거리 내 점만 렌더링
            if r >= settings.RAY_MAX_RANGE:
                continue
            
            world_hit_x = sensor.x + r * math.cos(abs_rad)
            world_hit_y = sensor.y + r * math.sin(abs_rad)
            
            self.global_map.add((int(world_hit_x), int(world_hit_y)))
        
        # 상대 좌표
        # Q. dx, dy는 센서를 무조건 (0, 0)으로 설정. 그렇기 때문에 '상대적인 거리'를 구할 수 있음. 그러니까 왜 dx, dy를 안 씀?
        # A. 회전 시에 dx, dy는 여전히 그 방향의 값을 가지고 있으므로 좌표가 꼬임. 그렇기 때문에 절대 좌표로 매핑한 이후에 하는 것.
        if self.view_mode == "LOCAL":
            # 점
            for wx, wy in self.global_map:
                lx = wx - sensor.x
                ly = wy - sensor.y
                
                # Sensor 정면이 항시 위로 고정 (회전율 고려)
                # rad의 각도는 단위원에서 1사분면
                # 그러나 minimap에서는 단위원에서 4사분면
                # 그렇기 때문에 역회전을 시켜주고 정면 고정을 위해 90도 더 회전.
                
                # 2D 회전 변환 행렬 공식 참고
                rad = math.radians(-sensor.angle - 90)
                rx = lx * math.cos(rad) - ly * math.sin(rad)
                ry = lx * math.sin(rad) + ly * math.cos(rad)
                
                draw_x = (rx * scale) + self.width // 2
                draw_y = (ry * scale) + self.height // 2
                
                if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                    pygame.draw.circle(surface, settings.MINIMAP_POINT_COLOR, (int(draw_x), int(draw_y)), 1)
                
            # 센서, 방향선
            pygame.draw.circle(surface, (0, 200, 80), (self.center_x, self.center_y), 6)
            arrow_color = (200, 200, 200, 150)
            
            start_p = (self.center_x - 1, self.center_y)
            end_p = (self.center_x - 1, self.center_y - 15)
            
            pygame.draw.line(surface, arrow_color, start_p, end_p, 2)
            
            left_wing = (end_p[0] - 3, end_p[1] + 4)
            right_wing = (end_p[0] + 3, end_p[1] + 4)
            
            pygame.draw.line(surface, arrow_color, end_p, left_wing, 2)
            pygame.draw.line(surface, arrow_color, end_p, right_wing, 2)
            
                       
            # 외각선
            pygame.draw.rect(surface, (50, 50, 50), (0, 0, self.width, self.height), 3)
            
            screen.blit(surface, (self.pos_x, self.pos_y))
                
                
                
        else:
            # GLOBAL VIEW
            pass
            