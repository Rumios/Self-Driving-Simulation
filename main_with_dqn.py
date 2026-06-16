import pygame
import math
from config.settings import *
from core.vehicle_with_lidar import Vehicle
from map.map_parser import parse_map_to_objects, get_start_position, get_goal_position, CELL_SIZE
from map.map_data import get_grid_map
from rule import RuleManager
from dqn_agent import DQNAgent  # 생성한 DQN 에이전트 주입

pygame.init()
font = pygame.font.SysFont("arial", 18, bold=True) # HUD 텍스트용 폰트

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Autonomous DQN Self-Driving Simulation")

# DQN 에이전트 초기화 (8차원 상태 정보 입력 -> 4개 행동 중 선택)
agent = DQNAgent(state_dim=8, action_dim=4)

clock = pygame.time.Clock()
running = True

# 글로벌 스탯 추적용
episode = 1
success_count = 0

# --- 에피소드 초기화 함수 ---
def reset_environment():
    grid = get_grid_map()
    objects = parse_map_to_objects(grid)
    start_x, start_y = get_start_position(grid)
    goal_x, goal_y = get_goal_position(grid)
    
    vehicle = Vehicle(start_x, start_y)
    rule_manager = RuleManager(vehicle, objects)
    
    initial_state = vehicle.get_state(objects, goal_x, goal_y)
    return grid, objects, start_x, start_y, goal_x, goal_y, vehicle, rule_manager, initial_state

# 첫 번째 판 세팅
grid, objects, start_x, start_y, goal_x, goal_y, vehicle, rule_manager, state = reset_environment()
episode_reward = 0.0
step_count = 0

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. DQN 에이전트가 행동 선택
    action = agent.get_action(state)
    
    # 2. 선택한 행동 차량에 바인딩 및 업데이트
    vehicle.apply_action(action)
    vehicle.update()
    
    # 3. 규칙 검사 (벽 충돌 여부) 및 골인 여부 연산
    is_collided = rule_manager.update()
    current_dist = math.hypot(vehicle.x - goal_x, vehicle.y - goal_y)
    
    # 4. 보상 시스템 디자인 (Reward Engineering)
    reward = -0.05 # 타임 패널티 (빨리 깨도록 유도)
    
    # 목적지에 한걸음 가까워질 때마다 가산점
    prev_dist = math.hypot(state[2]*1000 - goal_x, state[2]*1000 - goal_y) # 이전 상태 기반 복원 거리 계산 대신 심플 보상 부여 가능
    # 여기서는 직관적으로 목표 보상을 설계합니다.
    reward += (1.0 - (current_dist / 1000.0)) * 0.1
    
    done = False
    status_text = "DRIVING"
    
    if is_collided:
        reward = -50.0  # 벽 박으면 가차없이 마이너스
        done = True
        status_text = "COLLIDED"
    elif current_dist < CELL_SIZE:
        reward = 100.0  # 목적지 터치 시 보상 폭탄
        done = True
        success_count += 1
        status_text = "GOAL!!"
        
    # 타임아웃 방지 (한 판당 최대 800 스텝)
    step_count += 1
    if step_count > 800:
        done = True
        status_text = "TIMEOUT"

    # 5. 다음 상태 획득 및 메모리 적재 후 학습
    next_state = vehicle.get_state(objects, goal_x, goal_y)
    agent.memory.push(state, action, reward, next_state, done)
    
    agent.train_step(batch_size=64)
    
    state = next_state
    episode_reward += reward

    # --- 그리기 구문 (시각화) ---
    screen.fill(BG_COLOR)
    
    # 카메라 동적 이동 락온
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
    
    vehicle.draw(screen, camera_x, camera_y)
    
    # [있어보이는 포인트 2] 실시간 인공지능 학습 상태창 UI 렌더링 (HUD 패널)
    hud_bg = pygame.Surface((280, 150))
    hud_bg.set_alpha(180)
    hud_bg.fill((30, 30, 30))
    screen.blit(hud_bg, (10, 10))
    
    stats = [
        f"EPISODE : {episode}",
        f"STATUS : {status_text}",
        f"STEP SCORE : {episode_reward:.2f}",
        f"EPSILON : {agent.epsilon:.3f}",
        f"SUCCESSES : {success_count}",
        f"MEM BUFFER : {len(agent.memory)}"
    ]
    
    for idx, txt in enumerate(stats):
        color = (0, 255, 100) if "GOAL" in txt else (255, 255, 255)
        if "COLLIDED" in txt: color = (255, 50, 50)
        surf = font.render(txt, True, color)
        screen.blit(surf, (20, 15 + idx * 22))

    pygame.display.flip()

    # 에피소드가 끝났으면 입실론 줄이고 자동 다음 환경 빌드
    if done:
        print(f"에피소드: {episode:3d} | 결과: {status_text} | 총 보상: {episode_reward:3.2f} | 엡실론: {agent.epsilon:.3f}")
        
        if agent.epsilon > agent.epsilon_min:
            agent.epsilon *= agent.epsilon_decay
            
        grid, objects, start_x, start_y, goal_x, goal_y, vehicle, rule_manager, state = reset_environment()
        episode += 1
        episode_reward = 0.0
        step_count = 0

pygame.quit()