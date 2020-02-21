# Comms2 External
### Goal 
1. Connecting Ultra96 with evaluation server (socket programming)
2. Information encryption
3. Synchronization delay between the dancers

### Run server and client
1. run server
2. run client
3. key in secret key in server
```
cd C:\Repository\CG4002-Capstone-Project\Comms2_external
python eval_server.py 127.0.0.1 8888 6
python eval_client.py 127.0.0.1 8888 6 cg40024002group6
```

secret key (length is 16):
```
cg40024002group6
```
### Run client on Ultra96
* USB: http://192.168.3.1
* WiFi access point: http://192.168.2.1

WIFI connection
```
cd C:\Repository\CG4002-Capstone-Project\Comms2_external
python eval_server.py 172.25.104.211 5050 6
python3 eval_client.py 172.25.104.211 5050 6 cg40024002group6
```
Ethernet connection
```
python eval_server.py 192.168.2.7 5050 6
python3 eval_client.py 192.168.2.7 5050 6 cg40024002group6
```


