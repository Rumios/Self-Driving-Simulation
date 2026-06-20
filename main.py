import pygame
import math
from config.settings import *
from core.vehicle import Vehicle
from core.dqn_agent import DQNAgent
from map.map_parser import parse_map_to_objects, get_start_position, get_goal_position, CELL_SIZE
from map.map_data import get_grid_map
from rule import RuleManager
from map.pathfinding import astar
from logger import LearningLogger

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Self_Driving_Simulation")

grid = get_grid_map()
objects = parse_map_to_objects(grid)
start_x, start_y = get_start_position(grid)
goal_x, goal_y = get_goal_position(grid)

start_grid = None
goal_grid = None

for r in range(len(grid)):
    for c in range(len(grid[0])):
        if grid[r][c] == 2:
            start_grid = (r, c)
        elif grid[r][c] == 3:
            goal_grid = (r, c)

grid_path = astar(grid, start_grid, goal_grid)

# 실제 픽셀 waypoint 리스트 생성 (시작 노드 제외)
waypoints = []
if grid_path:
    for r, c in grid_path[1:]:
        pixel_x = c * CELL_SIZE + CELL_SIZE // 2
        pixel_y = r * CELL_SIZE + CELL_SIZE // 2
        waypoints.append((pixel_x, pixel_y))

# 모듈
vehicle = Vehicle(start_x, start_y)
rule_manager = RuleManager(vehicle, objects)
agent = DQNAgent(vehicle, waypoints[:])
logger = LearningLogger()

# 학습
epsilon = 1.0

clock = pygame.time.Clock()
running = True

# 학습 진행률 및 설정
episode = 1
frame_count = 0
ACTION_REPEAT = 3

RENDER_EVERY = 100

# 과적합 및 정체하는 것 방지
consecutive_failuers = 0
MIN_EPSILON = 0.01

# 거리 및 보상 추적 변수 초기화
total_distance = 0.0
episode_reward = 0.0
best_reward = -float('inf')
prev_x, prev_y = vehicle.x, vehicle.y

while running:
    do_render = (episode % RENDER_EVERY == 0)
    
    if do_render:
        clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # 프레임 스킵 (Action Repeat) 로직 적용
    if frame_count % ACTION_REPEAT == 0:
        state = agent.get_state()
        action = agent.select_action(state, epsilon)
    
    agent.apply_action(action)
    vehicle.update()
    
    # 이동 거리 누적 계산
    dist_moved = math.hypot(vehicle.x - prev_x, vehicle.y - prev_y)
    total_distance += dist_moved
    prev_x, prev_y = vehicle.x, vehicle.y
    
    agent.update_waypoints()
    
    is_collided = rule_manager.update()
    reward = agent.calculate_reward(is_collided)
    episode_reward += reward
    
    next_state = agent.get_state()
    
    # 저장 및 학습 루프
    done = is_collided or not agent.waypoints
    agent.memory.append((state, action, reward, next_state, done))
    
    if frame_count % 4 == 0:
        agent.train(batch_size=32)
    frame_count += 1
    
    if done:
        is_success = not agent.waypoints
        
        logger.record(episode, episode_reward, is_success, total_distance)
        
        if is_success:
            consecutive_failuers = 0
            print(f"[{episode} 에피소드] 목적지 도달 성공 (거리: {total_distance:.1f}px, 보상: {episode_reward:.2f}, Epsilon: {epsilon:.3f})")
            
            if episode_reward > best_reward:
                best_reward = episode_reward
            
            # 성공 시 epsilon 감소
            epsilon = max(MIN_EPSILON, epsilon * 0.5)
        else:
            consecutive_failuers += 1
            print(f"[{episode} 에피소드] 충돌 발생. (거리: {total_distance:.1f}px, 보상: {episode_reward:.2f}, Epsilon: {epsilon:.3f})")
            
            epsilon = max(MIN_EPSILON, epsilon * 0.995)
            
            if consecutive_failuers >= 5 and epsilon < 0.1:
                epsilon = 0.5
                consecutive_failuers = 0
                print("학습 정체 발생. epsilon 0.5 리셋")
        
        if episode % 50 == 0:
            logger.save_plot(window=50)
            print("학습 그래프 업데이트")
            
        # 차량 상태 초기화
        vehicle.x, vehicle.y = start_x, start_y
        vehicle.speed = 0.0
        vehicle.angle = 0.0
        vehicle.steer_angle = 0.0
        
        # 경로 다시 할당
        agent.waypoints = waypoints[:]
        
        # 탐험률(Epsilon) 감소
        epsilon = max(0.01, epsilon * 0.995) 
        
        # 에피소드 변수 초기화
        episode += 1
        frame_count = 0
        total_distance = 0.0
        episode_reward = 0.0
        prev_x, prev_y = vehicle.x, vehicle.y
    
    if do_render:
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

        # 현재 에이전트가 추적 중인 남은 웨이포인트 렌더링
        if len(agent.waypoints) > 0:
            camera_applied_path = [(wx - camera_x, wy - camera_y) for wx, wy in agent.waypoints]
            if len(camera_applied_path) > 1:
                pygame.draw.lines(screen, GREEN, False, camera_applied_path, 3)
        
        vehicle.draw(screen, camera_x, camera_y)
        
        pygame.display.flip()

pygame.quit()