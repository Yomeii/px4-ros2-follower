#!/bin/bash

echo "========================================"
echo "Installing PX4+ROS2+Gazebo Dependencies"
echo "========================================"

# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装基础工具
sudo apt install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3-dev \
    python3-pip

# 安装ROS2相关
sudo apt install -y \
    ros-humble-ros-core \
    ros-humble-ament-cmake \
    ros-humble-ament-cmake-python \
    ros-humble-rclpy \
    ros-humble-rclcpp \
    ros-humble-std-msgs \
    ros-humble-geometry-msgs \
    ros-humble-sensor-msgs \
    ros-humble-nav-msgs \
    ros-humble-tf2 \
    ros-humble-tf2-ros

# 安装Gazebo
sudo apt install -y \
    gazebo \
    ros-humble-gazebo-ros \
    ros-humble-gazebo-plugins

# 安装可视化工具
sudo apt install -y \
    ros-humble-rviz2 \
    ros-humble-rqt

# 安装OpenCV
sudo apt install -y \
    libopencv-dev \
    python3-opencv

# 安装cv_bridge
sudo apt install -y \
    ros-humble-cv-bridge \
    ros-humble-image-transport

# 安装PX4
echo "Cloning PX4 Autopilot..."
cd ~
if [ ! -d "PX4-Autopilot" ]; then
    git clone https://github.com/PX4/PX4-Autopilot.git
fi
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh

# 安装micro-ROS
echo "Setting up micro-ROS..."
sudo apt install -y \
    ros-humble-micro-ros-setup

echo "========================================"
echo "Installation completed!"
echo "========================================"
echo ""
echo "Please run: source /opt/ros/humble/setup.bash"
echo ""
