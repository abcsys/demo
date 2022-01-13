.PHONY: query
query:
	# TBD
	digi query "home"

.PHONY: run compose all stop
run:
	digi run lamp l1 l2 l3
	digi run room r1 r2 r3
	digi run home home
	digi run scene s1 s2 s3
	digi run multiscene ms
compose:
	digi space mount l1 s1 r1
	digi space mount l2 s2 r2
	digi space mount l3 s3 r3
	digi space mount r1 r2 r3 home
	digi space pipe ms.output.scenes.s1.objects s1.input.objects &
	digi space pipe ms.output.scenes.s2.objects s2.input.objects &
	digi space pipe ms.output.scenes.s3.objects s3.input.objects
all: | run compose
stop:
	digi stop `digi ls -q`
	digi space pipe -d ms.output.scenes.s1.objects s1.input.objects >/dev/null 2>&1 & \
	digi space pipe -d ms.output.scenes.s2.objects s2.input.objects >/dev/null 2>&1 & \
	digi space pipe -d ms.output.scenes.s3.objects s3.input.objects >/dev/null 2>&1
