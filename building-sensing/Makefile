.PHONY: run stop
run:
	python expt.py
stop:
	digi stop `digi ls -q`

.PHONY: min build stop
build:
	digi build lamp occupancy
min:
	digi run lamp l1
	digi run appliance a1
	digi run room r1
	digi run floor f1
	digi run group g1
	digi run building b1
	digi run campus c1
	digi space mount l1 a1 r1
	digi space mount r1 f1
	digi space mount r1 g1
	digi space mount f1 b1
	digi space mount b1 c1
# TBD use python script
.PHONY: lamp energy kw rank phone
lamp:
	digi run lamp l1
	digi run appliance a1
energy: | min
rank:
	digi run appliance a1 a2 a3
	digi run room r1 r2
	digi run building b1
	digi space mount a1 r1
	digi space mount a2 a3 r2
	digi space mount r1 r2 b1
kw:
	digi run appliance a1
	digi run room r1
	digi space mount a1 r1
phone:
	digi run appliance a1
	digi run phone p1
	digi space mount a1 p1

.PHONY: occupancy-min occupancy corr
occupancy-min:
	digi run underdesk ud1 ud2
	digi run room r1 r2
	digi run building b1
	digi space mount ud1 r1
	digi space mount ud2 r2
	digi space mount r1 r2 b1
occupancy:
	digi run underdesk ud1 ud2 ud3 ud4 ud5 ud6
	digi run room r1 r2
	digi run building b1
	digi space mount ud1 ud2 ud3 ud4 r1
	digi space mount ud5 ud6 r2
	digi space mount r1 r2 b1
corr: | occupancy
	digi run appliance a1
	digi space mount a1 r1
