import pandas as pd
import requests
import json
from tqdm import tqdm

# =========================
# CONFIG
# =========================

MODEL_NAME = "command-r"
USE_SAMPLE = True
DATASET_PATH = "shortjokes.csv"  

# =========================
# DATASET
# =========================

df = pd.read_csv(DATASET_PATH)

if "Joke" in df.columns:
    df.rename(columns={"Joke": "jokeText"}, inplace=True)

if USE_SAMPLE:
    df = df.sample(n=10000, random_state=42).reset_index(drop=True)

# =========================
# CATEGORIES
# =========================

categories = {
    "Edgy Content": "Sex, taboos, death, shock",
    "Cultural Reference": "Politics, celebrities, pop culture",
    "Wordplay": "Puns, linguistic ambiguity",
    "Absurdity": "Illogical logic, surrealism, nonsense",
    "Relatable": "Everyday life, technology, relationships, self-irony",
    "Offensive Humor": "Insult, stereotypes, racism, sarcasm"
}

# inizializza colonne
for cat in categories:
    df[f"{MODEL_NAME}_{cat}"] = None

# =========================
# OLLAMA CALL
# =========================

def ask_ollama(prompt):
    # Usiamo l'endpoint CHAT, non GENERATE. Command-R è un modello chat.
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "format": "json",  # <--- FONDAMENTALE: Forza l'output JSON puro
        "stream": False,
        "options": {
            "temperature": 0.0, # Perfetto
            # "num_predict": 200 # Puoi toglierlo o lasciarlo, Command-R gestisce bene la lunghezza
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=300) # Timeout lungo ok
        response.raise_for_status() # Lancia errore se c'è (es. 404 o 500)
        
        # Con l'endpoint chat, la risposta è dentro ['message']['content']
        return response.json()["message"]["content"]
        
    except Exception as e:
        print(f"Ollama error: {e}")
        return None

# =========================
# CLASSIFICATION LOOP
# =========================

for idx, joke in tqdm(enumerate(df["jokeText"]), total=len(df)):

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
            # Command-R con format='json' di solito risponde PULITO.
            # Ma per sicurezza, usiamo json.loads direttamente.
            scores = json.loads(output) 

            for cat in categories:
                # Usa .get con default 0 o None
                df.at[idx, f"{MODEL_NAME}_{cat}"] = scores.get(cat, None)
        else:
            print(f"Null output at index {idx}")

    except json.JSONDecodeError:
        print(f"JSON Parsing error at index {idx}: Output was -> {output}")
    except Exception as e:
        print(f"Generic Error at index {idx}: {e}")

    if idx % 100 == 0 and idx > 0:
        df.to_csv("results_partial.csv", index=False)
        print("Checkpoint saved")

# =========================
# SAVE
# =========================

df.to_csv("results_command_r_35b.csv", index=False)

print("DONE")
