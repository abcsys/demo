import time

from digi.util import patch_spec, get_spec

alice_duri = ("smarthome.mock.digi.dev",
              "v1", "humans",
              "human-test", "default")
# alice

home_duri = ("smarthome.mock.digi.dev",
              "v1", "homes",
              "home", "default")

room_duris = {
    name: ("smarthome.mock.digi.dev",
           "v1", "rooms",
           name, "default")
    for name in ["livingroom", "bedroom", "bathroom"]
}

lamp_duris = {
    name: ("smarthome.mock.digi.dev",
           "v1", "lamps",
           name, "default")
    for name in ["l1", "l2", "l3"]
}


def setup():
    # ray.init()
    # construct digi graph
    pass


cur_time = 0


def step():
    global cur_time
    cur_time += 1
    patch_spec(*alice_duri,
               spec={
                   "control": {
                       "cur_time": {
                           "intent": cur_time
                       }
                   },
               })


def main():
    for _ in range(10):
        step()
        time.sleep(2)


if __name__ == '__main__':
    main()
