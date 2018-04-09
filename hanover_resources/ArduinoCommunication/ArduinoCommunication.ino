// Messaging Variabl
String send1 = "";
String sendInfo = "";
char READ_UNTIL = ':';

// Output variables
int LED_PIN = 13;
int personInView = 0;

void setup() 
{
  Serial.begin(9600);  // start serial port at 9600 bps
  Serial.setTimeout(10); //Super important. Makes Serial.parseInt() not wait a long time after an integer has ended.
  pinMode(LED_PIN, OUTPUT);
}


void loop()
{
  while(Serial.available() > 0){
    String var = Serial.readStringUntil(READ_UNTIL);
    float value = Serial.parseFloat();

    if(var.equals("person")){
      personInView = value;
      Serial.println("[OK: " + String(value) + "]");
    }
  }

  // Send signal to robot
  if(personInView > 0){
    digitalWrite(LED_PIN, HIGH);
  }else{
    digitalWrite(LED_PIN, LOW);
  }
} 





