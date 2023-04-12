import subprocess
import json
import sys

DIGIPHONE_NAMES = ["jamsheediphone", "silveryiphone"]
digiphone_state = {}

# Dictionary to keep track of each digiphone's state
for digiphone_name in DIGIPHONE_NAMES:
    digiphone_state[digiphone_name] = {
        "mounted_name": None,
        "mounted_bssid": None,
        "mounted_digi": None,
        "printed": False
    }

# Read rooms.json file for room data
with open('rooms.json') as file:
    rooms = json.loads(file.read())

# Loop forever to mount
while True:
    for digiphone_name in DIGIPHONE_NAMES:
        mounted_name = digiphone_state[digiphone_name]["mounted_name"]
        mounted_bssid = digiphone_state[digiphone_name]["mounted_bssid"]
        mounted_digi = digiphone_state[digiphone_name]["mounted_digi"]
        printed = digiphone_state[digiphone_name]["printed"]

        output = subprocess.run(f'digi query -f json {digiphone_name}@bssid "sort -r event_ts | head"', shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

        if output == "":
            if not printed:
                print(f'{digiphone_name} is not currently in any known rooms')
                digiphone_state[digiphone_name]["printed"] = True
            continue

        try:
            curr_bssid = json.loads(str(output))['bssid']
        except json.decoder.JSONDecodeError:
            continue

        found_room = False

        # Search through our list of rooms
        for room in rooms:
            room_name, room_bssid, room_digi = room.values()

            if curr_bssid == mounted_bssid:
                found_room = True
                break

            # If we found a match, and it's not the same as the currently mounted room
            elif curr_bssid == room_bssid:
                # Unmount & print info
                    if mounted_digi is None:
                        print(f'{digiphone_name} connected to {room_name}')
                    else:
                        subprocess.run(f'digi space mount -d {digiphone_name} {mounted_digi}', shell=True)
                        print(f'{digiphone_name} moved from {mounted_name} to {room_name}')

                    # Mount
                    subprocess.run(f'digi space mount {digiphone_name} {room_digi}', shell=True)

                    # Update state
                    digiphone_state[digiphone_name]["mounted_name"] = room_name
                    digiphone_state[digiphone_name]["mounted_bssid"] = room_bssid
                    digiphone_state[digiphone_name]["mounted_digi"] = room_digi
                    digiphone_state[digiphone_name]["printed"] = False

                    # Stop searching
                    found_room = True
                    break

        if not found_room:
            if mounted_digi is not None:
                subprocess.run(f'digi space mount -d {digiphone_name} {mounted_digi}', shell=True)

            # If we reach here, we are not in any currently known rooms
            digiphone_state[digiphone_name]["mounted_name"] = None
            digiphone_state[digiphone_name]["mounted_bssid"] = None
            digiphone_state[digiphone_name]["mounted_digi"] = None

            if not printed:
                print(f'{digiphone_name} is not currently in any known rooms')
                digiphone_state[digiphone_name]["printed"] = True
