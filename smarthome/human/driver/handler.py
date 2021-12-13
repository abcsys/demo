import json
import os

import digi
import digi.util as util

import numpy as np
import yaml

gvr_room = "smarthome.mock.digi.dev/v1/rooms"
_dir = os.path.dirname(os.path.abspath(__file__))
_behavior_config = os.path.join(_dir, "behavior.yaml")


# Human model
class Human:
    def __init__(self, name="misc", seed=42):
        with open(_behavior_config, "r") as f:
            self.behavior_config = yaml.load(f, Loader=yaml.FullLoader)
        self.name = name
        self.cur_time = 0
        self.cur_room = "bedroom"
        self.last_room = None
        self.cur_activity = "sleep"
        self.max_time = 48
        np.random.seed(seed)

    def __str__(self):
        return json.dumps({
            "name": self.name,
            "time": self.cur_time,
            "phase": self.phase_of_day(),
            "activity": self.cur_activity,
            "room": self.cur_room,
            "last_room": self.last_room,
        })

    def phase_of_day(self):
        ratio = self.cur_time / self.max_time
        if ratio < 0.25:  # 6 - 12
            return "morning"
        elif ratio < 0.5:  # 12 - 18
            return "afternoon"
        elif ratio < 0.625:  # 18 - 21
            return "evening"
        else:
            return "night"

    def _transition(self, src, phase):
        """Return the destination given source and phase of day."""
        dests, probs = list(), list()
        for dest, config in self.behavior_config[src] \
                ["transition"][phase].items():
            dests.append(dest)
            probs.append(config["p"])
        return np.random.choice(dests, 1, p=probs)[0]

    def _activity(self, src):
        """Return the activity."""
        actvs, probs = list(), list()
        for dest, config in self.behavior_config[src] \
                ["activity"].items():
            actvs.append(dest)
            probs.append(config["p"])
        return np.random.choice(actvs, 1, p=probs)[0]

    def step(self):
        phase = self.phase_of_day()
        next_room = self._transition(self.cur_room, phase)
        if next_room != "stay":
            self.last_room = self.cur_room
            self.cur_room = next_room

        self.cur_activity = self._activity(self.cur_room)
        self.cur_time = (self.cur_time + 1) % self.max_time

    def update_room(self, rooms):
        for room_name, model in rooms.items():
            room_name = util.simple_name(room_name)

            # update human presence
            util.update(model, "spec.obs.human_presence",
                        room_name == self.cur_room, create=True)

            # update room objects
            room_objects = util.get(model, "spec.obs.objects", [])
            new_room_objects = list()

            for o in room_objects:
                if o["class"] == "human" and o["name"] == self.name:
                    continue
                new_room_objects.append(o)

            if room_name == self.cur_room:
                new_room_objects.append({
                    "class": "human",
                    "name": self.name,
                    "activity": self.cur_activity
                })
            util.update(model,
                        "spec.obs.objects",
                        new_room_objects,
                        create=True)

            # update room brightness
            if room_name == self.cur_room:
                # let the api-server to decide the difference
                # alternatively, we can get the room's current
                # brightness and decide what to set
                brightness = util.get(self.behavior_config,
                                      f"{room_name}.activity."
                                      f"{self.cur_activity}.brightness")
                util.update(model,
                            "spec.control.brightness.intent",
                            brightness,
                            create=True)
            elif room_name != self.last_room:
                # close the lamp
                util.update(model,
                            "spec.control.brightness.intent",
                            0.0,
                            create=True)

human = Human(name=digi.name)


@digi.on.model
def do_step(pv):
    global human
    rooms = util.get(pv, f"mount.'{gvr_room}'", {})
    cur_time = util.get(pv, f"control.cur_time.intent", -1)

    if human.cur_time % human.max_time < cur_time:
        human.step()
    human.update_room(rooms)

    util.update(pv, f"control.cur_time.status", human.cur_time)

    digi.logger.info(f"DEBUG: {str(human)}")

if __name__ == '__main__':
    digi.run()
