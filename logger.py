import matplotlib.pyplot as plt
import numpy as np
import os

class LearningLogger:
    def __init__(self):
        self.episodes = []
        self.rewards = []
        self.successes = []
        self.distances = []
        self.steps = []
        self.outcomes = []

    def record(self, episode, reward, success, distance, steps, reason):
        self.episodes.append(episode)
        self.rewards.append(reward)
        self.successes.append(1 if success else 0)
        self.distances.append(distance)
        self.steps.append(steps)
        self.outcomes.append(reason)

    def save_plot(self, window=50, filename="learning_curve.png"):
        if len(self.rewards) < window:
            return

        # 1, 2번 그래프용 데이터
        rewards_ma = np.convolve(self.rewards, np.ones(window)/window, mode='valid')
        success_ma = np.convolve(self.successes, np.ones(window)/window, mode='valid') * 100
        steps_ma = np.convolve(self.steps, np.ones(window)/window, mode='valid')
        
        step_efficiency = [d / s if s > 0 else 0 for d, s in zip(self.distances, self.steps)]
        efficiency_ma = np.convolve(step_efficiency, np.ones(window)/window, mode='valid')

        fig, (ax1, ax3, ax5) = plt.subplots(3, 1, figsize=(12, 15))

        # ==========================================
        # 1. 보상 & 성공률 추이
        # ==========================================
        ax1.plot(range(window, len(self.rewards)+1), rewards_ma, 'b-', label='Avg Reward')
        ax1.set_xlabel('Episode', fontweight='bold')
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
        # 2. 총 스텝 수 & 스텝당 주행 효율성
        # ==========================================
        ax3.plot(range(window, len(self.steps)+1), steps_ma, 'r-', label='Avg Steps')
        ax3.set_xlabel('Episode', fontweight='bold')
        ax3.set_ylabel('Total Steps (Time)', color='r', fontweight='bold')
        ax3.tick_params('y', colors='r')
        ax3.grid(True, alpha=0.3)
        ax3.set_title('AI Driving Efficiency - Steps & Step Efficiency', fontweight='bold')

        ax4 = ax3.twinx()
        ax4.plot(range(window, len(step_efficiency)+1), efficiency_ma, 'm-', label='Dist / Step')
        ax4.set_ylabel('Distance per Step (px)', color='m', fontweight='bold')
        ax4.tick_params('y', colors='m')

        # ==========================================
        # 3. [변경됨] Rolling Window 기반 누적 영역 차트 (Stacked Area Chart)
        # ==========================================
        # 텍스트 데이터를 0과 1로 변환
        success_arr = np.array([1 if o == 'success' else 0 for o in self.outcomes])
        collision_arr = np.array([1 if o == 'collision' else 0 for o in self.outcomes])
        timeout_arr = np.array([1 if o == 'timeout' else 0 for o in self.outcomes])

        # convolve를 이용해 각 구간(window)별 발생 '횟수 합계' 계산
        success_roll = np.convolve(success_arr, np.ones(window), mode='valid')
        collision_roll = np.convolve(collision_arr, np.ones(window), mode='valid')
        timeout_roll = np.convolve(timeout_arr, np.ones(window), mode='valid')

        x_axis = range(window, len(self.outcomes) + 1)
        colors = ['#2ca02c', '#d62728', '#ff7f0e'] # Green(Success), Red(Collision), Orange(Timeout)

        # 누적 영역 렌더링
        ax5.stackplot(x_axis, success_roll, collision_roll, timeout_roll, 
                      labels=['Success', 'Collision', 'Timeout'], 
                      colors=colors, alpha=0.8)

        ax5.set_title(f'Rolling Termination Causes Distribution (Window={window})', fontweight='bold')
        ax5.set_xlabel('Episode', fontweight='bold')
        ax5.set_ylabel(f'Count (out of {window})', fontweight='bold')
        ax5.margins(x=0, y=0) # 그래프가 축에 꽉 차게 설정
        ax5.legend(loc='upper left')
        ax5.grid(True, alpha=0.3)

        fig.tight_layout()
        plt.savefig(filename)
        plt.close()