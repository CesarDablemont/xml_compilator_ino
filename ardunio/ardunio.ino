// Macros pour simplifier le code
#define ATTENDRE(ms) delay(ms)
#define ALLUMER(pin) digitalWrite(pin, HIGH)
#define ETEINDRE(pin) digitalWrite(pin, LOW)
#define LIRE(pin) digitalRead(pin)
#define BUZZ(pin) tone(pin, 600, 20)

struct Sensor {
int trig;
int echo;
};

int currentState = 7;
struct Sensor U1 = { 10, 8 };

void setup() {
  Serial.begin(115200);

  pinMode(10, OUTPUT);
  pinMode(8, INPUT);
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
}

void loop() {
  Serial.print("Etat actuel: ");
  Serial.println(currentState);

  switch (currentState) {
    case 1:
      Serial.println("Eteindre pin 1");
      ETEINDRE(1);
      currentState = 8;
      break;

    case 2:
      Serial.println("Allumer pin 1");
      ALLUMER(1);
      currentState = 4;
      break;

    case 3:
      Serial.println("Eteindre pin 2");
      ETEINDRE(2);
      currentState = 9;
      break;

    case 4:
      Serial.println("Allumer pin 2");
      ALLUMER(2);
      currentState = 6;
      break;

    case 5:
      Serial.println("Eteindre pin 4");
      ETEINDRE(4);
      currentState = 7;
      break;

    case 6:
      Serial.println("Allumer pin 4");
      ALLUMER(4);
      currentState = 7;
      break;

    case 7:
      Serial.println("Condition: U1 < 15");
      if (distance(U1) < 15) { currentState = 2;}
      else { currentState = 1;}
      break;

    case 8:
      Serial.println("Condition: U1 < 30");
      if (distance(U1) < 30) { currentState = 4;}
      else { currentState = 3;}
      break;

    case 9:
      Serial.println("Condition: U1 < 50");
      if (distance(U1) < 50) { currentState = 6;}
      else { currentState = 5;}
      break;

    default:
      Serial.println("Etat inconnu");
      currentState = 7;
      break;
  }
}
