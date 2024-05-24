#define _TIMERINTERRUPT_LOGLEVEL_     3   // This must be the first line for the interrupt timer to work correctly

#include "ESP32TimerInterrupt.h"
#include "PCA9685.h"

#define READ_PIN                      4
#define SAMPLING_PERIOD_US            10000
ESP32Timer ITimer(0);

// Data variables
const int read_len = 50;
volatile int raw_reading;
volatile double filtered_reading[read_len];
double ave = 0.0;

bool bent_fingers = false;
int last_bend = 0;

// Filter variables
// Matlab was used to design the filter
const double a[7] = {1,	3.24187835356609,	5.90911693455883,	6.60249322640082,	5.01216578909717,	2.32504327700163,	0.609920214625014};
const double b[7] = {0.00618881713972113,	0,	-0.0185664514191634,	0,	0.0185664514191634,	0,	-0.00618881713972113};
const int n = 7; //length of a and b arrays
volatile double z[7] = {0, 0, 0, 0, 0, 0, 0};

// Servo
PCA9685 servo_cont;


bool IRAM_ATTR sampler(void * timerNo){
  raw_reading = analogRead(READ_PIN);

  // Shifting the filtered output array
  for(int i = 0; i < read_len-1; i++){
    filtered_reading[i] = filtered_reading[i+1];
  }
  // Applying the filter
  filtered_reading[read_len-1] = b[0]*raw_reading + z[0];
  for(int i = 1; i < n; i++){
    z[i-1] = b[i]*raw_reading + z[i] - a[i]*filtered_reading[read_len-1];
  }

  return true;
}

void setup() {
  // Setting up the input pin and serial port
  pinMode(READ_PIN, INPUT);

  //Serial.begin(115200);
  Serial.begin(9600);
  while(!Serial && millis()<5000);
  delay(500);
  Wire.begin();

  // Servo
  servo_cont.resetDevices();
  servo_cont.init();
  servo_cont.setPWMFrequency(200);

  //Setting up the timer interrupt
  if(ITimer.attachInterruptInterval(SAMPLING_PERIOD_US, sampler)){
    Serial.println("Started sampling.");
  }
  else{
    Serial.println("Interrupt did not get set up.");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  int start = millis();
  Serial.print(raw_reading);
  Serial.print("\t");
  Serial.println(abs(filtered_reading[read_len-1]));

  if((filtered_reading[read_len-1] > ave*2) & (abs(filtered_reading[read_len-1] - ave*2) > 1) & (millis()-last_bend > 1000)){
    if(bent_fingers){
      // unbend fingers
      servo_cont.setChannelPWM(1, 128<<4);  // Pointer finger
      servo_cont.setChannelPWM(2, 50<<4);   // Pinkie finger
      servo_cont.setChannelPWM(3, 20<<4);   // Middle finger
      servo_cont.setChannelPWM(4, 50<<4);   // Ring finger and thumb
      
      Serial.println("Unbend Fingers");
      
      bent_fingers = false;
    }
    else{
      // bend fingers
      servo_cont.setChannelPWM(1, 64<<4);
      servo_cont.setChannelPWM(2, 128<<4);
      servo_cont.setChannelPWM(3, 115<<4);
      servo_cont.setChannelPWM(4, 128<<4);
      
      Serial.println("Bend Fingers");

      bent_fingers = true;
    }
    last_bend = millis();
  }
  ave = average(read_len, filtered_reading);

  delay(9);
  delayMicroseconds(900);
}

double average(int num, volatile double *array){
  double sum = 0;
  for(int i = 0; i < num; i++){
    sum += array[i];
  }
  double average = sum/num;
  return average;
}