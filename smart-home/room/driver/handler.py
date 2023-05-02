import digi
import digi.on as on

import digi.util as util
from digi.util import deep_get, deep_set, mount_size

gvr_lamp = "smarthome.mock.digi.dev/v1/lamps"

lamp_converters = {
    gvr_lamp: {
        "brightness": {
            "from": lambda x: x,
            "to": lambda x: x,
        }
    },
}


@on.control
@on.mount
def do_room_status(parent, mounts):
    room, devices = parent, mounts
    deep_set(room, f"control.brightness.status",
             deep_get(room, "control.brightness.intent"))

    # def set_room_mode_brightness():
    #     room_brightness, matched = 0, True
    #
    #     mode = deep_get(room, "control.mode.intent")
    #
    #     brightness_convert = lamp_converters[gvr_lamp]["brightness"]["from"]
    #
    #     # iterate over individual lamp
    #     for n, lamp in devices.get(gvr_lamp, {}).items():
    #         if "spec" not in lamp:
    #             continue
    #
    #         lamp_spec = lamp["spec"]
    #         lamp_brightness = deep_get(lamp_spec, "control.brightness.status", 0)
    #
    #         room_brightness += brightness_convert(lamp_brightness)
    #
    #     room_brightness = min(room_brightness, 1)
    #     deep_set(room, f"control.brightness.status", room_brightness)
    #
    #     deep_set(room, f"control.mode.status", mode if matched else "undef")
    #
    # # other devices
    # # ...
    #
    # # TBD use class for room
    # set_room_mode_brightness()


@on.mount
@on.control("brightness")
def do_brightness(parent, mounts):
    room, devices = parent, mounts

    brightness = deep_get(room, "control.brightness.intent")
    if brightness is None:
        return

    num_active_lamp = \
        mount_size(mounts, {gvr_lamp}, has_spec=True)

    if num_active_lamp < 1:
        return

    brightness_div = brightness / num_active_lamp
    _set_bright(devices, brightness_div)


def _set_bright(ds, b):
    _lc = lamp_converters[gvr_lamp]["brightness"]["to"]

    for _, _l in ds.get(gvr_lamp, {}).items():
        deep_set(_l, "spec.control.brightness.intent",
                 _lc(b))


def load():
    model = digi.rc.view()

    record = {
        "brightness": util.deep_get(model, "control.brightness.status"),
    }

    mounts = model.get("mount", {})
    lamps = mounts.get(gvr_lamp, None)
    if lamps is not None:
        record.update({"num_lamp": len(lamps)})

    objects = util.deep_get(model, f"obs.objects", None)
    if objects is not None:
        num_human, humans = 0, list()
        for o in objects:
            if "human" in o:
                num_human += 1
                humans.append(o["human"].get("name", None))
        record.update({"num_human": num_human, "human": humans})

    digi.pool.load([record])


loader = util.Loader(load_fn=load)


@on.meta
def do_meta(meta):
    i = meta.get("load_interval", -1)
    if i < 0:
        digi.logger.info("Stop loader")
        loader.stop()
    else:
        loader.reset(i)
        loader.start()


if __name__ == '__main__':
    digi.run()
