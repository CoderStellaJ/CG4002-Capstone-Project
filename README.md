# CG4002 Dance Dance

Setting up FreeRTOS for Arduino

Visit this link for more info: https://exploreembedded.com/wiki/Setting_Up_FreeRTOS_on_Arduino

Note: Don't forget to #include <Arduino_FreeRTOS.h> at the top of the Arduino sketch

Note: Download FreeRTOSconfig.h header file and replace the original header file in the Arduino_FreeRTOS folder with it. It contains the minimal amount of configurations to ensure smaller memory usage on the Arduino board of the Beetle.

run these in order in bluetoothctl: rfkill unblock bluetooth -> sudo service bluetooth restart -> scan on -> discoverable on -> pairable on -> trust <address> -> connect <address>
