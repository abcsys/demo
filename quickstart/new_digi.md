```
digi init tv
vim tv/model.yaml
digi gen tv
vim tv/driver/handler.py
vim tv/deploy/cr.yaml # default off
digi build tv -q
digi run tv tv
digi check tv
digi edit tv tv # turn on
digi check tv
```

