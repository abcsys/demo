import digi
import digi.on as on
import digi.util as util

import sys
import time
import threading
import random

gvr_lamp_geeni = "mock.digi.dev/v1/lamp-geenis"
gvr_lamp_lifx = "mock.digi.dev/v1/lamp-lifxes"
gvr_lamp_phue = "mock.digi.dev/v1/lamp-phues"


class Sim(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_flag = threading.Event()

    def run(self):
        self._stop_flag.clear()
        while not self._stop_flag.is_set():
            model = digi.rc.view()
            mounts = model.get("mounts", {})
            digi.logger.info(str(model))
            for _, geeni in mounts.get(gvr_lamp_geeni, {}):
                if random.random() > 0.5:
                    continue
                util.deep_set(geeni, "spec.control.power.intent", random.choice(["on", "off"]))
                util.deep_set(geeni, "spec.control.brightness.intent", round(random.random(), 1))

            for _, lifx in mounts.get(gvr_lamp_lifx, {}):
                if random.random() > 0.5:
                    continue
                util.deep_set(lifx, "spec.control.power.intent", random.choice(["on", "off"]))
                util.deep_set(lifx, "spec.control.brightness.intent", round(random.random(), 1))
                util.deep_set(lifx, "spec.control.infrared_brightness.intent", round(random.random(), 1))
                util.deep_set(lifx, "spec.control.waveform.intent", random.choice(["SINE", "SAW",
                                                                                   "HALF_SINE", "TRIANGLE",
                                                                                   "PULSE"]), 1)
            for _, phue in mounts.get(gvr_lamp_phue, {}):
                if random.random() > 0.5:
                    continue
                util.deep_set(phue, "spec.control.power.intent", random.choice(["on", "off"]))
                util.deep_set(phue, "spec.control.brightness.intent", round(random.random(), 1))
                util.deep_set(phue, "spec.control.color.intent", random.choice(["yellow", "white", "purple", "red"], 1))

            util.check_gen_and_patch_spec(*digi.auri,
                                          spec={
                                              "mounts": mounts
                                          },
                                          gen=sys.maxsize)
            time.sleep(random.randint(1, 10))



    def stop(self):
        self._stop_flag.set()


@on.control
def do_building_mode():
    s = Sim()
    s.stop()
    s.start()


if __name__ == '__main__':
    digi.run()
