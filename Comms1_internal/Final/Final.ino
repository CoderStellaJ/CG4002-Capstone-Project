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

// Store the previous ypr and accel value, to detect the differences and update the thresholding
// array accordingly
volatile float lastYaw = 0.0;
volatile float lastPitch = 0.0;
volatile float lastRoll = 0.0;
volatile long lastAccelX = 0;
volatile long lastAccelY = 0;
volatile long lastAccelZ = 0;

// Variables to compute thresholding
volatile float yprDiff[THRESHOLDING_SAMPLES][3] = { 0.0 };
volatile long accelDiff[THRESHOLDING_SAMPLES][3] = { 0 };
volatile int yprIndex = 0;
volatile int accelIndex = 0;

// Variable to check whether the dancer has stopped moving or not
volatile boolean stoppedMoving = false;
// Variable to set the setOnce variable only once
volatile boolean setOnce = false;

// Communication variables
char transmit_buffer[70];
char timestamp_arr[10];
unsigned long timestamp = 0;
bool is_repeat_dance = true;
int dance_counter = 0;

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

  // load and configure the DMP
  devStatus = mpu.dmpInitialize();

  // supply your own gyro offsets here, scaled for min sensitivity
  mpu.setXGyroOffset(275);
  mpu.setYGyroOffset(-75);
  mpu.setZGyroOffset(53);
  mpu.setZAccelOffset(727);


  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {
    // turn on the DMP, now that it's ready
    mpu.setDMPEnabled(true);

    // enable Arduino interrupt detection
    attachInterrupt(0, dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // set our DMP Ready flag so the main loop() function knows it's okay to use it
    dmpReady = true;

    // get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
    // ERROR!
    // 1 = initial memory load failed
    // 2 = DMP configuration updates failed
    // (if it's going to break, usually the code will be 1)
  }
  receiveHandshakeAndClockSync();
}

void receiveHandshakeAndClockSync()
{
  unsigned long tmp_recv_timestamp;
  unsigned long tmp_send_timestamp;
  while (1) {
    if (Serial.available() && Serial.read() == 'T') { // need to do time calibration
      while (1) {
        if (Serial.available() && Serial.read() == 'H') {
          Serial.print('T');
          tmp_recv_timestamp = millis();
          Serial.print(tmp_recv_timestamp);
          break;
        }
      }
      Serial.print('|');
      tmp_send_timestamp = millis();
      Serial.print(tmp_send_timestamp);
      Serial.print('>');
      while (1) {
        if (Serial.available() && Serial.read() == 'A') { // ultra96 received timestamp
          break;
        } else if (Serial.available() && Serial.read() == 'R') { // retransmit timestamp as ultra96 did not receive it
          Serial.print('T');
          Serial.print(tmp_recv_timestamp);
          Serial.print('|');
          Serial.print(tmp_send_timestamp);
          Serial.print('>');
        }
      }
      break;
    } else if (Serial.available() && Serial.read() == 'A') { // no need to do time calibration
      break;
    }
  }
}

void loop() {
  int tmp = 0;
  while (1) {
    timestamp = 0;
    setOnce = false;
    // Get the initial timestamp of this new dance move
    for (int i = 0; i < 200; i++) {
      if (getYPR_worldAccel() == 0) {
        i--;
        continue;
      }
      tmp = i;
      // Store the differences for ypr and accel into yprDiff and accelDiff into the circular buffer
      yprDiff[yprIndex][0] = abs((ypr[0] * 180 / M_PI) - lastYaw);
      yprDiff[yprIndex][1] = abs((ypr[1] * 180 / M_PI) - lastPitch);
      yprDiff[yprIndex][2] = abs((ypr[2] * 180 / M_PI) - lastRoll);
      yprIndex++;

      accelDiff[accelIndex][0] = abs(accelWorld.x - lastAccelX);
      accelDiff[accelIndex][1] = abs(accelWorld.y - lastAccelY);
      accelDiff[accelIndex][2] = abs(accelWorld.z - lastAccelZ);
      accelIndex++;

      // Update the lastYPR and lastAccel values to the current value
      lastYaw = ypr[0] * 180 / M_PI;
      lastPitch = ypr[1] * 180 / M_PI;
      lastRoll = ypr[2] * 180 / M_PI;
      lastAccelX = accelWorld.x;
      lastAccelY = accelWorld.y;
      lastAccelZ = accelWorld.z;

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

      for (int j = 0; j < THRESHOLDING_SAMPLES; j++) {
        yawDiffSum += yprDiff[j][0];
        pitchDiffSum += yprDiff[j][1];
        rollDiffSum += yprDiff[j][2];
        accelXDiffSum += accelDiff[j][0];
        accelYDiffSum += accelDiff[j][1];
        accelZDiffSum += accelDiff[j][2];
      }
      if (tmp > 40 && !setOnce && (abs(yawDiffSum) <= 10 || abs(pitchDiffSum) <= 10 || abs(rollDiffSum) <= 10) && (abs(accelXDiffSum) <= 2000 || abs(accelYDiffSum) <= 2000 || abs(accelZDiffSum) <= 2000)) {
        stoppedMoving = true;
      }

      if (!setOnce && stoppedMoving && ((abs(yawDiffSum) >= 15 || abs(pitchDiffSum) >= 15 || abs(rollDiffSum) >= 15) && (abs(accelXDiffSum) >= 5000 || abs(accelYDiffSum) >= 5000 || abs(accelZDiffSum) >= 5000))) {
        stoppedMoving = false;
        setOnce = true;
        timestamp = millis();
      }

      int chksum = 0;
      char yaw[5];
      char pitch[5];
      char roll[5];
      char accx[5];
      char accy[5];
      char accz[5];
      strcat(transmit_buffer, "D");
      Serial.print('D');
      ultoa(timestamp, timestamp_arr, 10);
      strcat(transmit_buffer, timestamp_arr);
      Serial.print(timestamp_arr);
      strcat(transmit_buffer, ",");
      Serial.print(',');
      itoa(int(round(ypr[0] * 100 * 180 / M_PI)), yaw, 10);
      strcat(transmit_buffer, yaw);
      strcat(transmit_buffer, ",");
      Serial.print(yaw);
      Serial.print(',');
      itoa(int(round(ypr[1] * 100 * 180 / M_PI)), pitch, 10);
      strcat(transmit_buffer, pitch);
      strcat(transmit_buffer, ",");
      Serial.print(pitch);
      Serial.print(',');
      itoa(int(round(ypr[2] * 100 * 180 / M_PI)), roll, 10);
      strcat(transmit_buffer, roll);
      strcat(transmit_buffer, ",");
      Serial.print(roll);
      Serial.print(',');
      itoa(accelWorld.x * 100, accx, 10);
      strcat(transmit_buffer, accx);
      strcat(transmit_buffer, ",");
      Serial.print(accx);
      Serial.print(',');
      itoa(accelWorld.y * 100, accy, 10);
      strcat(transmit_buffer, accy);
      strcat(transmit_buffer, ",");
      Serial.print(accy);
      Serial.print(',');
      itoa(accelWorld.z * 100, accz, 10);
      strcat(transmit_buffer, accz);
      Serial.print(accz);
      for (int a = 0; a < strlen(transmit_buffer); a++) {
        chksum ^= transmit_buffer[a];
      }
      Serial.print('|');
      Serial.print(chksum);
      Serial.print('>');
      memset(&transmit_buffer[0], 0, sizeof(transmit_buffer));
      delay(50);
    }
    while (1) {
      if (Serial.available() && Serial.read() == 'B') { // repeat dance
        is_repeat_dance = true;
        break;
      } else if (Serial.available() && Serial.read() == 'Z') { // dance success
        is_repeat_dance = false;
        break;
      }
    }
    if (is_repeat_dance) {
      continue;
    } else {
      break;
    }
  }
  receiveHandshakeAndClockSync();
}
