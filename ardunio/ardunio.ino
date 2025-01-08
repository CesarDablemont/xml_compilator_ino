// Macros pour simplifier le code
#define ATTEND(ms) delay(ms)
#define ALLUME_LED(pin) digitalWrite(pin, HIGH)
#define ETEINT_LED(pin) digitalWrite(pin, LOW)
#define LIRE(pin) digitalRead(pin)

int currentState = 6;

// Pas de variable a initialiser ici : Debut

void setup() {
  Serial.begin(115200);

  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(39, INPUT_PULLUP);
  pinMode(37, INPUT_PULLUP);
  pinMode(35, INPUT_PULLUP);
}

void loop() {
  Serial.print("Etat actuel: ");
  Serial.println(currentState);

  switch (currentState) {
    case 1:
      Serial.println("AllumeLed pin 1");
      ALLUME_LED(1);
      currentState = 7;
      break;

    case 2:
      Serial.println("EteintLed pin 1");
      ETEINT_LED(1);
      currentState = 7;
      break;

    case 3:
      Serial.println("AllumeLed pin 2");
      ALLUME_LED(2);
      currentState = 8;
      break;

    case 4:
      Serial.println("EteintLed pin 2");
      ETEINT_LED(2);
      currentState = 5;
      break;

    case 5:
      Serial.println("Attend 500ms");
      ATTEND(500);
      currentState = 6;
      break;

    case 6:
      Serial.println("Condition: Lire pin 39");
      if (LIRE(39)) { currentState = 1;}
      else { currentState = 2;}
      break;

    case 7:
      Serial.println("Condition: Lire pin 37");
      if (LIRE(37)) { currentState = 3;}
      else { currentState = 8;}
      break;

    case 8:
      Serial.println("Condition: Lire pin 35");
      if (LIRE(35)) { currentState = 4;}
      else { currentState = 5;}
      break;

    default:
      Serial.println("Etat inconnu");
      currentState = 6;
      break;
  }
}
