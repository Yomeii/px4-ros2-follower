#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 包路径
    pkg_follower_simulator = FindPackageShare('follower_simulator')
    gazebo_models_path = PathJoinSubstitution([pkg_follower_simulator, 'models'])
    gazebo_worlds_path = PathJoinSubstitution([pkg_follower_simulator, 'worlds'])
    
    # Launch参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='indoor_environment.world')
    
    # 设置Gazebo环境变量
    gazebo_env = {
        'GAZEBO_MODEL_PATH': str(gazebo_models_path),
        'GAZEBO_RESOURCE_PATH': str(gazebo_worlds_path),
        'GAZEBO_PLUGIN_PATH': '/opt/ros/humble/lib',
    }
    
    # PX4 SITL
    px4_sitl = Node(
        package='follower_simulator',
        executable='px4_sitl_node',
        name='px4_sitl',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
        ],
    )
    
    # Gazebo服务器
    gzserver = Node(
        package='gazebo_ros',
        executable='gzserver',
        arguments=['-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so',
                   PathJoinSubstitution([gazebo_worlds_path, world])],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        env=gazebo_env,
    )
    
    # Gazebo客户端
    gzclient = Node(
        package='gazebo_ros',
        executable='gzclient',
        output='screen',
    )
    
    # RViz
    rviz_config_path = PathJoinSubstitution([pkg_follower_simulator, 'config', 'gazebo.rviz'])
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value='indoor_environment.world'),
        
        gzserver,
        gzclient,
        px4_sitl,
        rviz,
    ])
