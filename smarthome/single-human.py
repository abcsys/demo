from typing import Optional

import os
import time
import gym
from gym import spaces
import yaml
import numpy as np

import digi.util as util

from home.driver.learn import PG_Trainer

_dir = os.path.dirname(os.path.abspath(__file__))
_behavior_config = os.path.join(_dir, "human", "driver", "behavior.yaml")

alice_duri = ("smarthome.mock.digi.dev",
              "v1", "humans",
              "alice", "default")

with open(_behavior_config, "r") as f:
    behavior_model = yaml.load(f, Loader=yaml.FullLoader)

home_duri = ("smarthome.mock.digi.dev",
             "v1", "homes",
             "home", "default")

room_duris = {
    name: ("smarthome.mock.digi.dev",
           "v1", "rooms",
           name, "default")
    for name in ["livingroom", "bedroom", "kitchen"]
}

lamp_duris = {
    name: ("smarthome.mock.digi.dev",
           "v1", "lamps",
           name, "default")
    for name in ["l1", "l2", "l3"]
}


class HomeBrightnessEnv(gym.Env):
    def __init__(self,
                 home_duri=home_duri,
                 human_duri=alice_duri,
                 use_dspace=False,
                 ):

        self.rooms = list(room_duris.keys())
        # TBD should be adapted to number of rooms, time, and activity;
        # read these configurations from external yamls
        self.encode_room_index = {
            "bedroom": 0,
            "kitchen": 1,
            "livingroom": 2,
        }
        self.decode_room_index = {v: k for k, v in self.encode_room_index.items()}
        self.encode_brightness_level= {
            i: np.round(v, 1) for i, v in enumerate(np.arange(0.0, 1.1, 0.1))
        }
        self.decode_brightness_level = {v: k for k, v in self.encode_room_index.items()}
        self.encode_phase = {
            "morning": 0,
            "afternoon": 1,
            "evening": 2,
            "night": 3,
        }
        self.decode_phase = {v: k for k, v in self.encode_phase.items()}
        self.encode_activity = {
            "none": 0,
            "sleep": 1,
            "work": 2,
            "read": 3,
            "cook": 4,
            "wash": 5,
            "watch-tv": 6,
        }
        self.decode_activity = {v: k for k, v in self.encode_activity.items()}
        # XXX assuming 3 rooms; should be adapt to number of rooms
        self.action_space = spaces.MultiDiscrete([11, 11, 11])
        self.observation_space = spaces.MultiDiscrete(
            [4, 11, 11, 11, 7, 7, 7]
        )   # phase of day, room_1_bright, ... room_3_bright,
            # room_1_act ... room_3_act
        print(self.action_space.shape)
        print(self.observation_space.sample())
        print(self.observation_space.shape)
        self.behavior_model = behavior_model

        """dSpace setup"""
        if use_dspace:
            self.dspace = use_dspace
            self.home_duri = home_duri
            self.human_duri = human_duri

            self.cur_gen = self._fetch_human_gen()
            self.cur_time = 0
            self.last_state = dict()
            self.max_episode_steps = 48
            self.min_interval = 2

    def reset(self, seed: Optional[int] = None):
        # XXX 3 rooms
        self.state = np.array([0, 0, 0, 0, 1, 0, 0])
        return self.state

    def _get_reward(self, action):
        pass

    def step(self, action):
        pass

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def render(self, mode="human"):
        pass

    """Run in dSpace"""

    def step_remote(self):
        self.cur_time += 1
        self._update_human_time()

        time.sleep(self.min_interval)

        state = self._parse_state(self._fetch_home_state())
        reward = self._calculate_reward(state)
        done = self.cur_time == (self.max_episode_steps - 1)

        self.last_state = state

        return state, reward, done, False

    def _parse_state(self, raw):
        obs = dict()
        for name, obs in raw.items():
            brightness = obs["brightness"]
            if len(obs["objects"]) > 0:
                human = obs["objects"][0]
                activity = self.encode_activity.get(human["activity"], 0)
            else:
                activity = 0  # none
            obs[name] = [brightness, activity]
        print(self.cur_time, raw["bedroom"]["brightness"], )

    def _calculate_reward(self, state):
        # return ob, rew, done, _ = env.step(ac)
        # TBD parse home states
        pass

    def _fetch_home_state(self):
        spec, _, _ = util.get_spec(*self.home_duri)
        return util.get(spec, "obs.rooms", self.last_state)

    def _fetch_human_gen(self):
        spec, _, _ = util.get_spec(*self.human_duri)
        return util.get(spec, "control.cur_gen.status", 0)

    def reset_remote(self):
        self.cur_gen += 1
        self._update_human_gen()
        self.cur_time = 0
        self._update_human_time()

    def _update_human_time(self):
        util.patch_spec(*self.human_duri,
                        spec={"control":
                                  {"cur_time": {"intent": self.cur_time}},
                              })

    def _update_human_gen(self):
        util.patch_spec(*self.human_duri,
                        spec={"control":
                                  {"cur_gen": {"intent": self.cur_gen}},
                              })


def setup():
    # ray.init()
    # construct digi graph
    ...


def main():
    env = HomeBrightnessEnv()
    ob = env.reset()
    print(ob)
    # for _ in range(env.max_episode_steps):
    #     ob, rew, done, _ = env.step()


if __name__ == '__main__':
    main()
