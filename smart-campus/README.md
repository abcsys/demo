# CNT Demo
## Description
This article aims to demonstrate the power of the dSpace network, enabling data exchange between personal devices and the environment. In this demo, data collection is performed by the "digilite", an app running on an iOS device that connects to a "digiphone", a digi designed specifically to ingest data from the digilite and propagate it to the dSpace network.

## Setup
First, in order to enable communciations between the digilite and digiphone, the EMQX meta digi is used. To start it, run `digi space start emqx`.

Next, clone the [CNT demo directory](https://github.com/digi-project/demo/tree/main/cnt) in order to have all of the digis required for this demo (building, room, and digiphone). Additionally, this directory contains the dynamic room mounting script.

Run the digis to model the physical layout of Soda Hall.

```bash
$ digi run digiphone jamsheediphone
jamsheediphone

$ digi run room soda411 soda420 soda430
soda411
soda420
soda430

$ digi run building soda
soda

$ digi space mount soda411 soda420 soda430 soda
```

Note that we do not mount `jamsheediphone` to anything yet. Our dynamic room mounting script will take care of dynamically mounting `jamsheediphone` to a room depending on which room the phone is physically located in.

## Dynamic Room Mounting Script
Configure the dynamic room mounting script to include data about the room in `room-mounter/rooms.json`.

```json
[
	{
		"name": "Soda 411",
		"bssid": "0:4e:35:e2:d8:b2",
		"digi": "soda411"
	},
	{
		"name": "Soda 420",
		"bssid": "0:4e:35:eb:2d:d2",
		"digi": "soda420"
	},
	{
		"name": "Soda 430",
		"bssid": "0:4e:35:e2:ee:f2",
		"digi": "soda430"
	}
]
```

The `bssid` field is used to dynamically mount a digiphone to a room depending on its bssid. The `digi` field specifies the name of the digi to mount to. The `name` field is used for logging.

Next, configure which digiphones we should listen to for dynamic mounting in `room-mounter/mounter.py` on line 5:

```python
DIGIPHONE_NAMES = ["jamsheediphone", "silveryiphone"]
```

Finally, run the dynamic room mounting script:

```bash
$ python3 mounter.py
jamsheediphone is not currently in any known rooms
```

## Digilite
The digilite repository is currently closed-source. However, if you have access, you can enter the dSpace IP/domain and EMQX port (normally 30000). Finally, enter the digi name for your digiphone from the setup section.

![View of the digilite UI](https://i.imgur.com/xBVHTQQ.jpg)

Finally, click "Save and Launch".

## Demo
Upon running the digilite, you should notice that the mounter script will automatically detect the bssid of the phone. If the bssid is connected to a known room specified in `room-mounter/rooms.json`, the dynamic room mounting script will automatically mount the digiphone to the corresponding room's digi, allowing the egress of the digiphone to send network information data.

You should notice that the mounter script now has a new line in the log, showing that the digiphone is now connected to a room.

```bash
$ python3 mounter.py
jamsheediphone is not currently in any known rooms
jamsheediphone connected to Soda 420
```

We can query the digiphone bssid egress to see the latest bssid. This corresponds to the digiphone's current room. The dynamic mounting script uses this egress to determine how and where to mount.

```bash
$ dq jamsheediphone@bssid "bssid | sort -r event_ts | cut bssid | head"
{bssid:"0:4e:35:eb:2d:d2"}
```

Since the digiphone is now dynamically mounted to the room, the room's handler will determine how many digiphones are mounted, and automatically dump the occupancy to its pool.

```bash
$ dq soda420@occupancy "occupancy | sort -r event_ts | cut occupancy | head"
{occupancy:1}
```

If we query another room, we can see that the occupancy is 0.

```bash
$ dq soda430@occupancy "occupancy | sort -r event_ts | cut occupancy | head"
{occupancy:0}
```

Upon connecting to a new bssid, the digilite will automatically run an network active measurement test. The test takes 20 seconds. Once this time has elapsed, an `activeMeasurement` record is dumped to the digiphone pool, and to the `activeMeasurement` egress. This data schema follows the NDT7 protocol, which can be found [here](https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md).

```bash
$ dq jamsheediphone@activeMeasurement "activeMeasurement | sort -r event_ts | cut activeMeasurement | head"
{activeMeasurement:{download:{ConnectionInfo:{UUID:"ndt-qssls_1679132002_000000000017EBCF",Server:"[2001:438:fffd:2d::152]:443",Client:"[2607:f140:400:a010:8c5b:ad01:4557:a806]:64172"},TCPInfo:{BytesRetrans:35910,PacingRate:25712323,RcvSsThresh:64096,BytesAcked:224119351,DataSegsIn:44,SndWnd:2042240,RcvOooPack:0,RcvMSS:1184,Backoff:0,RcvRTT:0,TotalRetrans:27,Options:7,RcvSpace:14400,Probes:0,RTTVar:2107,CAState:0,AdvMSS:1428,LastDataRecv:160,BytesSent:224607461,RTO:224000,LastDataSent:4,SndSsThresh:242,Retrans:0,ReordSeen:0,Unacked:340,MaxPacingRate:-1,DeliveredCE:0,State:1,DataSegsOut:168882,SndBufLimited:0,ATO:40000,DSackDups:0,Fackets:0,Sacked:0,SegsOut:168885,MinRTT:4593,Reordering:3,LastAckSent:0,SegsIn:13345,RWndLimited:4000,PMTU:1500,NotsentBytes:2191840,ElapsedTime:10000743,RTT:22819,BytesReceived:3674,BusyTime:10020000,SndMSS:1330,Lost:0,DeliveryRate:19147286,LastAckRecv:4,WScale:118,SndCwnd:342,Retransmits:0,Delivered:168516,AppLimited:0},BBRInfo:{ElapsedTime:10000743,PacingGain:256,BW:25972043,MinRTT:4593,CwndGain:512}},upload:{ConnectionInfo:{UUID:"ndt-qssls_1679132002_00000000001910D3",Server:"[2001:438:fffd:2d::152]:443",Client:"[2607:f140:400:a010:8c5b:ad01:4557:a806]:64173"},BBRInfo:{ElapsedTime:9470736,PacingGain:739,BW:266440,MinRTT:4991,CwndGain:739},TCPInfo:{BytesRetrans:13654,PacingRate:7289822,RcvSsThresh:3144064,BytesAcked:59554,DataSegsIn:286007,SndWnd:131072,RcvOooPack:1,RcvMSS:1330,Backoff:0,RcvRTT:77474,TotalRetrans:21,Options:7,RcvSpace:3647092,Probes:0,RTTVar:4391,CAState:0,AdvMSS:1428,LastDataRecv:0,BytesSent:73208,RTO:280000,LastDataSent:212,SndSsThresh:2147483647,Retrans:0,ReordSeen:0,Unacked:0,MaxPacingRate:-1,DeliveredCE:0,State:1,DataSegsOut:115,SndBufLimited:0,ATO:40000,DSackDups:3,Fackets:0,Sacked:0,SegsOut:116938,MinRTT:4991,Reordering:3,LastAckSent:0,SegsIn:286145,RWndLimited:0,PMTU:1500,NotsentBytes:0,ElapsedTime:9470736,RTT:76064,BytesReceived:379901807,BusyTime:4932000,SndMSS:1330,Lost:0,DeliveryRate:766239,LastAckRecv:132,WScale:118,SndCwnd:18,Retransmits:0,Delivered:92,AppLimited:1}},deviceInfo:{os:"16.3.1",model:"iPhone14,3"},ssid:"eduroam",bssid:"0:4e:35:eb:2d:d2"}}
```

However, the above data is messy and unreadable. Luckily, the room's ingress formats the data from the digiphone's activeMeasurement egress into a human-readable format. Query ingress of soda420 to see calculated & formatted data.

```bash
$ dq soda420@networkSpeed “networkSpeed | sort -r event_ts | cut networkSpeed | head"
{networkSpeed:{downloadSpeed:179.28216013550193,uploadSpeed:320.9058362517971,ping:4.991}}
```

If we physically move the device to Soda 411, the dynamic mounting script will automatically unmount the digiphone from Soda 420, and mount to Soda 411.

```bash
$ dq soda420@occupancy "occupancy | sort -r event_ts | cut occupancy | head"
{occupancy:0}
```

```bash
$ dq soda411@occupancy "occupancy | sort -r event_ts | cut occupancy | head"
{occupancy:1}
```

Finally, we can view attributes about the building's occupancy (total number of people in the building) and utilization (number of rooms that have at least 1 person).

```bash
$ dq soda "building_occupancy | sort -r event_ts | cut building_occupancy | head"
{building_occupancy:1}
```

Since there are 3 rooms, there should be 33% utilization.

```bash
$ dq soda "building_utilization | sort -r event_ts | cut building_utilization | head"
{building_utilization:0.3333333333333333}
```

## Benchmarks
### Data Freshness
The data follows a pipeline to get from the digilite to the dSpace network. Here is a breakdown of the data pipeline and how long each step takes. The timings vary based on (1) the network speed and (2) the CPU running the dSpace, so we conduct 2 experiments: one on a UC Berkeley dSpace hosted by Google Cloud Platform, and another on a local dSpace hosted entirely on a Mac laptop and local network.

This first experiment was run on eduroam at UC Berkeley in Soda Hall. The download speed is 179.28Mbps, the upload speed is 320.91Mbps, and the ping is 4.99ms. The machine running the dSpace is a Google Cloud Platform e2-standard-2 instance.

- Data generated on digilite → data sent on digilite: **136 μs**
- Data sent on digilite → data received on MQTT driver: **242 ms**
- Data received on MQTT driver → data dumped to digi pool: **302 ms**
- Data dumped to digi pool → dynamic mount: **1698 ms**
- Dynamic mount → room occupancy record generated: **909 ms**
- Room occupancy record generated → building occupancy record generated: **2167 ms**

This second experiment was run on a local network on a M1 Pro MacBook Pro 2021.

- Data generated on digilite → data sent on digilite: **119 μs**
- Data sent on digilite → data received on MQTT driver: **21 ms**
- Data received on MQTT driver → data dumped to digi pool: **55 ms**
- Data dumped to digi pool → dynamic mount: **226 ms**
- Dynamic mount → room occupancy record generated: **180 ms**
- Room occupancy record generated → building occupancy record generated: **350 ms**

### Lines of Code
#### Digilite
Swift source files

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Swift                            8            152            118            553
-------------------------------------------------------------------------------
SUM:                             8            152            118            553
-------------------------------------------------------------------------------
```

Including all generated code, libraries, etc

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Objective-C                      6           3069           1418           9694
Swift                           65           1994           1782           7469
XML                             19             34              3            948
Markdown                         4            231              2            589
C/C++ Header                     6            201           1731            396
Bourne Shell                     1             24             24            142
JSON                             3              0              0             31
Text                             1             10              0             25
-------------------------------------------------------------------------------
SUM:                           105           5563           4960          19294
-------------------------------------------------------------------------------
```

#### Dynamic Room Mounting Script
Python script, JSON data source

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                           1             17             10             58
JSON                             1              0              0             17
-------------------------------------------------------------------------------
SUM:                             2             17             10             75
-------------------------------------------------------------------------------
```

#### Digiphone Digi
driver/handler.py, deploy/cr.yaml, model.yaml

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
YAML                             2              0              0             17
Python                           1              2              0              7
-------------------------------------------------------------------------------
SUM:                             3              2              0             24
-------------------------------------------------------------------------------
```

#### Room Digi
driver/handler.py, deploy/cr.yaml, model.yaml

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
YAML                             2              0              0             31
Python                           1              3              0             13
-------------------------------------------------------------------------------
SUM:                             3              3              0             44
-------------------------------------------------------------------------------
```

#### Building Digi
driver/handler.py, deploy/cr.yaml, model.yaml

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
YAML                             2              0              0             52
Python                           1              1              0              4
-------------------------------------------------------------------------------
SUM:                             3              1              0             56
-------------------------------------------------------------------------------
```

### Query Complexity
#### Digiphone Digi
Egress

- `activeMeasurement` - 1
- `bssid` - 14

#### Room Digi
Ingress

- `activeMeasurement` - 1

Egress

- `occupancy` - 5
- `networkSpeed` - 48

#### Building Digi
Ingress

- `occupancy` - 13
- `utilization` - 24
- `networkSpeed` - 29

Egress

- `occupancy` - 5
- `utilization` - 5
- `networkSpeed` - 5
