# 최종 목표 : 도시 규모의 맵에서 원하는 목적지까지 이동하는 (교통 법규를 지키며) AI 제작
# Algorithm : DQN
# Map은 10 x 10으로.
# 이동은 Grid 형태가 아니라 대각이든 어디로든 이동할 수 있게.
# 1차적으로 우선 자동차 이동 시스템을 구현하기.

import pygame
from config.settings import *
from vehicle.vehicle import Vehicle

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Self_Driving_Simulation")


vehicle = Vehicle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(FPS) / 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((255, 255, 255))
    
    vehicle.handle_input(dt)
    vehicle.update(dt)
    vehicle.draw(screen, 0, 0)
    
    pygame.display.flip()

pygame.quit()