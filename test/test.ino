// Macros pour simplifier le code
#define ATTEND(ms) delay(ms)
#define ALLUME_LED(pin) digitalWrite(pin, HIGH)
#define ETEINT_LED(pin) digitalWrite(pin, LOW)

int currentState = 1;

bool Obstacle = false;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.print("Etat actuel: ");
  Serial.println(currentState);

  switch (currentState) {
    case 1:
      Serial.println("Attend 2s");
      ATTEND(2000);
      currentState = 4;
      break;

    case 2:
      Serial.println("Stop");
      stop();
      currentState = 1;
      break;

    case 3:
      Serial.println("Avance");
      avance();
      currentState = 1;
      break;

    case 4:
      Serial.println("Obstacle = !Obstacle");
      Obstacle = !Obstacle;

      currentState = 5;
      break;

    case 5:
      Serial.println("Condition: Obstacle");
      if (Obstacle) { currentState = 2;}
      else { currentState = 3;}
      break;

    default:
      Serial.println("Etat inconnu");
      currentState = 1;
      break;
  }
}
