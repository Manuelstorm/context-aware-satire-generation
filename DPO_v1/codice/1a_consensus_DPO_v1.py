import pandas as pd
import numpy as np
import os

# ==========================================
# 1. CONFIGURAZIONE
# ==========================================
base_path = r"C:\Users\lipar\OneDrive\Desktop\Progetto_NLP_PULITO\PPO_v1\model_checkpoints\sample10000"

data_files = {
    "llama3": os.path.join(base_path, "categoriz_short_sample10000_llama3.csv"),
    "mistral": os.path.join(base_path, "categoriz_short_sample10000_mistral.csv"),
    "gemma": os.path.join(base_path, "categoriz_short_sample10000_gemma.csv"),
}

categories = [
    "Edgy Content", "Cultural Reference", "Wordplay", 
    "Absurdity", "Relatable", "Offensive Humor"
]


# ==========================================
# 2. CARICAMENTO E MERGE
# ==========================================
print("Caricamento e merge dei file...")

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

# ==========================================
# 3. CALCOLO BORDA COUNT
# ==========================================
print("Calcolo punteggi Borda...")

def compute_lpr_borda_filter(df, category, model_names):
    cols = [f"{m}_{category}" for m in model_names]
    valid_cols = [c for c in cols if c in df.columns]
    if not valid_cols: return pd.Series(0, index=df.index)

    # Rank: più il voto è alto maggiore sarà la posizione in classifica
    ranks = df[valid_cols].rank(axis=0, method='min', ascending=False)
    rank_sum = ranks.sum(axis=1)
    
    # Invertiamo per avere score positivo
    max_score = len(df) * len(valid_cols)
    return max_score - rank_sum

for cat in categories:
    merged_df[f"{cat}_LPR_Borda"] = compute_lpr_borda_filter(merged_df, cat, list(data_files.keys()))

# ==========================================
# 4. FILTRO "BEST OF"
# ==========================================

# Calcolo Score Totale (Wordplay + Cultural) per l'ordinamento
merged_df['Total_Score'] = merged_df['Wordplay_LPR_Borda'] + merged_df['Cultural Reference_LPR_Borda']

jokes_with_scores_df = merged_df.sort_values(by='Total_Score', ascending=False)

# ==========================================
# 5. SALVATAGGIO
# ==========================================

# FILE 1: Quello pulito per lo script successivo (SOLO TESTO)
file_clean = "jokes_sample.csv"
jokes_with_scores_df[[text_col]].to_csv(file_clean, index=False)
print(f"\n FILE PULITO SALVATO: {file_clean} (Usa questo per il DPO)")

# FILE 2: Quello per il check (CON SCORE E VOTI)
# Testo, Score Totale, Score Borda delle categorie, e i voti originali dei modelli
cols_to_save = [text_col, 'Total_Score'] + \
               [c for c in jokes_with_scores_df.columns if '_LPR_Borda' in c] + \
               [c for c in jokes_with_scores_df.columns if any(m in c for m in data_files.keys())]

file = "jokes_with_scores.csv"
jokes_with_scores_df[cols_to_save].to_csv(file, index=False)

print(f"FILE DEBUG SALVATO: {file}")
