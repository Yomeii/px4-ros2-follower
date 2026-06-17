#!/usr/bin/env python3
"""
障碍物检测器
"""

import cv2
import numpy as np


class ObstacleDetector:
    """基于边缘检测的障碍物检测器"""

    def __init__(self, front_distance=1.5, safe_distance=0.8):
        """
        初始化检测器
        
        Args:
            front_distance: 前方检测距离
            safe_distance: 安全距离
        """
        self.front_distance = front_distance
        self.safe_distance = safe_distance
        self.fov = 62.0  # 摄像头水平视场角

    def detect(self, frame):
        """
        检测障碍物
        
        Args:
            frame: 输入图像
            
        Returns:
            dict: 检测结果
        """
        # 灰度化
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Canny边缘检测
        edges = cv2.Canny(gray, 100, 200)
        
        # 在前方ROI区域检测
        h, w = frame.shape[:2]
        roi_top = h // 3
        roi_bottom = h
        roi_left = w // 4
        roi_right = 3 * w // 4
        
        roi = edges[roi_top:roi_bottom, roi_left:roi_right]
        
        # 计算边缘密度
        edge_density = np.sum(roi) / (roi.size * 255)
        
        result = {
            'detected': False,
            'distance': float('inf'),
            'density': edge_density
        }
        
        # 如果边缘密度高，认为有障碍物
        if edge_density > 0.15:  # 阈值
            result['detected'] = True
            # 估计距离（简单模型）
            estimated_distance = self.front_distance * (1 - edge_density)
            result['distance'] = max(estimated_distance, self.safe_distance)
        
        return result
