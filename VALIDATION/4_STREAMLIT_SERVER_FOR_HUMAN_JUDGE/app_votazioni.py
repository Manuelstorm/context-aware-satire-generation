import streamlit as st
import random
import os

st.set_page_config(layout="wide")
st.title(" Humor Generation AI - Blind Test")

# --- ARRAY CON 20 PROMPT CASUALI ESTRATTI DAI PRECEDENTI 50 ---
esempi = [
    # --- 10 BATTUTE GENERALISTE (Senza RAG) ---
     {
        "prompt": "Make a joke about working from home.",
        "A": "\"The best part of working from home? Not having to wear pants.\"",
        "B": "\"Working from home used to be a dream until I realized my couch is also my boss's couch.\"",
        "C": "\"Turns out my productivity skyrocketed when I started wiping down my kitchen counter between meetings.\""
    },
    {
        "prompt": "Tell me a joke about software engineers.",
        "A": "Why did the software engineer quit his job? Because he wanted to work on a project with a real chance of success.",
        "B": "Why did the software engineer quit their job? Because they wanted to work in a field where they could actually see what they're creating.",
        "C": "Why did the software engineer quit his job? His company wanted him to act human."
    },
    {
        "prompt": "Make a sarcastic comment about autocorrect ruining texts.",
        "A": "\"Autocorrect may think it knows what I mean, but in reality, it's just replacing every word with something completely wrong.\"",
        "B": "\"Autocorrect may save us time, but it also has a twisted sense of humor that turns our messages into unintended masterpieces.\"",
        "C": "\"I used to think relationships broke down over miscommunication, but now I know it's just autocorrect.\""
    },
    {
        "prompt": "Make a joke about going to the gym in January.",
        "A": "\"I joined a gym in January, but I'm already thinking of quitting... In February.\"",
        "B": "\"I joined a gym in January... I guess you could say I'm now a part of the monthly cancellation fee.\"",
        "C": "\"I joined a gym last January. This year I just changed the date on my membership card.\""
    },
    {
        "prompt": "Make a sarcastic comment about family dinners.",
        "A": "\"Family dinners are like a game of Russian roulette - you never know which relative will pull out a loaded conversation topic.\"",
        "B": "\"Family dinners are like nuclear warheads - packed with explosive levels of awkwardness and the potential for long-lasting emotional fallout.\"",
        "C": "\"Nothing says 'I love you' quite like sweatpants and cold silence passed around the table.\""
    },
    {
        "prompt": "Tell me a joke about trying to assemble IKEA furniture.",
        "A": "Why did IKEA open a psychiatric ward next to their store? To save customers the trip home and back.",
        "B": "Why did the Swedish meatball go to IKEA? To get some assembly instructions. Turns out, even Swedes need help sometimes.",
        "C": "\"Ikea furniture comes with all the pieces you need... Except for the instructions. Which they give you in Swedish, just to rub it in.\""
    },
    {
        "prompt": "Make a sarcastic comment about public transport.",
        "A": "\"The only way public transportation gets you anywhere faster than walking is by running over your feet.\"",
        "B": "\"The only thing constant in life is the delayed arrival of your next train.\"",
        "C": "\"Nothing says 'quality time' like being packed into a smelly metal tube with strangers' armpits.\""
    },
    {
        "prompt": "Make a dark humor joke about going to the doctor.",
        "A": "Why did the skeleton go to the doctor? To get a career change.",
        "B": "Why did the patient refuse anesthesia before surgery? He wanted to meet the surgeon face to face.",
        "C": "\"I thought my obsession with hand sanitizer was weird, but my doctor told me I have a clinical case of OCD... Turns out she's just really into me.\""
    },
    {
        "prompt": "Tell me a dark humor joke about student loans.",
        "A": "\"Why did the student loan officer go bankrupt? Because his clients couldn't pay him back.\"",
        "B": "Why did the bank robber wear a graduation gown? Because he wanted to be forgiven for his debt.",
        "C": "Why did the suicide hotline disconnect my call? They said I shouldn't have any outstanding balances."
    },
    {
        "prompt": "Make a sarcastic comment about the end of the world.",
        "A": "As the world burns around us and chaos reigns supreme, I can't help but think that this might just be the best year ever for air pollution standards. At least we're finally meeting our goals.",
        "B": "As the sky turned a fiery red and the ground shook beneath my feet, I couldn't help but think, \"Well, this is certainly what I meant when I said I wanted to spice up my routine.\"",
        "C": "\"I always figured the apocalypse would be more exciting than this.\""
    },
    
    # --- 10 BATTUTE DI ATTUALITA' (Con RAG) ---
    {
        "prompt": "Tell me a joke about the Sanremo 2026 music festival.",
        "A": "Q: What do you get when you cross the Sanremo music festival with a time machine? A: A chance to relive the same exact performances over and over again in 2026.",
        "B": "Why did they call this year's Sanremo Music Festival \"Sal Da Vinci\"? Because Leonardo da Pesce painted his famous masterpiece in just six weeks... And all the songs sound like they took that long to write.",
        "C": "Why did they call this year's Sanremo Music Festival \"Sal Da Vinci\"? Because it's going to Italy and coming back full of cheese."
    },
    {
        "prompt": "Tell me a joke about Apple releasing the new iPhone 17.",
        "A": "Why did Apple release the iPhone 17e instead of the expected 17? Because they wanted to give their customers an \"easier\" experience.",
        "B": "Why did Apple release the iPhone 17e instead of the highly anticipated iPhone 18? Because they wanted to give their customers an \"easy\" upgrade option.",
        "C": "Why did Apple skip 16 and go straight to 17? because the new iPhone is so smart, it knows 15."
    },
    {
        "prompt": "Tell me a joke about Elon Musk's latest controversial tweet on X.",
        "A": "Why did Elon Musk change X's name from Twitter to X?",
        "B": "Why did Elon Musk change Twitter's name to X? Because he wanted a social media platform where everyone could spell their last names incorrectly.",
        "C": "Why did Elon Musk change X's name to Twitter 2.0? He realized he could lose half his users and still keep all the angry ones."
    },
    {
        "prompt": "Make a dark humor joke about the latest OpenAI model taking our jobs.",
        "A": "\"I just got laid off from my job as a copywriter because my company replaced me with a cheaper, faster, and more reliable AI model. On the bright side, now I have all the free time in the world to train for the upcoming robot apocalypse.\"",
        "B": "As AI continues to advance, the future of employment looks bleak. But fear not, because soon enough we'll have robots replacing robots, leaving us all jobless... Except for the guy who writes jokes for AI models. Now that's a real career killer.",
        "C": "\"They say GPT-5 will take all our jobs... But who's gonna write all those unemployment letters?\""
    },
    {
        "prompt": "Make a sarcastic comment about Jeff Bezos' Blue Origin space flights.",
        "A": "\"Jeff Bezos has finally found a way to avoid paying taxes – by launching himself into outer space.\"",
        "B": "Jeff Bezos' latest venture, Blue Origin, aims to save us all from the imminent threat of asteroids. Because what could possibly go wrong when the richest man in the world starts blasting objects into space? At least we know if he ever decides to retire, his rockets will provide the perfect exit strategy.",
        "C": "Jeff Bezos's Blue Origin finally found a customer willing to pay millions of dollars for a quick trip to space – asteroids!"
    },
    {
        "prompt": "Make a sarcastic comment about Taylor Swift's latest album release.",
        "A": "\"Taylor Swift's newest album may have missed the mark, but at least she's finally found her true calling as a professional critic.\"",
        "B": "\"Swift justice has been served. Taylor Swift's newest album may have fallen short, but at least now we know that justice is blindfolded by bad dance moves.\"",
        "C": "\"They say absolution is good for the soul, but Taylor Swift's latest album left me feeling more confessed than forgiven.\""
    },
    {
        "prompt": "Tell me a joke about the most absurd TikTok dance trend of 2026.",
        "A": "In 2026, the hottest TikTok dance move is called \"The Flop.\" It's when you fall dramatically to the ground, flail your limbs uncontrollably for ten seconds, then get back up and pretend nothing happened. Experts say it's the perfect way to show off your flexibility and lack of coordination all at once. .",
        "B": "In 2026, the hottest TikTok dance trend involves people spinning around in circles for hours, only stopping to post selfies of their dizzy faces on social media. It's called the \"Spiral Frenzy\" – because that's what your brain feels like afterwards.",
        "C": "In 2026, scientists discovered that dancing to \"Old Town Road\" for hours reverses climate change. It's called the Yeehaw Agenda."
    },
    {
        "prompt": "Make a joke about Netflix raising its subscription prices again.",
        "A": "Netflix just raised their prices again, making it official: now I have to pay to watch other people cry on \"Love Is Blind.\"",
        "B": "Netflix just announced another price hike, so now I have to choose between eating ramen noodles every day or having a social life. At least their shows will still be binge-worthy.",
        "C": "Netflix just raised their prices again. Good thing I stopped watching because my boyfriend kept rewinding \"The Kissing Booth\" every time we got to the good part."
    },
    {
        "prompt": "Tell me a joke about the price of an espresso in Milan in 2026.",
        "A": "In 2026, when visiting Milan, don't forget your spacesuit – a single espresso will cost you $5,000 due to the new law requiring all coffee shops to install hyperdrive engines to keep up with inflation caused by intergalactic currency fluctuations.",
        "B": "In the year 2026, when visiting Milan, forget about sightseeing and museums – the real attraction will be getting your hands on a cup of espresso. At $5,000 a shot, it'll be the world's most expensive coffee... And the only way to afford it is by selling one of your kidneys on the black market. But hey, at least the latte art will be impeccable – a perfect heart shape",
        "C": "\"They say in the future, Milan will be the world's first $10/cup coffee city. But who needs a morning pick-me-up when you have 20 grand just to get out of bed?\""
    },
    {
        "prompt": "Make a joke about the completely unpredictable weather in Europe this summer.",
        "A": "\"Europe's climate just declared war on fashion - one day they're wearing shorts, the next they're melting into their leather boots.\"",
        "B": "\"Europe's weather has been so erratic this summer, I heard they had to cancel Wimbledon and replace it with an ice sculpture competition.\"",
        "C": "\"They said Brexit would bring uncertainty to Britain, but it looks like Europe's taking weather tips from them.\""
    }
]

# Dizionario segreto per risalire dalla lettera al vero modello
mappa_modelli = {
    "A": "Zephyr_Base",
    "B": "PPO_v2",
    "C": "DPO_v2.2"
}

if not os.path.exists("risultati_voti.csv"):
    with open("risultati_voti.csv", "w", encoding="utf-8") as f:
        # Salviamo direttamente il nome del modello, non la lettera!
        f.write("ID_Prompt,Modello_Votato\n") 

if 'indice' not in st.session_state:
    st.session_state.indice = 0
if 'ordine_schermo' not in st.session_state:
    st.session_state.ordine_schermo = []

def salva_voto(modello_scelto):
    with open("risultati_voti.csv", "a", encoding="utf-8") as f:
        f.write(f"{st.session_state.indice},{modello_scelto}\n")
    st.session_state.indice += 1
    # Resetta l'ordine per la prossima domanda
    st.session_state.ordine_schermo = []

indice = st.session_state.indice

if indice < len(esempi):
    st.write("Aiutami con la tesi! Leggi il prompt e vota la battuta che ti fa più ridere tra le 3 proposte... [Testo accorciato per brevità]")
    dato_corrente = esempi[indice]
    
    st.markdown(f"## Prompt: {dato_corrente['prompt']}")
    st.write("---")
    
    # --- LA MAGIA DEL BLIND TEST (RIMESCOLAMENTO) ---
    if not st.session_state.ordine_schermo:
        st.session_state.ordine_schermo = random.sample(["A", "B", "C"], 3)
    
    ordine = st.session_state.ordine_schermo
    
    # Crea 3 colonne per affiancare le battute mischiate
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Battuta A**")
        st.write(dato_corrente[ordine[0]])
        if st.button(" Vota A", key=f"btn_1_{indice}"):
            salva_voto(mappa_modelli[ordine[0]]) # Salva il VERO nome del modello!
            st.rerun()
            
    with col2:
        st.success("**Battuta B**")
        st.write(dato_corrente[ordine[1]])
        if st.button(" Vota B", key=f"btn_2_{indice}"):
            salva_voto(mappa_modelli[ordine[1]])
            st.rerun()

    with col3:
        st.warning("**Battuta C**")
        st.write(dato_corrente[ordine[2]])
        if st.button(" Vota C", key=f"btn_3_{indice}"):
            salva_voto(mappa_modelli[ordine[2]])
            st.rerun()

    # --- SEZIONE NESSUNA DI QUESTE ---
    st.write("  ") 
    st.write("  ") 
    
    col_vuota1, col_centrale, col_vuota2 = st.columns([1, 2, 1]) 
    
    with col_centrale:
        st.error("**❌ Nessuna di queste fa ridere**")
        if st.button("Scarta tutte le battute", key=f"btn_d_{indice}", use_container_width=True):
            salva_voto("Nessuna")
            st.rerun()

else:
    st.balloons() 
    st.success(" Hai finito! Grazie mille per aver contribuito alla mia tesi Magistrale!")