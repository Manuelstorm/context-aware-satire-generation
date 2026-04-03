import pandas as pd

df = pd.read_csv("C:/Users/lipar/OneDrive/Desktop/Progetto_NLP_PULITO_FINAL/VALIDATION/FINAL_TEST/EVALUATION_GENERATION/dataset_valutazione_finale.csv")
modelli = ["Zephyr_Base", "PPO_v2",  "DPO_v2.2"]

with open("battute_estratte_fin.md", "w", encoding="utf-8") as f:
    f.write("# Dataset Completo delle Battute Generate\n\n")
    for index, row in df.iterrows():
        f.write(f"### {index + 1}. Prompt: *{row['Prompt']}*\n")
        for mod in modelli:
            # Pulisce eventuali a capo extra
            battuta = str(row[mod]).replace('\n', ' ') 
            f.write(f"- **{mod}:** {battuta}\n")
        f.write("\n---\n\n")

print("File 'battute_estratte_fin.md' creato con successo!")