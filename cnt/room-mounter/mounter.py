import subprocess
import json
import sys

DIGIPHONE_NAMES = ["jamsheediphone", "silveryiphone"]

# Read rooms.json file for room data
with open('rooms.json') as file:
    rooms = json.loads(file.read())

mounted_name = None
mounted_bssid = None
mounted_digi = None

printed = False

# Loop forever to mount
while True:
    for digiphone_name in DIGIPHONE_NAMES:
        output = subprocess.run(f'digi query -f json {digiphone_name}@bssid "sort -r event_ts | head"', shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

        if output == "":
            if not printed:
                print(f'{digiphone_name} is not currently in any known rooms')
                printed = True
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
                mounted_name, mounted_bssid, mounted_digi = room_name, room_bssid, room_digi
                printed = False

                # Stop searching
                found_room = True
                break

        if not found_room:
            if mounted_digi is not None:
                subprocess.run(f'digi space mount -d {digiphone_name} {mounted_digi}', shell=True)

            # If we reach here, we are not in any currently known rooms
            mounted_name = None
            mounted_bssid = None
            mounted_digi = None

            if not printed:
                print(f'{digiphone_name} is not currently in any known rooms')
                printed = True
