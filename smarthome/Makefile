.PHONY: graph stop human
#graph:
	#digi run lamp l1 && digi run room livingroom && digi space mount l1 livingroom && \
#	digi run lamp l2 && digi run room bathroom && digi space mount l1 bathroom && \
#	digi run lamp l3 && digi run room bedroom && digi space mount l1 bedroom
#clean:
	#digi stop l1 && digi stop l2 && digi stop l3 && \
#	digi stop livingroom && digi stop bath-room && digi stop bedroom && \
#	digi stop alice
#run:
	#digi run human alice && digi space mount livingroom alice && \
#	digi space mount bathroom alice && digi space mount bedroom alice
#all: | graph run
graph:
	digi run room livingroom && digi run room bedroom
	digi run home home && digi mount livingroom home
	digi mount bedroom home
stop:
	digi stop livingroom && digi stop bedroom
	digi stop home
human:
	ds mount bedroom human-test
	ds mount livingroom human-test
run:
	python single-human.py
