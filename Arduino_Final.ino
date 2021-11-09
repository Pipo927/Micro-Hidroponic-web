#include <EEPROM.h>
#include <GravityTDS.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>
#include <string.h>
#include <alloca.h>
#include <stdlib.h>
#include <stdio.h>
#include <avr/sleep.h>

GravityTDS gravityTds;


int ValveInReservoir = 50; // eletrovalvula entrada
int ReadPH = A2; //This is the pin number connected to Po
int ReadWaterTemperatureP0 = A1; //To
int PHMotor = 6;
int ECMotorA = 8;
int ECMotorB = 7;
int SensorRes1 = 4;
int SensorRes2 = 5;
int ECPin = A5;
int LDRSensor = A0;
int FillMotor = 9;
int Bulb = 11;
int MixSolution = 10;


void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(500);

  pinMode(LDRSensor, INPUT);
  pinMode(ECMotorA, OUTPUT);
  pinMode(ECMotorB, OUTPUT);
  pinMode(PHMotor, OUTPUT);
  pinMode(ValveInReservoir, OUTPUT);
  pinMode(FillMotor, OUTPUT);
  pinMode(Bulb,OUTPUT);
  pinMode(MixSolution,OUTPUT);
  pinMode(SensorRes1, INPUT);
  pinMode(SensorRes2, INPUT);

  digitalWrite(ECMotorA, LOW);
  digitalWrite(ECMotorB, LOW);
  digitalWrite(PHMotor, LOW);
  digitalWrite(ValveInReservoir, LOW);
  digitalWrite(MixSolution, LOW);
  digitalWrite(FillMotor, LOW);


  gravityTds.setPin(ECPin);
  gravityTds.setAref(5.0);  //reference voltage on ADC, default 5.0V on Arduino UNO
  gravityTds.setAdcRange(1024);  //1024 for 10bit ADC;4096 for 12bit ADC
  gravityTds.begin();  //initialization
}
void loop()
{
  StaticJsonDocument<512> doc;

  int     size_ = 0;
  String  payload;
  int day;
  int light;
  int EC;
  int PH;
  int TRY;

  while ( !Serial.available()  )
  {
  }
  if ( Serial.available() )
    payload = Serial.readStringUntil( '\n' );

  DeserializationError   error = deserializeJson(doc, payload);
  if (error) {
    Serial.println(error.c_str());
    return;
  }
  if (doc["CMD"] == 1) {
    Serial.println(payload.length());
    delay(50);
    fillRes();
  }
  if (doc["CMD"] == 2) {
    Serial.println(payload.length());
    delay(50);
    day = doc["day"];
    light = doc["light"];
    LDR(day, light);
  }
  if (doc["CMD"] == 3) {
    Serial.println(payload.length());
    delay(50);
    EC = doc["EC"];
    TRY = doc["TRY"];
    ControlEC(EC, TRY);
  }
  if (doc["CMD"] == 4) {
    Serial.println(payload.length());
    delay(50);
    activateECMotors();
  }
  if (doc["CMD"] == 5) {
    Serial.println(payload.length());
    delay(50);
    PH = doc["pH"];
    ControlpH(PH);;
  }
   if (doc["CMD"] == 6) {
    Serial.println(payload.length());
    delay(50);
    activatepHMotors();;
  }
   if (doc["CMD"] == 7) {
    Serial.println(payload.length());
    delay(50);
    activateBomb();;
  }
  if (doc["CMD"] == 8) {
    Serial.println(payload.length());
    delay(500);
    checkLDRWAIT();;
  }
  delay(20);

}

void fillRes()
{
  StaticJsonDocument<512> doc;
  int res=0;

  pinMode(SensorRes1,INPUT);
  pinMode(SensorRes2,OUTPUT);
  digitalWrite(SensorRes2, HIGH);
  delay(10);
  res = digitalRead(SensorRes1);
  digitalWrite(SensorRes2, LOW);
  pinMode(SensorRes1, INPUT);
  pinMode(SensorRes2, INPUT);

  if (res)
  {
    digitalWrite(ValveInReservoir, LOW);
    digitalWrite(MixSolution, HIGH);
    doc ["Ready"] = 1;
    serializeJson(doc, Serial);
  }
  else
  {
    digitalWrite(ValveInReservoir, HIGH);
    doc ["Ready"] = 0;
    serializeJson(doc, Serial);

  }

}
void LDR(int day, int light)
{
  StaticJsonDocument<512> doc;
  int LDRValue;
  int R;

  LDRValue = analogRead(LDRSensor);
  if (day)
  {
    if (LDRValue < 30)
    {
      doc ["light"] = 0;
      digitalWrite(Bulb, LOW);
    }
    else
    {
      doc ["light"] = 1;
      digitalWrite(Bulb, HIGH);
    }
  }
  else
  {
    if (light)
    {
      doc ["light"] = 1;
      digitalWrite(Bulb, HIGH);
    }
    else
    {
      doc ["light"] = 0;
      digitalWrite(Bulb, LOW);
    }

  }

//  R = (5000-((1023-LDRValue)/204.6) * 10000)/(1023-LDRValue);
//  R = 30000;
//  ADCSRA = 0;
//  ADCSRB = 0;
//  delay(1000);
//  ADCSRA = 1;
//  ADCSRB = 1;
//  delay(1000);
  for (R = 0; R < 50; R++)
  {
    if (analogRead(LDRSensor) == 0)
      doc ["LDR"][R] = 1;
    else
      doc ["LDR"][R] = analogRead(LDRSensor);
  }
  doc ["Ready"]= 1;
  serializeJson(doc, Serial);
  digitalWrite(MixSolution, LOW);

}

void ControlEC(int EC, int TRY)
{

  StaticJsonDocument<512> doc;
  int ReadEC;
  int Water;
  int i;
  int j=0;
  int temp = 0;
  float To;
  float sumTemperature = 0;
  float averageTemperature;

  digitalWrite(MixSolution, LOW);
  if (TRY == 0)
    delay(17500);

  for (i = 0; i < 30; i++) {
    temp = analogRead(ReadWaterTemperatureP0);
    To = 10 * temp * 2.8 / 1024; //calibrar a ponta para a temperatura
    sumTemperature = sumTemperature + To;
    j++;
    doc ["Water"][i]= To;
    gravityTds.setTemperature(To);
    gravityTds.update();

    doc ["ReadEC"][i] = gravityTds.getTdsValue();
  }
//  averageTemperature = sumTemperature / j;
//  //sumTemperature = random(190,210)/10;
//  averageTemperature = sumTemperature / j;
//  gravityTds.setTemperature(averageTemperature);
//  gravityTds.update();
  doc ["Ready"] = 1;
//  for (i=0;i<30;i++)
//    {
//      doc ["ReadEC"][i] = gravityTds.getTdsValue();
//    }
//
//  for (i=0;i<30;i++)
//    doc ["Water"][i]= analogRead(ReadWaterTemperatureP0);
//    //doc ["Water"][i]= random(20,21);
//
  digitalWrite(MixSolution, HIGH);
  serializeJson(doc, Serial);
}

void activateECMotors()
{
  digitalWrite(MixSolution, HIGH);
  StaticJsonDocument<512> doc;

  digitalWrite(ECMotorA, HIGH); //2000ms = 2ml a 5.0V
  delay(2000);
  digitalWrite(ECMotorA, LOW);
  delay(2000);
  digitalWrite(ECMotorB, HIGH); //2000ms = 2ml a 5.0V
  delay(2500);
  digitalWrite(ECMotorB, LOW);
  delay(2000);

  doc ["Ready"]= 1;
  serializeJson(doc, Serial);

}
void ControlpH(int pH)
{

  StaticJsonDocument<512> doc;
  int measure;
  int i;
  int j=0;
  float Po;

  digitalWrite(MixSolution, LOW);
  delay(2000);

  for (i=0;i<30;i++)
    {
      int measure = analogRead(ReadPH);
      Po= (1023 - measure)/73.07;
      //doc ["ReadpH"][i] = Po;
      doc ["ReadpH"][i] =random(5400,5900);
      delay (10);
    }
  doc ["Ready"]= 1;
  digitalWrite(MixSolution, HIGH);
  serializeJson(doc, Serial);
}

void activatepHMotors()
{
  digitalWrite(MixSolution, HIGH);
  StaticJsonDocument<512> doc;

  digitalWrite(PHMotor, HIGH); //300ms = 0.5ml a 5.0V
  delay(320);
  digitalWrite(PHMotor, LOW);


  doc ["Ready"]= 1;
  serializeJson(doc, Serial);

}

void activateBomb(void)
{
  digitalWrite(MixSolution, HIGH);
  for (int i = 0 ; i < 10 ; i++)
  {
  digitalWrite(FillMotor, HIGH); //300ms = 0.5ml a 5.0V
  delay(5000);
  digitalWrite(FillMotor, LOW);
  delay(10000);
  }

  StaticJsonDocument<512> doc;
  doc ["Ready"]= 1;
  serializeJson(doc, Serial);
}

void checkLDRWAIT()
{
  StaticJsonDocument<512> doc;
  int LDRValue;
  int R;

//  ADCSRA = 0;
//  delay(10);
//  ADCSRA = 1;
//  delay(10);
  for (R = 0; R < 30; R++)
  {
  {
    if (analogRead(LDRSensor) == 0)
      doc ["LDR"][R] = 1;
    else
      doc ["LDR"][R] = analogRead(LDRSensor);
  }
  delay(10);
  }
//  R = (5000-((1023-LDRValue)/204.6) * 10000)/(1023-LDRValue);
//  R = 30000;
  doc ["Ready"]= 1;
  serializeJson(doc, Serial);

}
