### Setting up FreeRTOS for Arduino
Visit this link for more info: https://exploreembedded.com/wiki/Setting_Up_FreeRTOS_on_Arduino

Note: Don't forget to #include <Arduino_FreeRTOS.h> at the top of the Arduino sketch

Note: Download FreeRTOSconfig.h header file and replace the original header file in the Arduino_FreeRTOS folder with it. It contains the minimal amount of configurations to ensure smaller memory usage on the Arduino board of the Beetle.

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


