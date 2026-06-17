# 🐛 调试指南

## 日志和诊断

### 启用ROS2调试输出

```bash
# 设置ROS2日志级别
export RCL_LOG_LEVEL=DEBUG

# 或在代码中设置
import rclpy
rclpy.logging.initialize()
logger = rclpy.logging.get_logger('my_logger')
logger.debug('Debug message')
```

### 查看日志

```bash
# 查看ROS2日志目录
ls ~/.ros/log/

# 显示最新的日志
cat ~/.ros/log/latest/*/rosout.log
```

## 话题监控

### 实时监控话题

```bash
# 监控摄像头图像（显示频率）
ros2 topic hz /camera/image_raw

# 监控目标位置
ros2 topic hz /target/position

# 监控消息大小
ros2 topic bw /camera/image_raw
```

### 话题统计信息

```bash
# 获取话题详细信息
ros2 topic info /target/position

# 输出示例：
# Type: geometry_msgs/Point
# Publisher count: 1
# Subscriber count: 1
```

### 记录话题数据

```bash
# 记录特定话题到文件
ros2 bag record /target/position /target/detected --output ~/ros_bags/session_1

# 查看录制的数据
ros2 bag info ~/ros_bags/session_1

# 回放数据
ros2 bag play ~/ros_bags/session_1
```

## 节点诊断

### 列出所有节点

```bash
ros2 node list

# 输出示例：
# /vision_node
# /follower_node
# /obstacle_node
# /gazebo
```

### 查看节点详细信息

```bash
# 查看节点发布的话题
ros2 node info /vision_node

# 输出示例：
# Subscriptions:
#   /camera/[image_transport]
# Publications:
#   /camera/image_raw: sensor_msgs/msg/Image
#   /target/position: geometry_msgs/msg/Point
#   ...
```

### 杀死节点

```bash
ros2 node kill /vision_node
```

## 可视化调试

### 使用RViz

```bash
# ���动RViz
rviz2

# 或使用配置文件
rviz2 -d config/visualization.rviz
```

### RViz常用操作

1. **添加显示**：左下角 "Add" → 选择消息类型
2. **查看摄像头图像**：Add → Image → 选择 `/camera/image_raw`
3. **查看点云**：Add → PointCloud2 → 选择话题
4. **查看坐标系**：Add → TF
5. **查看轨迹**：Add → Path → 选择轨迹话题

### 使用rqt进行可视化

```bash
# 启动rqt
rqt

# 常用插件
rqt_plot      # 绘制数据曲线
rqt_image_view # 显示图像话题
rqt_graph     # 显示节点连接图
rqt_topic     # 监控话题
```

## 性能分析

### 测量话题延迟

```python
import rclpy
import time
from geometry_msgs.msg import Point

class LatencyMonitor:
    def __init__(self):
        self.start_time = None
        self.latencies = []
    
    def callback(self, msg):
        current_time = time.time()
        if self.start_time:
            latency = (current_time - self.start_time) * 1000  # ms
            self.latencies.append(latency)
            if len(self.latencies) % 100 == 0:
                avg = sum(self.latencies) / len(self.latencies)
                print(f"Average latency: {avg:.2f}ms")
        self.start_time = current_time

rclpy.init()
node = rclpy.create_node('latency_monitor')
monitor = LatencyMonitor()
node.create_subscription(Point, '/target/position', monitor.callback, 10)
rclpy.spin(node)
```

### CPU和内存使用

```bash
# 监控所有ROS2进程
top -p $(pgrep -f ros2 | tr '\n' ',')

# 使用ps查看
ps aux | grep ros2
```

## 常见问题调试

### 问题1：无人机无法起飞

**检查清单**：
```bash
# 1. 检查PX4是否运行
ros2 topic list | grep mavros

# 2. 检查GPS状态
ros2 topic echo /mavros/global_position/gp_origin

# 3. 查看飞控日志
cat ~/.local/share/PX4-Autopilot/build/px4_sitl_default/logs/latest/log.txt

# 4. 检查无人机是否解锁
ros2 service call /mavros/cmd/arming mavros_msgs/CommandBool "{value: true}"
```

### 问题2：视觉识别失败

**调试代码**：
```python
import cv2
import numpy as np

image = cv2.imread('frame.jpg')
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 测试HSV范围
lower = np.array([0, 50, 50])
upper = np.array([10, 255, 255])
mask = cv2.inRange(hsv, lower, upper)

# 显示结果
cv2.imshow('Original', image)
cv2.imshow('Mask', mask)
cv2.waitKey(0)
```

**HSV范围查找**：
```python
import cv2
import numpy as np

def get_hsv_range(image_path):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 创建滑块调整范围
    def nothing(x):
        pass
    
    cv2.namedWindow('HSV')
    cv2.createTrackbar('H_min', 'HSV', 0, 180, nothing)
    cv2.createTrackbar('S_min', 'HSV', 0, 255, nothing)
    cv2.createTrackbar('V_min', 'HSV', 0, 255, nothing)
    cv2.createTrackbar('H_max', 'HSV', 180, 180, nothing)
    cv2.createTrackbar('S_max', 'HSV', 255, 255, nothing)
    cv2.createTrackbar('V_max', 'HSV', 255, 255, nothing)
    
    while True:
        h_min = cv2.getTrackbarPos('H_min', 'HSV')
        s_min = cv2.getTrackbarPos('S_min', 'HSV')
        v_min = cv2.getTrackbarPos('V_min', 'HSV')
        h_max = cv2.getTrackbarPos('H_max', 'HSV')
        s_max = cv2.getTrackbarPos('S_max', 'HSV')
        v_max = cv2.getTrackbarPos('V_max', 'HSV')
        
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        
        cv2.imshow('Result', mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'Lower: {[h_min, s_min, v_min]}')
            print(f'Upper: {[h_max, s_max, v_max]}')
            break
    
    cv2.destroyAllWindows()

get_hsv_range('target_image.jpg')
```

### 问题3：跟随��稳定

**调试步骤**：

1. **检查控制频率**
```bash
ros2 topic hz /target/position
ros2 topic hz /drone/state
ros2 topic hz /mavros/setpoint_velocity/cmd_vel
```

2. **记录PID参数**
```python
import rclpy
from follower_control.controller import PIDController

controller = PIDController(kp=1.2, ki=0.1, kd=0.5)
errors = []
errors.append(0.5)  # 第一个误差
error_derivative = []

for i, error in enumerate(errors[1:]):
    de = error - errors[i]
    error_derivative.append(de)
    output = controller.update(error)
    print(f"Error: {error:.3f}, dE: {de:.3f}, Output: {output:.3f}")
```

3. **绘制控制曲线**
```bash
ros2 run rqt_plot rqt_plot
# 添加话题：/target/position/x /drone/state/pose/pose/position/x
```

### 问题4：内存泄漏

**检查内存使用**：
```bash
# 运行30秒并监控内存
watch -n 1 'ps aux | grep ros2 | grep -v grep'

# 使用valgrind进行内存检查
valgrind --leak-check=full ros2 run follower_vision vision_node
```

## 单元测试

### 运行测试

```bash
# 运行所有测试
colcon test

# 运行特定包的测试
colcon test --packages-select follower_vision

# 显示测试输出
colcon test --packages-select follower_vision --verbose
```

### 编写测试

```python
# tests/test_detector.py
import unittest
from follower_vision.detector import TargetDetector
import cv2
import numpy as np

class TestTargetDetector(unittest.TestCase):
    def setUp(self):
        self.detector = TargetDetector(
            lower_hsv=[0, 50, 50],
            upper_hsv=[10, 255, 255]
        )
    
    def test_detect_red_target(self):
        # 创建测试图像
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # 绘制红色圆形
        cv2.circle(frame, (320, 240), 50, (0, 0, 255), -1)
        
        result = self.detector.detect(frame)
        self.assertTrue(result['detected'])
        self.assertLess(abs(result['center'][0] - 320), 10)

if __name__ == '__main__':
    unittest.main()
```

## 交互式调试

### 使用Python调试器

```python
import pdb

def problematic_function():
    x = 1
    pdb.set_trace()  # 调试器会在这里停止
    y = x + 1
    return y
```

### 使用IPython进行交互式测试

```bash
# 安装IPython
pip3 install ipython

# 启动交互式Python
ipython

# 在IPython中
from follower_vision.detector import TargetDetector
import cv2

detector = TargetDetector([0, 50, 50], [10, 255, 255])
frame = cv2.imread('test_image.jpg')
result = detector.detect(frame)
print(result)
```

## 性能基准测试

```python
import time
import cv2
from follower_vision.detector import TargetDetector

detector = TargetDetector([0, 50, 50], [10, 255, 255])
frame = cv2.imread('test_image.jpg')

# 基准测试
start = time.time()
for _ in range(100):
    result = detector.detect(frame)
end = time.time()

avg_time = (end - start) / 100 * 1000  # ms
fps = 1000 / avg_time

print(f"Average detection time: {avg_time:.2f}ms")
print(f"FPS: {fps:.1f}")
```

## 下一步

- 📖 查看[使用教程](USAGE.md)
- 🔧 参考[API文档](API.md)
