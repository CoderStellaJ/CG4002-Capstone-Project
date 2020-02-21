### Handshaking
- Ultra96 -> "H"  
- Beetle -> "A"
- Beetle -> receiving timestamp
- Beetle -> "|" + sending timestamp + ">"

### Set up
- rfkill unblock bluetooth 
- sudo service bluetooth restart 
- bluetoothctl
- scan on 
- discoverable on 
- pairable on 
- trust address(replaced with address of your beetle)
- connect address
  
If the above doesn't work, need to manually turn off bluetooth of ubuntu (top-right corner).
