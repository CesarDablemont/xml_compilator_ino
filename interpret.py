import re  # Pour les regex

# Dictionnaire de fonction
keyword_to_function = {
    # fonction ardunio :
    "Attendre": "ATTENDRE",
    "Allumer": "ALLUMER",  # (digital)
    "Eteindre": "ETEINDRE",  # (digital)
    "Lire": "LIRE",  # (digital)
    # fonction custom :
    "Stop": "stop",
    "Avance": "avance",
}

# Unités de temps et leurs multiplicateurs
time_units = {
    "s": 1000,  # Secondes → Millisecondes
    "ms": 1,  # Millisecondes → Millisecondes
}


def interpret_init_variable(node_label):
    stripped_label = node_label.strip().strip('"')
    if stripped_label == "Debut":
        return "// Pas de variable a initialiser ici : Debut\n"

    match = re.match(r"([a-zA-Z0-9_]+)\s*=\s*(.+)", node_label)
    if match:
        variable = match.group(1)  # Le nom de la variable
        value = match.group(2)  # La valeur après '='

        # Détection du type
        if value.strip() in ["True", "False"]:
            var_type = "bool"
        elif value.strip().isdigit():
            var_type = "int"
        else:
            var_type = "auto"  # Par défaut, on utilise 'auto' pour d'autres types

        return f"{var_type} {variable} = {value.strip().lower()};\n"

    # Si aucune cas correspond
    return ValueError('{node_label} si tu n\'a rien a mettre met  "Debut"\n')


def interpret_variable(node_label):
    match = re.search(r"([a-zA-Z0-9_]+)\s*(=|\+=|-=|\*=|/=|%=)\s*(.+)", node_label)
    if match:
        variable = match.group(1)  # Le nom de la variable
        opperator = match.group(2)
        value = match.group(3)  # La valeur après '='
        return f"{variable} {opperator} {value}"


# Fonction pour interpréter les commandes spéciales avec macros
def interpret_command_with_macros(node_label):
    # Vérification de la syntaxe 'variable ='
    result = interpret_variable(node_label)
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

        elif macro in ["ALLUMER", "ETEINDRE"] and len(params) >= 2:
            pin = params[1] if params[0].lower() == "pin" else params[0]
            return f"{macro}({pin});"

        elif macro in ["stop", "avance"]:
            return f"{macro}();"

    return f"// Commande inconnue: {node_label}"


def interpret_condition(node_label):
    # Vérifier si c'est une assignation ou une opération
    condition = interpret_variable(node_label)
    if condition:
        return condition  # Retirer le point-virgule pour une condition

    # Vérifier si c'est une macro de commande
    parts = node_label.split()
    command = parts[0]
    params = parts[1:] if len(parts) > 1 else []

    if command in keyword_to_function:
        macro = keyword_to_function[command]
        if macro == "LIRE" and len(params) >= 2:
            pin = params[1] if params[0].lower() == "pin" else params[0]
            return f"{macro}({pin})"

    # Par défaut, renvoyer tel quel
    return node_label


def search_pinMode(loop_nodes, diamond_nodes):
    commandList = []

    for node_id, node_label in loop_nodes.items():
        parts = node_label.split()
        command = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        if command in keyword_to_function:
            macro = keyword_to_function[command]

            if macro in ["ALLUMER", "ETEINDRE"] and len(params) >= 2:
                pin = params[1] if params[0].lower() == "pin" else params[0]
                command = f"  pinMode({pin}, OUTPUT);\n"
                if not command in commandList:
                    commandList.append(command)

    for node_id, node_label in diamond_nodes.items():
        parts = node_label.split()
        command = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        if command in keyword_to_function:
            macro = keyword_to_function[command]

            if macro == "LIRE" and len(params) >= 2:
                pin = params[1] if params[0].lower() == "pin" else params[0]
                command = f"  pinMode({pin}, INPUT_PULLUP);\n"
                if not command in commandList:
                    commandList.append(command)

    return commandList
