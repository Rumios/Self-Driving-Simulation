import torch
import torch.nn as nn
import torch.optim as optim
import random
import math
import numpy as np
from config.settings import *

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        
        # 신경망 구축
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
        
    def forward(self, x):
        return self.net(x)

# PER 메모리
# 알고리즘 이해해봐야할 듯.
class ReplayBuffer:
    def __init__(self, capacity = 20000):
        self.capacity = capacity
        self.memory = []
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.pos = 0
        self.size = 0
    
    def append(self, experience):
        # 가장 높은 우선순위로 넣어서 최소 1번은 학습되도록 처리
        max_prio = max(self.priorities) if self.size > 0 else 1.0

        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.pos] = experience
        
        self.priorities[self.pos] = max_prio
        self.pos = (self.pos + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)    

    def sample(self, batch_size, alpha = 0.6):
        # 우선순위 비례 확률적 데이터 sampling
        current_priorities = self.priorities[:self.size]
        probs = current_priorities ** alpha
        probs /= probs.sum()
        
        indices = np.random.choice(len(self.memory), batch_size, p = probs, replace=False)
        samples = [self.memory[idx] for idx in indices]
        
        return samples, indices

    def update_priorities(self, indices, errors, offset=0.1):
        for idx, err in zip(indices, errors):
            self.priorities[idx] = err + offset
    
    def __len__(self):
        return len(self.memory)
    
class DQNAgent:
    def __init__(self, vehicle, waypoints, state_dim = 14, action_dim = 5):
        self.vehicle = vehicle
        self.waypoints = waypoints
        
        self.model = DQN(state_dim, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.memory = ReplayBuffer()
        self.gamma = 0.99 # 할인율
        self.action_dim = action_dim
        
    def get_state(self, current_lidar, prev_lidar):
        # 반환값 : [속도, 조향각, 목표와의 거리, 각도 오차] + 현재 라이다[5] + 이전 라이다[5]
        if not self.waypoints:
            return np.zeros(14, dtype=np.float32)
        
        target_idx = min(LOOKAHEAD_INDEX, len(self.waypoints) - 1)
        target_wp = self.waypoints[target_idx]
        
        dx = target_wp[0] - self.vehicle.x
        dy = target_wp[1] - self.vehicle.y
        
        # 목표 웨이포인트까지의 거리
        dist = math.hypot(dx, dy)
        target_angle = math.degrees(math.atan2(dy, dx))
        
        # 조향 오차 계산
        angle_diff = target_angle - self.vehicle.angle
        angle_diff = (angle_diff + 180) % 360 - 180
        
        # state 정규화
        norm_speed = self.vehicle.speed / self.vehicle.MAX_SPEED
        norm_steer = self.vehicle.steer_angle / self.vehicle.MAX_STEER
        norm_dist = min(dist / 800.0, 1.0)
        norm_angle_diff = angle_diff / 180.0 

        norm_current = [d / 150.0 for d in current_lidar]
        norm_prev = [d / 150.0 for d in prev_lidar]
        
        state = [norm_speed, norm_steer, norm_dist, norm_angle_diff] + norm_current + norm_prev
            
        return np.array(state, dtype=np.float32)
    
    # 웨이포인트 주변 threshold px 안에 다가오면 업데이트
    def update_waypoints(self, threshold=WAYPOINT_MARGIN):
        if self.waypoints:
            dist = math.hypot(self.waypoints[0][0] - self.vehicle.x, self.waypoints[0][1] - self.vehicle.y)
            if dist < threshold:
                self.waypoints.pop(0)
    
    def select_action(self, state, epsilon):
        if random.random() < epsilon:
            return random.randint(0, 4)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state_tensor)
        return q_values.argmax().item()

    def apply_action(self, action):
        # 0: 유지, 1: 가속, 2: 브레이크, 3: 좌회전, 4: 우회전
        if action == 1: 
            self.vehicle.speed = min(self.vehicle.speed + 0.6, self.vehicle.MAX_SPEED)
        elif action == 2: 
            self.vehicle.speed = max(self.vehicle.speed - 0.5, 0.0)
        else:
            if self.vehicle.speed > 0:
                self.vehicle.speed = max(self.vehicle.speed - 0.1, 0.0)
                
        if action == 3: 
            self.vehicle.steer_angle = max(self.vehicle.steer_angle - 15, -self.vehicle.MAX_STEER)
        elif action == 4: 
            self.vehicle.steer_angle = min(self.vehicle.steer_angle + 15, self.vehicle.MAX_STEER)
        elif action in [0, 1, 2]:
            if self.vehicle.steer_angle > 0:
                self.vehicle.steer_angle = max(self.vehicle.steer_angle - 6, 0.0)
            elif self.vehicle.steer_angle < 0:
                self.vehicle.steer_angle = min(self.vehicle.steer_angle + 6, 0.0)
    
    def calculate_reward(self, current_distance, prev_distance, current_lidar, 
                         is_waypoint_cleared, is_goal_reached, is_timeout, is_collided, angle_diff):
        if is_goal_reached:
            return REWARD_GOAL
        if is_timeout:
            return PENALTY_TIMEOUT
        if is_collided:
            return PENALTY_COLLISION
        
        reward = 0.0
        
        # waypoint 도착 시
        if is_waypoint_cleared:
            reward += REWARD_WAYPOINT
        
        dist_delta = prev_distance - current_distance
        if dist_delta > 0:
            reward += (dist_delta * REWARD_DISTANCE_SCALE)
            
        # Heading Error Penalty
        normalized_heading_error = abs(angle_diff) / 180.0
        heading_penalty = normalized_heading_error * HEADING_PENALTY_SCALE
        reward -= heading_penalty

        min_lidar_dist = min(current_lidar)
        if min_lidar_dist < LIDAR_SAFE_DISTANCE:
            max_danger = (LIDAR_SAFE_DISTANCE - min_lidar_dist) / LIDAR_SAFE_DISTANCE
            
            risk_penalty = (max_danger ** LIDAR_PENALTY_EXPONENT) * LIDAR_PENALTY_MAX
            reward -= risk_penalty
        
        return reward

    def train(self, batch_size=32):
        if len(self.memory) < batch_size: return
        
        batch, indices = self.memory.sample(batch_size)
                
        # zip(*memory) -> 여러 튜플이 모인 리스트를 열 단위로 분리해줌.
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # 왜 states는 안하지?
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards).unsqueeze(1)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones).unsqueeze(1)
        
        current_q = self.model(states).gather(1, actions)
        
        with torch.no_grad():
            next_q = self.model(next_states).max(1)[0].unsqueeze(1)
            target_q = rewards + (self.gamma * next_q * (1 - dones))
        
        # 왜 그동안 이거 안 썼지.
        # 오차가 틀린 정도를 가지고 높게 나온 데이터의 우선순위를 높게 수정
        # 예측과 비슷한 것은 우선순위가 하락
        # -> 이미 반영된 데이터는 뒤로 미루고 반영되지 않은 데이터를 더 높게 수정
        td_errors = torch.abs(current_q - target_q).detach().numpy()
        
        self.memory.update_priorities(indices, td_errors.flatten())
        
        loss = nn.MSELoss()(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()