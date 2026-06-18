import streamlit as st
import pandas as pd
import random
import os
import re
import streamlit.components.v1 as components # <--- AGGIUNGI QUESTO
# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Dynamic Quiz Loader", page_icon="🚽", layout="wide")

# --- COSTANTI GLOBALI ---
MAX_DOMANDE_ESAME = 33

# --- 1. FUNZIONI UTILITY ---

def crea_csv_esempio_se_mancano():
    """Crea un file di test in csv/ se non ci sono quiz disponibili."""
    csv_dir = 'csv'
    os.makedirs(csv_dir, exist_ok=True)
    files_csv = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
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
        pd.DataFrame(data_demo).to_csv(os.path.join(csv_dir, 'Quiz_Demo.csv'), index=False)

def get_lista_quiz():
    """Scansiona csv/ e md/ e restituisce home, quizzes e cheatsheets."""
    crea_csv_esempio_se_mancano()
    csv_dir = 'csv'
    md_dir = 'md'
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(md_dir, exist_ok=True)

    quizzes = {}
    cheatsheets = {}

    if os.path.isdir(csv_dir):
        for f in os.listdir(csv_dir):
            if f.endswith('.csv'):
                nome_pulito = f.replace('.csv', '').replace('_', ' ').title()
                quizzes[nome_pulito] = os.path.join(csv_dir, f)

    if os.path.isdir(md_dir):
        for root, dirs, files in os.walk(md_dir):
            for f in files:
                if f.endswith('.md'):
                    rel_path = os.path.relpath(root, md_dir)
                    if rel_path == '.':
                        category = 'OTHER'
                    else:
                        category = rel_path.upper()
                    nome_pulito = f.replace('.md', '').replace('_', ' ')
                    label = f"{category} {nome_pulito}"
                    cheatsheets[label] = os.path.join(root, f)

    readme_item = 'README.md' if os.path.exists('README.md') else None
    return readme_item, quizzes, cheatsheets


def parse_cheatsheet_category(label):
    """Estrae categoria e ordine numerico da un nome di cheatsheet."""
    if label.startswith("📤 "):
        label = label[2:]
    label = label.strip()
    parts = label.split()
    if not parts:
        return "Other", 999, label

    category = parts[0].upper()
    order = None
    if len(parts) > 1:
        match = re.match(r'^(\d+)', parts[1])
        if match:
            order = int(match.group(1))

    if order is None:
        match = re.search(r'(\d+)', label)
        if match:
            order = int(match.group(1))

    # Compute display
    display = ' '.join(parts[1:]) if len(parts) > 1 else label
    if display and display[0].isdigit():
        space_index = display.find(' ')
        if space_index != -1:
            display = display[:space_index] + '. ' + display[space_index+1:]

    return category, order if order is not None else 999, display


def build_cheatsheet_categories(cheatsheet_map):
    categories = {}
    for label, item in cheatsheet_map.items():
        category, order, display = parse_cheatsheet_category(label)
        categories.setdefault(category, []).append((order, display, item))

    for cat, items in categories.items():
        items.sort(key=lambda x: (x[0], x[1]))
        categories[cat] = items

    return dict(sorted(categories.items(), key=lambda x: x[0]))

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
if 'answer_already_counted' not in st.session_state:
    st.session_state.answer_already_counted = False

def reset_quiz_state():
    """Resetta completamente lo stato quando si cambia quiz."""
    st.session_state.domanda_corrente = None
    st.session_state.fase = 'selezione'
    st.session_state.selezione_utente = None
    st.session_state.opzioni_mix = []
    st.session_state.answer_already_counted = False
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
st.sidebar.write("Seleziona una sezione:")

readme_item, quiz_map, cheatsheet_map = get_lista_quiz()

# --- CARICA CSV PERSONALIZZATO ---
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Carica Quiz o Cheatsheet Markdown")

uploaded_file = st.sidebar.file_uploader("Scegli un file CSV o MD", type=['csv', 'md'])

if uploaded_file is not None:
    try:
        uploaded_name = uploaded_file.name
        if uploaded_name.lower().endswith('.md'):
            raw_bytes = uploaded_file.getvalue()
            try:
                markdown_text = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                markdown_text = raw_bytes.decode('latin-1')

            nome_file = uploaded_name.replace('.md', '')
            nome_pulito = nome_file.replace('_', ' ').title()
            cheatsheet_map[f"📤 {nome_pulito}"] = {'type': 'md', 'content': markdown_text}
            st.sidebar.success("✅ Markdown caricato con successo!")
        else:
            # Leggi il file caricato
            uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8-sig', sep=',')
            uploaded_df.columns = [c.strip().replace('\ufeff', '') for c in uploaded_df.columns]
            
            # Valida le colonne richieste
            colonne_richieste = ['domanda', 'opzioneA', 'opzioneB', 'opzioneC', 'soluzione']
            if all(col in uploaded_df.columns for col in colonne_richieste):
                nome_file = uploaded_name.replace('.csv', '')
                nome_pulito = nome_file.replace('_', ' ').title()
                quiz_map[f"📤 {nome_pulito}"] = uploaded_df
                st.sidebar.success("✅ CSV caricato con successo!")
            else:
                st.sidebar.error(f"❌ Colonne mancanti. Richieste: {', '.join(colonne_richieste)}")
    except Exception as e:
        st.sidebar.error(f"❌ Errore caricamento: {str(e)}")

st.sidebar.markdown("---")

if not quiz_map and not cheatsheet_map and readme_item is None:
    st.error("Nessun file CSV o MD trovato nella cartella!")
    st.stop()

section_options = []
if readme_item is not None:
    section_options.append("Home")
if quiz_map:
    section_options.append("Quiz")
if cheatsheet_map:
    section_options.append("Cheatsheets")

selected_section = st.sidebar.radio(
    "Seleziona sezione:",
    section_options,
    index=0,
    on_change=reset_quiz_state,
    key="section_selection"
)

scelta_utente = None
file_selezionato = None
if selected_section == "Home":
    scelta_utente = "Home"
    file_selezionato = readme_item
elif selected_section == "Quiz":
    scelta_utente = st.sidebar.radio(
        "Quiz disponibili:",
        list(quiz_map.keys()),
        on_change=reset_quiz_state,
        key="quiz_selection"
    )
    file_selezionato = quiz_map[scelta_utente]
else:
    cheatsheet_categories = build_cheatsheet_categories(cheatsheet_map)
    category_options = list(cheatsheet_categories.keys())
    selected_category = st.sidebar.selectbox(
        "Categoria Cheatsheets:",
        category_options,
        key="cheatsheet_category"
    )

    cheatsheet_items = cheatsheet_categories[selected_category]
    cheatsheet_labels = [label for _, label, _ in cheatsheet_items]
    scelta_utente = st.sidebar.radio(
        "Cheatsheet disponibili:",
        cheatsheet_labels,
        on_change=reset_quiz_state,
        key="cheatsheet_selection"
    )
    file_selezionato = next(
        item for order, label, item in cheatsheet_items if label == scelta_utente
    )

# --- PRACTICE MODE TOGGLE ---
st.sidebar.markdown("---")
if st.session_state.wrong_answers or st.session_state.practice_mode:
    if st.session_state.wrong_answers:
        st.sidebar.write(f"❌ Risposte sbagliate: **{len(st.session_state.wrong_answers)}**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # Toggle logic handles the rerun
        if st.button("🔄 Pratica" if not st.session_state.practice_mode else "⏸️ Esci Pratica", use_container_width=True):
            st.session_state.practice_mode = not st.session_state.practice_mode
            st.session_state.idx = 0
            st.session_state.domanda_corrente = None
            reset_quiz_state()
            st.rerun()
    with col2:
        if st.button("🗑️ Cancella", use_container_width=True):
            st.session_state.wrong_answers = []
            st.session_state.practice_mode = False
            st.rerun()

@st.cache_data
def load_markdown(file_item):
    """Carica il contenuto di un file Markdown locale o caricato."""
    try:
        if isinstance(file_item, dict) and file_item.get('type') == 'md':
            return file_item.get('content', '')
        if isinstance(file_item, str):
            with open(file_item, 'r', encoding='utf-8') as f:
                return f.read()
        if hasattr(file_item, 'read'):
            raw = file_item.read()
            if isinstance(raw, bytes):
                try:
                    return raw.decode('utf-8')
                except UnicodeDecodeError:
                    return raw.decode('latin-1')
            return str(raw)
    except UnicodeDecodeError:
        if isinstance(file_item, str):
            with open(file_item, 'r', encoding='latin-1') as f:
                return f.read()
    except Exception as e:
        st.error(f"Errore caricamento Markdown: {e}")
    return ''


def is_markdown_file(item):
    if isinstance(item, dict) and item.get('type') == 'md':
        return True
    if isinstance(item, str) and item.lower().endswith('.md'):
        return True
    if hasattr(item, 'name') and isinstance(item.name, str) and item.name.lower().endswith('.md'):
        return True
    return False

# --- 4. CARICAMENTO DATI ---
if is_markdown_file(file_selezionato):
    markdown_content = load_markdown(file_selezionato)
    
    # 1. AGGIUNGI L'UI DEL PROGRESSO NELLA SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="padding: 5px 0;">
            <div id="sidebar-scroll-text" style="text-align: center; font-size: 13px; font-weight: bold; margin-top: 4px;">0.00 %</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 2. SCRIPT JAVASCRIPT AGGIORNATO
    js_code = f"""
    <script>
        // ID univoco per forzare il re-render: {scelta_utente}
        const doc = window.parent.document;
        
        // 1. SCROLL TO TOP
        const mainDiv = doc.querySelector('.stMain') || doc.documentElement;
        if (mainDiv) {{
            mainDiv.scrollTop = 0;
        }}
        window.parent.scrollTo(0, 0);

        // 2. PULIZIA FONDAMENTALE PRECEDENTE BARRA (Failsafe)
        const oldContainer = doc.getElementById('reading-progress-container');
        if (oldContainer) oldContainer.remove();
        
        if (window.parent._scrollListener) {{
            doc.removeEventListener('scroll', window.parent._scrollListener, true);
        }}

        // 3. CREAZIONE NUOVA PROGRESS BAR TOP
        const container = doc.createElement('div');
        container.id = 'reading-progress-container';
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100%';
        container.style.height = '5px';
        container.style.backgroundColor = 'transparent';
        container.style.zIndex = '9999999';
        
        const bar = doc.createElement('div');
        bar.id = 'reading-progress-bar';
        bar.style.height = '100%';
        bar.style.width = '0%';
        bar.style.backgroundColor = '#FF4B4B'; 
        bar.style.transition = 'width 0.1s ease';
        bar.style.borderRadius = '0 2px 2px 0';
        
        container.appendChild(bar);
        doc.body.appendChild(container);
        
        // 4. FUNZIONE DI AGGIORNAMENTO SCROLL (Modificata per la sidebar)
        window.parent._scrollListener = () => {{
            const scrollElement = doc.querySelector('.stMain') || doc.documentElement;
            const scrollTop = scrollElement.scrollTop || doc.body.scrollTop;
            const scrollHeight = scrollElement.scrollHeight || doc.body.scrollHeight;
            const clientHeight = scrollElement.clientHeight || doc.documentElement.clientHeight;
            
            const sidebarText = doc.getElementById('sidebar-scroll-text');
            const sidebarBar = doc.getElementById('sidebar-scroll-bar');
            
            const height = scrollHeight - clientHeight;
            let percentage = 0;
            
            if (height > 0) {{
                percentage = (scrollTop / height) * 100;
                // Previeni valori oltre il 100% o sotto lo 0% a causa del rimbalzo dello scroll (overscroll)
                percentage = Math.min(Math.max(percentage, 0), 100); 
            }} else {{
                percentage = 100;
            }}
            
            const widthStr = percentage + '%';
            const textStr = percentage.toFixed(2) + ' %';
            
            // Aggiorna UI Superiore
            bar.style.width = widthStr;
            
            // Aggiorna UI Sidebar
            if (sidebarText) sidebarText.innerText = textStr;
            if (sidebarBar) sidebarBar.style.width = widthStr;
        }};
        
        // Esegui subito per inizializzare i valori se la pagina è corta
        window.parent._scrollListener();
        
        // Attacchiamo l'evento
        doc.addEventListener('scroll', window.parent._scrollListener, true);

        // 5. CLEANUP QUANDO SI CAMBIA PAGINA O SEZIONE
        window.addEventListener('unload', () => {{
            if (container && container.parentNode) {{
                container.parentNode.removeChild(container);
            }}
            if (window.parent._scrollListener) {{
                doc.removeEventListener('scroll', window.parent._scrollListener, true);
                window.parent._scrollListener = null;
            }}
        }});
    </script>
    """
    
    components.html(js_code, height=0, width=0)
    
    st.title(scelta_utente)
    st.write("---")
    st.markdown(markdown_content)
    st.stop()


@st.cache_data
def load_data(filename):
    """
    Carica un CSV di quiz in modo robusto.
    Se filename è un DataFrame, lo restituisce direttamente.
    """
    try:
        # Se è già un DataFrame (caricato da file uploader), restituiscilo
        if isinstance(filename, pd.DataFrame):
            df = filename.copy()
        else:
            # Altrimenti carica da file
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


def load_practice_data():
    """Carica i dati per la modalità pratica dalle risposte sbagliate."""
    if st.session_state.wrong_answers:
        df_practice = pd.DataFrame(st.session_state.wrong_answers)
        if len(df_practice) > 0:
            # Rimuovi la colonna original_index se esiste
            if 'original_index' in df_practice.columns:
                df_practice = df_practice.drop(columns=['original_index'])
            return df_practice.sample(frac=1).reset_index(drop=True)
    return None

if st.session_state.practice_mode:
    # Pratica modalità: usa solo risposte sbagliate
    df = load_practice_data()
    if df is None:
        df = load_data(file_selezionato)
        st.session_state.practice_mode = False
else:
    df = load_data(file_selezionato)

if df is None:
    st.error(f"Errore nella lettura del file {file_selezionato}.")
    st.stop()

# --- FIX APPLICATO QUI ---
# Abbiamo rimosso la logica che resettava le wrong_answers quando practice_mode era True
if 'quiz_df' not in st.session_state or st.session_state.get('current_quiz_name') != scelta_utente or st.session_state.get('last_practice_mode') != st.session_state.practice_mode:
    st.session_state.current_quiz_name = scelta_utente
    st.session_state.last_practice_mode = st.session_state.practice_mode
    st.session_state.quiz_df = df.sample(frac=1).reset_index(drop=True)
    st.session_state.idx = 0
    reset_quiz_state()
    st.session_state.domanda_corrente = None
    
    # !!! HO RIMOSSO QUESTE LINEE !!!
    # if st.session_state.practice_mode:
    #    reset_wrong_answers()

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
        if st.session_state.practice_mode:
             st.success("🎉 Pratica finita! Torno alla modalità normale.")
             st.session_state.practice_mode = False
             st.session_state.idx = 0
             reset_quiz_state()
             st.rerun()
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
    if str(st.session_state.selezione_utente).strip().lower() != str(corretta).strip().lower():
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
    if (str(st.session_state.selezione_utente).strip().lower() == str(corretta).strip().lower() and st.session_state.practice_mode):        
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
        # Se col è il modulo st, chiama direttamente st.button()
        if isinstance(col, type(st)):
            st.button(
                option_text if option_text else "(vuoto)",
                key=key,
                use_container_width=True,
                on_click=gestisci_click,
                args=(option_text,)
            )
        else:
            # Altrimenti usa col come context manager (per colonne)
            with col:
                st.button(
                    option_text if option_text else "(vuoto)",
                    key=key,
                    use_container_width=True,
                    on_click=gestisci_click,
                    args=(option_text,)
                )

# Rendering griglia
q_idx = st.session_state.idx 

if ha_opzioneD:
    render_button_with_feedback(opts[0], f"b0_{q_idx}", c1)
    render_button_with_feedback(opts[1], f"b1_{q_idx}", c2)
    render_button_with_feedback(opts[2], f"b2_{q_idx}", c1)
    render_button_with_feedback(opts[3], f"b3_{q_idx}", c2)
else:
    render_button_with_feedback(opts[0], f"b0_{q_idx}", st)
    render_button_with_feedback(opts[1], f"b1_{q_idx}", st)
    render_button_with_feedback(opts[2], f"b2_{q_idx}", st)

st.write("---")

# --- Feedback & Navigazione ---

if st.session_state.fase == 'verificato':
    sel_utente = str(st.session_state.selezione_utente).strip()
    
    # Traccia la risposta (solo una volta)
    if not st.session_state.answer_already_counted:
        if not st.session_state.practice_mode:
            track_wrong_answer()
        else:
            remove_correct_from_wrong_list()
        st.session_state.answer_already_counted = True
    


    if st.button("PROSSIMA DOMANDA", type="primary", use_container_width=True):
        st.session_state.answer_already_counted = False
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
    if motivazione and str(motivazione) != "nan":
        st.info(f"**Motivazione:**\n\n{motivazione}")
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

    sel = str(st.session_state.selezione_utente).strip().lower()
    corr = str(corretta).strip().lower()

    if sel == corr:
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
