#include <Arduino_FreeRTOS.h>

char transmit_buffer[19];
char clock_sync_receiving_timestamp[5];
char clock_sync_sending_timestamp[5];

void setup()
{
  Serial.begin(115200);
  receiveHandshakeAndClockSync();
  xTaskCreate(init, "init", 100, NULL, 1, NULL);
}

void loop() {

}

void receiveHandshakeAndClockSync()
{
  //char timestamp[15];
  while (1) {
    if (Serial.available() && Serial.read() == 'H') {
      Serial.print('A');
      Serial.print(millis());
      break;
    }
  }
  Serial.print('|');
  Serial.print(millis());
  Serial.print('>');
  while (1) {
    if (Serial.available() && Serial.read() == 'A') {
      break;
    }
  }
}

void init(void* pvParameters)
{
  while (1)
  {
    TickType_t xCurrWakeTime = xTaskGetTickCount();

    //readSensorData();
    processSendData();

    vTaskDelayUntil(&xCurrWakeTime, 2000 / portTICK_PERIOD_MS);
  }
}

void processSendData() {
  memset(&transmit_buffer[0], 0, sizeof(transmit_buffer));
  char send_timestamp[5];
  char yaw[5];
  char pitch[5];
  char roll[5];
  int chksum = 0;
  itoa(millis(), send_timestamp, 10);
  Serial.print('D');
  strcat(transmit_buffer, "D");
  Serial.print(send_timestamp);
  strcat(transmit_buffer, send_timestamp);
  strcat(transmit_buffer, ",");
  Serial.print(',');
  Serial.print(12.23);
  strcat(transmit_buffer, dtostrf(12.23, 5, 2, yaw));
  Serial.print(15.34);
  strcat(transmit_buffer, dtostrf(15.34, 5, 2, pitch));
  Serial.print(17.26);
  strcat(transmit_buffer, dtostrf(17.26, 5, 2, roll));
  for (int a = 0; a < strlen(transmit_buffer); a++) {
    chksum ^= transmit_buffer[a];
  }
  strcat(transmit_buffer, "|");
  Serial.print('|');
  Serial.print(chksum);
  /*char checksum_arr[4];
  itoa(int(chksum), checksum_arr, 10);
  for (int i = 0; i < strlen(checksum_arr); i++) {
    Serial.print(checksum_arr[i]);
  }*/
}
