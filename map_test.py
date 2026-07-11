import pygame
import sys
import math  # [추가] math 모듈 import (hypot, atan2 등 사용)
from config.settings import *
from map.map_parser import setup_new_episode, CELL_SIZE
from core.vehicle import Vehicle  # (주의) 폴더 구조에 맞게 경로 확인 필요

def main():
    pygame.init()
    # 화면 크기 설정
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # 최초 맵 로드
    grid, static_objects, dynamic_objects, start_x, start_y, goal_x, goal_y, waypoints = setup_new_episode()
    objects = static_objects + dynamic_objects

    # 수동 조작할 차량 객체 생성
    vehicle = Vehicle(start_x, start_y)

    # 카메라 및 마우스 드래그 상태 변수 초기화
    camera_x = 0
    camera_y = 0
    dragging = False
    last_mouse_pos = (0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                # [R] 키를 누르면 맵 새로고침 및 차량 원위치
                if event.key == pygame.K_r:
                    print("맵을 다시 불러옵니다...")
                    grid, static_objects, dynamic_objects, start_x, start_y, goal_x, goal_y, waypoints = setup_new_episode()
                    objects = static_objects + dynamic_objects
                    
                    # 차량 초기화
                    vehicle = Vehicle(start_x, start_y)
                    
                    camera_x = 0
                    camera_y = 0

            # 마우스 조작 이벤트 처리 (화면 드래그용)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    camera_x -= dx
                    camera_y -= dy
                    last_mouse_pos = event.pos

        # ==========================================
        # 차량 수동 조작 (W, A, S, D)
        # ==========================================
        keys = pygame.key.get_pressed()

        # 가속 및 감속
        if keys[pygame.K_w]:
            vehicle.speed += VEHICLE_ACCEL
        elif keys[pygame.K_s]:
            vehicle.speed -= VEHICLE_ACCEL
        else: # 자연 감속
            if vehicle.speed > 0:
                vehicle.speed = max(0, vehicle.speed - DECEL)
            elif vehicle.speed < 0:
                vehicle.speed = min(0, vehicle.speed + DECEL)

        # 최고 속도 제한
        vehicle.speed = max(-VEHICLE_MAX_SPEED, min(VEHICLE_MAX_SPEED, vehicle.speed))

        # 조향
        if keys[pygame.K_a]:
            vehicle.steer_angle = -VEHICLE_MAX_STEER
        elif keys[pygame.K_d]:
            vehicle.steer_angle = VEHICLE_MAX_STEER
        else:
            vehicle.steer_angle = 0

        # 차량 위치 물리 업데이트
        vehicle.update()
        
        # =================================================================
        # [추가] main.py와 완전히 동일한 웨이포인트 스킵/삭제 로직
        # =================================================================
        waypoint_cleared = False
        
        if len(waypoints) > 0:
            wp0_x, wp0_y = waypoints[0]
            dx0 = wp0_x - vehicle.x
            dy0 = wp0_y - vehicle.y
            dist_to_wp0 = math.hypot(dx0, dy0)
            
            angle_to_wp0 = math.degrees(math.atan2(dy0, dx0))
            angle_diff_wp0 = (angle_to_wp0 - vehicle.angle + 180) % 360 - 180
            
            look_ahead_idx = min(LOOKAHEAD_INDEX, len(waypoints) - 1)
            wp1_x, wp1_y = waypoints[look_ahead_idx]
            dist_to_1 = math.hypot(wp1_x - vehicle.x, wp1_y - vehicle.y)
            
            cond_margin = (dist_to_wp0 < WAYPOINT_MARGIN)
            
            if look_ahead_idx > 0:
                cond_angle = abs(angle_diff_wp0) > 90.0 and dist_to_1 < CELL_SIZE * 1.5
                cond_closer_to_next = dist_to_1 < dist_to_wp0
            else:
                cond_angle = False
                cond_closer_to_next = False
            
            if cond_margin or cond_angle or cond_closer_to_next:
                if len(waypoints) > 1:
                    waypoints.pop(0)
                    waypoint_cleared = True
                    print(f"웨이포인트 통과! 남은 개수: {len(waypoints)}")
                else:
                    waypoint_cleared = True
        # =================================================================

        # 1. 동적 장애물 위치 업데이트
        for dyn_obj in dynamic_objects:
            dyn_obj.update()

        # 2. 화면 초기화
        screen.fill(BG_COLOR)

        # 3. 시작점(초록색) / 목적지(주황색) 타일 그리기
        start_tile_x = start_x - (CELL_SIZE // 2) - camera_x
        start_tile_y = start_y - (CELL_SIZE // 2) - camera_y
        goal_tile_x = goal_x - (CELL_SIZE // 2) - camera_x
        goal_tile_y = goal_y - (CELL_SIZE // 2) - camera_y

        pygame.draw.rect(screen, GREEN, (start_tile_x, start_tile_y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, YELLOW, (goal_tile_x, goal_tile_y, CELL_SIZE, CELL_SIZE))

        # 목적지 도달 판정 반경(빨간 원)에 GOAL_RADIUS 적용
        pygame.draw.circle(
            screen,
            RED,
            (int(goal_x - camera_x), int(goal_y - camera_y)),
            int(GOAL_RADIUS),
            2
        )

        # 4. 정적 & 동적 객체(장애물) 그리기
        for obj in objects:
            obj.draw(screen, camera_x, camera_y)

        # 5. A* 웨이포인트 경로 선 및 포인트 그리기
        if waypoints:
            path_points = [(wx - camera_x, wy - camera_y) for wx, wy in waypoints]
            if len(path_points) > 1:
                pygame.draw.lines(screen, GREEN, False, path_points, 3)
            for px, py in path_points:
                pygame.draw.circle(screen, GREEN, (int(px), int(py)), 5)

        # 차량 화면에 그리기
        vehicle.draw(screen, camera_x, camera_y)

        # 목표 거리 계산
        dist_to_goal = math.hypot(goal_x - vehicle.x, goal_y - vehicle.y)
        
        # 상단 캡션바 디버깅 출력에 GOAL_RADIUS 적용
        pygame.display.set_caption(f"Goal Dist: {dist_to_goal:.1f} (Margin: {GOAL_RADIUS})")

        # ---------------------------------------------------------
        # [수정] 성공 조건에도 waypoint_cleared 로직 연동
        # ---------------------------------------------------------
        is_success = (dist_to_goal < GOAL_RADIUS) and (len(waypoints) == 0 or (len(waypoints) == 1 and waypoint_cleared))
        
        if is_success:
            print(f"★★★ 완주 성공! ★★★ (목표 도달 & 웨이포인트 클리어)")
            # 계속 메시지가 뜨는 것을 방지하고 싶다면 running = False 처리하거나 맵을 리셋할 수 있습니다.
            
        # 화면 업데이트 및 FPS 고정
        pygame.display.flip()
        clock.tick(FPS) 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()