// Referenced jrowberg's MPU6050_DMP6 library example
// https://github.com/jrowberg/i2cdevlib/blob/master/Arduino/MPU6050/examples/MPU6050_DMP6/MPU6050_DMP6.ino

#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

#define THRESHOLDING_SAMPLES 10

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MPU6050 mpu;

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorFloat gravity;    // [x, y, z]            gravity vector
VectorInt16 accel;      // [x, y, z]            accel sensor measurements
VectorInt16 accelReal;  // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 accelWorld; // [x, y, z]            world-frame accel sensor measurements
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

// These 2 ypr values is to check whether there are sudden movements, if there are then set flag to true
volatile float ypr_firstCheck[3] = {0.0, 0.0, 0.0}; // Variabe to store the 1st ypr value 
volatile float ypr_lastCheck[3] = {0.0, 0.0, 0.0};  // Variable to store the 2nd ypr value 
volatile float yawDiff = 0.0;
volatile float pitchDiff = 0.0;
volatile float rollDiff = 0.0;

volatile long accel_firstCheck[3] = {0, 0, 0};
volatile long accel_lastCheck[3] = {0, 0, 0};
volatile long accelXDiff = 0;
volatile long accelYDiff = 0;
volatile long accelZDiff = 0;

volatile float yprDiff[THRESHOLDING_SAMPLES][3] = { 0.0 };
volatile long accelDiff[THRESHOLDING_SAMPLES][3] = { 0 };
volatile int yprIndex = 0;
volatile int accelIndex = 0;

volatile boolean stoppedMoving = false;

unsigned long timestamp = 0;

// Interrupt detection routine
volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

// Function to get yaw pitch roll values
int getYPR_worldAccel() {
  // if programming failed, don't try to do anything
  if (!dmpReady) return;

  // wait for MPU interrupt or extra packet(s) available
  while (!mpuInterrupt && fifoCount < packetSize) {
    // other program behavior stuff here
  }

  // reset interrupt flag and get INT_STATUS byte
  mpuInterrupt = false;
  mpuIntStatus = mpu.getIntStatus();

  // get current FIFO count
  fifoCount = mpu.getFIFOCount();

  // check for overflow
  if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
    // reset so we can continue cleanly
    mpu.resetFIFO();
    Serial.println(F("FIFO overflow!"));
    
    // Indicate that there is a failure in getting data
    return 0;
  // otherwise, check for DMP data ready interrupt
  } else if (mpuIntStatus & 0x02) {
    // wait for correct available data length
    while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();

    // read a packet from FIFO
    mpu.getFIFOBytes(fifoBuffer, packetSize);
    
    // track FIFO count here in case there is > 1 packet available
    // (this lets us immediately read more without waiting for an interrupt)
    fifoCount -= packetSize;

    // display Euler angles in degrees
    mpu.dmpGetQuaternion(&q, fifoBuffer);
    mpu.dmpGetGravity(&gravity, &q);
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);

    // display initial world-frame acceleration, adjusted to remove gravity
    // and rotated based on known orientation from quaternion
    mpu.dmpGetAccel(&accel, fifoBuffer);
    mpu.dmpGetLinearAccel(&accelReal, &accel, &gravity);
    mpu.dmpGetLinearAccelInWorld(&accelWorld, &accelReal, &q);

    // Indicate that the data retrieval is successful
    return 1;
  }
}

void setup() {
  timestamp = millis();
  // join I2C bus (I2Cdev library doesn't do this automatically)
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
      Wire.begin();
      TWBR = 24; // 400kHz I2C clock (200kHz if CPU is 8MHz)
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
      Fastwire::setup(400, true);
  #endif

  Serial.begin(115200);

  // initialize MPU6050 IMU device
  mpu.initialize();

  // verify connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // load and configure the DMP
  Serial.println(F("Initializing DMP..."));
  devStatus = mpu.dmpInitialize();

  // supply your own gyro offsets here, scaled for min sensitivity
  mpu.setXGyroOffset(-102);
  mpu.setYGyroOffset(-84);
  mpu.setZGyroOffset(-659);
  mpu.setZAccelOffset(1257);
  
  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {
    // turn on the DMP, now that it's ready
    Serial.println(F("Enabling DMP..."));
    mpu.setDMPEnabled(true);

    // enable Arduino interrupt detection
    Serial.println(F("Enabling interrupt detection (Arduino external interrupt 0)..."));
    attachInterrupt(0, dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // set our DMP Ready flag so the main loop() function knows it's okay to use it
    Serial.println(F("DMP ready! Waiting for first interrupt..."));
    dmpReady = true;

    // get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
    // ERROR!
    // 1 = initial memory load failed
    // 2 = DMP configuration updates failed
    // (if it's going to break, usually the code will be 1)
    Serial.print(F("DMP Initialization failed (code "));
    Serial.print(devStatus);
    Serial.println(F(")"));
  }

  // Delay for approximately 10 seconds so that the MPU6050 can stabilise itself
  //delay(10000);
  Serial.println("Stabilising completed");
}

void loop() {  
  // Get two YPRs at the start to avoid FIFO overflow issues
  // Get an initial YPR value
  
  while (1) {
    if (getYPR_worldAccel() == 1) {
      ypr_firstCheck[0] = ypr[0] * 180/M_PI;
      ypr_firstCheck[1] = ypr[1] * 180/M_PI;
      ypr_firstCheck[2] = ypr[2] * 180/M_PI;
      accel_firstCheck[0] = accelWorld.x;
      accel_firstCheck[1] = accelWorld.y;
      accel_firstCheck[2] = accelWorld.z;
      break;
    }
  }
  delay(50);
  
  // Get a secondary YPR value
  while (1) {
    if (getYPR_worldAccel() == 1) {
      ypr_lastCheck[0] = ypr[0] * 180/M_PI;
      ypr_lastCheck[1] = ypr[1] * 180/M_PI;
      ypr_lastCheck[2] = ypr[2] * 180/M_PI;
      accel_lastCheck[0] = accelWorld.x;
      accel_lastCheck[1] = accelWorld.y;
      accel_lastCheck[2] = accelWorld.z;
      break;
    }
  }
  delay(50);
  
  // Compute the differences between these 2 YPR values to detect if there is a sudden movement 
  yawDiff = ypr_lastCheck[0] - ypr_firstCheck[0];
  pitchDiff = ypr_lastCheck[1] - ypr_firstCheck[1];
  rollDiff = ypr_lastCheck[2] - ypr_firstCheck[2];
  accelXDiff = accel_lastCheck[0] - accel_firstCheck[0];
  accelYDiff = accel_lastCheck[1] - accel_firstCheck[1];
  accelZDiff = accel_lastCheck[2] - accel_firstCheck[2]; 

  // Store the differences for ypr and accel into yprDiff and accelDiff into the circular buffer
  yprDiff[yprIndex][0] = abs(yawDiff); 
  yprDiff[yprIndex][1] = abs(pitchDiff);
  yprDiff[yprIndex][2] = abs(rollDiff);
  yprIndex++;

  accelDiff[accelIndex][0] = abs(accelXDiff);
  accelDiff[accelIndex][1] = abs(accelYDiff);
  accelDiff[accelIndex][2] = abs(accelZDiff);
  accelIndex++;

  // Reset the index of yprIndex and accelIndex for circular buffer
  if (yprIndex == THRESHOLDING_SAMPLES) {
    yprIndex = 0;
  }
  if (accelIndex == THRESHOLDING_SAMPLES) {
    accelIndex = 0;
  }

  // Compute the sum of differences
  volatile float yawDiffSum = 0.0;
  volatile float pitchDiffSum = 0.0;
  volatile float rollDiffSum = 0.0;
  volatile long accelXDiffSum = 0;
  volatile long accelYDiffSum = 0;
  volatile long accelZDiffSum = 0;
  
  for (int i = 0; i < THRESHOLDING_SAMPLES; i++) {
    yawDiffSum += yprDiff[i][0];
    pitchDiffSum += yprDiff[i][1];
    rollDiffSum += yprDiff[i][2];
    accelXDiffSum += accelDiff[i][0];
    accelYDiffSum += accelDiff[i][1];
    accelZDiffSum += accelDiff[i][2];
  }

  Serial.print("ypr and accel diff: ");
  Serial.print(yawDiffSum);
  Serial.print("\t");
  Serial.print(pitchDiffSum);
  Serial.print("\t");
  Serial.print(rollDiffSum);
  Serial.print("\t");
  Serial.print(accelXDiffSum);
  Serial.print("\t");
  Serial.print(accelYDiffSum);
  Serial.print("\t");
  Serial.println(accelZDiffSum);

  if ((abs(yawDiffSum) <= 10 || abs(pitchDiffSum) <= 10 || abs(rollDiffSum) <= 10) && (abs(accelXDiffSum) <= 2000 || abs(accelYDiffSum) <= 2000 || abs(accelZDiffSum) <= 2000)) {
    stoppedMoving = true;
  }
  
  if (stoppedMoving && ((abs(yawDiffSum) >= 15 || abs(pitchDiffSum) >= 15 || abs(rollDiffSum) >= 15) && (abs(accelXDiffSum) >= 5000 || abs(accelYDiffSum) >= 5000 || abs(accelZDiffSum) >= 5000))) {
    stoppedMoving = false;
    Serial.println("EXCEED THRESHOLD");
  }

  /**
  // Only start taking data if there is a spike is found in either one of the three differences 
  // The spike signifies a new dance move by the dancer 
  if (abs(yawDiff) >= 10 || abs(pitchDiff) >= 10 || abs(rollDiff) >= 10) {
    // Get the initial timestamp of this new dance move
    timestamp = millis();
    // Loop to get 50 samples from MPU6050 at the frequency of 20Hz
    for (int i = 0; i < 50; i++) {
      if (getYPR_worldAccel() == 0) {
        i--;
        continue;
      }
      Serial.print("ypr accelWorld\t");
      Serial.print(ypr[0] * 180/M_PI);
      Serial.print("\t");
      Serial.print(ypr[1] * 180/M_PI);
      Serial.print("\t");
      Serial.print(ypr[2] * 180/M_PI);
      Serial.print("\t");
      Serial.print(accelWorld.x);
      Serial.print("\t");
      Serial.print(accelWorld.y);
      Serial.print("\t");
      Serial.println(accelWorld.z);
      delay(50);
    }
  }
  

  Serial.println("50 Samples Collected");
  */
}
