from map.map_data import get_grid_map
from core.object import Object  # Object 클래스가 있는 경로에 맞게 수정해 주세요

# map_data.py 내부 또는 메인 스크립트 수정

CELL_SIZE = 60  # 요청하신 60으로 유지

def parse_map_to_objects(grid):
    """
    생성된 단일 grid 데이터를 받아서 장애물 Object 리스트를 반환합니다.
    """
    obstacles = []
    for row_idx in range(len(grid)):
        for col_idx in range(len(grid[0])):
            if grid[row_idx][col_idx] == 1:
                real_x = col_idx * CELL_SIZE
                real_y = row_idx * CELL_SIZE
                
                # 기존 25x25 대신 변수화된 CELL_SIZE 반영
                obs = Object(real_x, real_y, CELL_SIZE, CELL_SIZE)
                obstacles.append(obs)
                
    return obstacles

def get_start_position(grid):
    """
    생성된 단일 grid 데이터에서 숫자 2(시작점)가 있는 위치를 역추적하여 
    정확한 픽셀 좌표를 반환합니다. (하드코딩 제거)
    """
    for row_idx in range(len(grid)):
        for col_idx in range(len(grid[0])):
            if grid[row_idx][col_idx] == 2:
                return col_idx * CELL_SIZE + CELL_SIZE // 2, row_idx * CELL_SIZE + CELL_SIZE // 2
                
    # 만약 찾지 못했을 경우를 대비한 안전 장치 (기본값 1, 1)
    return 1 * CELL_SIZE, 1 * CELL_SIZE

def get_goal_position(grid):
    """
    목적지(3)의 픽셀 좌표도 동일한 방식으로 안전하게 추출할 수 있습니다.
    """
    for row_idx in range(len(grid)):
        for col_idx in range(len(grid[0])):
            if grid[row_idx][col_idx] == 3:
                return col_idx * CELL_SIZE + CELL_SIZE // 2, row_idx * CELL_SIZE + CELL_SIZE // 2
    return (len(grid[0])-2) * CELL_SIZE + CELL_SIZE // 2, (len(grid)-2) * CELL_SIZE + CELL_SIZE // 2