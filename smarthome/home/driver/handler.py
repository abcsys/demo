import json

import digi
import digi.on as on

import digi.util as util

room_gvr = "smarthome.mock.digi.dev/v1/rooms"


class Home:
    def __init__(self):
        self.room_object = dict()

    def __str__(self):
        return json.dumps({
            "rooms": self.room_object
        })

    def train(self):
        pass


home = Home()


@on.mount
def do_home_status(parent, mounts):
    home_model = parent

    # handle rooms
    rooms = mounts.get(room_gvr, {})

    # update observations
    obs_rooms = dict()
    for n, r in rooms.items():
        objects = util.get(r, "spec.obs.objects", {})
        obs_rooms[util.simple_name(n)] = {
            "objects": [{"class": o.get("class", None),
                         "name": o.get("name", None),
                         "activity": o.get("activity", None)} for o in objects],
            "brightness": util.get(r, "spec.control.brightness.status"),
        }
    util.update(home_model, "obs.rooms", obs_rooms)
    home.room_object = obs_rooms

    digi.logger.info(f"Home: {home}")


if __name__ == '__main__':
    digi.run()
