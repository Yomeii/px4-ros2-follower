#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    # 各个包的路径
    pkg_follower_simulator = FindPackageShare('follower_simulator')
    pkg_follower_vision = FindPackageShare('follower_vision')
    pkg_follower_control = FindPackageShare('follower_control')
    pkg_follower_obstacle = FindPackageShare('follower_obstacle')
    
    # 包含各个启动文件
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_follower_simulator, 'launch', 'gazebo.launch.py'])
        )
    )
    
    vision_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_follower_vision, 'launch', 'vision.launch.py'])
        )
    )
    
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_follower_control, 'launch', 'control.launch.py'])
        )
    )
    
    obstacle_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_follower_obstacle, 'launch', 'obstacle.launch.py'])
        )
    )
    
    return LaunchDescription([
        gazebo_launch,
        vision_launch,
        control_launch,
        obstacle_launch,
    ])
