.PHONY: run stop
run:
	digi run lamp l1 l2 l3
	digi run room lounge -v
	digi run scene scene
compose:
	digi space mount l1 l2 l3 scene lounge
stop:
	digi stop `digi ls -q`

