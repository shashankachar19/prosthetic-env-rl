# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Prosthetic Env Environment Implementation.

A custom Reinforcement Learning environment for the AI-Powered 
Prosthetic Management System (APMS). Trains an agent across 
5 distinct grip calibration tasks.
"""

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import ProstheticAction, ProstheticObservation
except ImportError:
    from models import ProstheticAction, ProstheticObservation


class ProstheticEnvironment(Environment):
    """
    Prosthetic Grip Calibration Environment.
    
    Tasks:
    1. Precision Grip: Match a specific mid-level force (3-7).
    2. Power Grip: Apply maximum force (>= 9).
    3. Relaxation: Release all force (<= 1).
    4. Delicate Pinch: Match light force exactly (2).
    5. Firm Handshake: Match strong, non-max force exactly (8).
    """

    # Enable concurrent WebSocket sessions.
    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    
    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_grip = 0
        self.target_grip = 5
        self.steps = 0
        self.max_steps = 15
        self.task_type = 1

    def reset(self):
        import random
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.steps = 0
        
        # Randomly assign one of the 5 distinct tasks
        self.task_type = random.choice([1, 2, 3, 4, 5])
        
        if self.task_type == 1:
            self.current_grip = 0
            self.target_grip = random.randint(3, 7)
        elif self.task_type == 2:
            self.current_grip = 0
            self.target_grip = 10
        elif self.task_type == 3:
            self.current_grip = 10
            self.target_grip = 0
        elif self.task_type == 4:
            self.current_grip = 0
            self.target_grip = 2
        else:
            self.current_grip = 0
            self.target_grip = 8
        
        return ProstheticObservation(
            current_grip=self.current_grip,
            target_grip=self.target_grip,
            done=False,
            reward=0.1  # Strictly > 0
        )

    def step(self, action: ProstheticAction):
        self.steps += 1
        self._state.step_count += 1
        
        self.current_grip += action.force_change
        self.current_grip = max(0, min(10, self.current_grip))
        
        done = False
        reward = 0.1  # Normalized to strictly > 0.0
        
        # Grading logic based on the 5 tasks
        if self.task_type == 1:
            if self.current_grip == self.target_grip:
                reward = 0.99  # Maximum reward strictly < 1.0
                done = True
        elif self.task_type == 2:
            if self.current_grip >= 9: 
                reward = 0.99
                done = True
        elif self.task_type == 3:
            if self.current_grip <= 1: 
                reward = 0.99
                done = True
        elif self.task_type == 4:
            if self.current_grip == self.target_grip:
                reward = 0.99
                done = True
        elif self.task_type == 5:
            if self.current_grip == self.target_grip:
                reward = 0.99
                done = True
                
        # Stop if we hit the step limit
        if self.steps >= self.max_steps:
            done = True

        return ProstheticObservation(
            current_grip=self.current_grip,
            target_grip=self.target_grip,
            done=done,
            reward=reward
        )
        
    @property
    def state(self) -> State:
        """
        Get the current environment state.
        """
        return self._state