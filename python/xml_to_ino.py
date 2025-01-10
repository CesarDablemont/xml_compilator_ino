import xml.etree.ElementTree as ET  # pour lire le xml
import interpret  # ficher local

# ========================================================================================
# Analyse du XML
# ========================================================================================


def xml_to_ino(xml_file_path):
    # Charger et analyser le fichier XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Trouver la section principale du graphe
    graph_section = root.find("./section[@name='graph']")

    # Trouver toute les boites et les fleches
    nodes = graph_section.findall("./section[@name='node']")
    edges = graph_section.findall("./section[@name='edge']")

    # Catégoriser les nœudsboites
    start_nodes = []  # Nœuds de type ellipse
    setup_nodes = {}  # Nœuds de type hexagon
    basic_nodes = {}  # Autres nœuds (dict pour accès rapide par ID)
    condition_nodes = {}  # Nœuds conditionnels

    for node in nodes:
        node_id = node.find("./attribute[@key='id']").text
        node_label = node.find("./attribute[@key='label']").text
        node_type = node.find("./section[@name='graphics']/attribute[@key='type']").text

        if node_type == "ellipse":
            start_nodes.append((node_id, node_label))
        elif node_type == "hexagon":
            setup_nodes[node_id] = node_label
        elif node_type == "diamond":
            condition_nodes[node_id] = node_label
        elif node_type == "rectangle":
            basic_nodes[node_id] = node_label
        else:
            print(f'[Warning] le blocs de type: "{node_type}" non gére !')

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

    # Trouver la première boîte du loop (celle pointée par l'ellipse)
    first_loop_node = None
    if start_nodes:
        start_nodes_id = start_nodes[0][0]
        for edge in edges:
            if edge.find("./attribute[@key='source']").text == start_nodes_id:
                first_loop_node = edge.find("./attribute[@key='target']").text
                break

    # Convertir les ID en entiers pour le switch
    id_to_int = {node_id: index + 1 for index, node_id in enumerate(basic_nodes.keys())}
    id_to_int.update(
        {
            node_id: index + 1 + len(basic_nodes)
            for index, node_id in enumerate(condition_nodes.keys())
        }
    )

    # ========================================================================================
    # Générer le code Arduino
    # ========================================================================================
    with open("./ardunio/ardunio.ino", "w") as ino_file:
        ino_file.write("// Macros pour simplifier le code\n")
        ino_file.write("#define ATTENDRE(ms) delay(ms)\n")
        ino_file.write("#define ALLUMER(pin) digitalWrite(pin, HIGH)\n")
        ino_file.write("#define ETEINDRE(pin) digitalWrite(pin, LOW)\n")
        ino_file.write("#define LIRE(pin) digitalRead(pin)\n")
        ino_file.write("#define BUZZ(pin) tone(pin, 600, 3)\n\n")

        ino_file.write("struct ultrasonSensor {\n")
        ino_file.write("int trig;\n")
        ino_file.write("int echo;\n")
        ino_file.write("};\n\n")

        ino_file.write(f"int currentState = {id_to_int.get(first_loop_node, 0)};\n")

        setupCodes, pinModes = interpret.interpret_init_variable(setup_nodes)
        for command in setupCodes:
            ino_file.write(command)

        ino_file.write("\nvoid setup() {\n")
        ino_file.write("  Serial.begin(115200);\n\n")

        # trouver et ecrire les pinModes dans le setup
        pinModes += interpret.search_pinMode(basic_nodes, condition_nodes)
        for command in pinModes:
            ino_file.write(command)

        ino_file.write("}\n\n")

        ino_file.write("void loop() {\n")
        ino_file.write('  Serial.print("Etat actuel: ");\n')
        ino_file.write("  Serial.println(currentState);\n\n")

        ino_file.write("  switch (currentState) {\n")

        # Parcourir les nœuds pour le loop
        for node_id, node_label in basic_nodes.items():
            state_int = id_to_int[node_id]
            ino_file.write(f"    case {state_int}:\n")
            ino_file.write(f'      Serial.println("{node_label}");\n')
            interpreted_command = interpret.interpret_basic_command(node_label)
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
        for node_id, node_label in condition_nodes.items():
            interpert_node = interpret.interpret_condition(node_label)
            if not interpert_node:
                raise SyntaxError('Condition non autorisé: "{node_label}"')

            state_int = id_to_int[node_id]
            ino_file.write(f"    case {state_int}:\n")
            ino_file.write(f'      Serial.println("Condition: {node_label}");\n')
            if node_id in connections:
                true_connection = None
                false_connection = None

                for target, label in connections[node_id]:
                    target_int = id_to_int.get(target, 0)
                    if label == "True":
                        true_connection = f"      if ({interpert_node}) {{ currentState = {target_int};}}\n"
                    elif label == "False":
                        false_connection = (
                            f"      else {{ currentState = {target_int};}}\n"
                        )

                # Écriture dans le bon ordre
                if true_connection:
                    ino_file.write(true_connection)
                if false_connection:
                    ino_file.write(false_connection)
            ino_file.write("      break;\n\n")

        ino_file.write("    default:\n")
        ino_file.write('      Serial.println("Etat inconnu");\n')
        ino_file.write(f"      currentState = {id_to_int.get(first_loop_node, 0)};\n")
        ino_file.write("      break;\n")

        ino_file.write("  }\n")
        ino_file.write("}\n")
        ino_file.close()

    print("Le fichier 'ardunio.ino' a été créé avec succès.")
