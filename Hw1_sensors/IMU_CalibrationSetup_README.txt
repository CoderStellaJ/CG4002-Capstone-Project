===============MPU6050 Calibration Setup README===============

***If you have I2Cdev and MPU6050 previously installed previously, move them out of the folder Program Files -> Arduino -> libraries

Afterwhich follow the following steps to setup the calibration accordingly:
1) Open Arduino IDE
2) Head to Tools -> Manage Libraries
3) Type MPU6050 into the textbook and click enter
4) Amongst the result, install the library by Electronic Cats Version 0.0.2
5) Close manage libraries pop up
6) Head to Files -> Examples -> MPU6050 -> IMU_Zero
7) Place the IMU/MPU6050 as flat as possible to the table and upload the sketch
8) Open up serial monitor at baudrate 9600 and wait till you see a "----- done -----" line appearing 
    **Do NOT touch the IMU/MPU6050 while the code is running**
9) After the line appears, look at the line above it, it will look something like the following:
    " [567,567] --> [-1,2] [-2223,-2223] --> [0,1] [1131,1132] --> [16374,16404] [155,156] --> [-1,1] [-25,-24] --> [0,3] [5,6] --> [0,4]"
10) This line is the optimum offsets for X accel, Y accel, Z accel, X gyro, Y gyro and Z gyro respectively. For example, 567 is the X accel offset, -2223 is the Y accel offset, etcetc to 5 being the Z gyro offset 
11) Upon getting this value, head back to our code and update the following lines under void setup():
    	mpu.setXGyroOffset(220);
	mpu.setYGyroOffset(76);
	mpu.setZGyroOffset(-85);
  	mpu.setZAccelOffset(1788);
    You will only need the X, Y and Z for gyro and Z for accel offsets for the code 
12) In order to test whether the offsets are working, open up the example "MPU6050_DMP6" and update the offsets accordingly under void setup() function and upload the sketch, use serial monitor (115200 baud rate) and watch the values of yaw pitch roll, it should be around -0.05~0.05 only (do not shift the IMU from its initial position of the calibration) 