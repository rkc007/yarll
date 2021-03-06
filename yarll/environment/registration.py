# -*- coding: utf8 -*-

# Inspired by https://github.com/openai/gym/blob/master/gym/envs/registration.py
# When making an environment, we first look if we registered a version of it ourselves.
# Else, we make just make one using the Environment class.
from typing import Sequence
import numpy as np

import gym
from yarll.misc.utils import AtariRescale42x42
from yarll.environment.environment import Environment

gym.logger.set_level(gym.logger.ERROR)

def make(env_id: str, **kwargs):
    spec = gym.envs.registry.spec(env_id)
    env = spec.make(**kwargs)

    if not isinstance(env, Environment):
        if (env.spec.max_episode_steps is not None) and not spec.tags.get('vnc'):
            from gym.wrappers.time_limit import TimeLimit
            env = TimeLimit(env,
                            max_episode_steps=env.spec.max_episode_steps)
        env = Environment(env)
    if "atari.atari_env" in env.unwrapped.__module__:
        env = AtariRescale42x42(env)
    if "wrapper_entry_points" in spec.tags:
        for wrapper_info in spec.tags["wrapper_entry_points"]:
            kwargs = {}
            if isinstance(wrapper_info, str):
                cls = gym.envs.registration.load(wrapper_info)
            else:
                cls = gym.envs.registration.load(wrapper_info["entry_point"])
                kwargs = wrapper_info["kwargs"]
            env = cls(env, **kwargs)
    return env

def make_environments(descriptions: Sequence[dict]) -> list:
    """Make environments using a list of descriptions."""
    return [make(**d) for d in descriptions]

def make_random_environments(env_id: str, n_envs: int) -> list:
    """Make n_envs random environments of the env_name class."""
    spec = gym.envs.registry.spec(env_id)
    cls = gym.envs.registration.load(spec.entry_point)
    envs = []
    for _ in range(n_envs):
        args = {"id": env_id}
        for p in cls.changeable_parameters:
            if p["type"] == "range":  # Assume for now only range parameters are used
                args[p["name"]] = np.random.uniform(p["low"], p["high"])
            else:
                raise NotImplementedError("Only able to make environments with range parameters.")
        envs.append(make(**args))
    for env in envs:
        print(id(env.metadata))
    return envs
