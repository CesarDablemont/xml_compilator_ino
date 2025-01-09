# **Projet Arduino : Générateur Automatique**

## **Prérequis**

1. **Python 3** :

   - Assurez-vous que **Python 3** est installé sur votre machine.
   - Pour vérifier, ouvrez un terminal ou une invite de commande et tapez :
     ```bash
     python --version
     ```
     ou
     ```bash
     python3 --version
     ```
   - Si Python n'est pas installé, téléchargez-le depuis [python.org](https://www.python.org/).

2. **yEd Graph Editor** :
   - Le schéma logique du projet doit être créé dans **yEd**.
   - Téléchargez yEd depuis [yEd Graph Editor](https://www.yworks.com/products/yed).
   - Enregistrez votre schéma au format **`.xgml`** après l'avoir terminé.

---

## **Instructions d'utilisation**

1. **Préparer le schéma logique** :

   - Créez un schéma logique correspondant à votre projet dans **yEd**.
   - Enregistrez le fichier dans le format **`.xgml`**.

2. **Lancer l'application** :
   - Double-cliquez sur **`app.bat`** pour exécuter l'application.
   - Une fenêtre s'ouvrira pour vous permettre de sélectionner votre fichier **`.xgml`**. Choisissez le fichier correspondant à votre projet.

---

## **Configuration du fichier `app.bat`**

Le fichier batch **`app.bat`** est déjà configuré pour fonctionner avec :

- Une carte **ESP32 Lolin S2 Mini**.
- Le port série **COM4**.

Tout est déjà renseigné, donc vous n'avez normalement rien à changer. Cependant, si vous souhaitez modifier la carte ou le port série, vous pouvez consulter la documentation officielle de **Arduino CLI** pour les instructions sur la configuration de la commande de compilation et d'upload :

- [Installation et configuration d'arduino-cli](https://arduino.github.io/arduino-cli/1.1/installation/)

### **Modifier les paramètres dans `app.bat`** :

1. Ouvrez **`app.bat`** dans un éditeur de texte (comme Notepad).
2. Si nécessaire, vous pouvez ajuster :
   - **`--fqbn esp32:esp32:lolin_s2_mini`** : Remplacez par la configuration de votre carte.
   - **`-p COM4`** : Remplacez par le port série de votre carte.

---

## **Dépannage**

- Si Python ou yEd ne sont pas correctement configurés, suivez les étapes d'installation dans les sections précédentes.
- Vérifiez que votre fichier `.xgml` est valide et correctement sélectionné lors de l'exécution de `app.bat`.
- Si vous rencontrez des erreurs liées à la compilation ou au téléversement, assurez-vous que le bon port et la bonne carte sont configurés dans **`app.bat`**.

---

## **Contributions**

Les contributions à ce projet sont les bienvenues. Si vous souhaitez proposer des améliorations ou signaler des problèmes, n'hésitez pas à ouvrir une issue ou une pull request.

---

## **Licence**

Ce projet est sous licence [MIT](LICENSE).
