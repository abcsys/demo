```
# start k8s clusters digi.dev/scripts
NAME=office REGION=us-west-1 make ec2
NAME=school REGION=us-west-2 make ec2
# ..and the local space: home
```

```
digi space ls
digi space show 
digi space checkout office
digi space ls -c
digi space show
digi space show school
```

Office:
```
digi space checkout school
digi ls
digi run lamp l1 l2
digi run room lounge -v
digi check lounge
# digi vz lounge
digi space mount l1 l2 lounge
digi check lounge
digi run scene scene
digi space mount scene lounge
digi edit lounge # adaptive mode
digi watch lounge
```

Home:
```
digi space checkout home
digi ls
digi run lamp l1 l2 l3 l4
digi run room r1 r2
digi run home home -v
digi check home
# digi vz home
digi edit home # sleep mode
digi check home
```