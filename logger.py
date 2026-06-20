# logger.py
import matplotlib.pyplot as plt
import numpy as np
import os

class LearningLogger:
    def __init__(self):
        self.episodes = []
        self.rewards = []
        self.successes = []
        self.distances = []

    def record(self, episode, reward, success, distance):
        self.episodes.append(episode)
        self.rewards.append(reward)
        self.successes.append(1 if success else 0)
        self.distances.append(distance)

    def save_plot(self, window=50, filename="learning_curve.png"):
        if len(self.rewards) < window:
            return  # 데이터가 최소 윈도우 사이즈만큼 쌓일 때까지는 그리지 않음

        # 이동 평균(Moving Average) 계산
        rewards_ma = np.convolve(self.rewards, np.ones(window)/window, mode='valid')
        success_ma = np.convolve(self.successes, np.ones(window)/window, mode='valid') * 100

        fig, ax1 = plt.subplots(figsize=(10, 5))

        # 축 1: 보상 그래프 (파란색)
        ax1.plot(range(window, len(self.rewards)+1), rewards_ma, 'b-', label='Avg Reward (50 ep)')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Reward', color='b')
        ax1.tick_params('y', colors='b')

        # 축 2: 성공률 그래프 (녹색)
        ax2 = ax1.twinx()
        ax2.plot(range(window, len(self.successes)+1), success_ma, 'g-', label='Success Rate (%)')
        ax2.set_ylabel('Success Rate (%)', color='g')
        ax2.tick_params('y', colors='g')
        ax2.set_ylim(-5, 105)

        plt.title('Autonomous Driving AI Learning Progress')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 덮어쓰기 방식으로 저장
        plt.savefig(filename)
        plt.close()