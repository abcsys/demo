import digi
import digi.on as on

import digi.util as util
from digi.util import deep_get, deep_set, deep_set_all


room_gvr = "smarthome.mock.digi.dev/v1/rooms"


@on.mount
def do_home_status(parent, mounts):
    home = parent

    # handle rooms
    rooms = mounts.get(room_gvr, {})

    # update observations
    obs_rooms = dict()
    for n, r in rooms.items():
        objects = deep_get(r, "spec.obs.objects", {})
        obs_rooms[util.simple_name(n)] = {
            "objects": [{"class": o.get("class", None),
                         "name": o.get("name", None),
                         "activity": o.get("activity", None)} for o in objects],
            "brightness": deep_get(r, "spec.control.brightness.status"),
        }
    deep_set(home, "obs.rooms", obs_rooms)


if __name__ == '__main__':
    digi.run()
