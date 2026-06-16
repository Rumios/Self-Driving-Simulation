import pygame
from core.object import Object
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

def load_test_map():
    """
    차량 초기 위치(400, 300) 안전 확보 테스트 맵
    - 화면 해상도(800x600) 기준
    - 정중앙(400, 300)은 장애물이 없는 넓은 사거리 교차로로 설정
    - 4개의 쿼터(사분면)에 각각 다른 형태의 주행 테스트 환경 배치
    """
    obstacles = []

    # --- 1. 외곽 경계벽 (맵 이탈 방지용, 두께 20) ---
    obstacles.append(Object(0, 0, SCREEN_WIDTH, 20))                           # 상단 
    obstacles.append(Object(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))          # 하단 
    obstacles.append(Object(0, 0, 20, SCREEN_HEIGHT))                          # 좌측 
    obstacles.append(Object(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT))          # 우측 

    # =================================================================
    # [안전 지대 확보] 
    # X: 300 ~ 450, Y: 220 ~ 380 구간은 중앙 사거리이므로 절대 장애물 배치 금지!
    # 초기 위치(400, 300)에서 차량이 안전하게 스폰됩니다.
    # =================================================================

    # --- 2. 북서쪽 (NW): 복잡한 상가 골목 (좁은 길 주행 테스트) ---
    obstacles.append(Object(50, 50, 100, 150))     # 상가 A
    obstacles.append(Object(200, 50, 80, 150))     # 상가 B (A와 B 사이 50px 좁은 골목)

    # --- 3. 북동쪽 (NE): 공장 지대 (막다른 길 Trap 테스트) ---
    # ㄷ자 모양으로 건물을 둘러싸서, AI가 잘못 진입하면 후진/유턴을 해야 빠져나올 수 있음
    obstacles.append(Object(450, 50, 250, 40))     # 북쪽 벽
    obstacles.append(Object(660, 90, 40, 110))     # 동쪽 막힌 벽
    obstacles.append(Object(450, 160, 250, 40))    # 남쪽 벽

    # --- 4. 남서쪽 (SW): 아파트 단지 (S자 커브 테스트) ---
    # 건물을 가로로 엇갈리게 배치하여 지그재그(S자) 주행을 유도
    obstacles.append(Object(50, 400, 180, 50))     # 1동 건물
    obstacles.append(Object(120, 500, 180, 50))    # 2동 건물

    # --- 5. 남동쪽 (SE): 다운타운 (직각 코너링 테스트) ---
    # ㄱ/ㄴ자 형태의 거대 건물을 배치해 모서리에서의 자연스러운 직각 코너링 학습
    obstacles.append(Object(480, 420, 60, 130))    # 세로로 긴 오피스 빌딩
    obstacles.append(Object(540, 490, 200, 60))    # 가로로 긴 주상복합 건물

    return obstacles    