import pygame
from core.object import Object
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

def load_test_map():
    """
    도시 도로망(City Grid) 스타일의 시뮬레이션 맵 데이터
    규격: 1080 x 720 해상도 최적화 배치
    - 정중앙(540, 360) 반경은 센서 시작 지점으로 완전히 비워둠 (중앙 교차로 역할)
    """
    obstacles = []

    # --- 1. 외곽 경계벽 (도시 바깥 테두리 벽) ---
    # 맵 외부로 탈출하는 것을 방지하는 얇은 외벽들
    obstacles.append(Object(0, 0, SCREEN_WIDTH, 20))                           # 상단 외벽
    obstacles.append(Object(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))           # 하단 외벽
    obstacles.append(Object(0, 0, 20, SCREEN_HEIGHT))                           # 좌측 외벽
    obstacles.append(Object(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT))           # 우측 외벽


    # --- 2. 북서쪽(Top-Left) 빌딩 구역 ---
    # 중앙 위쪽과 왼쪽으로 도로를 형성하는 거대 상업 지구 블록
    obstacles.append(Object(20, 20, 200, 200))     # 대형 빌딩 A
    obstacles.append(Object(280, 20, 160, 200))    # 가로로 긴 빌딩 B
    obstacles.append(Object(20, 280, 200, 120))    # 세로로 긴 빌딩 C


    # --- 3. 북동쪽(Top-Right) 빌딩 구역 ---
    # 복잡한 골목길(T자형 도로) 구조를 만드는 빌딩 단지
    obstacles.append(Object(640, 20, 180, 150))    # 오피스 빌딩 D
    obstacles.append(Object(880, 20, 180, 320))    # 우측 상단 거대 주상복합
    obstacles.append(Object(640, 230, 180, 90))    # 가로형 상가 블록


    # --- 4. 남서쪽(Bottom-Left) 빌딩 구역 ---
    # 센서가 좁은 도로를 따라 코너링을 테스트할 수 있는 구간
    obstacles.append(Object(20, 460, 150, 240))    # 세로형 아파트 단지 E
    obstacles.append(Object(230, 460, 210, 100))   # 가로형 빌딩 F
    obstacles.append(Object(230, 620, 210, 80))    # 하단 공원/구조물 블록 G


    # --- 5. 남동쪽(Bottom-Right) 빌딩 구역 ---
    # 넓은 대로변과 꺾이는 골목을 연출하는 다운타운 블록
    obstacles.append(Object(640, 460, 160, 140))   # 다운타운 빌딩 H
    obstacles.append(Object(860, 410, 200, 130))   # 우측 외곽 빌딩 I
    obstacles.append(Object(640, 660, 420, 40))    # 하단 가로 장벽 블록 J

    return obstacles