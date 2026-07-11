from map.map_data import get_grid_map
from core.object import Object, DynamicObject
from map.pathfinding import astar
from config.settings import *

CELL_SIZE = 60

def parse_map_to_objects(grid):
    """
    생성된 단일 grid 데이터를 받아서 장애물 Object 리스트를 반환합니다.
    """
    static_objects = []
    dynamic_objects = []
    
    for row_idx in range(len(grid)):
        for col_idx in range(len(grid[0])):
            real_x = col_idx * CELL_SIZE
            real_y = row_idx * CELL_SIZE
            
            # 1: 정적 벽
            if grid[row_idx][col_idx] == 1:
                obs = Object(real_x, real_y, CELL_SIZE, CELL_SIZE)
                static_objects.append(obs)
                
            # 4: 동적 장애물 (위아래 왕복)
            elif grid[row_idx][col_idx] == 4:
                dyn_obs = DynamicObject(real_x, real_y, CELL_SIZE, CELL_SIZE, 
                                        speed=OBJECT_SPEED, move_range=60.0, axis='y')
                dynamic_objects.append(dyn_obs)
                
    return static_objects, dynamic_objects

def get_start_position(grid):
    for row_idx in range(len(grid)):
        for col_idx in range(len(grid[0])):
            if grid[row_idx][col_idx] == 2:
                return col_idx * CELL_SIZE + CELL_SIZE // 2, row_idx * CELL_SIZE + CELL_SIZE // 2
                
    return 1 * CELL_SIZE, 1 * CELL_SIZE

def get_goal_position(grid):
    for row_idx in range(len(grid)):
        for col_idx in range(len(grid[0])):
            if grid[row_idx][col_idx] == 3:
                return col_idx * CELL_SIZE + CELL_SIZE // 2, row_idx * CELL_SIZE + CELL_SIZE // 2
    return (len(grid[0])-2) * CELL_SIZE + CELL_SIZE // 2, (len(grid)-2) * CELL_SIZE + CELL_SIZE // 2

def setup_new_episode():
    grid = get_grid_map()
    
    static_objects, dynamic_objects = parse_map_to_objects(grid)
    
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
            
    return grid, static_objects, dynamic_objects, start_x, start_y, goal_x, goal_y, waypoints