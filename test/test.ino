int currentState = 1;

void setup() {
  Serial.begin(9600);
  Serial.println("Obstacle = false");
}

void loop() {
  Serial.print("Etat actuel: "); Serial.println(currentState);

  switch (currentState) {
    case 1:
      Serial.println("Attend 1s");
      currentState = 4;
      break;

    case 2:
      Serial.println("Avance");
      currentState = 1;
      break;

    case 3:
      Serial.println("Stop");
      currentState = 1;
      break;

    case 4:
      Serial.println("Condition: Obstacle");
      if (true) { currentState = 2;}
      if (false) { currentState = 3;}
      break;

    default:
      Serial.println("Etat inconnu");
      currentState = 1;
      break;
  }
}
