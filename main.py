import pygame
from config.settings import *
from core.sensor import Sensor
from core.object import Object
from ui.minimap import Minimap

# 초기화
pygame.init()

screen_width = SCREEN_WIDTH
screen_height = SCREEN_HEIGHT

# 화면 설정
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sensor Simulation")

# font 설정
font = pygame.font.Font(None, 36)

objects = [
    Object(screen_width // 2 + 100, screen_height // 2 - 40, 50, 80)
]

sensor = Sensor(screen_width // 2, screen_height // 2)
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
            
    # 충돌 시 통과하지 못하게 해야함.
    sensor.handle_input()
    
    # 배경
    screen.fill(BG_COLOR)
    
    # 객체 렌더링
    for obj in objects:
        obj.draw(screen)
    
    # Dynamic Obstacle Avoidance를 위해 맵 클리어링을 주기적으로 해야함. (향후 업데이트)
    # 센서 & Minimap 렌더링
    sensor.draw(screen, font, True, objects)
    minimap.draw(screen, sensor)
    
    # 화면 업데이트
    pygame.display.flip()

pygame.quit()