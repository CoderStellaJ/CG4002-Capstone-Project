#include <Arduino_FreeRTOS.h>

char transmit_buffer[19];
char clock_sync_receiving_timestamp[5];
char clock_sync_sending_timestamp[5];

void setup()
{
  Serial.begin(115200);
  //receiveHandshakeAndClockSync();
  xTaskCreate(init, "init", 100, NULL, 1, NULL);
}

void loop() {

}

void receiveHandshakeAndClockSync()
{
  char timestamp[15];
  strcat(timestamp, 'A');
  while (1) {
    if (Serial.available() && Serial.read() == 'H') {
      itoa(millis(), clock_sync_receiving_timestamp, 10);
      break;
    }
  }
  strcat(timestamp, clock_sync_receiving_timestamp);
  strcat(timestamp, '|');
  itoa(millis(), clock_sync_sending_timestamp, 10);
  strcat(timestamp, clock_sync_sending_timestamp);
  strcat(timestamp, '>');
  for (int a = 0; a < strlen(timestamp); a++) {
    Serial.print(timestamp[a]);
  }
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
  char acc_x_data[5];
  char acc_y_data[5];
  /*itoa(millis(), send_timestamp, 10);
  strcat(transmit_buffer, 'D');
  strcat(transmit_buffer, ",");
  strcat(transmit_buffer, send_timestamp);
  strcat(transmit_buffer, ",");*/
  strcat(transmit_buffer, dtostrf(12.23, 5, 2, acc_x_data));
  strcat(transmit_buffer, ",");
  strcat(transmit_buffer, dtostrf(15.25, 5, 2, acc_y_data));
  for (int i = 0; i < strlen(transmit_buffer); i++) {
    Serial.print(transmit_buffer[i]);
  }
  /*int chksum = 0;
    for (int a = 0; a < strlen(transmit_buffer); a++) {
    chksum ^= transmit_buffer[a];
    }*/
}
