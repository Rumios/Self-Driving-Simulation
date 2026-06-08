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
        self.btn_font = pygame.font.SysFont("arial", 12, bold=True)
        
        # 중복 방지 절대 좌표 map
        self.global_map = set()
        
        # LOCAL / GLOBAL
        self.view_mode = "LOCAL"
        self.btn_rect_in_surf = pygame.Rect(self.width - 65, self.height - 32, 55, 22)
        
        # 실제 메인 스크린 마우스 클릭 감지용 전역 마우스 Rect
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
        
        # 실시간 데이터 global_map에 누적 기록
        for dx, dy, r, abs_rad in sensor.point_cloud:
            if r >= settings.RAY_MAX_RANGE:
                continue
            
            world_hit_x = sensor.x + r * math.cos(abs_rad)
            world_hit_y = sensor.y + r * math.sin(abs_rad)
            
            self.global_map.add((int(world_hit_x), int(world_hit_y)))
        
        # LOCAL VIEW 모드 (플레이어 기준 회전 및 확대)
        if self.view_mode == "LOCAL":
            for wx, wy in self.global_map:
                lx = wx - sensor.x
                ly = wy - sensor.y
                
                # 센서 방향 정면 고정을 위한 2D 회전 변환 행렬 적용
                rad = math.radians(-sensor.angle - 90)
                rx = lx * math.cos(rad) - ly * math.sin(rad)
                ry = lx * math.sin(rad) + ly * math.cos(rad)
                
                draw_x = (rx * scale) + self.center_x
                draw_y = (ry * scale) + self.center_y
                
                if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                    pygame.draw.circle(surface, settings.MINIMAP_POINT_COLOR, (int(draw_x), int(draw_y)), 1)
                
            # 센서 본체 고정 표시
            pygame.draw.circle(surface, (0, 200, 80), (self.center_x, self.center_y), 6)
            arrow_color = (200, 200, 200, 150)
            
            start_p = (self.center_x - 1, self.center_y)
            end_p = (self.center_x - 1, self.center_y - 12)
            pygame.draw.line(surface, arrow_color, start_p, end_p, 2)
            pygame.draw.line(surface, arrow_color, end_p, (end_p[0] - 3, end_p[1] + 4), 2)
            pygame.draw.line(surface, arrow_color, end_p, (end_p[0] + 3, end_p[1] + 4), 2)

        # GLOBAL VIEW 모드 (전체 지도를 내려다보는 월드 고정 뷰)
        else:
            global_scale = scale * 0.25 

            world_center_x = settings.SCREEN_WIDTH // 2
            world_center_y = settings.SCREEN_HEIGHT // 2
            
            # 점 렌더링
            for wx, wy in self.global_map:
                rx = wx - world_center_x
                ry = wy - world_center_y
                
                draw_x = (rx * global_scale) + self.center_x
                draw_y = (ry * global_scale) + self.center_y
                
                if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                    pygame.draw.circle(surface, settings.MINIMAP_POINT_COLOR, (int(draw_x), int(draw_y)), 1)
            
            s_rx = sensor.x - world_center_x
            s_ry = sensor.y - world_center_y
            s_draw_x = (s_rx * global_scale) + self.center_x
            s_draw_y = (s_ry * global_scale) + self.center_y
            
            if 0 <= s_draw_x < self.width and 0 <= s_draw_y < self.height:
                pygame.draw.circle(surface, (0, 200, 80), (int(s_draw_x), int(s_draw_y)), 5)
                s_rad = math.radians(sensor.angle)
                line_len = 12
                s_end_x = s_draw_x + line_len * math.cos(s_rad)
                s_end_y = s_draw_y + line_len * math.sin(s_rad)
                
                p_start = (int(s_draw_x), int(s_draw_y))
                p_end = (int(s_end_x), int(s_end_y))
                
                pygame.draw.line(surface, (255, 255, 255), p_start, p_end, 2)
                
                wing_len = 5
                wing_angle = math.radians(145)
                
                # 왼쪽 날개 끝점 계산
                left_wing_x = p_end[0] + wing_len * math.cos(s_rad + wing_angle)
                left_wing_y = p_end[1] + wing_len * math.sin(s_rad + wing_angle)
                
                # 오른쪽 날개 끝점 계산
                right_wing_x = p_end[0] + wing_len * math.cos(s_rad - wing_angle)
                right_wing_y = p_end[1] + wing_len * math.sin(s_rad - wing_angle)
                
                # 두께 2를 적용하여 날개선 그리기
                pygame.draw.line(surface, (255, 255, 255), p_end, (int(left_wing_x), int(left_wing_y)), 2)
                pygame.draw.line(surface, (255, 255, 255), p_end, (int(right_wing_x), int(right_wing_y)), 2)

        # 모드 텍스트 좌상단 indicator
        mode_text = self.mini_font.render(f"MODE: {self.view_mode}", True, (200, 200, 200))
        surface.blit(mode_text, (8, 8))
        
        # 우하단 토글 버튼
        btn_color = (60, 80, 100) if self.view_mode == "LOCAL" else (100, 60, 60)
        pygame.draw.rect(surface, btn_color, self.btn_rect_in_surf, border_radius=4)
        pygame.draw.rect(surface, (150, 150, 150), self.btn_rect_in_surf, 1, border_radius=4)
        
        # 버튼 문자열 중앙 정렬 배치
        btn_str = "GLOBAL" if self.view_mode == "LOCAL" else "LOCAL"
        btn_text = self.btn_font.render(btn_str, True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=self.btn_rect_in_surf.center)
        surface.blit(btn_text, text_rect)
        
        # 테두리 마감 및 메인 스크린에 출력
        pygame.draw.rect(surface, (50, 50, 50), (0, 0, self.width, self.height), 3)
        screen.blit(surface, (self.pos_x, self.pos_y))