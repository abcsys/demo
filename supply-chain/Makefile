.PHONY: stop test
stop:
	digi stop `digi ls -q`
test:
	digi run ship s1
	digi run port p1
	digi space mount s1 p1
	sleep 5
	digi space mount -d s1 p1
.PHONY: delay delay-run
delay:
	digi run airport a1 a2
	digi run port p1 p2
	digi run plane l1
	digi run ship s1
	digi run cargo c1
delay-run:
	# c1 l1 -> a1 -> a2; c1 s1 -> p1 -> p2
	# load to plane
	digi space mount c1 l1
	# wait 2 hour at a1
	digi space mount l1 a1; sleep 2
	digi space mount -d l1 a1
	# 1 hour flight; arrive at a2
	sleep 1
	# wait 3 hour at a2
	digi space mount l1 a2; sleep 3
	digi space mount -d l1 a2
	# 4 hour flight, off-plane l1, and immediately to port p1
	sleep 4
	digi space mount -d c1 l1
	# 2 hour transit and load to ship at p1
	sleep 2
	digi space mount c1 s1
	digi space mount s1 p1
	# wait 2 hours at p1
	sleep 2
	digi space mount -d s1 p1
	# 5 hours to p2
	sleep 5
	digi space mount s1 p2
	# 1 hour to offload
	sleep 1
	digi space mount -d c1 s1
