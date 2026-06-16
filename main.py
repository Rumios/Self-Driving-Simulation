# 최종 목표 : 도시 규모의 맵에서 원하는 목적지까지 이동하는 (교통 법규를 지키며) AI 제작
# Algorithm : DQN
# 이동은 Grid 형태가 아니라 대각이든 어디로든 이동할 수 있게.
# 1차적으로 우선 자동차 이동 시스템을 구현하기.

import pygame
from config.settings import *
from core.vehicle import Vehicle
from map.map_parser import parse_map_to_objects, get_start_position, get_goal_position, CELL_SIZE
from map.map_data import get_grid_map
from rule import RuleManager

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Self_Driving_Simulation")

grid = get_grid_map()
objects = parse_map_to_objects(grid)
start_x, start_y = get_start_position(grid)
goal_x, goal_y = get_goal_position(grid)

vehicle = Vehicle(start_x, start_y)

rule_manager = RuleManager(vehicle, objects)

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BG_COLOR)
    
    # 차량 중앙에 고정
    camera_x = vehicle.x - (SCREEN_WIDTH // 2)
    camera_y = vehicle.y - (SCREEN_HEIGHT // 2)

    start_tile_x = start_x - (CELL_SIZE // 2) - camera_x
    start_tile_y = start_y - (CELL_SIZE // 2) - camera_y
    goal_tile_x = goal_x - (CELL_SIZE // 2) - camera_x
    goal_tile_y = goal_y - (CELL_SIZE // 2) - camera_y
    
    pygame.draw.rect(screen, GREEN, (start_tile_x, start_tile_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, YELLOW, (goal_tile_x, goal_tile_y, CELL_SIZE, CELL_SIZE))
    
    for obj in objects:
        obj.draw(screen, camera_x, camera_y)
    
    vehicle.handle_input()
    vehicle.update()
    
    # 이후에 DQN으로 학습 시, 부딪혔을 때 초기화 용
    is_collided = rule_manager.update()
    
    vehicle.draw(screen, camera_x, camera_y)
    
    pygame.display.flip()

pygame.quit()