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

# Filtrare solo gli ID che compaiono esattamente una volta
unique_ids = {k: v for k, v in id_to_files.items() if len(v) == 1}

# Scrivere il file con nome file e ID unici
with open("file_id_unici.txt", "w") as f:
    for activity_id, filenames in unique_ids.items():
        for filename in filenames:
            f.write(f"{filename}: {activity_id}\n")

# Scrivere il file con solo i nomi dei file con ID unici
with open("nomi_file_unici.txt", "w") as f:
    for filenames in unique_ids.values():
        for filename in filenames:
            f.write(f"{filename}\n")

# Scrivere il file con solo gli ID unici
with open("id_unici.txt", "w") as f:
    for activity_id in unique_ids.keys():
        f.write(f"{activity_id}\n")

print("Elaborazione completata. File generati:")
print("- file_id_unici.txt")
print("- nomi_file_unici.txt")
print("- id_unici.txt")
