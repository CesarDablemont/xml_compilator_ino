void avance() {
  // allume moteur1 et 2
  Serial.println("Fonction avance");
}

void stop() {
  // eteind moteur1 et 2
  Serial.println("Fonction stop");
}

float distance(Sensor sensor) {

  // Envoyer une impulsion de 10 microsecondes sur la broche Trigger
  digitalWrite(sensor.trig, LOW);
  delayMicroseconds(2);
  digitalWrite(sensor.trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensor.trig, LOW);

  // Lire la durée de l'écho
  long dureeEcho = pulseIn(sensor.echo, HIGH);
  // Calculer la distance en centimètres
  float distanceMesuree = (dureeEcho * 0.0343) / 2;

  return distanceMesuree;
}