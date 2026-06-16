# map_data.py
import random

def get_grid_map():
    """
    세로 6칸 x 가로 N칸의 모듈형 단방향 트랙 (물리 충돌 방지 버전)
    - 맵 외곽 상/하/좌/우 모두 벽(1)으로 완벽 차단
    - 자동차가 회전하며 지나갈 수 있도록 모든 주행 통로는 최소 너비 2칸 보장
    - 시작점을 1칸 앞으로 당겨 스폰 시 안전성 확보
    """
    SECTOR_ROWS = 6  # 세로 6칸 고정 (0행, 5행은 외곽 벽)
    
    # [기본 뼈대 생성] 위아래를 벽으로 막고 내부 4칸을 뚫어줍니다.
    def create_base_sector(cols):
        sector = [[1 for _ in range(cols)] for _ in range(SECTOR_ROWS)]
        for r in range(1, SECTOR_ROWS - 1):
            for c in range(cols):
                sector[r][c] = 0
        return sector

    # ====================================================
    # 1. 통로 섹터 (크기: 6x3) - 총 4개 생성 예정
    # ====================================================
    def get_path_sector():
        return create_base_sector(3)

    # ====================================================
    # 2. 장애물 섹터 5종 (크기: 6x6 ~ 6x12)
    # *핵심: 차가 끼지 않도록 장애물을 설치해도 무조건 2칸의 여유 차선 확보
    # ====================================================
    
    # [장애물 1] 상단 차단 (크기: 6x6) - 아래쪽 2칸(3, 4행)으로 통과
    obs1 = create_base_sector(6)
    for c in range(2, 4):
        obs1[1][c] = 1
        obs1[2][c] = 1

    # [장애물 2] 하단 차단 (크기: 6x6) - 위쪽 2칸(1, 2행)으로 통과
    obs2 = create_base_sector(6)
    for c in range(2, 4):
        obs2[3][c] = 1
        obs2[4][c] = 1

    # [장애물 3] 중앙 터널 병목 (크기: 6x8) - 정중앙 2칸(2, 3행)으로 통과
    obs3 = create_base_sector(8)
    for c in range(2, 6):
        obs3[1][c] = 1  # 맨 위 차선 막기
        obs3[4][c] = 1  # 맨 아래 차선 막기

    # [장애물 4] 부드러운 슬라롬 A (크기: 6x12) - 상단 막힌 후, 여유 공간 뒤 하단 막힘
    obs4 = create_base_sector(12)
    for c in range(2, 4):  # 먼저 상단(1,2행) 차단
        obs4[1][c] = 1
        obs4[2][c] = 1
    # 열 4~7까지는 차선 변경을 위한 안전 여유 공간 (전체 개방)
    for c in range(8, 10): # 이후 하단(3,4행) 차단
        obs4[3][c] = 1
        obs4[4][c] = 1

    # [장애물 5] 부드러운 슬라롬 B (크기: 6x12) - 하단 막힌 후, 여유 공간 뒤 상단 막힘
    obs5 = create_base_sector(12)
    for c in range(2, 4):  # 먼저 하단(3,4행) 차단
        obs5[3][c] = 1
        obs5[4][c] = 1
    # 열 4~7까지는 차선 변경을 위한 안전 여유 공간 (전체 개방)
    for c in range(8, 10): # 이후 상단(1,2행) 차단
        obs5[1][c] = 1
        obs5[2][c] = 1

    # ====================================================
    # 3. 출발 및 도착 섹터 (맵 경계 완벽 차단)
    # ====================================================
    b_start = create_base_sector(4)
    for r in range(SECTOR_ROWS):
        b_start[r][0] = 1  # [요청 반영] 맵의 맨 왼쪽 경계를 벽으로 꽉 막음
    b_start[2][2] = 2      # [요청 반영] 시작점을 기존 [2][1]에서 [2][2]로 1칸 앞으로 당김

    b_goal = create_base_sector(4)
    for r in range(SECTOR_ROWS):
        b_goal[r][3] = 1   # [요청 반영] 맵의 맨 오른쪽 경계를 벽으로 꽉 막음
    b_goal[2][1] = 3       # 목적지

    # ====================================================
    # 4. 무작위 섹터 조립 (Random Stitching)
    # ====================================================
    passage_pool = [get_path_sector() for _ in range(4)]
    obstacle_pool = [obs1, obs2, obs3, obs4, obs5]
    
    middle_pool = passage_pool + obstacle_pool
    random.shuffle(middle_pool)
    
    all_sectors = [b_start] + middle_pool + [b_goal]
    
    grid = []
    for r in range(SECTOR_ROWS):
        combined_row = []
        for sector in all_sectors:
            combined_row.extend(sector[r])
        grid.append(combined_row)
        
    return grid