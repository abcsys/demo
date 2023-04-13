import digi
import digi.on as on

gvr_digiphone = "campus.digi.dev/v1/digiphones"

@on.mount
def do_occupancy():
    model = digi.rc.view()
    mounts = model.get("mount", {})
    digiphones = mounts.get(gvr_digiphone, {})
    room_occupancy = None if digiphones is None else len(digiphones)
    if room_occupancy is not None:
        digi.pool.load([{"occupancy":room_occupancy}])

if __name__ == '__main__':
    digi.run()
