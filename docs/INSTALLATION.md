# 📚 安装指南

## 系统要求

### 硬件要求
- **CPU**: Intel i5或更高 / AMD Ryzen 5或更高
- **内存**: 至少8GB RAM（推荐16GB）
- **存储**: 至少20GB可用空间
- **网络**: 稳定的互联网连接

### 操作系统
- **Ubuntu 22.04 LTS** (推荐)
- 其他Linux发行版可能需要调整
- 不支持Windows/Mac原生运行（可使用Docker）

## 软件依赖

### 系统级依赖
```bash
sudo apt update
sudo apt upgrade -y

# 基础工具
sudo apt install -y build-essential cmake git wget curl
sudo apt install -y python3-dev python3-pip
```

### ROS2安装

#### 1. 添加ROS2仓库
```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

#### 2. 安装ROS2 Humble
```bash
sudo apt update
sudo apt install -y ros-humble-desktop
```

#### 3. 激活ROS2
```bash
source /opt/ros/humble/setup.bash

# 为了每次打开终端都自动激活，��加到 ~/.bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Gazebo安装
```bash
sudo apt install -y gazebo ros-humble-gazebo-ros ros-humble-gazebo-plugins
```

### 必要的ROS2包
```bash
sudo apt install -y \
  ros-humble-ament-cmake \
  ros-humble-ament-cmake-python \
  ros-humble-rclpy \
  ros-humble-rclcpp \
  ros-humble-std-msgs \
  ros-humble-geometry-msgs \
  ros-humble-sensor-msgs \
  ros-humble-nav-msgs \
  ros-humble-tf2 \
  ros-humble-tf2-ros \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-rviz2 \
  ros-humble-rqt
```

### OpenCV安装
```bash
sudo apt install -y libopencv-dev python3-opencv

# 验证安装
python3 -c "import cv2; print(cv2.__version__)"
```

### PX4安装
```bash
# 创建目录
mkdir -p ~/src
cd ~/src

# 克隆PX4
git clone https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot

# 运行安装脚本
bash ./Tools/setup/ubuntu.sh

# 编译SITL版本
make px4_sitl_default gazebo
```

### micro-ROS安装
```bash
sudo apt install -y ros-humble-micro-ros-setup

# 创建micro-ROS工作空间
mkdir -p ~/microros_ws/src
cd ~/microros_ws

# 拉取micro-ROS
micro_ros_setup.sh docker create
```

## 项目安装

### 1. 克隆项目
```bash
# 创建工作空间
mkdir -p ~/px4_ros2_ws/src
cd ~/px4_ros2_ws/src

# 克隆项目
git clone https://github.com/Yomeii/px4-ros2-follower.git
cd ..
```

### 2. 安装项目依赖
```bash
# 使用提供的脚本
chmod +x src/px4-ros2-follower/scripts/install_dependencies.sh
cd src/px4-ros2-follower
./scripts/install_dependencies.sh
cd ~/px4_ros2_ws
```

### 3. 编译项目
```bash
# 编译所有包
colcon build --symlink-install

# 如果出错，尝试逐个编译
colcon build --packages-select follower_vision --symlink-install
colcon build --packages-select follower_control --symlink-install
colcon build --packages-select follower_obstacle --symlink-install
colcon build --packages-select follower_simulator --symlink-install
```

### 4. 激活工作空间
```bash
source ~/px4_ros2_ws/install/setup.bash

# 添加到bashrc自动激活
echo "source ~/px4_ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## 环境配置

### 设置Gazebo环境变量
```bash
# 临时设置
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/px4_ros2_ws/src/px4-ros2-follower/src/follower_simulator/models
export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:~/px4_ros2_ws/src/px4-ros2-follower/src/follower_simulator/worlds

# 永久设置，添加到 ~/.bashrc
echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/px4_ros2_ws/src/px4-ros2-follower/src/follower_simulator/models' >> ~/.bashrc
echo 'export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:~/px4_ros2_ws/src/px4-ros2-follower/src/follower_simulator/worlds' >> ~/.bashrc
source ~/.bashrc
```

### 设置PX4环境变量
```bash
# 添加到 ~/.bashrc
echo 'export PX4_HOME_LAT=47.397742' >> ~/.bashrc
echo 'export PX4_HOME_LON=8.545594' >> ~/.bashrc
echo 'export PX4_HOME_ALT=1338' >> ~/.bashrc
source ~/.bashrc
```

## 验证安装

### 检查ROS2
```bash
ros2 --version
# 应输出: ROS 2: humble release
```

### 检查Python包
```bash
python3 -c "import rclpy; print('rclpy OK')"
python3 -c "import cv2; print('OpenCV OK')"
python3 -c "import numpy; print('NumPy OK')"
```

### 列出可用包
```bash
colcon list
```

### 测试启动文件
```bash
ros2 launch follower_simulator gazebo.launch.py --show-args
```

## 常见问题解决

### 问题1: colcon command not found
**解决方案**:
```bash
pip3 install colcon-common-extensions
```

### 问题2: gazebo command not found
**解决方案**:
```bash
sudo apt install -y gazebo
# 验证
gazebo --version
```

### 问题3: 编译失败 - missing dependencies
**解决方案**:
```bash
# 使用rosdep解决依赖
rosdep install --from-paths ~/px4_ros2_ws/src -i -y --rosdistro humble
```

### 问题4: Python import errors
**解决方案**:
```bash
# 重新激活工作空间
cd ~/px4_ros2_ws
source install/setup.bash

# 验证Python路径
python3 -c "import sys; print(sys.path)"
```

### 问题5: 权限错误
**解决方案**:
```bash
# 添加用户到必要的组
sudo usermod -a -G dialout $USER
sudo usermod -a -G video $USER

# 重新登录或运行
newgrp dialout
```

## Docker安装（可选）

如果不想在本地安装所有依赖，可以使用Docker：

```bash
# 构建Docker镜像
cd ~/px4_ros2_ws/src/px4-ros2-follower
docker build -t px4-ros2-follower:latest docker/

# 运行容器
docker run -it --rm --name px4-follower \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/px4_ros2_ws:/home/ros/px4_ros2_ws \
  px4-ros2-follower:latest bash

# 在容器内
cd /home/ros/px4_ros2_ws
source install/setup.bash
ros2 launch follower_simulator gazebo.launch.py
```

## 下一步

- 📖 阅读[使用教程](USAGE.md)
- 🔧 参考[API文档](API.md)
- 🐛 查看[调试指南](DEBUG.md)
