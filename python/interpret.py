import re  # Pour les regex

# Dictionnaire de fonction
keyword_to_function = {
    # fonction ardunio :
    "Attendre": "ATTENDRE",
    "Allumer": "ALLUMER",  # (digital)
    "Eteindre": "ETEINDRE",  # (digital)
    "Lire": "LIRE",  # (digital)
    "Buzz": "BUZZ",  # (digital)
    # fonction custom :
    "Stop": "stop",
    "Avance": "avance",
}

# Unités de temps et leurs multiplicateurs
time_units = {
    "s": 1000,  # Secondes → Millisecondes
    "ms": 1,  # Millisecondes → Millisecondes
}

sensors = []


def interpret_assignment_opperator(node_label):

    match = re.search(r"([a-zA-Z0-9_]+)\s*(=|\+=|-=|\*=|/=|%=)\s*(.+)", node_label)
    if match:
        variable = match.group(1)  # Le nom de la variable
        opperator = match.group(2)
        value = match.group(3)  # La valeur après '='
        return f"{variable} {opperator} {value}"

    # TODO lever l'erreur dans le else


def interpret_test_opperator(node_label):

    match = re.search(r"([a-zA-Z0-9_]+)\s*(==|<=|>=|<|>|!=)\s*(.+)", node_label)
    if match:
        variable = match.group(1)  # Le nom de la variable
        if variable in sensors:
            variable = f"distance({variable})"
        opperator = match.group(2)
        value = match.group(3)  # La valeur après '='
        return f"{variable} {opperator} {value}"


# Fonction pour interpréter les commandes spéciales avec macros
def interpret_command_with_macros(node_label):
    # Vérification de la syntaxe 'variable ='
    result = interpret_assignment_opperator(node_label)
    if result:
        return (
            result + ";\n"
        )  # Si interpret_variable retourne quelque chose, on le retourne directement

    parts = node_label.split()
    command = parts[0]
    params = parts[1:] if len(parts) > 1 else []

    if command in keyword_to_function:
        macro = keyword_to_function[command]

        if macro == "ATTENDRE" and params:
            match = re.match(r"(\d+)([a-zA-Z]+)", params[0])
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                multiplier = time_units.get(unit, 1)
                value *= multiplier
                return f"{macro}({value});"

        elif macro in ["ALLUMER", "ETEINDRE", "BUZZ"] and len(params) >= 1:
            pin = params[1] if params[0].lower() == "pin" else params[0]
            return f"{macro}({pin});"

        elif macro in ["stop", "avance"]:
            return f"{macro}();"
    else:
        print(f"[Warning] Commande inconnue: {node_label}")
        return f"// Commande inconnue: {node_label}"


def interpret_condition(node_label):
    # Vérifier si c'est une assignation ou une opération
    condition = interpret_test_opperator(node_label)
    if condition:
        return condition  # Retirer le point-virgule pour une condition

    # Vérifier si c'est une macro de commande
    parts = node_label.split()
    command = parts[0]
    params = parts[1:] if len(parts) > 1 else []

    if command in keyword_to_function:
        macro = keyword_to_function[command]
        if macro == "LIRE" and len(params) >= 1:
            pin = params[1] if params[0].lower() == "pin" else params[0]
            return f"{macro}({pin})"

    # Par défaut, renvoyer tel quel
    return node_label


def search_pinMode(basic_nodes, condition_nodes):
    commandList = []

    for node_id, node_label in basic_nodes.items():
        parts = node_label.split()
        command = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        if command in keyword_to_function:
            macro = keyword_to_function[command]

            if macro in ["ALLUMER", "ETEINDRE", "BUZZ"] and len(params) >= 1:
                pin = params[1] if params[0].lower() == "pin" else params[0]
                command = f"  pinMode({pin}, OUTPUT);\n"
                if not command in commandList:
                    commandList.append(command)

    for node_id, node_label in condition_nodes.items():
        parts = node_label.split()
        command = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        if command in keyword_to_function:
            macro = keyword_to_function[command]

            if macro == "LIRE" and len(params) >= 1:
                pin = params[1] if params[0].lower() == "pin" else params[0]
                command = f"  pinMode({pin}, INPUT_PULLUP);\n"
                if not command in commandList:
                    commandList.append(command)

    return commandList


def interpret_init_variable(setup_nodes):
    codesList = []
    pinModes = []

    for node_id, node_label in setup_nodes.items():
        parts = node_label.split(",")
        params = [p.strip() for p in parts]
        match = re.match(r"([a-zA-Z0-9_]+)\s*=\s*(.+)", node_label)

        if params[0].lower().startswith("ultrason") and len(params) >= 3:
            match_name = re.search(
                r"Ultrason\s+([a-zA-Z0-9_]+)", params[0], re.IGNORECASE
            )
            if match_name:
                sensorName = match_name.group(1)
                sensors.append(sensorName)
            else:
                print(f"[Warning] Nom de capteur manquant dans '{node_label}'")
                continue

            # Récupérer les broches Trig et Echo
            trigPin = None
            echoPin = None

            for param in params[1:]:
                if param.lower().startswith("trig"):
                    trigPin = int(re.search(r"\d+", param).group())
                elif param.lower().startswith("echo"):
                    echoPin = int(re.search(r"\d+", param).group())

            # Vérification et ajout des commandes si tout est OK
            if trigPin is not None and echoPin is not None:
                codesList.append(
                    f"struct Sensor {sensorName} = {{ {trigPin}, {echoPin} }};\n"
                )
                pinModes.append(
                    f"  pinMode({trigPin}, OUTPUT);\n  pinMode({echoPin}, INPUT);\n"
                )
            else:
                print(
                    f"[Warning] Paramètres 'Trig' ou 'Echo' manquants dans '{node_label}'"
                )

        elif match:
            variable = match.group(1)  # Le nom de la variable
            value = match.group(2)  # La valeur après '='

            # Détection du type
            if value.strip() in ["True", "False"]:
                var_type = "bool"
            elif value.strip().isdigit():
                var_type = "int"
            else:
                var_type = "auto"  # Par défaut, on utilise 'auto' pour d'autres types

            codesList.append(f"{var_type} {variable} = {value.strip().lower()};\n")

        else:
            # Si aucune cas correspond
            print(
                f'[Warning] "{node_label}" n\'a pas etait compris et donc non compilé\n'
            )

    return codesList, pinModes
