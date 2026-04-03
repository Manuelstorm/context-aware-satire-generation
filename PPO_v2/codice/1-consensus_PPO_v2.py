import pandas as pd
import numpy as np
import os

# === 1. CONFIGURAZIONE ===
# Usiamo i sample da 10000 originali per coerenza scientifica
base_path = r"C:\Users\lipar\OneDrive\Desktop\Progetto_NLP_PULITO\PPO_v1\model_checkpoints\sample10000" 

data_files = {
    "llama3": os.path.join(base_path, "categoriz_short_sample10000_llama3.csv"),
    "mistral": os.path.join(base_path, "categoriz_short_sample10000_mistral.csv"),
    "gemma": os.path.join(base_path, "categoriz_short_sample10000_gemma.csv"),
}

# Categorie Gold 
categories = ["Wordplay", "Cultural Reference"]

# === 2. CARICAMENTO E MERGE ===
try:
    df_dict = {}
    for model, path in data_files.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Rinomina colonne
            rename_map = {}
            for cat in categories:
                if cat in df.columns and f"{model}_{cat}" not in df.columns:
                    rename_map[cat] = f"{model}_{cat}"
            df.rename(columns=rename_map, inplace=True)
            df_dict[model] = df
        else:
            raise FileNotFoundError(f"File mancante: {path}")

    dfs = list(df_dict.values())
    merged_df = dfs[0]
    text_col = "jokeText" if "jokeText" in merged_df.columns else "text"
    
    for df_temp in dfs[1:]:
        merged_df = pd.merge(merged_df, df_temp, on=text_col, how="inner")

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

# === 5. SALVATAGGIO PER PPO v2 ===
# Questo file servirà per addestrare DeBERTa v2
output_file = "dataset_LPR_new_PPO_v2.csv"
merged_df[[text_col, 'LPR_new', 'Global_Borda_Rank']].to_csv(output_file, index=False)

print(f"Dataset PPO v2 con pesatura LPR_new generato: {output_file}")
print(f"Migliore battuta (Rank 1) Score: {merged_df['LPR_new'].max()}")
print(f"Peggiore battuta (Rank N) Score: {merged_df['LPR_new'].min()}")