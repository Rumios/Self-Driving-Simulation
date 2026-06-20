import matplotlib.pyplot as plt
import numpy as np
import os

class LearningLogger:
    def __init__(self):
        self.episodes = []
        self.rewards = []
        self.successes = []
        self.distances = []
        self.steps = []  # 💡 스텝 수 저장 리스트 추가

    # 💡 파라미터에 steps 추가
    def record(self, episode, reward, success, distance, steps):
        self.episodes.append(episode)
        self.rewards.append(reward)
        self.successes.append(1 if success else 0)
        self.distances.append(distance)
        self.steps.append(steps)  # 스텝 기록

    def save_plot(self, window=50, filename="learning_curve.png"):
        if len(self.rewards) < window:
            return  # 데이터가 최소 윈도우 사이즈만큼 쌓일 때까지는 그리지 않음

        # 이동 평균(Moving Average) 계산
        rewards_ma = np.convolve(self.rewards, np.ones(window)/window, mode='valid')
        success_ma = np.convolve(self.successes, np.ones(window)/window, mode='valid') * 100
        steps_ma = np.convolve(self.steps, np.ones(window)/window, mode='valid')          # 💡 스텝 수 이동평균
        distances_ma = np.convolve(self.distances, np.ones(window)/window, mode='valid')  # 💡 이동 거리 이동평균

        # 💡 위아래 2개의 그래프로 나누기 (figsize 세로 길이 증가)
        fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(10, 8))

        # ==========================================
        # [위쪽 그래프] 축 1: 보상 & 성공률
        # ==========================================
        ax1.plot(range(window, len(self.rewards)+1), rewards_ma, 'b-', label='Avg Reward')
        ax1.set_ylabel('Reward', color='b', fontweight='bold')
        ax1.tick_params('y', colors='b')
        ax1.grid(True, alpha=0.3)
        ax1.set_title('AI Learning Progress - Reward & Success Rate', fontweight='bold')

        ax2 = ax1.twinx()
        ax2.plot(range(window, len(self.successes)+1), success_ma, 'g-', label='Success Rate (%)')
        ax2.set_ylabel('Success Rate (%)', color='g', fontweight='bold')
        ax2.tick_params('y', colors='g')
        ax2.set_ylim(-5, 105)

        # ==========================================
        # [아래쪽 그래프] 축 2: 스텝 수 & 이동 거리
        # ==========================================
        ax3.plot(range(window, len(self.steps)+1), steps_ma, 'r-', label='Avg Steps')
        ax3.set_xlabel('Episode', fontweight='bold')
        ax3.set_ylabel('Steps (Time)', color='r', fontweight='bold')
        ax3.tick_params('y', colors='r')
        ax3.grid(True, alpha=0.3)
        ax3.set_title('AI Efficiency - Steps & Distance', fontweight='bold')

        # 거리 축 추가 (오렌지색)
        ax4 = ax3.twinx()
        ax4.plot(range(window, len(self.distances)+1), distances_ma, color='darkorange', label='Avg Distance')
        ax4.set_ylabel('Distance (px)', color='darkorange', fontweight='bold')
        ax4.tick_params('y', colors='darkorange')

        plt.tight_layout()
        
        # 덮어쓰기 방식으로 저장
        plt.savefig(filename, dpi=150)
        plt.close()