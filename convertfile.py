import tkinter as tk
from tkinter import filedialog
import os
import datetime

def read_schema(schema_file_path):
    attributes = {}
    rules = {}
    current_section = None

    with open(schema_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("#"):
                if "Attributes" in line:
                    current_section = "attributes"
                elif "Rules" in line:
                    current_section = "rules"
            elif current_section == "attributes" and ':' in line:
                name, attr_type = line.split(':')
                attributes[name.strip()] = attr_type.strip()
            elif current_section == "rules" and ':' in line:
                # Assuming rules indicate classification
                name, rule = line.split(':', 1)
                rules[name.strip()] = rule.strip()

    return attributes, rules

def convert_to_arff(dat_file_path, attributes, rules):
    with open(dat_file_path, 'r') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        data_values = line.strip().split()

        # Check if rules are present, indicating classification
        is_classification = bool(rules)
        if is_classification:
            # Example rule application (for illustration, adjust as needed)
            faults = int(data_values[-1])  # Assuming 'FAULTS' is the last column
            class_label = 'nfp' if faults < 3 else 'fp'
            data_values.append(class_label)  # Append class label

        processed_line = ','.join(data_values)
        processed_lines.append(processed_line)

    arff_file_path = dat_file_path.replace('.dat', '.arff')
    with open(arff_file_path, 'w') as file:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        file.write(f"% Title: Dataset\n% Author: Spencer Goldberg\n% Date: {current_date}\n\n")
        file.write('@relation data\n\n')
        for attr, attr_type in attributes.items():
            file.write(f'@attribute {attr} {attr_type}\n')
        if is_classification:
            file.write('@attribute class {nfp, fp}\n')
        file.write('\n@data\n')
        file.write('\n'.join(processed_lines))

    return arff_file_path

def process_folder():
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory()
    if not folder_path:
        print("No folder selected")
        root.destroy()
        return

    print(f"Selected folder: {folder_path}")

    schema_file_path = os.path.join(folder_path, 'schema.txt')
    if not os.path.exists(schema_file_path):
        print("schema.txt not found in the folder")
        root.destroy()
        return

    attributes, rules = read_schema(schema_file_path)

    try:
        for filename in ['fit.dat', 'test.dat']:
            dat_file_path = os.path.join(folder_path, filename)
            if os.path.exists(dat_file_path):
                result = convert_to_arff(dat_file_path, attributes, rules)
                if result.endswith('.arff'):
                    print(f"Converted {filename} to {result.split('/')[-1]}")
                else:
                    print("Conversion failed for:", filename)
            else:
                print(f"File not found: {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

    root.destroy()

if __name__ == "__main__":
    process_folder()
