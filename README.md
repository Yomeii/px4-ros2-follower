# 🚁 PX4+ROS2+Gazebo 自主跟随系统

一个完整的基于PX4、ROS2和Gazebo的四旋翼无人机自主跟随车辆系统。支持视觉识别、实时控制、避障和高度自动调整。

## 📋 系统特性

- ✅ **视觉跟随** - 使用OpenCV进行目标车辆识别和追踪
- ✅ **实时控制** - PID控制器维持固定距离和高度
- ✅ **避障功能** - 基于摄像头的前向避障系统
- ✅ **高度自动调整** - 根据任务自动调整飞行高度
- ✅ **SITL仿真** - 完整的Gazebo仿真环境
- ✅ **室内环境** - 优化的室内飞行算法
- ✅ **ROS2集成** - 完全基于ROS2框架

## 🛠️ 技术栈

- **飞控** - PX4自动驾驶仪
- **中间件** - micro-ROS（XRCE-DDS）
- **机器人框架** - ROS2 Humble
- **仿真** - Gazebo Classic / Gazebo
- **视觉处理** - OpenCV
- **编程语言** - Python / C++

## 📁 项目结构

```
px4-ros2-follower/
├── src/
│   ├── follower_vision/           # 视觉识别和目标跟踪
│   ├── follower_control/          # 跟随控制算法
│   ├── follower_obstacle/         # 避障模块
│   └── follower_simulator/        # Gazebo仿真
├── launch/                        # ROS2启动文件
├── config/                        # 配置文件
├── scripts/                       # 辅助脚本
└── README.md                      # 本文档
```

## 🚀 快速开始

### 系统要求

- Ubuntu 22.04 LTS
- ROS2 Humble
- PX4 v1.14+
- Gazebo 11+

### 安装与启动

```bash
# 克隆仓库
git clone https://github.com/Yomeii/px4-ros2-follower.git
cd px4-ros2-follower

# 安装依赖
chmod +x scripts/install_dependencies.sh
sudo ./scripts/install_dependencies.sh

# 编译
colcon build --symlink-install
source install/setup.bash

# 启动完整系统
ros2 launch follower_simulator gazebo.launch.py
```

## 📝 配置参数

编辑 `config/control_params.yaml`：

```yaml
follower:
  target_distance: 2.0           # 目标跟随距离 (m)
  target_height: 1.5             # 目标飞行高度 (m)
  pid:
    distance:
      kp: 1.2
      ki: 0.1
      kd: 0.5
```

## 📚 详细文档

- [安装指南](docs/INSTALLATION.md)
- [使用教程](docs/USAGE.md)
- [API文档](docs/API.md)
- [调试指南](docs/DEBUG.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
