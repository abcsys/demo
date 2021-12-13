import digi
import digi.on as on
import digi.util as util


@on.control("power")
def do_power(p):
    if "intent" in p:
        p["status"] = p["intent"]


@on.control("brightness")
def do_brightness(b):
    if "intent" in b:
        b["status"] = b["intent"]


@on.control("infrared_brightness")
def do_brightness(ib):
    if "intent" in ib:
        ib["status"] = ib["intent"]


@on.control("waveform")
def do_brightness(w):
    if "intent" in w:
        w["status"] = w["intent"]


def load():
    model = digi.rc.view()
    digi.pool.load(
        [{
            "power": util.deep_get(model, "control.power.status"),
            "brightness": util.deep_get(model, "control.brightness.status"),
            "infrared_brightness": util.deep_get(model, "control.infrared_brightness.status"),
            "waveform": {
                "waveform": util.deep_get(model, "control.waveform.status"),
                "duty_cycle": 1,
            },
            "vendor": util.deep_get(model, "meta.vendor"),
        }]
    )


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
