char transmit_buffer[19];
char timestamp[10];
unsigned int time_sync;
bool is_new_move = false;
void setup()
{
  Serial.begin(115200);
  receiveHandshakeAndClockSync();
}

void loop() {
  if (!is_new_move) {
    ultoa(millis(), timestamp, 10);
  }
  processSendData();
  delay(50);
}

void receiveHandshakeAndClockSync()
{
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

void processSendData() {
  char yaw[10];
  char pitch[10];
  char roll[10];
  int chksum = 0;
  strcat(transmit_buffer, "D");
  Serial.print('D');
  if (!is_new_move) {
    strcat(transmit_buffer, timestamp);
    Serial.print(timestamp);
    is_new_move = true;
  } else {
    strcat(transmit_buffer, "1");
    Serial.print('1');
  }
  strcat(transmit_buffer, ",");
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
  memset(&transmit_buffer[0], 0, sizeof(transmit_buffer));
}
