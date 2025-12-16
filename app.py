import streamlit as st
import pandas as pd
import random
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Dynamic Quiz Loader", page_icon="🚽", layout="wide")

# --- 1. FUNZIONI UTILITY ---

def crea_csv_esempio_se_mancano():
    """Crea dei file di test solo se non c'è nessun CSV nella cartella."""
    files_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not files_csv:
        data_demo = {
            'domanda': ['Quanto fa 1+1?', 'Il cielo è?'],
            'opzioneA': ['1', 'Verde'],
            'opzioneB': ['2', 'Blu'],
            'opzioneC': ['3', 'Giallo'],
            'opzioneD': ['4', 'Viola'],
            'soluzione': ['2', 'Blu'],
            'motivazione': ['Matematica base.', 'Rayleigh scattering.']
        }
        pd.DataFrame(data_demo).to_csv('Quiz_Demo.csv', index=False)

def get_lista_quiz():
    """Scansiona la cartella e restituisce un dizionario {Nome Visualizzato: Nome File}."""
    crea_csv_esempio_se_mancano() 
    
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    mappa_quiz = {}
    
    for f in files:
        # Rimuove l'estensione .csv e sostituisce gli underscore con spazi
        nome_pulito = f.replace('.csv', '').replace('_', ' ').title()
        mappa_quiz[nome_pulito] = f
        
    return mappa_quiz

# --- 2. GESTIONE RESET E STATO ---

def reset_quiz_state():
    """Resetta completamente lo stato quando si cambia quiz."""
    st.session_state.domanda_corrente = None
    st.session_state.fase = 'selezione'
    st.session_state.selezione_utente = None
    st.session_state.opzioni_mix = []

# --- 3. SIDEBAR DINAMICA ---

st.sidebar.title("Libreria Quiz")
st.sidebar.write("Seleziona un argomento:")

# Recuperiamo la lista dei file
mappa_quiz = get_lista_quiz()

if not mappa_quiz:
    st.error("Nessun file CSV trovato nella cartella!")
    st.stop()

# Menu di scelta
titoli_disponibili = list(mappa_quiz.keys())
scelta_utente = st.sidebar.radio(
    "Argomenti:", # Label nascosta o breve
    titoli_disponibili,
    on_change=reset_quiz_state 
)

# Recuperiamo il nome del file reale
file_selezionato = mappa_quiz[scelta_utente]

# --- 4. CARICAMENTO DATI ---

@st.cache_data
def load_data(filename):
    try:
        return pd.read_csv(filename, sep=None, engine='python')
    except Exception as e:
        return None

df = load_data(file_selezionato)

if df is None:
    st.error(f"Errore nella lettura del file {file_selezionato}.")
    st.stop()

# Verifica colonne minime
colonne_richieste = ['domanda', 'opzioneA', 'opzioneB', 'opzioneC', 'opzioneD', 'soluzione']
if not all(col in df.columns for col in colonne_richieste):
    st.error(f"Il file {file_selezionato} non ha le colonne corrette.")
    st.stop()

# --- 5. LOGICA QUIZ ---

if 'domanda_corrente' not in st.session_state:
    reset_quiz_state()

def nuova_domanda():
    idx = random.randint(0, len(df) - 1)
    row = df.iloc[idx]
    opts = [row['opzioneA'], row['opzioneB'], row['opzioneC'], row['opzioneD']]
    random.shuffle(opts)
    
    st.session_state.domanda_corrente = row
    st.session_state.opzioni_mix = opts
    st.session_state.selezione_utente = None
    st.session_state.fase = 'selezione'

# Callback click istantaneo
def gestisci_click(risposta_cliccata):
    st.session_state.selezione_utente = risposta_cliccata
    st.session_state.fase = 'verificato'

if st.session_state.domanda_corrente is None:
    nuova_domanda()

q = st.session_state.domanda_corrente
opts = st.session_state.opzioni_mix
corretta = q['soluzione']
motivazione = q['motivazione'] if 'motivazione' in df.columns else ""

# --- 6. CSS STILE E COLORI ---
css_style = """
<style>
div.stButton > button {
    height: 85px; width: 100%; font-size: 19px; border-radius: 12px;
    font-weight: 600; transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 8px rgba(0,0,0,0.15);
}
"""
if st.session_state.fase == 'verificato':
    posizioni = {
        0: "div[data-testid='column']:nth-of-type(1) div.stButton:nth-of-type(1) button",
        1: "div[data-testid='column']:nth-of-type(2) div.stButton:nth-of-type(1) button",
        2: "div[data-testid='column']:nth-of-type(1) div.stButton:nth-of-type(2) button",
        3: "div[data-testid='column']:nth-of-type(2) div.stButton:nth-of-type(2) button"
    }
    selezione = st.session_state.selezione_utente
    for i, opt in enumerate(opts):
        selector = posizioni[i]
        val_opt = str(opt).strip()
        val_corr = str(corretta).strip()
        val_sel = str(selezione).strip()
        
        if val_opt == val_corr:
            # VERDE (Corretta)
            css_style += f"{selector} {{ background-color: #d1e7dd !important; border: 2px solid #198754 !important; color: #0f5132 !important; opacity: 1 !important; }}"
        elif val_opt == val_sel and val_sel != val_corr:
            # ROSSO (Errore utente)
            css_style += f"{selector} {{ background-color: #f8d7da !important; border: 2px solid #dc3545 !important; color: #842029 !important; opacity: 1 !important; }}"
        else:
            # FADE (Altre opzioni)
            css_style += f"{selector} {{ opacity: 0.5 !important; filter: grayscale(80%); }}"

css_style += "</style>"
st.markdown(css_style, unsafe_allow_html=True)

# --- 7. INTERFACCIA UI ---

st.title(f"{scelta_utente}") # Titolo dinamico

st.markdown(f"### {q['domanda']}")

c1, c2 = st.columns(2)
disabilitato = (st.session_state.fase == 'verificato')

# Rendering bottoni con callback
with c1: st.button(opts[0], key="b0", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[0],))
with c2: st.button(opts[1], key="b1", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[1],))
with c1: st.button(opts[2], key="b2", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[2],))
with c2: st.button(opts[3], key="b3", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[3],))

st.write("---")

# Area Feedback
if st.session_state.fase == 'verificato':
    if str(st.session_state.selezione_utente).strip() == str(corretta).strip():
        st.success("**Risposta Esatta!**")
    else:
        st.error(f"**Sbagliato** La risposta giusta era: **{corretta}**")
    
    if motivazione and str(motivazione) != "nan":
        st.info(f"**Motivazione:**\n\n{motivazione}")
    
    if st.button("PROSSIMA DOMANDA", type="primary", use_container_width=True):
        nuova_domanda()
        st.rerun()

elif st.session_state.fase == 'selezione':
    if st.button("Salta Domanda", use_container_width=True):
        nuova_domanda()
        st.rerun()