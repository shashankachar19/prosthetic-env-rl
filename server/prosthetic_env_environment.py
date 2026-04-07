# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Prosthetic Env Environment Implementation.

A custom Reinforcement Learning environment for the AI-Powered 
Prosthetic Management System (APMS). Trains an agent across 
3 distinct grip calibration tasks.
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
    1. Precision Grip: Match a specific mid-level force.
    2. Power Grip: Apply maximum force (>= 9).
    3. Relaxation: Release all force (<= 1).
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
        
        # Randomly assign one of the 3 distinct tasks
        self.task_type = random.choice([1, 2, 3])
        
        if self.task_type == 1:
            # Task 1: Precision Grip (match a specific mid-level force)
            self.current_grip = 0
            self.target_grip = random.randint(3, 7)
        elif self.task_type == 2:
            # Task 2: Maximum Power Grip
            self.current_grip = 0
            self.target_grip = 10
        else:
            # Task 3: Relaxation (Start tense, release to 0)
            self.current_grip = 10
            self.target_grip = 0
        
        return ProstheticObservation(
            current_grip=self.current_grip,
            target_grip=self.target_grip,
            done=False,
            reward=0.0
        )

    def step(self, action: ProstheticAction):
        self.steps += 1
        self._state.step_count += 1
        
        self.current_grip += action.force_change
        self.current_grip = max(0, min(10, self.current_grip))
        
        done = False
        reward = -1.0  # Battery/time penalty for taking a step
        
        # Grading logic based on the 3 tasks
        if self.task_type == 1:
            if self.current_grip == self.target_grip:
                reward = 10.0
                done = True
        elif self.task_type == 2:
            if self.current_grip >= 9: # Close enough to max power
                reward = 10.0
                done = True
        elif self.task_type == 3:
            if self.current_grip <= 1: # Successfully relaxed
                reward = 10.0
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

        Returns:
            Current State with episode_id and step_count
        """
        return self._state