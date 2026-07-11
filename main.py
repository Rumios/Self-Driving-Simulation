import pygame
import math
from config.settings import *
from core.vehicle import Vehicle
from core.dqn_agent import DQNAgent
from map.map_parser import setup_new_episode, CELL_SIZE
from map.map_data import get_grid_map
from rule import RuleManager
from map.pathfinding import astar
from logger import LearningLogger

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Self_Driving_Simulation")

grid, static_objects, dynamic_objects, start_x, start_y, goal_x, goal_y, waypoints = setup_new_episode()
objects = static_objects + dynamic_objects

# 첫 번째 웨이포인트를 바라보는 초기 각도 계산
initial_angle = 0.0
if waypoints:
    dx = waypoints[0][0] - start_x
    dy = waypoints[0][1] - start_y
    initial_angle = math.degrees(math.atan2(dy, dx))

# 모듈
vehicle = Vehicle(start_x, start_y)
vehicle.angle = initial_angle
rule_manager = RuleManager(vehicle, objects)
agent = DQNAgent(vehicle, waypoints[:])
logger = LearningLogger()

# Lidar
current_lidar = vehicle.get_lidar_readings(objects)
prev_lidar = current_lidar[:]

# 학습
epsilon = 1.0

clock = pygame.time.Clock()
running = True

# 학습 진행률 및 설정
episode = 1
frame_count = 0
ACTION_REPEAT = 3
TRAIN_INTERVAL = 8
RESET_EPSILON_INTERVAL = 5
RENDER_EVERY = 50
MAX_STEPS = 3000

# 과적합 및 정체하는 것 방지
consecutive_failuers = 0
MIN_EPSILON = 0.0001

# 거리 및 보상 추적 변수 초기화
total_distance = 0.0
episode_reward = 0.0
best_reward = -float('inf')
prev_x, prev_y = vehicle.x, vehicle.y

current_wp_dist = 0.0
if waypoints:
    current_wp_dist = math.hypot(vehicle.x - waypoints[0][0], vehicle.y - waypoints[0][1])

macro_reward = 0.0
macro_state = None
macro_action = None

while running:
    done = False
    
    while not done and running: 
        do_render = (episode % RENDER_EVERY == 0)
        
        if do_render:
            clock.tick(FPS)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not running:
            break  # 창을 닫으면 내부 루프 즉시 탈출
            
        # [추가] 매 프레임마다 동적 장애물 위치 업데이트 (올려주신 코드에서 누락되어 추가함)
        for dyn_obj in dynamic_objects:
            dyn_obj.update()
            
        # 프레임 스킵 (Action Repeat) 로직 적용 및 Macro 상태/행동 저장
        if frame_count % ACTION_REPEAT == 0:
            current_lidar = vehicle.get_lidar_readings(objects)
            macro_state = agent.get_state(current_lidar, prev_lidar)
            macro_action = agent.select_action(macro_state, epsilon)
            macro_reward = 0.0  # 새로운 주기 시작 시 누적 보상 초기화
        
        prev_wp_dist = current_wp_dist
        
        # 저장된 macro_action을 주기 동안 지속적으로 적용
        agent.apply_action(macro_action)
        vehicle.update()
        
        # 이동 거리 누적 계산
        dist_moved = math.hypot(vehicle.x - prev_x, vehicle.y - prev_y)
        total_distance += dist_moved
        prev_x, prev_y = vehicle.x, vehicle.y
        
        waypoint_cleared = False
        
        if len(agent.waypoints) > 0:
            # 현재 타겟
            wp0_x, wp0_y = agent.waypoints[0]
            dx0 = wp0_x - vehicle.x
            dy0 = wp0_y - vehicle.y
            dist_to_wp0 = math.hypot(dx0, dy0)
            
            angle_to_wp0 = math.degrees(math.atan2(dy0, dx0))
            angle_diff_wp0 = (angle_to_wp0 - vehicle.angle + 180) % 360 - 180
            
            look_ahead_idx = min(LOOKAHEAD_INDEX, len(agent.waypoints) - 1)
            wp1_x, wp1_y = agent.waypoints[look_ahead_idx]
            dist_to_1 = math.hypot(wp1_x - vehicle.x, wp1_y - vehicle.y)
            
            cond_margin = (dist_to_wp0 < WAYPOINT_MARGIN) and abs(angle_diff_wp0) < HEADING_MARGIN

            if cond_margin:
                if len(agent.waypoints) > 1:
                    agent.waypoints.pop(0)
                    waypoint_cleared = True
                else:
                    waypoint_cleared = False
        
        if agent.waypoints:
            dx = agent.waypoints[0][0] - vehicle.x
            dy = agent.waypoints[0][1] - vehicle.y
            current_wp_dist = math.hypot(dx, dy)
        else:
            current_wp_dist = 0.0
        
        dist_to_goal = math.hypot(goal_x - vehicle.x, goal_y - vehicle.y)
        
        is_collided = rule_manager.update()
        is_timeout = frame_count >= MAX_STEPS
        is_success = (dist_to_goal < GOAL_RADIUS) and abs(angle_diff_wp0) < HEADING_MARGIN
        
        done = is_collided or is_success or is_timeout
        
        next_lidar = vehicle.get_lidar_readings(objects)
        
        current_angle_diff = 0.0
        if agent.waypoints:
            target_idx = min(LOOKAHEAD_INDEX, len(agent.waypoints) - 1)
            dx = agent.waypoints[target_idx][0] - vehicle.x
            dy = agent.waypoints[target_idx][1] - vehicle.y
            target_angle = math.degrees(math.atan2(dy, dx))
            current_angle_diff = (target_angle - vehicle.angle + 180) % 360 - 180
        
        # 현재 스텝의 보상을 계산
        reward = agent.calculate_reward(
            current_distance=current_wp_dist,
            prev_distance=prev_wp_dist,
            current_lidar=next_lidar,
            is_waypoint_cleared=waypoint_cleared,
            is_goal_reached=is_success,
            is_timeout=is_timeout,
            is_collided=is_collided,
            angle_diff=current_angle_diff
        )
        
        macro_reward += reward
        episode_reward += reward
        
        if (frame_count + 1) % ACTION_REPEAT == 0 or done:
            next_state = agent.get_state(next_lidar, current_lidar)
            
            if macro_state is not None:
                agent.memory.append((macro_state, macro_action, macro_reward, next_state, done))
            
            prev_lidar = current_lidar[:]
            
            if ((frame_count + 1) // ACTION_REPEAT) % TRAIN_INTERVAL == 0:
                agent.train(batch_size=32)
        
        if done:
            if is_success:
                reason = 'success'
            elif is_collided:
                reason = 'collision'
            elif is_timeout:
                reason = 'timeout'
            else:
                reason = 'unknown'
            
            logger.record(episode, episode_reward, is_success, total_distance, frame_count, reason)
            
            if is_success:
                consecutive_failuers = 0
                print(f"[{episode} 에피소드] 목적지 도달 성공 (거리: {total_distance:.1f}px, 스텝: {frame_count}, 보상: {episode_reward:.2f}, Epsilon: {epsilon:.4f})")
                
                if episode_reward > best_reward:
                    best_reward = episode_reward
                
                epsilon = max(MIN_EPSILON, epsilon * 0.7)
            else:
                consecutive_failuers += 1
                print(f"[{episode} 에피소드] 충돌/시간초과 발생. (거리: {total_distance:.1f}px, 스텝: {frame_count}, 보상: {episode_reward:.2f}, Epsilon: {epsilon:.4f})")
                
                epsilon = max(MIN_EPSILON, epsilon * 0.995)
                
                if consecutive_failuers >= RESET_EPSILON_INTERVAL and epsilon < 0.1:
                    epsilon = 0.5
                    consecutive_failuers = 0
                    print("학습 정체 발생. epsilon 0.5 리셋")
            
            if episode % 50 == 0:
                logger.save_plot(window=50)
                print("학습 그래프 업데이트")
                
            # [수정] 동적 객체 분리 반영
            grid, static_objects, dynamic_objects, start_x, start_y, goal_x, goal_y, waypoints = setup_new_episode()
            objects = static_objects + dynamic_objects
            rule_manager.obstacles = objects
            
            initial_angle = 0.0
            if waypoints:
                dx = waypoints[0][0] - start_x
                dy = waypoints[0][1] - start_y
                initial_angle = math.degrees(math.atan2(dy, dx))
            
            vehicle.x, vehicle.y = start_x, start_y
            vehicle.speed = 0.0
            vehicle.angle = initial_angle
            vehicle.steer_angle = 0.0
            
            agent.waypoints = waypoints[:]
            
            episode += 1
            frame_count = 0
            total_distance = 0.0
            episode_reward = 0.0
            prev_x, prev_y = vehicle.x, vehicle.y
            rule_manager.is_collided = False
            
            if waypoints:
                current_wp_dist = math.hypot(vehicle.x - waypoints[0][0], vehicle.y - waypoints[0][1])
            else:
                current_wp_dist = 0.0
                
            macro_reward = 0.0
            macro_state = None
            macro_action = None
            prev_lidar = vehicle.get_lidar_readings(objects)
            frame_count = -1 
        
        frame_count += 1
        
        if do_render:
            screen.fill(BG_COLOR)
            
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

            if len(agent.waypoints) > 0:
                camera_applied_path = [(wx - camera_x, wy - camera_y) for wx, wy in agent.waypoints]

                if len(camera_applied_path) > 1:
                    pygame.draw.lines(screen, GREEN, False, camera_applied_path, 3)
                    
                for px, py in camera_applied_path:
                    pygame.draw.circle(screen, GREEN, (int(px), int(py)), 5)
            
            vehicle.draw(screen, camera_x, camera_y)
            vehicle.draw_lidar(screen, objects, camera_x, camera_y)
            
            pygame.display.flip()

pygame.quit()