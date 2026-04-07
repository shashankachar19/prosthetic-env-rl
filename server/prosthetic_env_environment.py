# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Prosthetic Env Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
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
    A simple echo environment that echoes back messages.

    This environment is designed for testing the HTTP server infrastructure.
    It maintains minimal state and simply echoes back whatever message it receives.

    Example:
        >>> env = ProstheticEnvironment()
        >>> obs = env.reset()
        >>> print(obs.echoed_message)  # "Prosthetic Env environment ready!"
        >>>
        >>> obs = env.step(ProstheticAction(message="Hello"))
        >>> print(obs.echoed_message)  # "Hello"
        >>> print(obs.message_length)  # 5
    """

    # Enable concurrent WebSocket sessions.
    # Set to True if your environment isolates state between instances.
    # When True, multiple WebSocket clients can connect simultaneously, each
    # getting their own environment instance (when using factory mode in app.py).
    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_grip = 0
        self.target_grip = 5
        self.steps = 0
        self.max_steps = 15

    def reset(self):
        import random
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_grip = 0
        self.target_grip = random.randint(2, 8) 
        self.steps = 0
        
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
        
        if self.current_grip == self.target_grip:
            reward = 10.0
            done = True
        else:
            reward = -1.0 
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
