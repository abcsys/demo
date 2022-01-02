from typing import Optional, Iterable

import os
import time
import gym
from gym import spaces
import yaml
import numpy as np

import digi.util as util

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


class Env(gym.Env):
    def __init__(self,
                 max_episode_steps=48, *,
                 use_dspace=False,
                 home_duri=home_duri,
                 human_duri=alice_duri,
                 ):
        self.state = None
        self.last_state = None
        self.cur_time = 0
        self.rooms = list(room_duris.keys())
        self.num_room = len(self.rooms)
        self.max_episode_steps = max_episode_steps

        # TBD should be adapted to number of rooms, time, and activity;
        # read these configurations from external yamls
        self.encode_room_index = {
            "bedroom": 0,
            "kitchen": 1,
            "livingroom": 2,
        }
        self.decode_room_index = {v: k for k, v in self.encode_room_index.items()}

        self.encode_brightness_level = {
            np.round(v, 1): i for i, v in enumerate(np.arange(0.0, 1.1, 0.1))
        }
        self.decode_brightness_level = {v: k for k, v in self.encode_brightness_level.items()}

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

        self.num_phase = len(self.encode_phase)
        self.num_brightness_level = len(self.encode_brightness_level)
        self.num_activity = len(self.encode_activity)

        # self.action_space = spaces.MultiDiscrete([self.num_brightness_level for _ in range(self.num_room)])
        self.observation_space = spaces.MultiDiscrete(
            [self.num_phase] +
            [self.num_brightness_level for _ in range(self.num_room)] +
            [self.num_activity for _ in range(self.num_room)]
        )

        n_action = tuple([self.num_brightness_level for _ in range(self.num_room)])
        self.action_space = spaces.Discrete(np.prod(n_action))
        self.action_mapping = tuple(np.ndindex(n_action))
        # n_observation = tuple([self.num_phase] + \
        #                       [self.num_brightness_level for _ in range(self.num_room)] + \
        #                       [self.num_activity for _ in range(self.num_room)])
        # self.observation_space = spaces.Discrete(np.prod(n_observation))
        # self.observation_mapping = tuple(np.ndindex(n_observation))

        print(self.action_space.n)
        print(self.observation_space.sample())
        # print(self.observation_space.n)
        print(self.observation_space.shape)
        # exit()
        self.behavior_model = behavior_model

        """dSpace setup"""
        if use_dspace:
            self.dspace = use_dspace
            self.home_duri = home_duri
            self.human_duri = human_duri

            self.cur_gen = self._fetch_human_gen()
            self.cur_time = 0
            self.last_state = dict()
            self.min_interval = 2

    def reset(self, seed: Optional[int] = None):
        # XXX 3 rooms
        self.state = np.array([0, 0, 0, 0, 1, 0, 0])
        self.last_state = None
        self.cur_time = 0
        self.total_effort = 0
        self.actions = list()
        return self.state

    def load_model(self):
        pass

    def step(self, action):
        if action is not None:
            action = self.action_mapping[action]
            # print("ACTION:", action)

            # apply brightness
            for i, a in enumerate(action):
                self.state[i + 1] = a

        phase = self.decode_phase[self.state[0]]
        brightness_state = self.state[1:self.num_room + 1]
        activity_state = self.state[self.num_room + 1:]
        # last_room =  if self.last_state is not None else None
        room = None
        for i, a in enumerate(activity_state):
            if a != 0:  # none
                room_index = i
                room = self.decode_room_index[room_index]

        # decide next room
        dests, probs = list(), list()
        for dest, config in self.behavior_model[room]["transition"][phase].items():
            dests.append(dest)
            probs.append(config["p"])
        next_room = np.random.choice(dests, 1, p=probs)[0]

        if next_room == "stay":
            next_room = room

        # next activity
        actvs, probs = list(), list()
        for name, config in self.behavior_model[room]["activity"].items():
            actvs.append(name)
            probs.append(config["p"])
        next_room_activity = np.random.choice(actvs, 1, p=probs)[0]
        next_room_brightness = self.behavior_model[room]["activity"][next_room_activity]["brightness"]
        _min, _max = next_room_brightness["min"], next_room_brightness["max"]

        next_room_index = self.encode_room_index[next_room]

        # set the state vector
        self.cur_time += 1
        next_phase = self.encode_phase[self.phase_of_day(self.cur_time)]

        self.last_state = self.state

        last_brightness_state = self.last_state[1:self.num_room + 1]
        next_brightness_state = [0 for _ in range(self.num_room)]
        # last room, if different from the current room,
        # remains unchanged to give a chance for the agent
        next_brightness_state[room_index] = last_brightness_state[room_index]
        if not (_min <= self.decode_brightness_level[last_brightness_state[next_room_index]] <= _max):
            next_brightness_state[next_room_index] = self.encode_brightness_level[np.round((_min + _max) / 2, 1)]

        next_activity_state = [0 for _ in range(self.num_room)]
        next_activity_state[next_room_index] = self.encode_activity[next_room_activity]

        self.state = np.array([next_phase] + next_brightness_state + next_activity_state)

        # print(action, self.last_state, self.state)

        # calculate reward
        cost = sum(1 if i != j else 0 for i, j in zip(next_brightness_state, last_brightness_state))

        self.total_effort += -cost
        self.actions.append((self.cur_time, self.total_effort, action, self.last_state, self.state))
        # if self.cur_time > 47 and self.total_effort > -40:
        #     print(self.actions)
        print(last_brightness_state, next_brightness_state, cost)
        return np.array(self.state), -cost, self.cur_time == self.max_episode_steps, None

    def close(self):
        pass

    def render(self, mode="human"):
        pass

    def phase_of_day(self, cur_time):
        ratio = cur_time / self.max_episode_steps
        if ratio < 0.25:  # 6 - 12
            return "morning"
        elif ratio < 0.5:  # 12 - 18
            return "afternoon"
        elif ratio < 0.625:  # 18 - 21
            return "evening"
        else:
            return "night"

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
    env = Env()
    ob = env.reset()
    rewards = list()
    # import torch
    # from home.driver.learn.policies import MLP_policy
    # model = MLP_policy()
    # checkpoint = torch.load("./trained.d99")
    # model.load_state_dict(checkpoint['model_state_dict'])
    # model.eval()

    for _ in range(env.max_episode_steps):
        # ob, rew, done, _ = env.step(np.product([0, 9, 9]))
        ob, rew, done, _ = env.step(None)
        rewards.append(rew)
    print("Total reward:", sum(rewards))


if __name__ == '__main__':
    main()
