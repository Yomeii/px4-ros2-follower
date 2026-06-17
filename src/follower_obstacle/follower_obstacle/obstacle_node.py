#!/usr/bin/env python3
"""
避障节点
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Float32
from cv_bridge import CvBridge
import cv2
import numpy as np
from .obstacle_detector import ObstacleDetector


class ObstacleNode(Node):
    """避障节点"""

    def __init__(self):
        super().__init__('obstacle_node')
        
        # 声明参数
        self.declare_parameter('front_distance', 1.5)
        self.declare_parameter('safe_distance', 0.8)
        self.declare_parameter('detection_frequency', 20)
        
        # 获取参数
        self.front_distance = self.get_parameter('front_distance').value
        self.safe_distance = self.get_parameter('safe_distance').value
        self.detection_frequency = self.get_parameter('detection_frequency').value
        
        # 初始化检测器
        self.detector = ObstacleDetector(
            front_distance=self.front_distance,
            safe_distance=self.safe_distance
        )
        
        self.bridge = CvBridge()
        
        # 订阅者
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        
        # 发布者
        self.obstacle_pub = self.create_publisher(Bool, '/obstacle/detected', 10)
        self.obstacle_distance_pub = self.create_publisher(
            Float32, '/obstacle/distance', 10
        )
        
        self.get_logger().info('Obstacle node initialized')

    def image_callback(self, msg):
        """图像回调"""
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return
        
        # 检测障碍物
        obstacle_info = self.detector.detect(frame)
        
        # 发布检测结果
        obstacle_msg = Bool(data=obstacle_info['detected'])
        self.obstacle_pub.publish(obstacle_msg)
        
        if obstacle_info['detected']:
            distance_msg = Float32(data=obstacle_info['distance'])
            self.obstacle_distance_pub.publish(distance_msg)
            self.get_logger().warn(
                f'Obstacle detected at distance: {obstacle_info["distance"]:.2f}m'
            )


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
