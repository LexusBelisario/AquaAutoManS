#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 4 // Pin where the DS18B20 is connected
#define PH_SENSOR_PIN A1 // Pin where the Gravity pH sensor is connected
#define TURBIDITY_SENSOR_PIN A3 // Pin where the Turbidity sensor is connected

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

float temperature = 0.0;
float dissolvedOxygen = 0.0;
float pHValue = 0.0;

float doCalibrationFactor = 0.72; // Adjust according to your sensor's calibration

int turbiditySensorPin = A0;

void setup() {
  Serial.begin(9600);
  sensors.begin();
  
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
}

void loop() {
  // Get temperature from DS18B20
  sensors.requestTemperatures();
  temperature = sensors.getTempCByIndex(0);

  // Get pH value
  int pHSensorValue = analogRead(PH_SENSOR_PIN);
  pHValue = (pHSensorValue * 5.0 / 1024.0) * 3.5; // Adjust 3.5 as necessary based on your calibration

  // Get turbidity value
  int sensorValue = analogRead(turbiditySensorPin);
  int turbidity = map(sensorValue, 0, 750, 100, 0);
  
  // Print sensor values to Serial
  // Serial.print("Temperature (C): ");
  Serial.print(temperature);
  // Serial.println("°C");

  Serial.print(" ");

  if (temperature >= 26 && temperature <= 32) {
    Serial.print("NormalTemperature");
  } 
  else if (temperature < 26 && temperature > 20) {
    Serial.print("BelowAverageTemperature");
  } 
  else if (temperature <= 20) {
    Serial.print("ColdTemperature");
  } 
  else if (temperature > 26 && temperature < 35) {
    Serial.print("AboveAverageTemperature");
  } 
  else if (temperature >= 35) {
    Serial.print("HotTemperature");
  }

  Serial.print(" ");

  // Serial.print("pH Value: ");
  Serial.print(pHValue);
  Serial.print(" ");
if (pHValue < 4) {
    Serial.print("VeryAcidic");
} else if (pHValue >= 4 && pHValue < 6) {
    Serial.print("Acidic");
} else if (pHValue >= 6 && pHValue <= 7.5) {
    Serial.print("NormalpH");
} else if (pHValue > 7 && pHValue <= 9) {
    Serial.print("Alkaline");
} else if (pHValue > 9) {
    Serial.print("VeryAlkaline");
}

  // Serial.print("Turbidity Sensor Value: ");
  // Serial.println(sensorValue);
  
  // Serial.print("Turbidity: ");
  Serial.print(" ");
  Serial.print(turbidity);
    Serial.print(" ");
  

  // Determine water status based on turbidity
  if (turbidity < 20) {
    Serial.print("CLEAN");
  } 
  else if (turbidity >= 20 && turbidity < 50) {
    Serial.print("CLOUDY");
  } 
  else if (turbidity >= 50) {
    Serial.print("DIRTY");
  }

  Serial.println();

  // Delay for readability
  delay(2000);
}
