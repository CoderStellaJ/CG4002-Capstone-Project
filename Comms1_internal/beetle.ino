#include <Arduino_FreeRTOS.h>

/* Packet Format */
typedef struct TPacket{
  char packet_type = 'D';
  long timestamp;
  char start;
  float IMU1[6];
  float IMU2[6];
  char checksum[4];
} TPacket;

TPacket data;

char transmit_buffer[4000];
char acc_x_data[6];
char acc_y_data[6];

void setup()
{
  
  Serial.begin(115200);

  receiveHandshake();
  //clockSynchronize();

  xTaskCreate(init, "init", 200, NULL, 1, NULL);
}

void loop() {
  
}

void receiveHandshake()
{
  while(1) {
    if (Serial.available() && Serial.read() == 'H') { // "HELLO" packet received from Ultra96
      Serial.println("Hello packet received");
      Serial.write('A');
      while(1) {
        if (Serial.available() && Serial.read() == 'A') { // "ACK" packet received from Ultra96
          Serial.println("ACK packet received. Handshaking complete.");
          break;
        }
      }
      break;
    }
  }
}

void clockSynchronize(){

}

void init(void* pvParameters)
{
  while(1)
  {
    TickType_t xCurrWakeTime = xTaskGetTickCount();

    //readSensorData();
    //processSendData();
    
    vTaskDelayUntil(&xCurrWakeTime, 1000/portTICK_PERIOD_MS);
  }
}

void processSendData() {
  int radix = 10;
  char res_buffer[33];
  char *strptr;
  strptr = ltoa(12345,res_buffer,radix);
  strcat(transmit_buffer, 'D');
  strcat(transmit_buffer, ",");
  strcat(transmit_buffer, strptr);
  strcat(transmit_buffer, ",");
  strcat(transmit_buffer, 'S');
  strcat(transmit_buffer, ",");
  strcat(transmit_buffer, dtostrf(12.23, 5, 2, acc_x_data));
  strcat(transmit_buffer, ",");
  strcat(transmit_buffer, dtostrf(15.25, 5, 2, acc_y_data));
  for(int i = 0; i < strlen(transmit_buffer); i++){
    Serial.write(transmit_buffer[i]);
  }
  /*memset(transmit_buffer, 0, sizeof(transmit_buffer));
  int chksum = 0;
  for (int a = 0; a < strlen(transmit_buffer); a++) {
    chksum ^= transmit_buffer[a];
  }*/
}
