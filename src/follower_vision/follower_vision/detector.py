#!/usr/bin/env python3
"""
目标检测器 - 使用颜色识别
"""

import cv2
import numpy as np


class TargetDetector:
    """基于颜色的目标检测器"""

    def __init__(self, lower_hsv, upper_hsv):
        """
        初始化检测器
        
        Args:
            lower_hsv: HSV下限 [H, S, V]
            upper_hsv: HSV上限 [H, S, V]
        """
        self.lower_hsv = np.array(lower_hsv)
        self.upper_hsv = np.array(upper_hsv)
        
        # 形态学核
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def detect(self, frame):
        """
        检测图像中的目标
        
        Args:
            frame: 输入图像 (BGR)
            
        Returns:
            dict: 检测结果
        """
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 创建掩码
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        # 形态学操作
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        result = {
            'detected': False,
            'center': None,
            'contour': None,
            'velocity': np.array([0.0, 0.0]),
            'area': 0
        }
        
        if len(contours) > 0:
            # 找最大轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # 过滤最小面积
            if area > 500:
                # 计算质心
                M = cv2.moments(largest_contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    
                    result['detected'] = True
                    result['center'] = np.array([cx, cy])
                    result['contour'] = largest_contour
                    result['area'] = area
        
        return result
