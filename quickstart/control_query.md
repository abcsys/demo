```
digi kind
digi run lamp l1 l2
digi check l1
digi edit l1 		 # turn on
digi check l1
digi run room lounge
digi space mount l1 l2 lounge
digi check lounge 
digi edit lounge # sleep mode
digi check lounge
digi check l1
digi query lounge "avg(brightness)"
digi query l1 "select brightness as b where power=='on' | avg(b)"
```

