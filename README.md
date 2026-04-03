[README.md](https://github.com/user-attachments/files/26466247/README.md)
# Progettazione e implementazione di un sistema avanzato di Humor Generation basato su Direct Preference Optimization e Retrieval-Augmented Generation per la produzione di satira context-aware

Questo repository contiene il codice sorgente e l'intera pipeline MLOps sviluppata per il progetto di Tesi Magistrale in Ingegneria Informatica indirizzo Artificial Intelligence & Machine Learning.

L'obiettivo del progetto è la creazione di un modello generativo (Large Language Model) capace di comprendere e formulare battute satiriche, superando il Diversity Collapse e l'appiattimento stilistico tipico dei modelli commerciali (Alignment Tax). Il sistema finale integra l'allineamento tramite Direct Preference Optimization (DPO) e la contestualizzazione dinamica tramite Retrieval-Augmented Generation (RAG) sulle notizie di attualità.

## Struttura dell'Architettura (Pipeline MLOps)
Il progetto è modulare e suddiviso in 6 fasi sequenziali:

### 1. Data_Preparation_and_Categorization
**Descrizione**: Filtraggio del dataset originale (Short Jokes) ed estrazione delle misure di consenso. Utilizzo del paradigma LLM-as-a-Judge (Ensemble di modelli: Llama 3, Mistral, Gemma, Phi-4, GPT-OSS) per valutare le battute secondo specifiche categorie umoristiche (es. Wordplay, Cultural Reference).

**Output**: Dataset pulito e annotato con i punteggi grezzi.

### 2. Reward_Modeling_and_Preferences
**Descrizione**: Risoluzione delle discrepanze tra i modelli valutatori tramite Borda Voting ed estrazione della misura continua proprietaria $LPR_{new}$. Costruzione del dataset di preferenze Pairwise (Chosen/Rejected) e addestramento del giudice DeBERTa-v3.

**Output**: Dataset delle preferenze formattato per l'allineamento.

### 3. DPO_Alignment
**Descrizione**: Il cuore algoritmico del progetto. Abbandono della baseline Proximal Policy Optimization (PPO) (soggetta a Reward Hacking) in favore del DPO. Il modello generativo base (Zephyr-7B) viene sottoposto a fine-tuning sui dati di preferenza.

**Tecnologie**: Ottimizzazione parametrica efficiente tramite QLoRA (Quantizzazione a 4-bit NF4) per consentire l'addestramento su singola GPU.

**Output**: Pesi (Adapter LoRA) del modello allineato (es. v2_1 e v2_2).

### 4. Evaluation_and_Ablation
**Descrizione**: Notebook di validazione e Ablation Study. Confronto empirico tra il modello Base e il modello DPO per dimostrare la soppressione del verbosity bias e l'efficacia del Constraint Prompting nel mitigare le allucinazioni e il Prompt Bleed.

**Output**: Tabelle CSV di inferenza comparativa pronte per l'analisi qualitativa.

### 5. RAG_Application_and_Demo
**Descrizione**: L'applicazione finale. Integrazione del modello Zephyr DPO con un modulo RAG connesso in tempo reale ai feed RSS.

**Funzionamento**: Il sistema intercetta un topic dall'utente, esegue lo scraping delle ultime notizie, inietta il contesto reale nel prompt e genera satira mirata e fattualmente corretta. Include un'analisi del fenomeno del context overriding.

### 6. Human_Evaluation_Streamlit
* **Descrizione:** Piattaforma web interattiva sviluppata in Streamlit per condurre la validazione umana (Blind Test). L'applicazione sottopone agli utenti valutatori le generazioni anonimizzate delle 3 iterazioni architetturali principali (Zephyr Base, PPO v2, DPO v2.2).
* **Funzionamento:** Previene il position bias randomizzando l'ordine delle risposte e mitiga il rumore statistico tramite un tasto di scarto globale ("Nessuna di queste fa ridere").

##  Risultati Ufficiali (Human Blind Test)
La validazione finale dell'architettura è stata condotta tramite un test alla cieca su piattaforma Streamlit, raccogliendo le preferenze umane su prompt generalisti e di attualità. I dati empirici confermano il successo dell'allineamento DPO:

* **Totale Voti raccolti:** 700
* **Numero di Tester:** 35
* **Accordo Inter-Annotatore (Fleiss' Kappa):** 0.066 (Accordo debole, tipico e fisiologico per domini altamente soggettivi come l'umorismo).

### Percentuali di Vittoria
| Modello Generativo | Algoritmo di Allineamento | Preferenze (%) | Voti Assoluti |
| :--- | :--- | :--- | :--- |
| **Zephyr DPO_v2.2** | **DPO (Miglior Modello)** | **27.14%** | **190** |
| Zephyr PPO_v2 | PPO (Baseline RLHF) | 26.14% | 183 |
| Zephyr Base | Nessuno (Foundation Model) | 25.57% | 179 |
| *Nessuna (Fallback)* | *-* | *21.14%* | *148* |

### Analisi Verbosity (Word Count)
I modelli standard tendono a soffrire di *verbosity bias*, allungando il testo inutilmente. L'allineamento DPO ha permesso di interiorizzare il timing comico e la sintesi:
* Zephyr PPO_v2: 29.4 parole
* Zephyr Base: 27.7 parole
* **Zephyr DPO_v2.2: 18.7 parole** *(Estremamente più sintetico e tagliente della baseline)*

### Esecuzione e Riproducibilità
Tutti i notebook sono stati ingegnerizzati per essere eseguiti in ambienti Cloud con accelerazione hardware (testati su Kaggle Notebooks).

L'architettura supporta il caricamento dinamico dei pesi e la gestione di checkpoint intermedi per prevenire la perdita di dati in scenari di out-of-memory. Tutti i risultati e i dati raccolti sono riproducibili eseguendo gli script dedicati, in particolare `estrai_risultati.py` per le metriche del blind test.

## Model Weights
A causa dei limiti di archiviazione di GitHub per i file di grandi dimensioni, i pesi addestrati dei modelli valutatori (`deberta_judge.pth`, ~700MB) e gli adapter LoRA di Zephyr non sono inclusi direttamente in questa repository.

[👉 Clicca qui per scaricare i pesi completi da Google Drive]()

### Stack Tecnologico Principale

#### Linguaggio: Python 3.10.10

#### Deep Learning Framework: PyTorch

#### Modelli & NLP: Hugging Face transformers, datasets, trl (Transformer Reinforcement Learning per DPO)

#### Ottimizzazione (PEFT): peft, bitsandbytes, accelerate

#### Retrieval & Web Scraping: feedparser, beautifulsoup4, requests

#### UI & Data Viz: ipywidgets, pandas, matplotlib, streamlit

## Autore
**Silvio Emanuele Liparoti** Matricola: 242663

## Relatore 
**Prof. Andrea Tagarelli**

**Università della Calabria (UNICAL)**
**Corso di Laurea Magistrale in Ingegneria Informatica: Artificial Intelligence & Machine Learning**
