import gymnasium as gym # 강화학습에 필요한 Agent(AI가 움직일 개체)나 환경을 제공해주는 라이브러리
import torch # 딥러닝 프레임워크 메인 모듈
import torch.nn as nn # 인공신경망의 Layer들을 만들기 위한 모듈
import torch.nn.functional as F # 활성화 함수를 쓰기 위한 모듈

# Replay Buffer
import random
from collections import deque

# Agent
import torch.optim as optim

"""
DQN 학습 구조

1. 인공신경망에서 Q table 대용으로 미래 상황 예측해서 대응
2. 실제 학습 과정의 데이터(state)는 Replay buf에 저장(크기는 적절하게)
3. 매번 대략 32, 64개 정도 (여기서는)의 데이터를 한번에 주입시키면서 역전파 과정을 통해 오차를 줄이기 시작. (예전 선택에 대한 예측 점수와 실제 점수도 나와있음)
4. 반복
"""


# 인공 신경망 구축 (nn.Modul을 상속받아서)
class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        # state_dimension : 입력받을 state의 크기
        # action_dimension : 출력할 action의 개수
        
        super(QNetwork, self).__init__() # 부모 클래스(nn.Module)의 초기화 함수 호출 (아래의 학습 코드 실행을 위해 초기화)
        
        # 첫 번째 은닉층. 4개의 state 숫자를 받아서 64개의 특징으로 나눔
        self.fc1 = nn.Linear(state_dim, 64)
        
        # 두 번째 은닉층. 64개의 특징을 조합해 다른 64개의 고차원 특징으로 만듦
        self.fc2 = nn.Linear(64, 64)
        
        # 출력층
        self.fc3 = nn.Linear(64, action_dim)
    
    def forward(self, x):
        """
        입력층 -> 은닉층 -> 출력층으로 흘러가는 과정(순전파) 정의
        x : 현재 환경의 state 데이터 (Tensor 형태)
        """
        
        # nn.Linear은 단순 일차방정식 연산.
        # 그러나 곡선의 값처럼 직선을 바꾸기 위해 0보다 작으면 무조건 0으로 하고 크면 그 값을 그대로 통과시키는 함수로 0꺾임 현상을 이용해 복잡한 곡선 형태를 찾게 됨.
        
        # fc1을 통과 후, ReLU 활성화 함수를 적용 <- ReLU 배워보기
        x = F.relu(self.fc1(x))
        
        # fc 통과 후 ReLU 활성화 함수 적용
        x = F.relu(self.fc2(x))
        
        # 출력은 실제 예측값이므로 활성화 함수 씌우지 X
        return self.fc3(x)

# Replay Buffer (과거의 state 무작위로 꺼내줌)
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """
        한 턴이 끝날 때마다 발생하는 5가지 경험 state들을 저장 (done : 게임이 끝났는지 여부)
        """
        
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """
        랜덤으로 꺼내기 시작 (과적합 피하려고)
        """
        
        minibatch = random.sample(self.buffer, batch_size)
        
        # 이것들을 Tensor 타입으로 변형 -> 연산할 수 있도록
        # 대충 차원 바꿔서 torch가 연산할 수 있도록
        states = torch.FloatTensor([x[0] for x in minibatch])
        actions = torch.LongTensor([x[1] for x in minibatch]).unsqueeze(1) # 행동은 정수형
        rewards = torch.FloatTensor([x[2] for x in minibatch]).unsqueeze(1)
        next_states = torch.FloatTensor([x[3] for x in minibatch])
        dones = torch.FloatTensor([x[4] for x in minibatch]).unsqueeze(1)
        
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)

# 실제로 DQN을 수행할 Agent
class DQNAgent:
    def __init__(self, state_dim, action_dim):
        self.action_dim = action_dim
        
        # 신경망 내부 생성
        self.q_net = QNetwork(state_dim, action_dim)
        
        # 최적화 도구 (공부 더 필요)
        # lr(Learning rate, 학습률)로 오차 반영 비율 조정
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=0.001)
        
        # Replay Buffer 내부 생성
        self.memory = ReplayBuffer(capacity=10000)

        # 초반에는 무조건 무작위 탐험
        self.epsilon = 1.0
        self.epsilon_decay = 0.995 # 매 판마다 탐험률 0.5%씩 줄이기
        self.epsilon_min = 0.01 # 최소 1%는 무작위
    
    def get_action(self, state):
        # 0 ~ 1.0 사이에 무작위 실수
        if random.random() < self.epsilon:
            # ? action이 여기서 정확히 뭐였지
            return random.randint(0, self.action_dim - 1)
        else:
            # 뇌에 1개 상태를 포장해서 가장 높은 Q값을 행동에 반영
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_net(state_tensor)
            return torch.argmax(q_values).item() # 가장 점수가 높은 쪽의 인덱스 반환
    
    def train_step(self, batch_size = 32):
        if len(self.memory) < batch_size:
            return

        states, actions, rewards, next_states, dones = self.memory.sample(batch_size)
        
        # 과거 states 신경망에 넣어서 (여기 이해 안됨)
        current_q = self.q_net(states).gather(1, actions)
        
        with torch.no_grad(): # 불필요한 그래프 계산 꺼서 메모리, 속도 향상
            next_q = self.q_net(next_states).max(1)[0].unsqueeze(1)
            target_q = rewards + 0.99 * next_q * (1 - dones) # 게임이 다음에 끝났다면 미래 점수 0
        
        loss = F.mse_loss(current_q, target_q) # 평균 제곱 오차 (MSE) 구하기
        
        self.optimizer.zero_grad() # 메모리 clear
        loss.backward() # 역전파 (수정 방향 계산)
        self.optimizer.step() # 가중치 업데이트
            
env = gym.make('CartPole-v1')

# 생성한 환경이 제공하는 상태와 크기 자동으로 알아냄
state_dim = env.observation_space.shape[0]
action_dim = env.action_space.n

agent = DQNAgent(state_dim, action_dim)

for episode in range(300):
    state, info = env.reset()
    score = 0
    
    while True:
        action = agent.get_action(state)
        # ? 이해 안감
        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        # 방금 경험 Replay Buffer에 저장
        agent.memory.push(state, action, reward, next_state, done)
        
        agent.train_step(batch_size=32)
        
        state = next_state
        score += reward
        
        if done:
            break
    
    if agent.epsilon > agent.epsilon_min:
        agent.epsilon *= agent.epsilon_decay
    
    if (episode + 1) % 10 == 0:
        print(f"에피소드: {episode + 1:3d} | 최종 점수: {score:3.1f} | 현재 입실론(랜덤확률): {agent.epsilon:.3f}")