.PHONY: graph stop alice test run
graph:
	digi run -q room livingroom & digi run -q room bedroom & digi run -q room kitchen & \
	digi run -q home home & digi run human alice && sleep 12
	digi space mount livingroom home; sleep 2 && \
	digi space mount bedroom home; sleep 2 && \
	digi space mount kitchen home & \
	digi space mount livingroom alice; sleep 2 && \
	digi space mount bedroom alice; sleep 2 && \
	digi space mount kitchen alice
	digi list
stop:
	digi stop -q livingroom || true & digi stop -q bedroom || true & digi stop -q kitchen || true
	digi stop -q home || true &
	digi stop alice || true
	sleep 2
test:
	ds mount bedroom human-test; sleep 1
	ds mount livingroom human-test
	ds mount kitchen human-test
	ds mount bedroom home-test; sleep 1
	ds mount livingroom home-test
	ds mount kitchen home-test
run:
	python single-human.py
show:
	dq alice "select cur_time,cur_room,activity where cur_gen==0 | sort cur_time" -f table
