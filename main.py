import xml.etree.ElementTree as ET # pour lire le xml
import re # Pour les regex

# Dictionnaire de fonction
keyword_to_function = {
    # "in": "out"
    "Attend": "ATTEND",
    "AllumeLED": "ALLUME_LED",
    "EteintLED": "ETEINT_LED",
    "Stop" : "stop",
    "Avance" : "avance",
}

# Unités de temps et leurs multiplicateurs
time_units = {
    "s": 1000,   # Secondes → Millisecondes
    "ms": 1      # Millisecondes → Millisecondes
}

def interpret_init_variable(node_label):
    match = re.match(r"([a-zA-Z0-9_]+)\s*=\s*(.+)", node_label)
    if match:
        variable = match.group(1)  # Le nom de la variable
        value = match.group(2)     # La valeur après '='
        
        # Détection du type
        if value.strip() in ["True", "False"]:
            var_type = "bool"
        elif value.strip().isdigit():
            var_type = "int"
        else:
            var_type = "auto"  # Par défaut, on utilise 'auto' pour d'autres types

        return f"{var_type} {variable} = {value.strip().lower()};\n"
    
def interpret_variable(node_label):
    match = re.match(r"([a-zA-Z0-9_]+)\s*=\s*(.+)", node_label)
    if match:
        variable = match.group(1)  # Le nom de la variable
        value = match.group(2)     # La valeur après '='
        return f"{variable} = {value.strip()};\n"


# Fonction pour interpréter les commandes spéciales avec macros
def interpret_command_with_macros(node_label):
    # Vérification de la syntaxe 'variable ='
    result = interpret_variable(node_label)
    if result:
        return result  # Si interpret_variable retourne quelque chose, on le retourne directement
    
    
    parts = node_label.split()
    command = parts[0]
    params = parts[1:] if len(parts) > 1 else []
    
    if command in keyword_to_function:
        macro = keyword_to_function[command]
        
        if macro == "ATTEND" and params:
            match = re.match(r"(\d+)([a-zA-Z]+)", params[0])
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                multiplier = time_units.get(unit, 1)
                value *= multiplier
                return f"{macro}({value});"
        
        elif macro in ["ALLUME_LED", "ETEINT_LED"] and len(params) >= 1:
            pin = params[0]
            return f"{macro}({pin});"
        
        elif macro in ["stop", "avance"]:
            return f"{macro}();"
    
    return f"// Commande inconnue: {node_label}"

# ========================================================================================
# Analyse du XML
# ========================================================================================

if __name__ == "__main__":
    # Charger et analyser le fichier XML
    tree = ET.parse('shema1.xgml')
    root = tree.getroot()

    # Trouver la section principale du graphe
    graph = root.find("./section[@name='graph']")

    # Trouver toute les boites et les fleches
    nodes = graph.findall("./section[@name='node']")
    edges = graph.findall("./section[@name='edge']")

    # Catégoriser les nœudsboites
    setup_nodes = []  # Nœuds de type ellipse
    loop_nodes = {}   # Autres nœuds (dict pour accès rapide par ID)
    diamond_nodes = {}  # Nœuds conditionnels

    for node in nodes:
        node_id = node.find("./attribute[@key='id']").text
        node_label = node.find("./attribute[@key='label']").text
        node_type = node.find("./section[@name='graphics']/attribute[@key='type']").text
        
        if node_type == "ellipse":
            setup_nodes.append((node_id, node_label))
        elif node_type == "diamond":
            diamond_nodes[node_id] = node_label
        else:
            loop_nodes[node_id] = node_label

    # Créer les connexions pour le loop
    connections = {}
    for edge in edges:
        source = edge.find("./attribute[@key='source']").text
        target = edge.find("./attribute[@key='target']").text
        label = edge.find("./attribute[@key='label']")
        label_text = label.text if label is not None else ""
        if source not in connections:
            connections[source] = []
        connections[source].append((target, label_text))

    # Trouver la première boîte du loop (celle pointée par le setup)
    first_loop_node = None
    if setup_nodes:
        setup_node_id = setup_nodes[0][0]
        for edge in edges:
            if edge.find("./attribute[@key='source']").text == setup_node_id:
                first_loop_node = edge.find("./attribute[@key='target']").text
                break

    # Convertir les ID en entiers pour le switch
    id_to_int = {node_id: index + 1 for index, node_id in enumerate(loop_nodes.keys())}
    id_to_int.update({node_id: index + 1 + len(loop_nodes) for index, node_id in enumerate(diamond_nodes.keys())})

    # ========================================================================================
    # Générer le code Arduino
    # ========================================================================================
    with open('./test/test.ino', 'w') as ino_file:
        ino_file.write("// Macros pour simplifier le code\n")
        ino_file.write("#define ATTEND(ms) delay(ms)\n")
        ino_file.write("#define ALLUME_LED(pin) digitalWrite(pin, HIGH)\n")
        ino_file.write("#define ETEINT_LED(pin) digitalWrite(pin, LOW)\n\n")
    
        ino_file.write(f"int currentState = {id_to_int.get(first_loop_node, 0)};\n\n")
        
        for _, label in setup_nodes:
            ino_file.write(interpret_init_variable(label))
        
        ino_file.write("\nvoid setup() {\n")
        ino_file.write("  Serial.begin(115200);\n")
        ino_file.write("}\n\n")
        
        ino_file.write("void loop() {\n")
        ino_file.write("  Serial.print(\"Etat actuel: \");\n");
        ino_file.write("  Serial.println(currentState);\n\n");
        
        ino_file.write("  switch (currentState) {\n")
        
        # Parcourir les nœuds pour le loop
        for node_id, node_label in loop_nodes.items():
            state_int = id_to_int[node_id]
            ino_file.write(f"    case {state_int}:\n")
            ino_file.write(f"      Serial.println(\"{node_label}\");\n")
            interpreted_command = interpret_command_with_macros(node_label)
            ino_file.write(f"      {interpreted_command}\n")
            if node_id in connections:
                for target, label in connections[node_id]:
                    target_int = id_to_int.get(target, 0)
                    if label:  # Conditionnelle (True/False)
                        ino_file.write(f"      if ({label.lower()}()) {{\n")
                        ino_file.write(f"        currentState = {target_int};\n")
                        ino_file.write("        break;\n")
                        ino_file.write("      }\n")
                    else:  # Transition normale
                        ino_file.write(f"      currentState = {target_int};\n")
                        ino_file.write("      break;\n\n")
            # ino_file.write("      break;\n")
        
        # Gestion des diamonds (conditions)
        for node_id, node_label in diamond_nodes.items():
            state_int = id_to_int[node_id]
            ino_file.write(f"    case {state_int}:\n")
            ino_file.write(f"      Serial.println(\"Condition: {node_label}\");\n")
            if node_id in connections:
                for target, label in connections[node_id]:
                    target_int = id_to_int.get(target, 0)
                    if label == "True":
                        ino_file.write(f"      if ({node_label}) {{ currentState = {target_int};}}\n")
                    elif label == "False":
                        ino_file.write(f"      else {{ currentState = {target_int};}}\n")
            ino_file.write("      break;\n\n")
        
        ino_file.write("    default:\n")
        ino_file.write("      Serial.println(\"Etat inconnu\");\n")
        ino_file.write(f"      currentState = {id_to_int.get(first_loop_node, 0)};\n")
        ino_file.write("      break;\n")
        
        ino_file.write("  }\n")
        ino_file.write("}\n")

    print("Le fichier 'test.ino' a été créé avec succès.")
