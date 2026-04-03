import pandas as pd
import requests
import json
from tqdm import tqdm
import os

# =========================
# CONFIG
# =========================

MODEL_NAME = "phi4" 
USE_SAMPLE = True
DATASET_PATH = "shortjokes.csv"  
OUTPUT_FILE = f"categoriz_short_sample10000_{MODEL_NAME}.csv"

# =========================
# DATASET & RESUME LOGIC 
# =========================

print(f"--- AVVIO SCRIPT PER {MODEL_NAME} ---")

# 1. Controllo se esiste già un salvataggio parziale
if os.path.exists(OUTPUT_FILE):
    print(f" Trovato file di salvataggio: {OUTPUT_FILE}")
    print(" Carico i progressi e RIPRENDO da dove eri rimasto...")
    df = pd.read_csv(OUTPUT_FILE)
else:
    print("Nessun salvataggio trovato. Inizio da ZERO.")
    # Caricamento Originale
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("ERRORE: File csv non trovato. Controlla il nome o la cartella.")
        exit()

    if "Joke" in df.columns:
        df.rename(columns={"Joke": "jokeText"}, inplace=True)

    if USE_SAMPLE:
        df = df.sample(n=10000, random_state=42).reset_index(drop=True)
        print("Campione di 10.000 battute selezionato.")

# =========================
# CATEGORIES & INIT
# =========================

categories = {
    "Edgy Content": "Sex, taboos, death, shock",
    "Cultural Reference": "Politics, celebrities, pop culture",
    "Wordplay": "Puns, linguistic ambiguity",
    "Absurdity": "Illogical logic, surrealism, nonsense",
    "Relatable": "Everyday life, technology, relationships, self-irony",
    "Offensive Humor": "Insult, stereotypes, racism, sarcasm"
}

# Inizializza colonne SOLO se non esistono (fondamentale per il resume!)
for cat in categories:
    col_name = f"{MODEL_NAME}_{cat}"
    if col_name not in df.columns:
        df[col_name] = None

# =========================
# OLLAMA CALL (Chat Mode)
# =========================

def ask_ollama(prompt):
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "format": "json", 
        "stream": False,
        "options": {
            "temperature": 0.0, # Bassa temperatura per coerenza
            "num_ctx": 4096
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return None

# =========================
# CLASSIFICATION LOOP
# =========================

print(f"Inizio classificazione con {MODEL_NAME}...")

# Usiamo iterrows per controllare riga per riga
for idx, row in tqdm(df.iterrows(), total=df.shape[0]):

    # === CONTROLLO SALTO (RESUME) ===
    # Controlliamo se la prima categoria è già stata votata. Se sì, saltiamo.
    check_col = f"{MODEL_NAME}_Wordplay" # Una categoria a caso
    if pd.notna(row[check_col]) and str(row[check_col]) != "":
        continue
    # ================================

    joke = row['jokeText']
    
    category_list = "\n".join([f'- "{cat}": {desc}' for cat, desc in categories.items()])

    prompt = f""" You are a humor expert and researcher.
    
    For the following joke, rate from 0 to 10 how much it fits each category.

    Categories: {category_list}

    Joke:  \"\"\"{joke}\"\"\"

    Respond ONLY in this exact JSON format:

    {{
        "Edgy Content": 0,
        "Cultural Reference": 0,
        "Wordplay": 0,
        "Absurdity": 0,
        "Relatable": 0,
        "Offensive Humor": 0
    }}  
    """

    try:
        output = ask_ollama(prompt)

        if output:
            scores = json.loads(output)
            for cat in categories:
                df.at[idx, f"{MODEL_NAME}_{cat}"] = scores.get(cat, None)
        else:
            pass

    except json.JSONDecodeError:
        print(f"JSON Error riga {idx}")
    except Exception as e:
        print(f"Generic Error riga {idx}: {e}")

    # Salvataggio intermedio frequente (ogni 50) sul file corretto
    if idx % 50 == 0:
        df.to_csv(OUTPUT_FILE, index=False)

# =========================
# SAVE FINAL
# =========================

df.to_csv(OUTPUT_FILE, index=False)
print(f"Finito! File salvato: {OUTPUT_FILE}")