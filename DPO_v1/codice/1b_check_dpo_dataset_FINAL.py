import pandas as pd
import json

# ==========================================
#  CONFIGURAZIONE
# ==========================================
INPUT_FILE = "dpo_dataset_ready.jsonl"
OUTPUT_FILE = "dpo_dataset_CLEANED.jsonl"

print(f"Avvio analisi e pulizia su: {INPUT_FILE}\n")

try:
    # 1. CARICAMENTO ROBUSTO
    df = pd.read_json(INPUT_FILE, lines=True)
    
    initial_count = len(df)
    print(f"Righe totali: {initial_count}")

    # ==========================================
    # 2. PULIZIA DATI
    # ==========================================
    
    df_clean = df.dropna(subset=['chosen', 'rejected'])
    
    # Rimuoviamo righe dove le stringhe sono vuote o contengono solo spazi
    df_clean = df_clean[
        (df_clean['chosen'].str.strip().astype(bool)) & 
        (df_clean['rejected'].str.strip().astype(bool))
    ]
    
    final_count = len(df_clean)
    dropped_count = initial_count - final_count

    # ==========================================
    # 3. CONTROLLO QUALITÀ (SHOWCASE)
    # ==========================================
    print(f"\n ESTRAGGO 3 ESEMPI CASUALI PER VERIFICA:\n")
    
    if not df_clean.empty:
        # Prende 3 righe a caso dal mazzo
        samples = df_clean.sample(n=min(3, len(df_clean))) 
        
        for i, (index, row) in enumerate(samples.iterrows()):
            print(f" ESEMPIO RANDOM {i+1}")
            print(f" CHOSEN (Divertente): {row['chosen']}")
            print(f" REJECTED (Noiosa):   {row['rejected']}")
            print("-" * 60)
    else:
        print(" Attenzione: Il dataset è vuoto dopo la pulizia!")

    # ==========================================
    #  4. SALVATAGGIO FINALE
    # ==========================================
    if not df_clean.empty:
        df_clean.to_json(OUTPUT_FILE, orient='records', lines=True)
        print(f"\n PULIZIA COMPLETATA CON SUCCESSO!")
        print(f"   Originali: {initial_count}")
        print(f"   Valide:    {final_count}")
        print(f"   Scartate:  {dropped_count}")
        print(f" File pronto per il training salvato in: {OUTPUT_FILE}")
    else:
        print("\n ERRORE: Non c'è nulla da salvare.")

except ValueError:
    print(" ERRORE: Il file JSONL sembra malformato. Controlla che sia un JSONL valido.")
except FileNotFoundError:
    print(f" ERRORE: Non trovo il file '{INPUT_FILE}'. Assicurati che sia nella cartella.")
except Exception as e:
    print(f" ERRORE IMPREVISTO: {e}")