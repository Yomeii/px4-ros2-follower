# 📖 使用教程

## 快速开始

### 启动完整系统（推荐）

最简单的方法是使用完整系统启动文件，一次启动所有组件：

```bash
# 激活工作空间
cd ~/px4_ros2_ws
source install/setup.bash

# 启动完整系统
ros2 launch follower_simulator gazebo.launch.py
```

这会同时启动：
- Gazebo仿真环境
- PX4 SITL
- RViz可视化
- 所有ROS2节点

## 分步启动（高级用户）

### 步骤1: 启动Gazebo仿真

**终端1**:
```bash
cd ~/px4_ros2_ws
source install/setup.bash
ros2 launch follower_simulator gazebo.launch.py
```

你应该看到：
- Gazebo客户端窗口打开
- 室内环境加载
- 无人机和目标车辆模型出现

### 步骤2: 启动视觉识别节点

**终端2**:
```bash
cd ~/px4_ros2_ws
source install/setup.bash
ros2 launch follower_vision vision.launch.py
```

输出示例：
```
[INFO] [vision_node]: Vision node initialized
[INFO] [vision_node]: Target detected at (320, 240)
```

### 步骤3: 启动控制节点

**终端3**:
```bash
cd ~/px4_ros2_ws
source install/setup.bash
ros2 launch follower_control control.launch.py
```

输出示例：
```
[INFO] [follower_node]: Follower node initialized
[INFO] [follower_node]: Position: [0. 0. 0.], Target: [1. 1. 0.], Distance: 1.41m
```

### 步骤4: 启动避障节点

**终端4**:
```bash
cd ~/px4_ros2_ws
source install/setup.bash
ros2 launch follower_obstacle obstacle.launch.py
```

输出示例：
```
[INFO] [obstacle_node]: Obstacle node initialized
```

## 系统工作流程

```
1. Gazebo提供虚拟环境
   ↓
2. 视觉节点处理摄像头图像
   ├─ 检测红色目标车辆
   ├─ 计算目标位置
   └─ 发布目标信息
   ↓
3. 控制节点计算控制指令
   ├─ 接收目标位置
   ├─ 运行PID控制器
   └─ 发送速度命令
   ↓
4. 避障节点检测障碍物
   ├─ 处理摄像头图像
   ├─ 检测前方障碍
   └─ 发送避障信号
   ↓
5. PX4 SITL执行指令
   ├─ 接收速度命令
   ├─ 计算电机输出
   └─ 更新无人机位置
```

## 常见操作

### 在Gazebo中移动目标车辆

**方法1: 使用Gazebo GUI**
1. 在Gazebo窗口中右键点击目标车辆
2. 选择 "Move"
3. 拖动模型移动

**方法2: 使用ROS2指令**
```bash
# 发布目标位置
ros2 topic pub /target/position geometry_msgs/Point \
  "{x: 3.0, y: 2.0, z: 0.0}"
```

### 改��无人机飞行高度

编辑 `config/control_params.yaml`：
```yaml
follower:
  target_height: 2.0  # 改为2米
```

重启控制节点：
```bash
ros2 launch follower_control control.launch.py
```

### 调整跟随距离

编辑 `config/control_params.yaml`：
```yaml
follower:
  target_distance: 3.0  # 改为3米
```

重启控制节点应用更改。

### 改变目标识别颜色

编辑 `config/vision_params.yaml`：
```yaml
vision:
  target_color:
    lower_hsv: [100, 50, 50]   # 改为蓝色
    upper_hsv: [130, 255, 255]
```

重启视觉节点。

## 监控和调试

### 查看ROS2话题

**列出所有话题**:
```bash
ros2 topic list
```

输出示例：
```
/camera/image_raw
/drone/state
/target/position
/target/velocity
/target/detected
/obstacle/detected
/obstacle/distance
/mavros/setpoint_velocity/cmd_vel
```

### 订阅特定话题

**查看目标位置**:
```bash
ros2 topic echo /target/position
```

**查看无人机状态**:
```bash
ros2 topic echo /drone/state
```

**查看障碍物检测**:
```bash
ros2 topic echo /obstacle/detected
```

### 使用RViz可视化

```bash
# 启动RViz
rviz2 -d config/visualization.rviz
```

在RViz中你可以看到：
- 无人机位置和方向
- 目标车辆位置
- 摄像头视角
- 障碍物检测结果

### 查看节点信息

```bash
# 列出所有运行的节点
ros2 node list

# 查看节点详细信息
ros2 node info /vision_node
```

### 记录与回放

**记录数据**:
```bash
# 记录所有话题
ros2 bag record -a

# 指定输出目录
ros2 bag record -a -o ~/bags/follow_session_1

# 只记录特定话题
ros2 bag record /target/position /drone/state /obstacle/detected
```

**回放数据**:
```bash
ros2 bag play ~/bags/follow_session_1
```

## 性能优化

### 调整处理频率

编辑 `config/control_params.yaml`：
```yaml
follower:
  control_frequency: 50  # 增加到50Hz获得更好的控制
```

### 调整PID参数

**如果无人机抖动**:
```yaml
pid:
  distance:
    kp: 0.8  # 降低Kp
    kd: 0.8  # 增加Kd
```

**如果无人机反应缓慢**:
```yaml
pid:
  distance:
    kp: 1.5  # 增加Kp
    ki: 0.15 # 增加Ki
```

### 图像处理优化

编辑 `config/vision_params.yaml`：
```yaml
vision:
  processing:
    blur_kernel: [3, 3]  # 减小内核加快处理
  processing_frequency: 15  # 降低处理频率以提高稳定性
```

## 故障排查

### 无人机不起飞

1. 检查PX4状态
2. ��保GPS已锁定
3. 检查电池电量
4. 查看PX4日志

### 目标无法检测

1. 检查目标颜色
2. 调整HSV范围
3. 改善光照条件
4. 检查摄像头工作

### 跟随不稳定

1. 微调PID参数
2. 增加摄像头处理频率
3. 检查消息延迟
4. 降低目标移动速度

## 下一步

- 📚 阅读[API文档](API.md)
- 🐛 参考[调试指南](DEBUG.md)
- ⚙️ 查看[安装指南](INSTALLATION.md)
