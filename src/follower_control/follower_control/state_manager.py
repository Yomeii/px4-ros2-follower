#!/usr/bin/env python3
"""
状态管理器
"""

from enum import Enum


class DroneState(Enum):
    """无人机状态"""
    IDLE = 'idle'           # 空闲
    ARMED = 'armed'         # 解锁
    TAKEOFF = 'takeoff'     # 起飞
    FOLLOWING = 'following' # 跟随
    HOVER = 'hover'         # 悬停
    LANDING = 'landing'     # 着陆
    ERROR = 'error'         # 错误


class StateManager:
    """状态管理器"""

    def __init__(self):
        """初始化状态管理器"""
        self.current_state = DroneState.IDLE
        self.state_callbacks = {}

    def set_state(self, state):
        """
        设置状态
        
        Args:
            state: 新状态
        """
        if isinstance(state, str):
            try:
                new_state = DroneState(state)
            except ValueError:
                print(f'Invalid state: {state}')
                return
        else:
            new_state = state
        
        if new_state != self.current_state:
            print(f'State transition: {self.current_state.value} -> {new_state.value}')
            self.current_state = new_state
            
            # 执行回调
            if new_state in self.state_callbacks:
                self.state_callbacks[new_state]()

    def get_state(self):
        """
        获取当前状态
        
        Returns:
            DroneState: 当前状态
        """
        return self.current_state

    def register_callback(self, state, callback):
        """
        注册状态回调
        
        Args:
            state: 状态
            callback: 回调函数
        """
        self.state_callbacks[state] = callback
