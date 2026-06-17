#!/usr/bin/env python3
"""
目标追踪器 - 平滑位置和速度计算
"""

import numpy as np
from collections import deque


class TargetTracker:
    """目标追踪器"""

    def __init__(self, history_size=10):
        """
        初始化追踪器
        
        Args:
            history_size: 历史位置数
        """
        self.history_size = history_size
        self.position_history = deque(maxlen=history_size)
        self.timestamp_history = deque(maxlen=history_size)
        self.last_position = None
        self.last_timestamp = None

    def update(self, position, velocity=None, timestamp=None):
        """
        更新追踪器
        
        Args:
            position: 当前位置 [x, y]
            velocity: 当前速度 [vx, vy] (可选)
            timestamp: 时间戳 (可选)
        """
        self.position_history.append(position)
        if timestamp is not None:
            self.timestamp_history.append(timestamp)
        self.last_position = position
        self.last_timestamp = timestamp

    def get_smoothed_position(self):
        """
        获取平滑后的位置（使用移动平均）
        
        Returns:
            np.array: 平滑后的位置 [x, y]
        """
        if len(self.position_history) == 0:
            return np.array([0.0, 0.0])
        
        positions = np.array(list(self.position_history))
        smoothed_pos = np.mean(positions, axis=0)
        return smoothed_pos

    def get_velocity(self):
        """
        计算目标速度
        
        Returns:
            np.array: 速度 [vx, vy]
        """
        if len(self.position_history) < 2:
            return np.array([0.0, 0.0])
        
        positions = np.array(list(self.position_history))
        # 使用线性回归估计速度
        if len(positions) > 1:
            # 简单的有限差分
            delta_pos = positions[-1] - positions[0]
            num_points = len(positions) - 1
            if num_points > 0:
                velocity = delta_pos / (num_points * 0.033)  # 假设30Hz
                return velocity
        
        return np.array([0.0, 0.0])

    def predict_position(self, steps=1):
        """
        预测未来位置
        
        Args:
            steps: 预测步数
            
        Returns:
            np.array: 预测位置
        """
        current_pos = self.get_smoothed_position()
        velocity = self.get_velocity()
        predicted_pos = current_pos + velocity * steps
        return predicted_pos
