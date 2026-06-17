#!/usr/bin/env python3
"""
自主跟随主控制节点
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist, PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
import numpy as np
from .controller import FollowController
from .state_manager import StateManager


class FollowerNode(Node):
    """主控制节点"""

    def __init__(self):
        super().__init__('follower_node')
        
        # 声明参数
        self.declare_parameter('target_distance', 2.0)
        self.declare_parameter('target_height', 1.5)
        self.declare_parameter('control_frequency', 30)
        self.declare_parameter('pid_distance_kp', 1.2)
        self.declare_parameter('pid_distance_ki', 0.1)
        self.declare_parameter('pid_distance_kd', 0.5)
        
        # 获取参数
        self.target_distance = self.get_parameter('target_distance').value
        self.target_height = self.get_parameter('target_height').value
        self.control_frequency = self.get_parameter('control_frequency').value
        
        pid_params = {
            'distance': {
                'kp': self.get_parameter('pid_distance_kp').value,
                'ki': self.get_parameter('pid_distance_ki').value,
                'kd': self.get_parameter('pid_distance_kd').value,
            }
        }
        
        # 初始化控制器和状态管理器
        self.controller = FollowController(pid_params)
        self.state_manager = StateManager()
        
        # 订阅者
        self.target_pos_sub = self.create_subscription(
            Point, '/target/position', self.target_position_callback, 10
        )
        self.target_vel_sub = self.create_subscription(
            Twist, '/target/velocity', self.target_velocity_callback, 10
        )
        self.drone_state_sub = self.create_subscription(
            Odometry, '/drone/state', self.drone_state_callback, 10
        )
        self.target_detected_sub = self.create_subscription(
            Bool, '/target/detected', self.target_detected_callback, 10
        )
        
        # 发布者
        self.setpoint_pub = self.create_publisher(
            PoseStamped, '/mavros/setpoint_position/local', 10
        )
        self.velocity_pub = self.create_publisher(
            Twist, '/mavros/setpoint_velocity/cmd_vel', 10
        )
        
        # 状态变量
        self.target_position = np.array([0.0, 0.0, 0.0])
        self.target_velocity = np.array([0.0, 0.0, 0.0])
        self.drone_position = np.array([0.0, 0.0, 0.0])
        self.drone_velocity = np.array([0.0, 0.0, 0.0])
        self.target_detected = False
        self.target_lost_counter = 0
        self.target_lost_timeout = 3 * self.control_frequency  # 3秒
        
        # 定时器
        timer_period = 1.0 / self.control_frequency
        self.timer = self.create_timer(timer_period, self.control_loop)
        
        self.get_logger().info('Follower node initialized')

    def target_position_callback(self, msg):
        """目标位置回调"""
        self.target_position = np.array([msg.x, msg.y, msg.z])
        self.target_lost_counter = 0

    def target_velocity_callback(self, msg):
        """目标速度回调"""
        self.target_velocity = np.array([
            msg.linear.x,
            msg.linear.y,
            msg.linear.z
        ])

    def drone_state_callback(self, msg):
        """无人机状态回调"""
        self.drone_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])
        self.drone_velocity = np.array([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.linear.z
        ])

    def target_detected_callback(self, msg):
        """目标检测状态回调"""
        self.target_detected = msg.data
        if not self.target_detected:
            self.target_lost_counter += 1

    def control_loop(self):
        """主控制循环"""
        if self.target_lost_counter > self.target_lost_timeout:
            self.get_logger().warn('Target lost, hovering')
            self.state_manager.set_state('hover')
            return
        
        if not self.target_detected:
            return
        
        # 计算目标位置
        direction = self.target_position - self.drone_position
        distance = np.linalg.norm(direction[:2])  # 水平距离
        
        # 计算期望位置
        desired_position = self.calculate_desired_position()
        
        # 计算控制输出
        velocity_command = self.controller.compute(
            current_pos=self.drone_position,
            target_pos=self.target_position,
            current_vel=self.drone_velocity,
            target_vel=self.target_velocity,
            desired_distance=self.target_distance,
            desired_height=self.target_height
        )
        
        # 发布速度命令
        vel_msg = Twist()
        vel_msg.linear.x = velocity_command[0]
        vel_msg.linear.y = velocity_command[1]
        vel_msg.linear.z = velocity_command[2]
        self.velocity_pub.publish(vel_msg)
        
        self.get_logger().info(
            f'Position: {self.drone_position}, '
            f'Target: {self.target_position}, '
            f'Distance: {distance:.2f}m'
        )

    def calculate_desired_position(self):
        """
        计算期望位置
        
        Returns:
            np.array: 期望位置
        """
        # 计算方向向量
        direction = self.target_position[:2] - self.drone_position[:2]
        distance = np.linalg.norm(direction)
        
        if distance > 1e-6:
            direction = direction / distance
            # 保持固定距离
            desired_pos = self.target_position[:2] - direction * self.target_distance
        else:
            desired_pos = self.target_position[:2]
        
        # 添加高度
        desired_pos = np.append(desired_pos, self.target_height)
        return desired_pos


def main(args=None):
    rclpy.init(args=args)
    node = FollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
