from collections import defaultdict

# Nome del file di input
input_file = "progetto mics/id_list.txt"

# Dizionario per memorizzare ID e i rispettivi file associati
id_to_files = defaultdict(list)

# Leggere il file e popolare il dizionario
with open(input_file, "r") as f:
    for line in f:
        if ": " in line:
            filename, activity_id = line.strip().split(": ")
            id_to_files[activity_id].append(filename)

# Filtrare solo gli ID ripetuti
repeated_ids = {k: v for k, v in id_to_files.items() if len(v) > 1}

# Scrivere il file con nome file e ID ripetuti
with open("file_id_ripetuti.txt", "w") as f:
    for activity_id, filenames in repeated_ids.items():
        for filename in filenames:
            f.write(f"{filename}: {activity_id}\n")

# Scrivere il file con solo i nomi dei file con ID ripetuti
with open("nomi_file_ripetuti.txt", "w") as f:
    for filenames in repeated_ids.values():
        for filename in filenames:
            f.write(f"{filename}\n")

# Scrivere il file con solo gli ID ripetuti
with open("id_ripetuti.txt", "w") as f:
    for activity_id in repeated_ids.keys():
        f.write(f"{activity_id}\n")

print("Elaborazione completata. File generati:")
print("- file_id_ripetuti.txt")
print("- nomi_file_ripetuti.txt")
print("- id_ripetuti.txt")
