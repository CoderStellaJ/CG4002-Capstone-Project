### Setting up arduino to upload hardware files ###
The two libraries required to use the IMUs (MPU6050) are uploaded in this folder, the folders named I2Cdev and MPU6050. The following are the steps to setup the libraries:
 - Download the folders I2Cdev and MPU6050
 - Navigate to where Arduino was installed on your computer, reference path: Local Disk -> Program Files -> Arduino
 - Navigate to the libraries folders within Arduino
 - Place the 2 downloaded folders, I2Cdev and MPU6050 in this folder
 
### Usage of the Bluno Beetle and IMU (MPU6050) set ### 
The following are the steps prior to using the code to gather data:
 - Check which set are you holding onto and get the calibration values from the calibration textfile named IMU_CalibrationValues.txt in this folder
 - Head to the IMU code and edit the following lines within void setup() function to the respective values stated in the textfile
      - mpu.setXGyroOffset(220);
      - mpu.setYGyroOffset(76);
      - mpu.setZGyroOffset(-85);
      - mpu.setZAccelOffset(1788);

### EMG Features  ###
The following are the features (frequency/time domain features) extracted from the data by EMG:
  - Mean Amplitude (time domain)
  - Max Amplitude Value (time domain)
  - Root Mean Square: Amplitude (time domain)
  - Standard Deviation? (time domain) 
  
These data will allow us to identify the fatigue level of the muscle based on the following papers 
