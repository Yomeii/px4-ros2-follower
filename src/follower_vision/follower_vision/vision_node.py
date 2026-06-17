#!/usr/bin/env python3
"""
视觉处理节点 - 目标检测和追踪
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, Twist
from std_msgs.msg import Bool
from cv_bridge import CvBridge
import cv2
import numpy as np
from .detector import TargetDetector
from .tracker import TargetTracker


class VisionNode(Node):
    """视觉识别节点"""

    def __init__(self):
        super().__init__('vision_node')
        
        # 声明参数
        self.declare_parameter('camera_device', 0)
        self.declare_parameter('target_color_lower', [0, 50, 50])
        self.declare_parameter('target_color_upper', [10, 255, 255])
        self.declare_parameter('processing_frequency', 30)
        
        # 获取参数
        self.camera_device = self.get_parameter('camera_device').value
        self.target_color_lower = self.get_parameter('target_color_lower').value
        self.target_color_upper = self.get_parameter('target_color_upper').value
        self.processing_frequency = self.get_parameter('processing_frequency').value
        
        # 初始化检测器和追踪器
        self.detector = TargetDetector(
            lower_hsv=self.target_color_lower,
            upper_hsv=self.target_color_upper
        )
        self.tracker = TargetTracker(history_size=10)
        
        # 摄像头
        self.cap = cv2.VideoCapture(self.camera_device)
        self.bridge = CvBridge()
        
        # 发布者
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.target_pos_pub = self.create_publisher(Point, '/target/position', 10)
        self.target_vel_pub = self.create_publisher(Twist, '/target/velocity', 10)
        self.detection_pub = self.create_publisher(Bool, '/target/detected', 10)
        
        # 定时器
        timer_period = 1.0 / self.processing_frequency
        self.timer = self.create_timer(timer_period, self.process_frame)
        
        self.get_logger().info('Vision node initialized')

    def process_frame(self):
        """处理摄像头帧"""
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn('Failed to read frame from camera')
            return
        
        # 检测目标
        target_info = self.detector.detect(frame)
        
        if target_info['detected']:
            # 更新追踪器
            self.tracker.update(target_info['center'], target_info['velocity'])
            
            # 获取平滑后的位置和速度
            smoothed_pos = self.tracker.get_smoothed_position()
            smoothed_vel = self.tracker.get_velocity()
            
            # 发布目标位置
            pos_msg = Point()
            pos_msg.x = float(smoothed_pos[0])
            pos_msg.y = float(smoothed_pos[1])
            pos_msg.z = 0.0
            self.target_pos_pub.publish(pos_msg)
            
            # 发布目标速度
            vel_msg = Twist()
            vel_msg.linear.x = float(smoothed_vel[0])
            vel_msg.linear.y = float(smoothed_vel[1])
            vel_msg.linear.z = 0.0
            self.target_vel_pub.publish(vel_msg)
            
            # 发布检测状态
            detection_msg = Bool(data=True)
            self.detection_pub.publish(detection_msg)
            
            # 在图像上绘制
            cv2.circle(frame, tuple(map(int, smoothed_pos)), 5, (0, 255, 0), -1)
            cv2.drawContours(frame, [target_info['contour']], 0, (0, 255, 0), 2)
        else:
            # 发布未检测状态
            detection_msg = Bool(data=False)
            self.detection_pub.publish(detection_msg)
            self.get_logger().info('Target not detected')
        
        # 发布处理后的图像
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.image_pub.publish(img_msg)

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'cap'):
            self.cap.release()


def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
