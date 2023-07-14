#include <math.h>

#define TEMPERATURE_SENSOR A0
#define LIGHT A3

String light = "LIGHT";

String temp = "TEMP";
void setup() {
  Serial.begin(9600);
 }

float read_Temperature(int pin){
  const int B = 4275;               // B value of the thermistor
  const int R0 = 100000;            // R0 = 100k
  int a = analogRead(pin); // Integer: 0-1023
  float R = 1023.0/a-1.0;
  R = R0*R;
  float temperature = 1.0/(log(R/R0)/B+1/298.15)-273.15; // convert to temperature via datasheet
  return temperature;
}

void loop(){
  if (Serial.available() > 0){  // Check if there is data available to read from the Serial port.
    String inputCommand = Serial.readStringUntil("/r");
    if (inputCommand == temp){  // Check if the message matches the command. 
      float temp_C = read_Temperature(A0);
      Serial.println(temp_C);
    }

    else if (inputCommand == light) 
    {
      int analog_value = analogRead(LIGHT);
      int mapped_value = map(analog_value, 0, 800, 0, 10);
      Serial.println(mapped_value);
      
  }
}
}
