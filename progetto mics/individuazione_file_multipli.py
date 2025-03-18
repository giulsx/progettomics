import os
import shutil

# Percorsi delle cartelle
source_dir = "progetto mics/output copy"  # Cartella sorgente
destination_dir = "progetto mics/output multipli"  # Cartella di destinazione
file_list = "nomi_file_ripetuti.txt"  # File contenente i nomi dei file da copiare

# Creazione della cartella di destinazione se non esiste
os.makedirs(destination_dir, exist_ok=True)

# Leggere i nomi dei file dal file di testo
with open(file_list, "r") as f:
    filenames = [line.strip() for line in f]

# Copiare i file dalla cartella "output" a "output multipli"
for filename in filenames:
    src_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(destination_dir, filename)
    
    if os.path.exists(src_path):  # Controlla se il file esiste nella cartella "output"
        shutil.copy2(src_path, dest_path)  # Copia mantenendo i metadati
        print(f"Copiato: {filename}")
    else:
        print(f"File non trovato: {filename}")

print("Copia completata!")
