#!/bin/bash

echo "Setting up PX4+ROS2+Gazebo environment..."

# 源码激活ROS2
source /opt/ros/humble/setup.bash

# 创建工作空间
WORKSPACE="${HOME}/px4_ros2_ws"
if [ ! -d "$WORKSPACE" ]; then
    mkdir -p $WORKSPACE/src
    cd $WORKSPACE/src
    
    # 复制当前包到工作空间
    if [ -d "../../../px4-ros2-follower" ]; then
        cp -r ../../../px4-ros2-follower . 2>/dev/null
    fi
    
    cd ..
    colcon build --symlink-install
    source install/setup.bash
    echo "Workspace created at: $WORKSPACE"
fi

# 设置Gazebo环境变量
export GAZEBO_MODEL_PATH="$GAZEBO_MODEL_PATH:$WORKSPACE/src/px4-ros2-follower/src/follower_simulator/models"
export GAZEBO_RESOURCE_PATH="$GAZEBO_RESOURCE_PATH:$WORKSPACE/src/px4-ros2-follower/src/follower_simulator/worlds"

echo "Environment setup completed!"
echo "Workspace: $WORKSPACE"
echo ""
echo "To build the project:"
echo "  cd $WORKSPACE"
echo "  colcon build"
echo ""
echo "To run the system:"
echo "  source install/setup.bash"
echo "  ros2 launch follower_simulator gazebo.launch.py"
echo ""
