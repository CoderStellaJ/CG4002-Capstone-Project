### Handshaking
- Ultra96 -> "H"  
- Beetle -> "A"
- Beetle -> receiving timestamp
- Beetle -> "|" + sending timestamp + ">"

run these in order in bluetoothctl: rfkill unblock bluetooth -> sudo service bluetooth restart -> scan on -> discoverable on -> pairable on -> trust <address> -> connect <address>
