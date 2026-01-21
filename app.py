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
            'soluzione': ['B', 'B'], 
            'motivazione': ['Matematica base.', 'Rayleigh scattering.']
        }
        pd.DataFrame(data_demo).to_csv('Quiz_Demo.csv', index=False)

def get_lista_quiz():
    """Scansiona la cartella e restituisce un dizionario {Nome Visualizzato: Nome File}."""
    crea_csv_esempio_se_mancano() 
    
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    mappa_quiz = {}
    
    for f in files:
        nome_pulito = f.replace('.csv', '').replace('_', ' ').title()
        mappa_quiz[nome_pulito] = f
        
    return mappa_quiz

# --- 2. GESTIONE RESET E STATO ---

# Inizializza le variabili di session state critiche
if 'wrong_answers' not in st.session_state:
    st.session_state.wrong_answers = []
if 'practice_mode' not in st.session_state:
    st.session_state.practice_mode = False
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'wrong_count' not in st.session_state:
    st.session_state.wrong_count = 0

def reset_quiz_state():
    """Resetta completamente lo stato quando si cambia quiz."""
    st.session_state.domanda_corrente = None
    st.session_state.fase = 'selezione'
    st.session_state.selezione_utente = None
    st.session_state.opzioni_mix = []
    # Reset contatore domande quando si cambia quiz
    if 'domande_risposte_totali' in st.session_state:
        st.session_state.domande_risposte_totali = 0
    st.session_state.correct_count = 0
    st.session_state.wrong_count = 0

def reset_wrong_answers():
    """Resetta la lista delle risposte sbagliate."""
    st.session_state.wrong_answers = []
    st.session_state.practice_mode = False

# --- 3. SIDEBAR DINAMICA ---

st.sidebar.title("Libreria Quiz")
st.sidebar.write("Seleziona un argomento:")

mappa_quiz = get_lista_quiz()

if not mappa_quiz:
    st.error("Nessun file CSV trovato nella cartella!")
    st.stop()

titoli_disponibili = list(mappa_quiz.keys())
scelta_utente = st.sidebar.radio(
    "Argomenti:", 
    titoli_disponibili,
    on_change=reset_quiz_state 
)

# --- PRACTICE MODE TOGGLE ---
st.sidebar.markdown("---")
if st.session_state.wrong_answers:
    st.sidebar.write(f"❌ Risposte sbagliate: **{len(st.session_state.wrong_answers)}**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Pratica", use_container_width=True):
            st.session_state.practice_mode = True
            st.session_state.idx = 0
            st.session_state.domanda_corrente = None
            reset_quiz_state()
            st.rerun()
    with col2:
        if st.button("🗑️ Cancella", use_container_width=True):
            st.session_state.wrong_answers = []
            st.rerun()

file_selezionato = mappa_quiz[scelta_utente]

# --- 4. CARICAMENTO DATI ---

@st.cache_data
def load_data(filename):
    """
    Carica un CSV di quiz in modo robusto.
    """
    try:
        df = pd.read_csv(filename, encoding='utf-8-sig', sep=',')
        # Pulisce nomi colonne
        df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
        # NaN -> stringa vuota
        df = df.fillna("")
        # Forza stringhe
        for col in ['opzioneA', 'opzioneB', 'opzioneC', 'opzioneD']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df
    except Exception as e:
        st.error(f"Errore caricamento CSV: {e}")
        return None

if st.session_state.practice_mode and st.session_state.wrong_answers:
    # Pratica modalità: usa solo risposte sbagliate
    df_practice = pd.DataFrame(st.session_state.wrong_answers)
    if len(df_practice) > 0:
        # Rimuovi la colonna original_index se esiste
        if 'original_index' in df_practice.columns:
            df_practice = df_practice.drop(columns=['original_index'])
        df = df_practice.sample(frac=1).reset_index(drop=True)
    else:
        df = load_data(file_selezionato)
else:
    df = load_data(file_selezionato)
    st.session_state.practice_mode = False

if df is None:
    st.error(f"Errore nella lettura del file {file_selezionato}.")
    st.stop()

if 'quiz_df' not in st.session_state or st.session_state.get('current_quiz_name') != scelta_utente:
    st.session_state.current_quiz_name = scelta_utente
    st.session_state.quiz_df = df.sample(frac=1).reset_index(drop=True)
    st.session_state.idx = 0
    reset_quiz_state()
    st.session_state.domanda_corrente = None
    reset_wrong_answers()

colonne_richieste = ['domanda', 'opzioneA', 'opzioneB', 'opzioneC', 'soluzione']
if not all(col in df.columns for col in colonne_richieste):
    st.error(f"Il file {file_selezionato} non ha le colonne corrette (minimo: {colonne_richieste}).")
    st.stop()

ha_opzioneD = 'opzioneD' in df.columns

# --- 5. LOGICA QUIZ ---

if 'domanda_corrente' not in st.session_state:
    reset_quiz_state()

def nuova_domanda():
    if st.session_state.idx >= len(st.session_state.quiz_df):
        st.warning("Hai completato tutte le domande di questo quiz!")
        st.stop()

    row = st.session_state.quiz_df.iloc[st.session_state.idx]
    st.session_state.idx += 1
    
    if ha_opzioneD:
        opts = [row['opzioneA'], row['opzioneB'], row['opzioneC'], row['opzioneD']]
    else:
        opts = [row['opzioneA'], row['opzioneB'], row['opzioneC']]
    
    random.shuffle(opts)
    
    st.session_state.domanda_corrente = row
    st.session_state.opzioni_mix = opts
    st.session_state.selezione_utente = None
    st.session_state.fase = 'selezione'

def gestisci_click(risposta_cliccata):
    st.session_state.selezione_utente = risposta_cliccata
    st.session_state.fase = 'verificato'
    if 'domande_risposte_totali' in st.session_state:
        st.session_state.domande_risposte_totali += 1

def track_wrong_answer():
    """Traccia una risposta sbagliata aggiungendola alla lista."""
    if st.session_state.selezione_utente != corretta:
        # Aggiungi solo se non è già stato tracciato per questa domanda
        current_q_index = st.session_state.idx - 1
        if current_q_index not in [item.get('original_index', -1) for item in st.session_state.wrong_answers]:
            wrong_item = st.session_state.domanda_corrente.to_dict()
            wrong_item['original_index'] = current_q_index
            st.session_state.wrong_answers.append(wrong_item)
        st.session_state.wrong_count += 1
    else:
        st.session_state.correct_count += 1

def remove_correct_from_wrong_list():
    """Rimuove una domanda dalla lista di risposte sbagliate se risposta correttamente."""
    if st.session_state.selezione_utente == corretta and st.session_state.practice_mode:
        # Trova e rimuovi la domanda corrente dalla lista di risposte sbagliate
        current_q = st.session_state.domanda_corrente.to_dict()
        st.session_state.wrong_answers = [
            item for item in st.session_state.wrong_answers
            if item.get('domanda') != current_q.get('domanda')
        ]
        st.session_state.correct_count += 1
    elif st.session_state.practice_mode and st.session_state.selezione_utente != corretta:
        st.session_state.wrong_count += 1

def avanza_domanda_esame():
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

def salta_domanda_esame():
    if 'domande_risposte_totali' in st.session_state:
        st.session_state.domande_risposte_totali += 1
        
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

# -- Calcolo risposta corretta --
soluzione_raw = str(q['soluzione']).strip()
mappa_lettere = {'A': 'opzioneA', 'B': 'opzioneB', 'C': 'opzioneC'}
if ha_opzioneD:
    mappa_lettere['D'] = 'opzioneD'

if soluzione_raw.upper() in mappa_lettere:
    colonna_target = mappa_lettere[soluzione_raw.upper()]
    corretta = str(q[colonna_target]).strip()
else:
    corretta = soluzione_raw

motivazione = q['motivazione'] if 'motivazione' in df.columns else ""

# --- 6. CSS STILE E COLORI ---
# Nota: Ho aggiunto margin-bottom al bottone per allinearlo ai box HTML
css_style = """
<style>
div.stButton > button {
    height: 85px; width: 100%; font-size: 19px; border-radius: 12px;
    font-weight: 600; transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 8px rgba(0,0,0,0.15);
}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- 7. INTERFACCIA UI ---

st.title(f"🔄 Pratica - {scelta_utente}" if st.session_state.practice_mode else f"{scelta_utente}") 

if 'quiz_df' in st.session_state and 'domande_risposte_totali' in st.session_state:
    total_seen = st.session_state.domande_risposte_totali
    total_questions = len(st.session_state.quiz_df)
    correct = st.session_state.correct_count
    wrong = st.session_state.wrong_count
    skipped = total_seen - correct - wrong
    
    # Calcola il voto stimato su 33
    if total_seen > 0:
        score_per_question = (correct - (wrong * 0.33)) / total_seen
        estimated_grade = score_per_question * MAX_DOMANDE_ESAME
    else:
        estimated_grade = 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"📚 Domande viste: **{total_seen}/{total_questions}**")
    with col2:
        st.write(f"✅ Giuste: **{correct}** | ❌ Sbagliate: **{wrong}**")
    with col3:
        st.write(f"📊 Voto stimato: **{estimated_grade:.2f}/33**")

st.markdown(f"### {q['domanda']}")

c1, c2 = st.columns(2)

# --- FUNZIONE DI RENDERING BOTTONI (CORRETTA) ---
def render_button_with_feedback(option_text, key, col):
    selezione = str(st.session_state.selezione_utente).strip()
    val_opt = str(option_text).strip()
    val_corr = str(corretta).strip()
    
    # 1. SE ABBIAMO GIÀ RISPOSTO -> MOSTRA HTML COLORATO
    if st.session_state.fase == 'verificato':
        if val_opt == val_corr:
            # VERDE (Corretta)
            border_c = "#28a745"
            bg_c = "rgba(40, 167, 69, 0.2)"
            text_c = "#155724"
        elif val_opt == selezione:
            # ROSSO (Sbagliata)
            border_c = "#dc3545"
            bg_c = "rgba(220, 53, 69, 0.2)"
            text_c = "#721c24"
        else:
            # GRIGIO (Le altre)
            border_c = "#e9ecef"
            bg_c = "rgba(233, 236, 239, 0.4)"
            text_c = "#6c757d"

        col.markdown(f"""
        <div style="
            height: 85px; 
            width: 100%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border: 2px solid {border_c}; 
            background-color: {bg_c}; 
            color: {text_c};
            border-radius: 12px; 
            font-weight: 600; 
            font-size: 19px; 
            margin-bottom: 10px;
            padding: 5px;
            text-align: center;
            line-height: 1.2;
        ">
            {val_opt}
        </div>
        """, unsafe_allow_html=True)

    # 2. SE DOBBIAMO ANCORA RISPONDERE -> MOSTRA BOTTONE CLICCABILE
    else:
        with col:
            st.button(
                option_text if option_text else "(vuoto)",
                key=key,
                use_container_width=True,
                on_click=gestisci_click,
                args=(option_text,)
            )

# Rendering griglia
if ha_opzioneD:
    render_button_with_feedback(opts[0], "b0", c1)
    render_button_with_feedback(opts[1], "b1", c2)
    render_button_with_feedback(opts[2], "b2", c1)
    render_button_with_feedback(opts[3], "b3", c2)
else:
    render_button_with_feedback(opts[0], "b0", st)
    render_button_with_feedback(opts[1], "b1", st)
    render_button_with_feedback(opts[2], "b2", st)

st.write("---")

# --- Feedback & Navigazione ---

if st.session_state.fase == 'verificato':
    sel_utente = str(st.session_state.selezione_utente).strip()
    
    # Traccia la risposta sbagliata se non siamo in pratica
    if not st.session_state.practice_mode:
        track_wrong_answer()
    else:
        # Se siamo in pratica e la risposta è corretta, rimuovi dalla lista
        remove_correct_from_wrong_list()
    
    if motivazione and str(motivazione) != "nan":
        st.info(f"**Motivazione:**\n\n{motivazione}")

    if st.button("PROSSIMA DOMANDA", type="primary", use_container_width=True):
        if st.session_state.practice_mode:
            # Se siamo in pratica, torna alla modalità normale quando finisci
            if st.session_state.idx >= len(st.session_state.quiz_df):
                st.session_state.practice_mode = False
                st.session_state.idx = 0
                reset_quiz_state()
                st.success("✅ Hai completato la pratica delle risposte sbagliate!")
                st.rerun()
            else:
                nuova_domanda()
                st.rerun()
        elif st.session_state.modalita_esame:
            avanza_domanda_esame()
        else:
            nuova_domanda()
            st.rerun()

elif st.session_state.fase == 'selezione':
    if st.button("Salta Domanda", use_container_width=True):
        if 'domande_risposte_totali' in st.session_state:
            st.session_state.domande_risposte_totali += 1
        if st.session_state.modalita_esame:
            salta_domanda_esame()
        else:
            nuova_domanda()
            st.rerun()

# ==============================
# 8. MODALITÀ ESAME
# ==============================

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
if 'quiz_df' in st.session_state:
    if 'domande_risposte_totali' not in st.session_state:
        st.session_state.domande_risposte_totali = 0

st.sidebar.markdown("---")
st.session_state.modalita_esame = st.sidebar.checkbox(
    "📝 Modalità ESAME (33 domande)",
    value=st.session_state.modalita_esame
)

if st.session_state.modalita_esame:
    progress_value = min(st.session_state.domande_esame_fatte / MAX_DOMANDE_ESAME, 1.0)
    st.progress(progress_value)
    st.write(
        f"📊 **Domande:** {st.session_state.domande_esame_fatte}/{MAX_DOMANDE_ESAME} | "
        f"🎯 **Punteggio:** {round(st.session_state.punteggio, 2)}"
    )

# Calcolo Punteggio
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
    
# Fine Esame
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