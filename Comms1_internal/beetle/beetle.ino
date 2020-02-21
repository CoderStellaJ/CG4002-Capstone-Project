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

    vTaskDelayUntil(&xCurrWakeTime, 200 / portTICK_PERIOD_MS);
  }
}

void processSendData() {
  memset(&transmit_buffer[0], 0, sizeof(transmit_buffer));
  char timestamp[10];
  char yaw[10];
  char pitch[10];
  char roll[10];
  int chksum = 0;
  strcat(transmit_buffer, "D");
  Serial.print('D');
  ultoa(millis(), timestamp, 10);
  strcat(transmit_buffer, timestamp);
  strcat(transmit_buffer, ",");
  Serial.print(timestamp);
  Serial.print(',');
  dtostrf(12.23, 5, 2, yaw);
  strcat(transmit_buffer, yaw);
  strcat(transmit_buffer, ",");
  Serial.print(yaw);
  Serial.print(',');
  dtostrf(15.34, 5, 2, pitch);
  strcat(transmit_buffer, pitch);
  strcat(transmit_buffer, ",");
  Serial.print(pitch);
  Serial.print(',');
  dtostrf(17.26, 5, 2, roll);
  strcat(transmit_buffer, roll);
  Serial.print(roll);
  for (int a = 0; a < strlen(transmit_buffer); a++) {
    chksum ^= transmit_buffer[a];
  }
  Serial.print('|');
  Serial.print(chksum);
  Serial.print('>');
}
