import pandas as pd
import numpy as np
import os

# === 1. CONFIGURAZIONE ===
# Usiamo i sample da 10000 originali per coerenza scientifica
base_path = r"C:\Users\lipar\OneDrive\Desktop\Progetto_NLP_PULITO\PPO_v1\model_checkpoints\sample10000" 
base_path2 = r"C:\Users\lipar\OneDrive\Desktop\Progetto_NLP_PULITO\DPO_v2\model_checkpoints" 

data_files = {
    "llama3": os.path.join(base_path, "categoriz_short_sample10000_llama3.csv"),
    "mistral": os.path.join(base_path, "categoriz_short_sample10000_mistral.csv"),
    "gemma": os.path.join(base_path, "categoriz_short_sample10000_gemma.csv"),
    "gpt_oss": os.path.join(base_path2, "categoriz_short_sample10000_gpt_oss.csv"),
    "phi_4": os.path.join(base_path2, "categoriz_short_sample10000_phi4.csv")
}

# Categorie Gold 
categories = ["Wordplay", "Cultural Reference"]

# === 2. CARICAMENTO E MERGE  ===
try:
    df_dict = {}
    for model, path in data_files.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            
            # --- LOGICA DI RINOMINAZIONE ROBUSTA ---
            rename_map = {}
            for col in df.columns:
                for cat in categories:
                    if cat in col:
                        # Rinomina nel formato standard atteso dal Borda: "nomeModello_Categoria"
                        rename_map[col] = f"{model}_{cat}"
            df.rename(columns=rename_map, inplace=True)
            # ---------------------------------------
            
            df_dict[model] = df
        else:
            raise FileNotFoundError(f"File mancante: {path}")

    # 1. Prendiamo il primo DataFrame come base (che contiene già il testo)
    merged_df = df_dict["llama3"].copy()
    text_col = "jokeText" if "jokeText" in merged_df.columns else "text"
    
    # 2. Incolliamo le colonne degli altri modelli basandoci sull'INDICE (stesso ordine di righe)
    for model_name in ["mistral", "gemma", "gpt_oss", "phi_4"]:
        df_temp = df_dict[model_name]
        
        # Prendiamo solo le colonne dei voti (che iniziano col nome del modello) per non duplicare il testo
        cols_to_keep = [c for c in df_temp.columns if c.startswith(f"{model_name}_")]
        
        # Unione tramite indice (.join)
        merged_df = merged_df.join(df_temp[cols_to_keep])

    print(f"Merge completato. Totale battute: {len(merged_df)}")

except Exception as e:
    print(f"Errore: {e}")
    exit()


# === 3. CALCOLO BORDA RANKING ===
def compute_lpr_borda_rank(df, category, model_names):
    cols = [f"{m}_{category}" for m in model_names]
    # Rank 1 = Voto più alto (migliore battuta)
    ranks = df[cols].rank(axis=0, method='min', ascending=False)
    # Somma dei ranghi: più è bassa, più c'è consenso sulla qualità
    return ranks.sum(axis=1)

# Calcoliamo il ranking Borda per le categorie target
for cat in categories:
    merged_df[f"{cat}_Borda_Rank_Sum"] = compute_lpr_borda_rank(merged_df, cat, list(data_files.keys()))

# Rank finale globale basato sulla somma dei ranghi Borda
merged_df['Global_Borda_Rank'] = (merged_df['Wordplay_Borda_Rank_Sum'] + 
                                  merged_df['Cultural Reference_Borda_Rank_Sum']).rank(method='min')

# === 4. APPLICAZIONE PESATURA LPR_new (La richiesta del Prof) ===
# Formula: 10 * (1 - (Rank - 1) / (N - 1))
N = len(merged_df)
merged_df['LPR_new'] = 10 * (1 - (merged_df['Global_Borda_Rank'] - 1) / (N - 1))

merged_df = merged_df.sort_values(by='LPR_new', ascending=False)

# === 5. SALVATAGGIO PER DPO v2 ===
# Questo file servirà per addestrare DeBERTa v2
output_file = "dataset_LPR_new_DPO_v2_1.csv"
merged_df[[text_col, 'LPR_new', 'Global_Borda_Rank']].to_csv(output_file, index=False)

print(f"Dataset DPO v2 con pesatura LPR_new generato: {output_file}")
print(f"Migliore battuta (Rank 1) Score: {merged_df['LPR_new'].max()}")
print(f"Peggiore battuta (Rank N) Score: {merged_df['LPR_new'].min()}")