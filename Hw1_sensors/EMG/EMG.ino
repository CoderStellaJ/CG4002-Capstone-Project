/**
 * Myoware Muscle Sensor (EMG) processing code  
 * 
 * The idea behind this code to measure muscle fatigue is based on this paper:
 *  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6679263/
 *  https://www.wavemetrics.com/products/igorpro/dataanalysis/signalprocessing
 *  
 * 
 * EMG Window Period: 128ms 
 * Researchers state that the usual window period for EMG is from 100ms~300ms, however, 
 * arduino uno is capable of only supporting up to 200 bytes of data collected at one short and EMG signal requires
 * multiples of 2 for the samples, i chose 128 samples (1 sample per ms for 1khz sampling frequency)
 * Source of window period: https://www.researchgate.net/post/How_do_I_select_window_size_while_recording_EMG_using_Biopac_Single_Channel
 * 
 * The processing of values collected within 128ms will be carried out, the features extracted per window are as follow: 
 *  1) Max Amplitude in time domain 
 *  2) Mean Absolute Value (Amplitude) in time domain
 *  3) Root Mean Square in time domain
 *  4) Mean Frequency in frequency domain (carried out using ArduinoFFT library)
 *  
 *  The mean frequency computation is based on the example FFT_05 from the ArduinoFFT library which can be also found in the following link:
 *   https://github.com/kosme/arduinoFFT/blob/master/Examples/FFT_05/FFT_05.ino
**/

#include "arduinoFFT.h"

#define SAMPLES 128
#define SAMPLING_FREQUENCY 1000

double vReal[SAMPLES];
double vImag[SAMPLES];
double frequency[SAMPLES/2];

arduinoFFT FFT = arduinoFFT();

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
}

// the loop routine runs over and over again forever:
void loop() {
  double meanFrequency = 0;
  long long powerSpectrum = 0;
  long long powerSpectrumAndFreq = 0;
  
  double totalSensorValue = 0;
  double meanSquaredValue = 0;
  float meanAmplitude = 0;
  float rmsAmplitude = 0;
  float maxAmplitude = -1;
  
  // Collect 128 samples at the frequency of 1kHz, 128ms window period
  for (int i = 0; i < SAMPLES; i++) {
    float sensorValue = analogRead(A0);
    float convertedSensorValue = (sensorValue / 1024.0) * 5.0;

    // Collection of data for ArduinoFFT
    vReal[i] = sensorValue;
    vImag[i] = 0;
    Serial.println(sensorValue);
    // Recording the frequency
    if (i < SAMPLES/2) {
      frequency[i] = ((i * 1.0 * SAMPLING_FREQUENCY) / (SAMPLES * 1.0));
    }

    // Compute the sum of all samples collected
    totalSensorValue += convertedSensorValue;

    // Compute the sum of the squared value
    meanSquaredValue += (convertedSensorValue * convertedSensorValue);

    // Gather the largest amplitude of the EMG signal
    if (sensorValue > maxAmplitude) {
      maxAmplitude = convertedSensorValue;
    }

    // Serial.println(sensorValue);
    
    // Delay for a period of 1ms such that the frequency is 1kHz
    delay(1);
  }

  // Arduino FFT 
  FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD);
  FFT.ComplexToMagnitude(vReal, vImag, SAMPLES);

  // Serial.println("FFT");

  // Computing the mean frequency based on the formula in the research paper, sum of frequency multipled power spectra over sum of power spectra
  // The power spectra is computed by squaring the amplitude
  for (int i = 0; i < SAMPLES / 2; i++) {
    // Computing the power spectra value
    // Serial.println(frequency[i]);
    // Serial.print("vReal: ");
    // Serial.println(vReal[i]); 
    double powerSpec = vReal[i] * vReal[i];
    powerSpectrum += powerSpec;
    powerSpectrumAndFreq += (powerSpec * frequency[i]);
  }

  // Computing the mean frequency
  // Serial.println(powerSpectrumAndFreq);
  // Serial.println(powerSpectrum);
  meanFrequency = (powerSpectrumAndFreq * 1.0) / (powerSpectrum * 1.0);

  // Computing the mean amplitude value
  meanAmplitude = totalSensorValue / (SAMPLES * 1.0);

  // Computing the root mean square of the amplitude
  meanSquaredValue = meanSquaredValue / (SAMPLES * 1.0);
  rmsAmplitude = sqrt(meanSquaredValue);

  Serial.print("max amp: ");
  Serial.println(maxAmplitude);
  Serial.print("mean amp: ");
  Serial.println(meanAmplitude);
  Serial.print("rms amp: ");
  Serial.println(rmsAmplitude);
  Serial.print("mean freq: ");
  Serial.println(meanFrequency);

  delay(99999999);
}
