# 2D LiDAR SLAM 시뮬레이터 실습

본 프로젝트는 2D 레이캐스팅(Raycasting)을 통해 실시간으로 주변을 스캔하고, 로봇 중심(Local)과 세계(Global) 좌표계 변환을 처리하는 자율주행 SLAM의 기초 시스템임.

## 핵심 데이터 파이프라인 흐름

### 1. Emission (광선 조사)

- **내용:** 센서 각도(`sensor.angle`) 기준 좌우 `FOV // 2` 범위를 일정 간격(예: 4도)으로 쪼갬.
- **연산:** 각 degree 각도를 호도법(`Radian`)으로 변환하여 삼각함수 연산 준비.

### 2. DDA 탐색 (증분 점검)

- **내용:** 각도 벡터 방향으로 최대 감지 거리(`max_range`)까지 1픽셀씩 전진하며 탐색 좌표 생성.
- **공식:**
  $$check\_x = sensor.x + r \cdot \cos(rad)$$
  $$check\_y = sensor.y + r \cdot \sin(rad)$$

### 3. Collision Detection (충돌 판정)

- **내용:** 전진 중 장애물 영역(`collidepoint`) 진입 여부 매 스텝 체크.
- **처리:** 충돌 감지 즉시 해당 거리(`r`)를 최종 거리로 확정하고 루프 탈출(`break`).

### 4. Data Structuring (데이터 구조화)

- **내용:** 충돌 거리(`final_r`)와 사용된 절대 각도(`rad`)를 매칭하여 로봇 중심 상대 좌표(`dx, dy`) 계산.
- **저장:** `self.point_cloud.append((dx, dy, final_r, rad))` 형태로 묶어 미니맵 클래스로 토스.

### 5. Local & Global Mapping (SLAM 및 시각화)

- **필터링:** 최대 사정거리(`max_range`) 데이터는 허공이므로 지도 누적에서 제외.
- **SLAM 지도 빌드:** 유효 데이터는 센서 위치를 더해 절대 좌표(`world_hit`)로 복원 후 중복 제거를 위해 `global_map = set()`에 누적.
- **시각화 분기:**
    - **LOCAL 모드:** 센서를 미니맵 중앙에 박아두고, 전체 지도를 로봇 기준 역평행이동 및 역회전($-sensor.angle - 90^\circ$) 처리하여 렌더링. (로봇 정면이 항시 위쪽)
    - **GLOBAL 모드:** 월드 맵 좌표계를 고정하고, 센서 아이콘이 맵 안을 돌아다니도록 렌더링.
