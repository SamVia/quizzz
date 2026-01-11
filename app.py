import streamlit as st
import pandas as pd
import random
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Dynamic Quiz Loader", page_icon="🚽", layout="wide")

# --- COSTANTI GLOBALI ---
MAX_DOMANDE_ESAME = 33

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
            'soluzione': ['B', 'B'], # Esempio con lettere
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

# --- 4. CARICAMENTO DATI ---

@st.cache_data
def load_data(filename):
    """
    Carica un CSV di quiz in modo robusto:
    - Gestisce UTF-8 BOM
    - Forza separatore ','
    - Rimuove spazi e caratteri invisibili dai nomi delle colonne
    - Converte le opzioni in stringhe
    """
    try:
        # Legge il CSV con encoding UTF-8 BOM e separatore chiaro
        df = pd.read_csv(filename, encoding='utf-8-sig', sep=',')
        
        # Rimuove spazi e BOM dai nomi delle colonne
        df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
        
        # Riempie valori NaN con stringhe vuote
        df = df.fillna("")
        
        # Forza tutte le colonne opzioni a stringa
        for col in ['opzioneA', 'opzioneB', 'opzioneC', 'opzioneD']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Mostra le colonne lette per debug
        st.write("Colonne lette dal CSV:", df.columns.tolist())
        
        return df
    except Exception as e:
        st.error(f"Errore caricamento CSV: {e}")
        return None

#OLD_VERSION
#@st.cache_data
#def load_data(filename):
 #   try:
  #      df = pd.read_csv(filename, sep=None, engine='python')
        
        # 1. RIEMPI I VALORI VUOTI (NaN) CON STRINGHE VUOTE
   #     df = df.fillna("")
        
        # 2. FORZA LA CONVERSIONE IN STRINGA DELLE COLONNE OPZIONI
        # Questo evita che numeri (es. "1") vengano letti come interi, o celle vuote come float
    #    cols_opts = ['opzioneA', 'opzioneB', 'opzioneC', 'opzioneD']
     #   for col in cols_opts:
      #      if col in df.columns:
       #         df[col] = df[col].astype(str)
                
        #return df
    #except Exception as e:
     #   st.error(f"Errore caricamento: {e}")
      #  return None

df = load_data(file_selezionato)

if df is None:
    st.error(f"Errore nella lettura del file {file_selezionato}.")
    st.stop()

if 'quiz_df' not in st.session_state or st.session_state.get('current_quiz_name') != scelta_utente:
    # 1. Salviamo il nome del quiz corrente per capire se l'utente cambia argomento
    st.session_state.current_quiz_name = scelta_utente
    
    # 2. Mescoliamo il dataframe UNA VOLTA SOLA e lo salviamo nello stato
    # .sample(frac=1) è il modo pandas per mescolare le righe
    st.session_state.quiz_df = df.sample(frac=1).reset_index(drop=True)
    
    # 3. Resettiamo l'indice
    st.session_state.idx = 0
    
    # 4. Resettiamo lo stato della domanda (importante per pulire la UI)
    reset_quiz_state()
    # Forziamo il caricamento della prima domanda
    st.session_state.domanda_corrente = None

# Verifica colonne minime
colonne_richieste = ['domanda', 'opzioneA', 'opzioneB', 'opzioneC', 'soluzione']
if not all(col in df.columns for col in colonne_richieste):
    st.error(f"Il file {file_selezionato} non ha le colonne corrette (minimo: {colonne_richieste}).")
    st.stop()

# Determina se il file ha 3 o 4 opzioni
ha_opzioneD = 'opzioneD' in df.columns

# --- 5. LOGICA QUIZ ---

if 'domanda_corrente' not in st.session_state:
    reset_quiz_state()

def nuova_domanda():
    # Controlliamo se abbiamo finito le domande
    if st.session_state.idx >= len(st.session_state.quiz_df):
        st.warning("Hai completato tutte le domande di questo quiz!")
        st.stop() # O logica per ricominciare
        return

    # Recuperiamo la riga corrente usando l'indice salvato
    row = st.session_state.quiz_df.iloc[st.session_state.idx]
    
    # Incrementiamo l'indice PER LA PROSSIMA VOLTA
    st.session_state.idx += 1
    
    # Costruisci le opzioni in base al numero di colonne disponibili
    if ha_opzioneD:
        opts = [row['opzioneA'], row['opzioneB'], row['opzioneC'], row['opzioneD']]
    else:
        opts = [row['opzioneA'], row['opzioneB'], row['opzioneC']]
    
    random.shuffle(opts)
    
    st.session_state.domanda_corrente = row
    st.session_state.opzioni_mix = opts
    st.session_state.selezione_utente = None
    st.session_state.fase = 'selezione'

# Callback click istantaneo
def gestisci_click(risposta_cliccata):
    st.session_state.selezione_utente = risposta_cliccata
    st.session_state.fase = 'verificato'
#modified
# --- Reset flag quando si passa alla domanda successiva ---
def avanza_domanda_esame():
    # Se l'esame è già finito, ricomincia da capo
    if st.session_state.domande_esame_fatte >= MAX_DOMANDE_ESAME:
        st.session_state.punteggio = 0.0
        st.session_state.domande_esame_fatte = 0
        st.session_state.idx = 0
        reset_quiz_state()
        st.rerun()
        return
    
    st.session_state.risposta_gia_valutata = False
    nuova_domanda()
    st.rerun()
# added for exam mode
def salta_domanda_esame():
    if not st.session_state.salto_gia_contato:
        st.session_state.domande_esame_fatte += 1
        st.session_state.salto_gia_contato = True

    st.session_state.risposta_gia_valutata = False
    st.session_state.salto_gia_contato = False
    nuova_domanda()
    st.rerun()

if st.session_state.domanda_corrente is None:
    nuova_domanda()

q = st.session_state.domanda_corrente
opts = st.session_state.opzioni_mix

# -------------------------------------------------------------------------
# MODIFICA QUI: Logica per convertire "A/B/C/D" nel testo della risposta
# -------------------------------------------------------------------------
soluzione_raw = str(q['soluzione']).strip()

# Crea mappa dinamica solo con le colonne disponibili
mappa_lettere = {'A': 'opzioneA', 'B': 'opzioneB', 'C': 'opzioneC'}
if ha_opzioneD:
    mappa_lettere['D'] = 'opzioneD'

# Se la soluzione è una lettera (es. "A"), prendiamo il testo dalla colonna corrispondente
if soluzione_raw.upper() in mappa_lettere:
    colonna_target = mappa_lettere[soluzione_raw.upper()]
    corretta = str(q[colonna_target]).strip()
else:
    # Altrimenti assumiamo che la soluzione sia già il testo completo
    corretta = soluzione_raw
# -------------------------------------------------------------------------

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
    selezione = str(st.session_state.selezione_utente).strip()
    
    for i, opt in enumerate(opts):
        selector = posizioni[i]
        val_opt = str(opt).strip()
        val_corr = corretta # Ora contiene il testo completo, non "A" o "B"
        
        if val_opt == val_corr:
            # VERDE (Corretta)
            css_style += f"{selector} {{ background-color: #d1e7dd !important; border: 2px solid #198754 !important; color: #0f5132 !important; opacity: 1 !important; }}"
        elif val_opt == selezione and selezione != val_corr:
            # ROSSO (Errore utente)
            css_style += f"{selector} {{ background-color: #f8d7da !important; border: 2px solid #dc3545 !important; color: #842029 !important; opacity: 1 !important; }}"
        else:
            # FADE (Altre opzioni)
            css_style += f"{selector} {{ opacity: 0.5 !important; filter: grayscale(80%); }}"

css_style += "</style>"
st.markdown(css_style, unsafe_allow_html=True)

# --- 7. INTERFACCIA UI ---

st.title(f"{scelta_utente}") 

st.markdown(f"### {q['domanda']}")

c1, c2 = st.columns(2)
disabilitato = (st.session_state.fase == 'verificato')

# Rendering bottoni: adatta il numero di bottoni al numero di opzioni
if ha_opzioneD:
    # 4 opzioni: griglia 2x2
    with c1: st.button(opts[0] if opts[0] else "(vuoto)", key="b0", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[0],))
    with c2: st.button(opts[1] if opts[1] else "(vuoto)", key="b1", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[1],))
    with c1: st.button(opts[2] if opts[2] else "(vuoto)", key="b2", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[2],))
    with c2: st.button(opts[3] if opts[3] else "(vuoto)", key="b3", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[3],))
else:
    # 3 opzioni: colonna singola
    st.button(opts[0] if opts[0] else "(vuoto)", key="b0", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[0],))
    st.button(opts[1] if opts[1] else "(vuoto)", key="b1", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[1],))
    st.button(opts[2] if opts[2] else "(vuoto)", key="b2", use_container_width=True, disabled=disabilitato, on_click=gestisci_click, args=(opts[2],))

st.write("---")

# Area Feedback
if st.session_state.fase == 'verificato':
    sel_utente = str(st.session_state.selezione_utente).strip()
    
    if sel_utente == corretta:
        st.success("**Risposta Esatta!**")
    else:
        st.error(f"**Sbagliato!** La risposta giusta era: **{corretta}**")
    
    if motivazione and str(motivazione) != "nan":
        st.info(f"**Motivazione:**\n\n{motivazione}")

    if st.button("PROSSIMA DOMANDA", type="primary", use_container_width=True):
        if st.session_state.modalita_esame:
            avanza_domanda_esame()
        else:
            nuova_domanda()
            st.rerun()

#old VERSION
    #if st.button("PROSSIMA DOMANDA", type="primary", use_container_width=True):
     #   nuova_domanda()
      #  st.rerun()

elif st.session_state.fase == 'selezione':
    if st.button("Salta Domanda", use_container_width=True):
        if st.session_state.modalita_esame:
            salta_domanda_esame()
        else:
            nuova_domanda()
            st.rerun()

#old Version
#elif st.session_state.fase == 'selezione':
 #   if st.button("Salta Domanda", use_container_width=True):
  #      nuova_domanda()
   #     st.rerun()
    
# ==============================
# 8. MODALITÀ ESAME (ADD-ON FIX)
# ==============================

# --- Stato esame ---
if 'modalita_esame' not in st.session_state:
    st.session_state.modalita_esame = False

if 'punteggio' not in st.session_state:
    st.session_state.punteggio = 0.0

if 'domande_esame_fatte' not in st.session_state:
    st.session_state.domande_esame_fatte = 0

if 'risposta_gia_valutata' not in st.session_state:
    st.session_state.risposta_gia_valutata = False
    
if 'salto_gia_contato' not in st.session_state:
    st.session_state.salto_gia_contato = False


# --- Toggle sidebar ---
st.sidebar.markdown("---")
st.session_state.modalita_esame = st.sidebar.checkbox(
    "📝 Modalità ESAME (33 domande)",
    value=st.session_state.modalita_esame
)

# --- Mostra stato esame ---
if st.session_state.modalita_esame:
    progress_value = min(st.session_state.domande_esame_fatte / MAX_DOMANDE_ESAME, 1.0)
    st.progress(progress_value)
    st.write(
        f"📊 **Domande:** {st.session_state.domande_esame_fatte}/{MAX_DOMANDE_ESAME} | "
        f"🎯 **Punteggio:** {round(st.session_state.punteggio, 2)}"
    )

# --- Calcolo punteggio (IMMEDIATO) ---
if (
    st.session_state.modalita_esame
    and st.session_state.fase == 'verificato'
    and not st.session_state.risposta_gia_valutata
):
    if st.session_state.selezione_utente == corretta:
        st.session_state.punteggio += 1
    else:
        st.session_state.punteggio -= 0.33

    st.session_state.domande_esame_fatte += 1
    st.session_state.risposta_gia_valutata = True
    
# --- Fine esame ---
if (
    st.session_state.modalita_esame
    and st.session_state.domande_esame_fatte >= MAX_DOMANDE_ESAME
):
    st.markdown("---")
    st.subheader("🏁 ESAME TERMINATO")

    punteggio_finale = round(st.session_state.punteggio, 2)
    st.metric("Punteggio Finale", punteggio_finale)

    if punteggio_finale >= 18:
        st.success("✅ **ESAME SUPERATO**")
    else:
        st.error("❌ **ESAME NON SUPERATO**")

    if st.button("🔄 Ricomincia Esame", use_container_width=True):
        st.session_state.punteggio = 0.0
        st.session_state.domande_esame_fatte = 0
        st.session_state.idx = 0
        reset_quiz_state()
        st.rerun()

    st.stop()
