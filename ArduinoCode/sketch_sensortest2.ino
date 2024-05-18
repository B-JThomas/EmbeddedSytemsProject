#include <Bonezegei_DHT22.h>

// Constants
#define DHTPIN 2         // DHT22 data pin is connected to Arduino D2
#define PIRPIN 3         // PIR motion sensor output pin connected to Arduino D3

Bonezegei_DHT22 dht(DHTPIN);

// Variables to track time
unsigned long lastTempReadTime = 0;
unsigned long lastMotionCheckTime = 0;
//const long tempReadInterval = 300000; // Interval at which to send temperature data (5 minutes)
const long tempReadInterval = 15000;
const long motionCheckInterval = 1000; // Interval at which to check motion sensor (1 second)

bool motionDetectedFlag = false; // To track if motion was detected within the 5-minute interval

void setup() {
  Serial.begin(9600); // Start the serial communication
  dht.begin(); // Initialize the DHT22 sensor
  pinMode(PIRPIN, INPUT); // Set the PIR pin as an input
}

void loop() {
  unsigned long currentTime = millis();

  // Check the PIR sensor every second
  if (currentTime - lastMotionCheckTime >= motionCheckInterval) {
    lastMotionCheckTime = currentTime;
    checkMotion();
  }

  // Send temperature and motion update every 5 minutes
  if (currentTime - lastTempReadTime >= tempReadInterval) {
    lastTempReadTime = currentTime;
    sendTemperatureAndHumidity();
    sendMotionUpdate();
    motionDetectedFlag = false; // Reset motion detection flag
  }
}

void checkMotion() {
  if (digitalRead(PIRPIN) == HIGH) {
    motionDetectedFlag = true;
  }
}

void sendTemperatureAndHumidity() {
  // Read humidity and temperature or report any errors
  float humidity; 
  float temperature; 

  if (dht.getData()) {                               // get All data from DHT22
    temperature = dht.getTemperature();       // return temperature in celsius
  }

  // Check if any readings failed and exit early (to try again).
  if (isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print(" Temperature: ");
    Serial.print(temperature);
  }
}

void sendMotionUpdate() {
  // Print motion status for the last 5 minutes
  Serial.print(" Motion: ");
  Serial.println(motionDetectedFlag ? "True" : "False");
}