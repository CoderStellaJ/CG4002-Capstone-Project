/*
  ReadAnalogVoltage
  Reads an analog input on pin 0, converts it to voltage, and prints the result to the serial monitor.
  Graphical representation is available using serial plotter (Tools > Serial Plotter menu)
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.
*/

unsigned long long totalSensorValue = 0;
unsigned long long meanSquaredValue = 0;
float meanAmplitude = 0;
float rmsAmplitude = 0;
int maxAmplitude = -1;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
}

// the loop routine runs over and over again forever:
void loop() {
  
  // Collect 200 samples at the frequency of 1kHz, 200ms window period
  for (int i = 0; i < 200; i++) {
    int sensorValue = analogRead(A0);

    // Compute the sum of all samples collected
    totalSensorValue += sensorValue;

    // Compute the sum of the squared value
    meanSquaredValue += (sensorValue * sensorValue);

    // Gather the largest amplitude of the EMG signal
    if (sensorValue > maxAmplitude) {
      maxAmplitude = sensorValue;
    }
    
    // Delay for a period of 1ms such that the frequency is 1kHz
    delay(1);
  }

  // Computing the mean amplitude value
  meanAmplitude = totalSensorValue / 200.0;

  // Computing the root mean square of the amplitude
  meanSquaredValue = meanSquaredValue / 200.0;
  rmsAmplitude = sqrt(meanSquaredValue);

  Serial.println(maxAmplitude);
  Serial.println(meanAmplitude);
  Serial.println(rmsAmplitude);
}
