#!/usr/bin/env python3
"""
PID控制器
"""

import numpy as np


class PIDController:
    """PID控制器"""

    def __init__(self, kp=1.0, ki=0.1, kd=0.5, max_output=1.0):
        """
        初始化PID控制器
        
        Args:
            kp: 比例系数
            ki: 积分系数
            kd: 微分系数
            max_output: 最大输出
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_output = max_output
        
        self.integral = 0.0
        self.last_error = 0.0
        self.dt = 0.033  # 30Hz

    def update(self, error):
        """
        更新PID控制器
        
        Args:
            error: 当前误差
            
        Returns:
            float: 控制输出
        """
        # 积分项
        self.integral += error * self.dt
        self.integral = np.clip(self.integral, -1.0, 1.0)
        
        # 微分项
        derivative = (error - self.last_error) / self.dt if self.dt > 0 else 0
        
        # PID输出
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        output = np.clip(output, -self.max_output, self.max_output)
        
        self.last_error = error
        
        return output


class FollowController:
    """跟随控制器"""

    def __init__(self, pid_params):
        """
        初始化跟随控制器
        
        Args:
            pid_params: PID参数字典
        """
        # 创建各轴PID控制器
        self.distance_controller = PIDController(
            kp=pid_params['distance']['kp'],
            ki=pid_params['distance']['ki'],
            kd=pid_params['distance']['kd'],
            max_output=2.0
        )
        
        self.height_controller = PIDController(
            kp=0.8, ki=0.05, kd=0.3, max_output=1.0
        )
        
        self.velocity_controller = PIDController(
            kp=0.5, ki=0.02, kd=0.2, max_output=1.5
        )

    def compute(self, current_pos, target_pos, current_vel, target_vel,
                desired_distance, desired_height):
        """
        计算控制指令
        
        Args:
            current_pos: 当前位置 [x, y, z]
            target_pos: 目标位置 [x, y, z]
            current_vel: 当前速度 [vx, vy, vz]
            target_vel: 目标速度 [vx, vy, vz]
            desired_distance: 期望距离
            desired_height: 期望高度
            
        Returns:
            np.array: 速度命令 [vx, vy, vz]
        """
        # 计算水平距离和方向
        horizontal_vec = target_pos[:2] - current_pos[:2]
        horizontal_distance = np.linalg.norm(horizontal_vec)
        
        if horizontal_distance > 1e-6:
            direction = horizontal_vec / horizontal_distance
        else:
            direction = np.array([0.0, 0.0])
        
        # 距离控制
        distance_error = horizontal_distance - desired_distance
        distance_vel = self.distance_controller.update(distance_error)
        
        # 速度命令 = 方向 * 距离速度 + 目标速度同步
        velocity_x = direction[0] * distance_vel + target_vel[0] * 0.5
        velocity_y = direction[1] * distance_vel + target_vel[1] * 0.5
        
        # 高度控制
        height_error = target_pos[2] - current_pos[2]
        velocity_z = self.height_controller.update(height_error)
        
        return np.array([velocity_x, velocity_y, velocity_z])
