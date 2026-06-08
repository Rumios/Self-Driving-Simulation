import pygame
from config.settings import *
from core.sensor import Sensor
from core.object import Object
from ui.minimap import Minimap
from map.test_map import load_test_map

# 초기화
pygame.init()

# 화면 설정
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sensor Simulation")

# font 설정
font = pygame.font.Font(None, 36)

objects = load_test_map()

sensor = Sensor(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
minimap = Minimap()

# 게임 루프 변수
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                minimap.check_click(event.pos)
            
    # 충돌 시 통과하지 못하게 해야함.
    sensor.handle_input(objects)
    
    # 센서 정중앙에 고정
    camera_x = sensor.x - (SCREEN_WIDTH // 2)
    camera_y = sensor.y - (SCREEN_HEIGHT // 2)
    
    # 배경
    screen.fill(BG_COLOR)
    
    # 객체 렌더링
    for obj in objects:
        obj.draw(screen, camera_x, camera_y)
    
    # Dynamic Obstacle Avoidance를 위해 맵 클리어링을 주기적으로 해야함. (향후 업데이트)
    # 센서 & Minimap 렌더링
    sensor.draw(screen, font, True, objects, camera_x, camera_y)
    minimap.draw(screen, sensor)
    
    # 화면 업데이트
    pygame.display.flip()

pygame.quit()