# 🔧 API文档

## ROS2 节点

### vision_node (视觉节点)

视觉识别和目标追踪节点。

#### 发布的话题 (Publishers)

| 话题名 | 消息类型 | 频率 | 说明 |
|--------|---------|------|------|
| `/camera/image_raw` | `sensor_msgs/Image` | 30Hz | 处理后的摄像头图像 |
| `/target/position` | `geometry_msgs/Point` | 30Hz | 目标位置 (x, y, z) |
| `/target/velocity` | `geometry_msgs/Twist` | 30Hz | 目标速度 (vx, vy, vz) |
| `/target/detected` | `std_msgs/Bool` | 30Hz | 目标是否检测到 |

#### 订阅的话题 (Subscribers)

无

#### 参数 (Parameters)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `camera_device` | int | 0 | 摄像头设备ID |
| `target_color_lower` | list[int] | [0, 50, 50] | HSV下限 |
| `target_color_upper` | list[int] | [10, 255, 255] | HSV上限 |
| `processing_frequency` | int | 30 | 处理频率 (Hz) |

#### 使用示例

```python
import rclpy
from geometry_msgs.msg import Point

def target_position_callback(msg):
    print(f"Target position: ({msg.x}, {msg.y}, {msg.z})")

rclpy.init()
node = rclpy.create_node('subscriber')
node.create_subscription(Point, '/target/position', target_position_callback, 10)
rclpy.spin(node)
```

---

### follower_node (控制节点)

自主跟随控制节点。

#### 发布的话题 (Publishers)

| 话题名 | 消息类型 | 说明 |
|--------|---------|------|
| `/mavros/setpoint_position/local` | `geometry_msgs/PoseStamped` | 位置控制指令 |
| `/mavros/setpoint_velocity/cmd_vel` | `geometry_msgs/Twist` | 速度控制指令 |

#### 订阅的话题 (Subscribers)

| 话题名 | 消息类型 | 说明 |
|--------|---------|------|
| `/target/position` | `geometry_msgs/Point` | 目标位置 |
| `/target/velocity` | `geometry_msgs/Twist` | 目标速度 |
| `/drone/state` | `nav_msgs/Odometry` | 无人机状态 |
| `/target/detected` | `std_msgs/Bool` | 目标检测状态 |

#### 参数 (Parameters)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `target_distance` | float | 2.0 | ���标跟随距离 (m) |
| `target_height` | float | 1.5 | 目标飞行高度 (m) |
| `control_frequency` | int | 30 | 控制更新频率 (Hz) |
| `pid_distance_kp` | float | 1.2 | 距离PID Kp |
| `pid_distance_ki` | float | 0.1 | 距离PID Ki |
| `pid_distance_kd` | float | 0.5 | 距离PID Kd |

#### 使用示例

```python
import rclpy
from geometry_msgs.msg import Twist

def publish_velocity_command():
    rclpy.init()
    node = rclpy.create_node('velocity_publisher')
    pub = node.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel', 10)
    
    msg = Twist()
    msg.linear.x = 1.0  # 前进速度
    msg.linear.y = 0.0
    msg.linear.z = 0.5  # 上升速度
    pub.publish(msg)
    
    rclpy.spin(node)

if __name__ == '__main__':
    publish_velocity_command()
```

---

### obstacle_node (避障节点)

障碍物检测和避障节点。

#### 发布的话题 (Publishers)

| 话题名 | 消息类型 | 说明 |
|--------|---------|------|
| `/obstacle/detected` | `std_msgs/Bool` | 是否检测到障碍物 |
| `/obstacle/distance` | `std_msgs/Float32` | 障碍物距离 (m) |

#### 订阅的话题 (Subscribers)

| 话题名 | 消息类型 | 说明 |
|--------|---------|------|
| `/camera/image_raw` | `sensor_msgs/Image` | 摄像头图像 |

#### 参数 (Parameters)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `front_distance` | float | 1.5 | 前方检测距离 (m) |
| `safe_distance` | float | 0.8 | 最小安全距离 (m) |
| `detection_frequency` | int | 20 | 检测频率 (Hz) |

#### 使用示例

```python
import rclpy
from std_msgs.msg import Bool, Float32

def obstacle_callback(msg):
    if msg.data:
        print("Obstacle detected!")
    else:
        print("No obstacle")

def distance_callback(msg):
    print(f"Obstacle distance: {msg.data:.2f}m")

rclpy.init()
node = rclpy.create_node('obstacle_subscriber')
node.create_subscription(Bool, '/obstacle/detected', obstacle_callback, 10)
node.create_subscription(Float32, '/obstacle/distance', distance_callback, 10)
rclpy.spin(node)
```

---

## Python 类

### TargetDetector

目标检测器类。

```python
from follower_vision.detector import TargetDetector

# 初始化
detector = TargetDetector(
    lower_hsv=[0, 50, 50],
    upper_hsv=[10, 255, 255]
)

# 检测目标
result = detector.detect(frame)  # frame是OpenCV图像

# 结果格式
{
    'detected': bool,          # 是否检测到
    'center': np.array([x, y]),# 中心位置
    'contour': contour,        # 轮廓
    'velocity': np.array([vx, vy]),  # 速度
    'area': float              # 面积
}
```

#### 方法

**detect(frame)**
- 输入: OpenCV图像 (BGR)
- 输出: dict - 检测结果
- 描述: 检测图像中的目标

---

### TargetTracker

目标追踪器类。

```python
from follower_vision.tracker import TargetTracker
import numpy as np

# 初始化
tracker = TargetTracker(history_size=10)

# 更新追踪
tracker.update(
    position=np.array([100, 200]),
    velocity=np.array([2.0, 1.0]),
    timestamp=time.time()
)

# 获取平滑位置
smoothed_pos = tracker.get_smoothed_position()  # np.array([x, y])

# 获取速度
velocity = tracker.get_velocity()  # np.array([vx, vy])

# 预测未来位置
predicted_pos = tracker.predict_position(steps=5)  # np.array([x, y])
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `update()` | position, velocity, timestamp | None | 更新追踪数据 |
| `get_smoothed_position()` | 无 | np.array | 获取平滑后的位置 |
| `get_velocity()` | 无 | np.array | 计算目标速度 |
| `predict_position()` | steps | np.array | 预测未来位置 |

---

### PIDController

PID控制器类。

```python
from follower_control.controller import PIDController

# 初始化
controller = PIDController(
    kp=1.2,
    ki=0.1,
    kd=0.5,
    max_output=2.0
)

# 计算输出
error = desired_value - current_value
output = controller.update(error)  # float
```

#### 方法

**update(error)**
- 输入: float - 当前误差
- 输出: float - PID输出
- 描述: 计算PID控制输出

---

### FollowController

跟随控制器类。

```python
from follower_control.controller import FollowController
import numpy as np

# 初始化
controller = FollowController({
    'distance': {
        'kp': 1.2,
        'ki': 0.1,
        'kd': 0.5
    }
})

# 计算控制指令
velocity_cmd = controller.compute(
    current_pos=np.array([0.0, 0.0, 1.0]),
    target_pos=np.array([2.0, 0.0, 1.0]),
    current_vel=np.array([0.0, 0.0, 0.0]),
    target_vel=np.array([0.5, 0.0, 0.0]),
    desired_distance=2.0,
    desired_height=1.5
)  # 返回 np.array([vx, vy, vz])
```

#### 方法

**compute()**
- 输入: current_pos, target_pos, current_vel, target_vel, desired_distance, desired_height
- 输出: np.array([vx, vy, vz])
- 描述: 计算速度控制指令

---

### ObstacleDetector

障碍物检测器类。

```python
from follower_obstacle.obstacle_detector import ObstacleDetector

# 初始化
detector = ObstacleDetector(
    front_distance=1.5,
    safe_distance=0.8
)

# 检测
result = detector.detect(frame)

# 结果格式
{
    'detected': bool,      # 是否检测到
    'distance': float,     # 距离(m)
    'density': float       # 边缘密度
}
```

#### 方法

**detect(frame)**
- 输入: OpenCV图像
- 输出: dict - 检测结果
- 描述: 检测前方障碍物

---

## 消息格式

### geometry_msgs/Point
```python
from geometry_msgs.msg import Point

msg = Point()
msg.x = 1.0
msg.y = 2.0
msg.z = 3.0
```

### geometry_msgs/Twist
```python
from geometry_msgs.msg import Twist

msg = Twist()
msg.linear.x = 1.0   # 前进速度
msg.linear.y = 0.0   # 左右速度
msg.linear.z = 0.5   # 上下速度
msg.angular.x = 0.0  # 滚转角速度
msg.angular.y = 0.0  # 俯仰角速度
msg.angular.z = 0.0  # 偏航角速度
```

### nav_msgs/Odometry
```python
from nav_msgs.msg import Odometry

# 包含位置、方向、速度等信息
odometry = Odometry()
odometry.pose.pose.position.x = 0.0
odometry.pose.pose.position.y = 0.0
odometry.pose.pose.position.z = 1.0
odometry.twist.twist.linear.x = 0.5
```

## 配置文件格式

### control_params.yaml
```yaml
follower:
  target_distance: 2.0
  target_height: 1.5
  max_velocity: 2.0
  pid:
    distance:
      kp: 1.2
      ki: 0.1
      kd: 0.5
```

### vision_params.yaml
```yaml
vision:
  camera:
    device_id: 0
    width: 640
    height: 480
    fps: 30
  target_color:
    lower_hsv: [0, 50, 50]
    upper_hsv: [10, 255, 255]
  detection:
    min_area: 500
    max_area: 50000
```

## 返回值和错误处理

### 常见错误

```python
# ROS2连接错误
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    node.destroy_node()
    rclpy.shutdown()

# 话题订阅超时
from rclpy.executors import SingleThreadedExecutor
executor = SingleThreadedExecutor()
```

## 下一步

- 📖 查看[使用教程](USAGE.md)
- 🐛 参考[调试指南](DEBUG.md)
