import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os
from fpdf import FPDF
import random

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Gestionale Ordini & Preventivi (Demo)",
    page_icon="📦",
    layout="wide"
)

# Banner Demo Permanente in cima a tutte le schermate
st.markdown(
    """
    <div style="background-color: #ff4b4b; color: white; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        ⚠️ VERSIONE DEMO DI PROVA - NAGEST GESTIONALE (Funzionalità limitate)
    </div>
    """,
    unsafe_allow_html=True
)

# Connessione / Inizializzazione Database SQLite
DB_FILE = "gestionale_ordini.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabella Principale Ordini
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordini (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_ordine TEXT,
            fornitore TEXT,
            data_ordine TEXT,
            data_consegna TEXT,
            mandato_stampa_il TEXT,
            ditta TEXT,
            referente TEXT,
            note_stampa TEXT,
            stato TEXT DEFAULT 'In arrivo',
            allegati TEXT
        )
    ''')
    
    # Tabella Dettagli Articoli Ordini
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordini_dettagli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordine_id INTEGER,
            articolo TEXT,
            quantita INTEGER,
            descrizione TEXT,
            colore_articolo TEXT,
            colore_stampa TEXT,
            posizione_stampa TEXT,
            stampa TEXT,
            fornitore_articolo TEXT,
            numero_ordine_articolo TEXT,
            FOREIGN KEY (ordine_id) REFERENCES ordini (id) ON DELETE CASCADE
        )
    ''')

    # Tabelle dedicate per i Preventivi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preventivi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_preventivo TEXT,
            data_preventivo TEXT,
            ditta TEXT,
            referente TEXT,
            note TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preventivi_dettagli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preventivo_id INTEGER,
            descrizione TEXT,
            quantita INTEGER,
            prezzo REAL,
            subtotale REAL,
            iva_perc REAL,
            FOREIGN KEY (preventivo_id) REFERENCES preventivi (id) ON DELETE CASCADE
        )
    ''')

    # Tabella dedicata per i Memo di Bottega
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memo_bottega (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testo TEXT,
            data_inserimento TEXT
        )
    ''')

    # Tabella dedicata per il "Cervello"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cervello (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            lavorazione TEXT,
            descrizione TEXT,
            mandato_il TEXT,
            da_chi TEXT,
            fatto INTEGER DEFAULT 0
        )
    ''')
    
    # Migrazioni e verifiche colonne ordini
    cursor.execute("PRAGMA table_info(ordini)")
    columns = [col[1] for col in cursor.fetchall()]
    if "numero_ordine" not in columns:
        cursor.execute("ALTER TABLE ordini ADD COLUMN numero_ordine TEXT")
    if "fornitore" not in columns:
        cursor.execute("ALTER TABLE ordini ADD COLUMN fornitore TEXT")
    if "stato" not in columns:
        cursor.execute("ALTER TABLE ordini ADD COLUMN stato TEXT DEFAULT 'In arrivo'")
    if "mandato_stampa_il" not in columns:
        cursor.execute("ALTER TABLE ordini ADD COLUMN mandato_stampa_il TEXT")
    if "allegati" not in columns:
        cursor.execute("ALTER TABLE ordini ADD COLUMN allegati TEXT")
    
    cursor.execute("PRAGMA table_info(ordini_dettagli)")
    det_columns = [col[1] for col in cursor.fetchall()]
    if "fornitore_articolo" not in det_columns:
        cursor.execute("ALTER TABLE ordini_dettagli ADD COLUMN fornitore_articolo TEXT")
    if "numero_ordine_articolo" not in det_columns:
        cursor.execute("ALTER TABLE ordini_dettagli ADD COLUMN numero_ordine_articolo TEXT")
    
    conn.commit()
    conn.close()

init_db()

# Funzione per popolare dati demo nel database
def popola_dati_demo():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM ordini")
    count_ord = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM preventivi")
    count_prev = cursor.fetchone()[0]
    
    if count_ord < 5:
        cursor.execute('''
            INSERT INTO ordini (numero_ordine, fornitore, data_ordine, data_consegna, mandato_stampa_il, ditta, referente, note_stampa, stato, allegati)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("DEMO-01", "Fornitore Tessile SRL", str(date.today()), str(date.today()), None, "Moda Style SpA", "Mario Rossi", "Stampa serigrafica frontale a 2 colori.", "In arrivo", ""))
        o_id1 = cursor.lastrowid
        cursor.execute('''
            INSERT INTO ordini_dettagli (ordine_id, articolo, quantita, descrizione, colore_articolo, colore_stampa, posizione_stampa, stampa, fornitore_articolo, numero_ordine_articolo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (o_id1, "T-Shirt Cotone", 40, "Maglietta promozionale personalizzata", "Nero", "Bianco", "Petto", "serigrafia", "Fornitore Tessile", "ORD-FT-11"))

        cursor.execute('''
            INSERT INTO ordini (numero_ordine, fornitore, data_ordine, data_consegna, mandato_stampa_il, ditta, referente, note_stampa, stato, allegati)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("DEMO-02", "Gadget Express", str(date.today()), str(date.today()), str(date.today()), "Bar Sport Centrale", "Giulia Bianchi", "Applicazione DTF multicolor ad alta definizione.", "Mandati in stampa", ""))
        o_id2 = cursor.lastrowid
        cursor.execute('''
            INSERT INTO ordini_dettagli (ordine_id, articolo, quantita, descrizione, colore_articolo, colore_stampa, posizione_stampa, stampa, fornitore_articolo, numero_ordine_articolo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (o_id2, "Shopper Bag", 100, "Borsa in cotone ecologico", "Natural", "Full Color", "Fronte", "dtf", "Gadget Express", "GE-99"))

    if count_prev < 3:
        cursor.execute('''
            INSERT INTO preventivi (numero_preventivo, data_preventivo, ditta, referente, note)
            VALUES (?, ?, ?, ?, ?)
        ''', ("101", str(date.today()), "Officina Creativa", "Luca Verdi", "Preventivo promozionale valido 30 giorni."))
        p_id1 = cursor.lastrowid
        cursor.execute('''
            INSERT INTO preventivi_dettagli (preventivo_id, descrizione, quantita, prezzo, subtotale, iva_perc)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (p_id1, "Felpe personalizzate con ricamo logo", 25, 30.0, 750.0, 22.0))

    conn.commit()
    conn.close()

# Funzioni di utilità per la pulizia del testo
def clean_val(val, default=""):
    if val is None:
        return default
    if isinstance(val, float) and pd.isna(val):
        return default
    s = str(val).strip()
    if s.lower() in ["nan", "none"]:
        return default
    return s

def clean_int(val, default=1):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return int(val)
    except:
        return default

def clean_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(val)
    except:
        return default

def clean_pdf_text(text):
    if text is None:
        return ""
    text_str = str(text)
    text_str = text_str.replace("€", "euro").replace("’", "'").replace("“", '"').replace("”", '"')
    return text_str.encode('latin-1', 'replace').decode('latin-1')

# Classe per generare il PDF Ordine (Orizzontale)
class PDFOrder(FPDF):
    def header(self):
        y_start = 10
        if os.path.exists("logo.png"):
            try:
                self.image("logo.png", x=10, y=y_start, h=18)
                self.set_xy(50, y_start)
            except Exception:
                self.set_xy(10, y_start)
        else:
            self.set_xy(10, y_start)
        
        self.set_font('Arial', 'B', 14)
        self.cell(0, 7, 'IL TUO LOGO - LABORATORIO DI STAMPA', 0, 1, 'L')
        self.set_x(self.get_x())
        self.set_font('Arial', 'B', 11)
        self.cell(0, 6, 'MANDATO IN STAMPA / BOZZA ORDINE (DEMO)', 0, 1, 'L')
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, clean_pdf_text(f'Pagina {self.page_no()}'), 0, 0, 'C')

# Classe per generare il PDF Preventivo
class PDFPreventivo(FPDF):
    def header(self):
        if os.path.exists("logopreventivo.png"):
            try:
                self.image("logopreventivo.png", x=75, y=8, w=60)
                self.set_y(32)
            except Exception:
                self.set_y(15)
        else:
            self.set_y(15)
            
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-45)
        self.set_font('Arial', 'I', 6)
        conditions = (
            "Prezzi: I prezzi indicati sono validi al momento della compilazione del preventivo e sono soggetti a variazioni in base alla quantita, "
            "alla complessita del progetto e ad eventuali personalizzazioni richieste.\n"
            "File: Si prega di notare che non ci assumiamo responsabilita per eventuali errori presenti nei file forniti.\n"
            "Tempi di lavorazione: I tempi di lavorazione e progettazione indicati sono approssimativi e si basano su una stima di 15/20 giorni lavorativi.\n"
            "Spedizione: Le informazioni riguardanti la spedizione sono fornite a titolo informativo e sono soggette a variazioni."
        )
        self.multi_cell(0, 3, clean_pdf_text(conditions), 0, 'L')
        self.ln(2)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 8, clean_pdf_text(f'Pagina {self.page_no()}'), 0, 0, 'C')

def generate_pdf_ordine(ordine, dettagli):
    pdf = PDFOrder(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Arial', '', 9)
    pdf.set_fill_color(240, 240, 240)
    
    pdf.cell(138.5, 6, clean_pdf_text(f"N. Ordine: {ordine['numero_ordine'] or ''}"), 1, 0, 'L', True)
    pdf.cell(138.5, 6, clean_pdf_text(f"Ditta: {ordine['ditta'] or ''}"), 1, 1, 'L', True)
    
    pdf.cell(138.5, 6, clean_pdf_text(f"Fornitore Generale: {ordine['fornitore'] or ''}"), 1, 0, 'L', True)
    pdf.cell(138.5, 6, clean_pdf_text(f"Referente: {ordine['referente'] or ''}"), 1, 1, 'L', True)
    
    pdf.cell(138.5, 6, clean_pdf_text(f"Data Ordine: {ordine['data_ordine'] or ''}"), 1, 0, 'L', True)
    pdf.cell(138.5, 6, clean_pdf_text(f"Data Consegna: {ordine['data_consegna'] or ''}"), 1, 1, 'L', True)
    
    mandato_str = ordine['mandato_stampa_il'] if ordine['mandato_stampa_il'] else 'Non ancora inviato'
    pdf.cell(138.5, 6, clean_pdf_text(f"Mandato in Stampa il: {mandato_str}"), 1, 0, 'L', True)
    pdf.cell(138.5, 6, clean_pdf_text(f"Stato: {ordine['stato'] or ''}"), 1, 1, 'L', True)
    
    pdf.ln(4)
    
    if ordine['note_stampa']:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "Note di Stampa:", 0, 1, 'L')
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 5, clean_pdf_text(ordine['note_stampa']), 1, 'L')
        pdf.ln(4)
        
    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(220, 225, 230)
    
    headers = ['Articolo', 'Q.ta', 'Descrizione', 'Col. Art.', 'Col. Stampa', 'Posizione', 'Stampa', 'Fornitore', 'N. Ord. Art.']
    widths = [30, 12, 70, 28, 28, 25, 22, 32, 30]  # Totale 277 mm
    
    for i, h in enumerate(headers):
        pdf.cell(widths[i], 7, clean_pdf_text(h), 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_font('Arial', '', 7)
    
    for row in dettagli:
        valori = [
            clean_pdf_text(row['articolo'] or ''),
            clean_pdf_text(row['quantita'] or ''),
            clean_pdf_text(row['descrizione'] or ''),
            clean_pdf_text(row['colore_articolo'] or ''),
            clean_pdf_text(row['colore_stampa'] or ''),
            clean_pdf_text(row['posizione_stampa'] or ''),
            clean_pdf_text(row['stampa'] or ''),
            clean_pdf_text(row['fornitore_articolo'] or ''),
            clean_pdf_text(row['numero_ordine_articolo'] or '')
        ]
        
        num_lines = []
        for i, text in enumerate(valori):
            w = widths[i]
            lines = pdf.get_string_width(text) / max(1, (w - 2))
            num_lines.append(max(1, int(lines) + 1))
        
        max_lines = max(num_lines)
        row_height = max_lines * 5
        
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        if y_start + row_height > 195:
            pdf.add_page()
            y_start = pdf.get_y()
            x_start = pdf.get_x()
            
            pdf.set_font('Arial', 'B', 8)
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 7, clean_pdf_text(h), 1, 0, 'C', True)
            pdf.ln()
            pdf.set_font('Arial', '', 7)
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
        for i, text in enumerate(valori):
            w = widths[i]
            align = 'C' if i != 2 else 'L'
            
            pdf.rect(x_start, y_start, w, row_height)
            pdf.set_xy(x_start, y_start + (1 if max_lines == 1 else 0.5))
            pdf.multi_cell(w, 4, text, border=0, align=align)
            
            x_start += w
            
        pdf.set_xy(10, y_start + row_height)

    return pdf.output(dest='S').encode('latin-1')

def generate_pdf_preventivo(prev, dettagli):
    pdf = PDFPreventivo(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=50)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 6, clean_pdf_text(f"Preventivo # {prev['numero_preventivo'] or prev['id']}"), 0, 1, 'L')
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, clean_pdf_text(f"Spett.le Ditta: {prev['ditta'] or ''}"), 0, 1, 'L')
    pdf.cell(0, 5, clean_pdf_text(f"Referente: {prev['referente'] or ''}    -    Data: {prev['data_preventivo'] or ''}"), 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(220, 225, 230)
    
    widths = [85, 20, 25, 30, 30]
    headers = ['Descrizione', 'Quantita', 'Prezzo unit.', 'Subtotale', 'IVA (%)']
    
    for i, h in enumerate(headers):
        pdf.cell(widths[i], 7, clean_pdf_text(h), 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    tot_subtotale = 0.0
    tot_iva = 0.0
    
    for row in dettagli:
        desc = str(row['descrizione'] or '')
        qta = int(row['quantita'] or 1)
        prezzo = float(row['prezzo'] or 0.0)
        subtot = qta * prezzo
        iva_perc = float(row['iva_perc'] or 22.0)
        iva_val = subtot * (iva_perc / 100.0)
        
        tot_subtotale += subtot
        tot_iva += iva_val
        
        pdf.cell(widths[0], 6, clean_pdf_text(desc), 1, 0, 'L')
        pdf.cell(widths[1], 6, str(qta), 1, 0, 'C')
        pdf.cell(widths[2], 6, clean_pdf_text(f"{prezzo:.2f} euro"), 1, 0, 'R')
        pdf.cell(widths[3], 6, clean_pdf_text(f"{subtot:.2f} euro"), 1, 0, 'R')
        pdf.cell(widths[4], 6, f"{iva_perc:.0f}%", 1, 1, 'C')
        
    totale_generale = tot_subtotale + tot_iva
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(130, 6, "", 0, 0)
    pdf.cell(35, 6, "SUBTOTALE", 1, 0, 'L', True)
    pdf.cell(25, 6, clean_pdf_text(f"{tot_subtotale:.2f} euro"), 1, 1, 'R')
    
    pdf.cell(130, 6, "", 0, 0)
    pdf.cell(35, 6, "IVA", 1, 0, 'L', True)
    pdf.cell(25, 6, clean_pdf_text(f"{tot_iva:.2f} euro"), 1, 1, 'R')
    
    pdf.cell(130, 6, "", 0, 0)
    pdf.cell(35, 6, "TOTALE", 1, 0, 'L', True)
    pdf.cell(25, 6, clean_pdf_text(f"{totale_generale:.2f} euro"), 1, 1, 'R')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, "Cordiali saluti,", 0, 1, 'L')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "IL TUO LABORATORIO DI STAMPA", 0, 1, 'L')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA UTENTE ---

opzioni_navigazione = [
    "🏠 Dashboard (Panoramica)", 
    "➕ Nuovo Ordine", 
    "✏️ Modifica Ordine", 
    "📄 Preventivi", 
    "📂 Tutti gli Ordini", 
    "⏳ In arrivo", 
    "🖨️ Mandati in stampa", 
    "✅ Completati",
    "🧠 Cervello",
    "🎮 Pausa Caffè (Mini-Game)"
]

if "sezione_attiva" not in st.session_state:
    st.session_state["sezione_attiva"] = opzioni_navigazione[0]

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("🧭 Navigazione Rapida")

def cambia_sezione():
    st.session_state["sezione_attiva"] = st.session_state["menu_radio"]

sezione = st.sidebar.radio(
    "Scegli sezione:", 
    opzioni_navigazione,
    index=opzioni_navigazione.index(st.session_state["sezione_attiva"]),
    key="menu_radio",
    on_change=cambia_sezione,
    label_visibility="collapsed"
)

# Pannello Demo nella Sidebar per caricare i dati d'esempio con un click
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Strumenti Demo")
if st.sidebar.button("📥 Popola Dati di Prova", use_container_width=True):
    popola_dati_demo()
    st.sidebar.success("Dati demo caricati con successo!")
    st.rerun()

sezione_corrente = st.session_state["sezione_attiva"]

# --- SCHERMATA: DASHBOARD (Con Lavagna Memo di Bottega) ---
if sezione_corrente == "🏠 Dashboard (Panoramica)":
    st.title("📊 Dashboard - Panoramica Ordini (DEMO)")
    st.info("Benvenuto nel gestionale (Versione di Prova).")
    
    conn = get_db_connection()
    df_all = pd.read_sql_query("SELECT * FROM ordini", conn)
    conn.close()
    
    tot_ordini = len(df_all)
    tot_arrivo = len(df_all[df_all['stato'] == 'In arrivo']) if not df_all.empty else 0
    tot_stampa = len(df_all[df_all['stato'] == 'Mandati in stampa']) if not df_all.empty else 0
    tot_completati = len(df_all[df_all['stato'] == 'Completati']) if not df_all.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Totale Ordini", tot_ordini)
    col2.metric("⏳ In Arrivo", tot_arrivo)
    col3.metric("🖨️ Mandati in Stampa", tot_stampa)
    col4.metric("✅ Completati", tot_completati)
    
    st.markdown("---")
    st.subheader("🚀 Azioni Veloci")
    c_A, c_B, c_C, c_D = st.columns(4)
    with c_A:
        if st.button("➕ Nuovo Ordine", use_container_width=True):
            st.session_state["sezione_attiva"] = "➕ Nuovo Ordine"
            st.rerun()
    with c_B:
        if st.button("📄 Preventivo", use_container_width=True):
            st.session_state["sezione_attiva"] = "📄 Preventivi"
            st.rerun()
    with c_C:
        if st.button("📂 Archivio", use_container_width=True):
            st.session_state["sezione_attiva"] = "📂 Tutti gli Ordini"
            st.rerun()
    with c_D:
        if st.button("🧠 Cervello", use_container_width=True):
            st.session_state["sezione_attiva"] = "🧠 Cervello"
            st.rerun()

    # --- LAVAGNA MEMO DI BOTTEGA ---
    st.markdown("---")
    st.subheader("📌 Lavagna dei 'Memo di Bottega'")
    st.write("Post-it rapidi condivisi per il team di laboratorio:")

    with st.form("form_nuovo_memo", clear_on_submit=True):
        c_memo1, c_memo2 = st.columns([4, 1])
        with c_memo1:
            nuovo_testo_memo = st.text_input("Scrivi un nuovo memo:", placeholder="Es. Ricordarsi di ordinare felpe nere taglia L...", label_visibility="collapsed")
        with c_memo2:
            btn_aggiungi_memo = st.form_submit_button("➕ Appatta Post-it", use_container_width=True)
            
        if btn_aggiungi_memo:
            if nuovo_testo_memo.strip():
                conn_m = get_db_connection()
                cur_m = conn_m.cursor()
                cur_m.execute("INSERT INTO memo_bottega (testo, data_inserimento) VALUES (?, ?)", 
                              (nuovo_testo_memo.strip(), str(date.today())))
                conn_m.commit()
                conn_m.close()
                st.success("Post-it aggiunto alla lavagna!")
                st.rerun()
            else:
                st.warning("Il testo del memo non può essere vuoto.")

    conn_m = get_db_connection()
    df_memos = pd.read_sql_query("SELECT * FROM memo_bottega ORDER BY id DESC", conn_m)
    conn_m.close()

    if df_memos.empty:
        st.info("💡 Nessun memo presente sulla lavagna al momento. Scrivi il primo qui sopra!")
    else:
        memos_cols = st.columns(3)
        for index, row in df_memos.iterrows():
            target_col = memos_cols[index % 3]
            with target_col:
                st.markdown(f"""
                <div style="background-color: #fff9c4; padding: 15px; border-radius: 6px; border-left: 6px solid #fbc02d; margin-bottom: 12px; box-shadow: 2px 2px 6px rgba(0,0,0,0.08); color: #222;">
                    <strong>📝 Memo #{row['id']}</strong> <span style="font-size: 0.8em; color: #666;">({row['data_inserimento']})</span><br><br>
                    {row['testo']}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Rimuovi Post-it", key=f"del_memo_{row['id']}", use_container_width=True):
                    conn_del = get_db_connection()
                    cur_del = conn_del.cursor()
                    cur_del.execute("DELETE FROM memo_bottega WHERE id = ?", (row['id'],))
                    conn_del.commit()
                    conn_del.close()
                    st.rerun()

# --- SCHERMATA: CERVELLO (PROTETTA DA PASSWORD) ---
elif sezione_corrente == "🧠 Cervello":
    st.title("🧠 Cervello - Centrale Operativa")
    
    if "cervello_sbloccato" not in st.session_state:
        st.session_state["cervello_sbloccato"] = False
        
    if not st.session_state["cervello_sbloccato"]:
        st.warning("🔒 Questa sezione è protetta da password.")
        st.info("💡 **Prova a usare il cervello!** La password per sbloccare la demo è: **prova**")
        pwd = st.text_input("Inserisci la password:", type="password", key="pwd_cervello")
        if st.button("Sblocca Sezione", type="primary"):
            if pwd == "prova":
                st.session_state["cervello_sbloccato"] = True
                st.success("Accesso consentito!")
                st.rerun()
            else:
                st.error("❌ Password errata.")
    else:
        col_sbl1, col_sbl2 = st.columns([6, 1])
        with col_sbl1:
            st.success("🔓 Accesso autorizzato alla centrale 'Cervello'.")
        with col_sbl2:
            if st.button("🔒 Blocca", use_container_width=True):
                st.session_state["cervello_sbloccato"] = False
                st.rerun()
                
        # Form di inserimento nel Cervello
        with st.form("form_nuovo_cervello", clear_on_submit=True):
            st.subheader("➕ Inserisci Nuova Attività nel Cervello")
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                c_cliente = st.text_input("Cliente:")
                c_lavorazione = st.text_input("Lavorazione:")
            with cc2:
                c_mandato = st.date_input("Mandato il:", value=date.today())
                c_da_chi = st.text_input("Da chi:")
            with cc3:
                c_descrizione = st.text_area("Descrizione:", height=90)
                
            btn_salva_cervello = st.form_submit_button("💾 Salva nel Cervello", use_container_width=True)
            if btn_salva_cervello:
                if not c_cliente.strip():
                    st.error("⚠️ Il campo 'Cliente' è obbligatorio.")
                else:
                    conn_c = get_db_connection()
                    cur_c = conn_c.cursor()
                    cur_c.execute('''
                        INSERT INTO cervello (cliente, lavorazione, descrizione, mandato_il, da_chi, fatto)
                        VALUES (?, ?, ?, ?, ?, 0)
                    ''', (c_cliente.strip(), c_lavorazione.strip(), c_descrizione.strip(), str(c_mandato), c_da_chi.strip()))
                    conn_c.commit()
                    conn_c.close()
                    st.success("✅ Attività salvata nel Cervello!")
                    st.rerun()
        
        st.markdown("---")
        st.subheader("📂 Elenco Attività e Promemoria del Cervello")
        
        conn_c = get_db_connection()
        df_cervello = pd.read_sql_query("SELECT * FROM cervello ORDER BY id DESC", conn_c)
        conn_c.close()
        
        if df_cervello.empty:
            st.info("Nessuna attività registrata nel Cervello.")
        else:
            for _, row in df_cervello.iterrows():
                col_chk, col_info, col_del = st.columns([0.6, 7.9, 1.5])
                with col_chk:
                    is_fatto = st.checkbox("Fatto", value=bool(row['fatto']), key=f"chk_cerv_{row['id']}")
                    if is_fatto != bool(row['fatto']):
                        conn_u = get_db_connection()
                        cur_u = conn_u.cursor()
                        cur_u.execute("UPDATE cervello SET fatto = ? WHERE id = ?", (1 if is_fatto else 0, row['id']))
                        conn_u.commit()
                        conn_u.close()
                        st.rerun()
                with col_info:
                    status_badge = "✅ **[COMPLETATO]**" if row['fatto'] else "📌 **[ATTIVO]**"
                    st.markdown(f"{status_badge} — **Cliente:** {row['cliente']} | **Lavorazione:** {row['lavorazione']} | **Mandato il:** {row['mandato_il']} | **Da chi:** {row['da_chi']}")
                    if row['descrizione']:
                        st.write(f"*Descrizione:* {row['descrizione']}")
                with col_del:
                    if st.button("🗑️ Elimina", key=f"del_cerv_{row['id']}", use_container_width=True):
                        conn_d = get_db_connection()
                        cur_d = conn_d.cursor()
                        cur_d.execute("DELETE FROM cervello WHERE id = ?", (row['id'],))
                        conn_d.commit()
                        conn_d.close()
                        st.rerun()
                st.markdown("---")

# --- SCHERMATA: PAUSA CAFFÈ (MINI-GAME MONOGIOCATORE) ---
elif sezione_corrente == "🎮 Pausa Caffè (Mini-Game)":
    st.title("🎮 Pausa Caffè - Sfida il Plotter!")
    st.info("Sasso, Carta, Forbice in versione Tipografia! Sconfiggi l'intelligenza artificiale della stampante. ☕")

    if "punti_player" not in st.session_state:
        st.session_state.punti_player = 0
    if "punti_bot" not in st.session_state:
        st.session_state.punti_bot = 0

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("👤 Tuoi Punti", st.session_state.punti_player)
    col_m2.metric("🤖 Punti del Plotter", st.session_state.punti_bot)

    st.markdown("---")
    st.subheader("Scegli la tua arma:")

    def gioca(scelta_utente):
        opzioni = ["🧱 Telaio", "📄 Pellicola DTF", "✂️ Taglierina"]
        scelta_bot = random.choice(opzioni)
        
        st.session_state.ultima_scelta_utente = scelta_utente
        st.session_state.ultima_scelta_bot = scelta_bot
        
        if scelta_utente == scelta_bot:
            st.session_state.ultimo_risultato = "🤝 Pareggio esatto!"
        elif (
            (scelta_utente == "🧱 Telaio" and scelta_bot == "✂️ Taglierina") or
            (scelta_utente == "📄 Pellicola DTF" and scelta_bot == "🧱 Telaio") or
            (scelta_utente == "✂️ Taglierina" and scelta_bot == "📄 Pellicola DTF")
        ):
            st.session_state.ultimo_risultato = "🎉 Grande! Hai vinto questo round!"
            st.session_state.punti_player += 1
        else:
            st.session_state.ultimo_risultato = "🤖 Ha vinto il Plotter!"
            st.session_state.punti_bot += 1

    c_b1, c_b2, c_b3 = st.columns(3)
    with c_b1:
        if st.button("🧱 Telaio\n(Sasso)", use_container_width=True):
            gioca("🧱 Telaio")
            st.rerun()
    with c_b2:
        if st.button("📄 Pellicola DTF\n(Carta)", use_container_width=True):
            gioca("📄 Pellicola DTF")
            st.rerun()
    with c_b3:
        if st.button("✂️ Taglierina\n(Forbice)", use_container_width=True):
            gioca("✂️ Taglierina")
            st.rerun()

    if "ultimo_risultato" in st.session_state:
        st.markdown("---")
        st.subheader("Esito dello scontro:")
        rc1, rc2 = st.columns(2)
        rc1.write(f"La tua mossa: **{st.session_state.ultima_scelta_utente}**")
        rc2.write(f"La mossa del Plotter: **{st.session_state.ultima_scelta_bot}**")
        
        if "vinto" in st.session_state.ultimo_risultato:
            st.success(st.session_state.ultimo_risultato)
        elif "Plotter" in st.session_state.ultimo_risultato:
            st.error(st.session_state.ultimo_risultato)
        else:
            st.warning(st.session_state.ultimo_risultato)
            
        st.markdown("---")
        if st.button("🔄 Azzera Punteggio", use_container_width=True):
            st.session_state.punti_player = 0
            st.session_state.punti_bot = 0
            del st.session_state.ultimo_risultato
            st.rerun()

# --- SCHERMATA: NUOVO ORDINE ---
elif sezione_corrente == "➕ Nuovo Ordine":
    st.title("📝 Inserimento Nuovo Ordine (Demo)")
    
    # Controllo limite ordini (Max 5 nella demo)
    conn_lim = get_db_connection()
    cur_lim = conn_lim.cursor()
    cur_lim.execute("SELECT COUNT(*) FROM ordini")
    tot_ord_count = cur_lim.fetchone()[0]
    conn_lim.close()

    if tot_ord_count >= 5:
        st.error("⚠️ **LIMITE VERSIONE DEMO RAGGIUNTO**: Hai salvato il numero massimo di **5 ordini** consentiti in questa versione di prova.")
        st.warning("💡 **Vuoi sbloccare ordini e preventivi illimitati?** Contattaci per acquistare la versione completa di **NAGEST GESTIONALE**!")
    else:
        st.success(f"Compila i campi sottostanti per registrare un nuovo ordine. (Ordini inseriti: {tot_ord_count}/5)")

        if "righe_articolo" not in st.session_state:
            st.session_state["righe_articolo"] = [
                {"articolo": "", "quantita": 1, "descrizione": "", "colore_articolo": "", "colore_stampa": "", "posizione_stampa": "", "stampa": "serigrafia", "fornitore_articolo": "", "numero_ordine_articolo": ""}
            ]

        with st.expander("📌 1. Dati Principali del Cliente e dell'Ordine", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                ditta = st.text_input("DITTA (Cliente):", placeholder="Inserisci nome azienda...")
                referente = st.text_input("REFERENTE:", placeholder="Nome referente...")
            with c2:
                data_ordine = st.date_input("DATA ORDINE:", value=date.today())
                data_consegna = st.date_input("DATA DI CONSEGNA:", value=date.today())
            with c3:
                numero_ordine = st.text_input("NUMERO ORDINE:", placeholder="Es. ORD-2026-01...")
                fornitore = st.text_input("FORNITORE:", placeholder="Nome fornitore principale...")
            
            note_stampa = st.text_area("NOTE DI STAMPA:", placeholder="Istruzioni particolari per la produzione...", height=90)

        st.subheader("🛍️ 2. Articoli e Personalizzazioni")
        
        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        with col_btn1:
            if st.button("➕ Aggiungi Riga Articolo"):
                st.session_state["righe_articolo"].append(
                    {"articolo": "", "quantita": 1, "descrizione": "", "colore_articolo": "", "colore_stampa": "", "posizione_stampa": "", "stampa": "serigrafia", "fornitore_articolo": "", "numero_ordine_articolo": ""}
                )
                st.rerun()
        with col_btn2:
            if st.button("➖ Rimuovi Ultima") and len(st.session_state["righe_articolo"]) > 1:
                st.session_state["righe_articolo"].pop()
                st.rerun()

        for idx, riga in enumerate(st.session_state["righe_articolo"]):
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1.5, 0.8, 2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
            with c1:
                riga["articolo"] = st.text_input("ARTICOLO", value=riga["articolo"], key=f"art_{idx}")
            with c2:
                riga["quantita"] = st.number_input("Q.TÀ", min_value=1, value=int(riga["quantita"]), step=1, key=f"qta_{idx}")
            with c3:
                riga["descrizione"] = st.text_input("Descrizione", value=riga["descrizione"], key=f"desc_{idx}")
            with c4:
                riga["colore_articolo"] = st.text_input("COLORE ART.", value=riga["colore_articolo"], key=f"col_art_{idx}")
            with c5:
                riga["colore_stampa"] = st.text_input("COLORE STAMPA", value=riga["colore_stampa"], key=f"col_stampa_{idx}")
            with c6:
                riga["posizione_stampa"] = st.text_input("POSIZIONE", value=riga["posizione_stampa"], key=f"pos_stampa_{idx}")
            with c7:
                riga["stampa"] = st.text_input("TIPO STAMPA", value=riga.get("stampa", "serigrafia"), key=f"stampa_{idx}")
            with c8:
                riga["fornitore_articolo"] = st.text_input("FORNITORE", value=riga.get("fornitore_articolo", ""), key=f"forn_art_{idx}")
            with c9:
                riga["numero_ordine_articolo"] = st.text_input("N. ORDINE", value=riga.get("numero_ordine_articolo", ""), key=f"num_ord_art_{idx}")

        st.markdown("---")
        st.subheader("📎 3. Allegati e Grafiche")
        f_allegati = st.file_uploader("Carica file, bozze o grafiche per l'ordine (puoi selezionare più file):", accept_multiple_files=True, type=["pdf", "png", "jpg", "jpeg", "ai", "psd", "zip", "rar", "cdr"])

        st.markdown("---")

        if st.button("💾 SALVA DEFINITIVAMENTE L'ORDINE", type="primary", use_container_width=True):
            if not ditta.strip():
                st.error("⚠️ Il campo 'DITTA (Cliente)' è obbligatorio per procedere al salvataggio.")
            else:
                nomi_allegati = []
                if f_allegati:
                    os.makedirs("allegati", exist_ok=True)
                    for f in f_allegati:
                        percorso_file = os.path.join("allegati", f.name)
                        with open(percorso_file, "wb") as file_out:
                            file_out.write(f.getbuffer())
                        nomi_allegati.append(f.name)
                allegati_str = ", ".join(nomi_allegati) if nomi_allegati else ""

                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO ordini (numero_ordine, fornitore, data_ordine, data_consegna, mandato_stampa_il, ditta, referente, note_stampa, stato, allegati)
                    VALUES (?, ?, ?, ?, NULL, ?, ?, ?, 'In arrivo', ?)
                ''', (numero_ordine.strip(), fornitore.strip(), str(data_ordine), str(data_consegna), ditta.strip(), referente.strip(), note_stampa.strip(), allegati_str))
                
                ordine_id = cursor.lastrowid
                
                for riga in st.session_state["righe_articolo"]:
                    art_val = clean_val(riga["articolo"])
                    if art_val:
                        cursor.execute('''
                            INSERT INTO ordini_dettagli (ordine_id, articolo, quantita, descrizione, colore_articolo, colore_stampa, posizione_stampa, stampa, fornitore_articolo, numero_ordine_articolo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            ordine_id, 
                            art_val, 
                            clean_int(riga["quantita"]), 
                            clean_val(riga["descrizione"]), 
                            clean_val(riga["colore_articolo"]), 
                            clean_val(riga["colore_stampa"]), 
                            clean_val(riga["posizione_stampa"]), 
                            clean_val(riga["stampa"], "serigrafia"), 
                            clean_val(riga["fornitore_articolo"]), 
                            clean_val(riga["numero_ordine_articolo"])
                        ))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Ordine per '{ditta}' salvato con successo! (ID Ordine: #{ordine_id})")
                if nomi_allegati:
                    st.info(f"📎 File allegati salvati nella cartella 'allegati': {allegati_str}")
                st.session_state["righe_articolo"] = [
                    {"articolo": "", "quantita": 1, "descrizione": "", "colore_articolo": "", "colore_stampa": "", "posizione_stampa": "", "stampa": "serigrafia", "fornitore_articolo": "", "numero_ordine_articolo": ""}
                ]

# --- SCHERMATA: MODIFICA ORDINE ---
elif sezione_corrente == "✏️ Modifica Ordine":
    st.title("✏️ Modifica Ordine Esistente")
    st.info("Seleziona un ordine esistente, modifica i dati nei campi sottostanti e clicca su 'Salva Modifiche' per memorizzare tutto.")
    
    conn = get_db_connection()
    df_all_ordini = pd.read_sql_query("SELECT id, numero_ordine, ditta, data_consegna, stato FROM ordini ORDER BY data_consegna DESC", conn)
    conn.close()
    
    if df_all_ordini.empty:
        st.warning("Nessun ordine presente nel database da modificare.")
    else:
        mapping_ordini = {
            f"Ordine #{row['id']} (N. Ord: {row['numero_ordine'] or 'N/D'}) - {row['ditta']} (Consegna: {row['data_consegna']} | Stato: {row['stato']})": row['id'] 
            for _, row in df_all_ordini.iterrows()
        }
        
        scelta_modifica = st.selectbox("Seleziona l'ordine da modificare:", options=list(mapping_ordini.keys()), key="select_mod_ordine")
        
        if scelta_modifica:
            edit_id = mapping_ordini[scelta_modifica]
            
            conn_edit = get_db_connection()
            cursor_edit = conn_edit.cursor()
            cursor_edit.execute("SELECT * FROM ordini WHERE id = ?", (edit_id,))
            ord_data = cursor_edit.fetchone()
            
            df_det_edit = pd.read_sql_query(
                "SELECT articolo, quantita, descrizione, colore_articolo, colore_stampa, posizione_stampa, stampa, fornitore_articolo, numero_ordine_articolo FROM ordini_dettagli WHERE ordine_id = ?", 
                conn_edit, params=(edit_id,)
            )
            conn_edit.close()
            
            if ord_data:
                try:
                    d_ord_val = date.fromisoformat(ord_data['data_ordine']) if ord_data['data_ordine'] else date.today()
                except:
                    d_ord_val = date.today()
                try:
                    d_cons_val = date.fromisoformat(ord_data['data_consegna']) if ord_data['data_consegna'] else date.today()
                except:
                    d_cons_val = date.today()
                    
                if df_det_edit.empty:
                    df_edit_init = pd.DataFrame([{
                        "articolo": "", "quantita": 1, "descrizione": "", "colore_articolo": "", 
                        "colore_stampa": "", "posizione_stampa": "", "stampa": "serigrafia", 
                        "fornitore_articolo": "", "numero_ordine_articolo": ""
                    }])
                else:
                    df_edit_init = df_det_edit.copy()

                with st.form(key=f"form_modifica_ordine_{edit_id}"):
                    st.markdown(f"### 📋 Modifica Ordine #{edit_id} - {ord_data['ditta']}")
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        e_num_ord = st.text_input("N. Ordine", value=ord_data['numero_ordine'] or "")
                        e_ditta = st.text_input("Ditta (Cliente)*", value=ord_data['ditta'] or "")
                        e_forn = st.text_input("Fornitore Principale", value=ord_data['fornitore'] or "")
                        e_ref = st.text_input("Referente", value=ord_data['referente'] or "")
                    with col_m2:
                        e_data_ord = st.date_input("Data Ordine", value=d_ord_val)
                        e_data_cons = st.date_input("Data Consegna", value=d_cons_val)
                        
                    e_note = st.text_area("Note di Stampa", value=ord_data['note_stampa'] or "")
                    
                    st.markdown("#### 🛍️ Articoli associati (Modificabili in tabella):")
                    edited_df = st.data_editor(
                        df_edit_init,
                        num_rows="dynamic",
                        use_container_width=True,
                        column_config={
                            "stampa": st.column_config.TextColumn(
                                "Tipo Stampa",
                                required=True
                            ),
                            "quantita": st.column_config.NumberColumn(
                                "Q.tà",
                                min_value=1,
                                step=1,
                                required=True
                            )
                        },
                        key=f"editor_form_{edit_id}"
                    )
                    
                    st.markdown("---")
                    submit_button = st.form_submit_button("💾 SALVA MODIFICHE DEFINITIVE", use_container_width=True)
                    
                    if submit_button:
                        if not e_ditta.strip():
                            st.error("⚠️ Il campo 'DITTA (Cliente)' è obbligatorio.")
                        else:
                            conn_save = get_db_connection()
                            cursor_save = conn_save.cursor()
                            
                            cursor_save.execute('''
                                UPDATE ordini 
                                SET numero_ordine = ?, fornitore = ?, data_ordine = ?, data_consegna = ?, ditta = ?, referente = ?, note_stampa = ?
                                WHERE id = ?
                            ''', (e_num_ord.strip(), e_forn.strip(), str(e_data_ord), str(e_data_cons), e_ditta.strip(), e_ref.strip(), e_note.strip(), edit_id))
                            
                            cursor_save.execute("DELETE FROM ordini_dettagli WHERE ordine_id = ?", (edit_id,))
                            
                            for _, row in edited_df.iterrows():
                                art_val = clean_val(row.get('articolo', ''))
                                if art_val:
                                    qta_val = clean_int(row.get('quantita', 1))
                                    desc_val = clean_val(row.get('descrizione', ''))
                                    col_art = clean_val(row.get('colore_articolo', ''))
                                    col_st = clean_val(row.get('colore_stampa', ''))
                                    pos_st = clean_val(row.get('posizione_stampa', ''))
                                    st_val = clean_val(row.get('stampa', 'serigrafia'))
                                    f_art = clean_val(row.get('fornitore_articolo', ''))
                                    n_art = clean_val(row.get('numero_ordine_articolo', ''))
                                    
                                    cursor_save.execute('''
                                        INSERT INTO ordini_dettagli (ordine_id, articolo, quantita, descrizione, colore_articolo, colore_stampa, posizione_stampa, stampa, fornitore_articolo, numero_ordine_articolo)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (edit_id, art_val, qta_val, desc_val, col_art, col_st, pos_st, st_val, f_art, n_art))
                            
                            conn_save.commit()
                            conn_save.close()
                            st.success("✅ Modifiche salvate con successo in tutte le parti!")
                            st.rerun()

# --- SCHERMATA: PREVENTIVI (Nuovo, Modifica, Archivio) ---
elif sezione_corrente == "📄 Preventivi":
    st.title("📄 Gestione Preventivi (Demo)")
    st.info("Crea, modifica ed esporta in PDF i preventivi.")

    tab_nuovo, tab_modifica, tab_archivio = st.tabs(["➕ Crea Nuovo Preventivo", "✏️ Modifica Preventivo", "📂 Archivio Preventivi"])

    with tab_nuovo:
        # Controllo limite preventivi (Max 3 nella demo)
        conn_p_lim = get_db_connection()
        cur_p_lim = conn_p_lim.cursor()
        cur_p_lim.execute("SELECT COUNT(*) FROM preventivi")
        tot_prev_count = cur_p_lim.fetchone()[0]
        conn_p_lim.close()

        if tot_prev_count >= 3:
            st.error("⚠️ **LIMITE VERSIONE DEMO RAGGIUNTO**: Hai salvato il numero massimo di **3 preventivi** consentiti in questa versione di prova.")
            st.warning("💡 **Passa alla versione completa** per rimuovere ogni limite di inserimento!")
        else:
            st.success(f"Crea un nuovo preventivo. (Preventivi inseriti: {tot_prev_count}/3)")
            with st.form("form_nuovo_preventivo"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    num_prev = st.text_input("Numero Preventivo:", placeholder="Es. 1666")
                    ditta_prev = st.text_input("Ditta (Cliente)*:", placeholder="Nome azienda cliente...")
                with c2:
                    data_prev = st.date_input("Data Preventivo:", value=date.today())
                    referente_prev = st.text_input("Referente:", placeholder="Nome referente...")
                with c3:
                    note_prev = st.text_area("Note Aggiuntive:", placeholder="Condizioni particolari...", height=95)

                st.markdown("#### Voci e Servizi del Preventivo (Descrizione, Quantità, Prezzo Unitario, IVA %)")
                
                df_prev_init = pd.DataFrame([
                    {"descrizione": "Servizio Stampa / Articolo 1", "quantita": 10, "prezzo": 50.0, "iva_perc": 22.0}
                ])

                edited_prev_df = st.data_editor(
                    df_prev_init,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "descrizione": st.column_config.TextColumn("Descrizione", required=True),
                        "quantita": st.column_config.NumberColumn("Quantità", min_value=1, step=1, required=True),
                        "prezzo": st.column_config.NumberColumn("Prezzo Unit. (€)", min_value=0.0, format="%.2f €", required=True),
                        "iva_perc": st.column_config.NumberColumn("IVA (%)", min_value=0.0, max_value=100.0, step=1.0, required=True)
                    },
                    key="editor_preventivo_nuovo"
                )

                preview_sub = 0.0
                preview_iva = 0.0
                for _, r in edited_prev_df.iterrows():
                    d_val = clean_val(r.get('descrizione', ''))
                    if d_val:
                        q = clean_int(r.get('quantita', 1))
                        p = clean_float(r.get('prezzo', 0.0))
                        iv = clean_float(r.get('iva_perc', 22.0))
                        sub = q * p
                        preview_sub += sub
                        preview_iva += sub * (iv / 100.0)
                preview_tot = preview_sub + preview_iva

                st.markdown(f"**Anteprima Totali:** Subtotale: **{preview_sub:.2f} €** | IVA: **{preview_iva:.2f} €** | Totale: **{preview_tot:.2f} €**")

                submit_prev = st.form_submit_button("💾 SALVA E GENERA PREVENTIVO", use_container_width=True)

                if submit_prev:
                    if not ditta_prev.strip():
                        st.error("⚠️ Il campo 'Ditta (Cliente)' è obbligatorio.")
                    else:
                        conn_p = get_db_connection()
                        cur_p = conn_p.cursor()
                        
                        cur_p.execute('''
                            INSERT INTO preventivi (numero_preventivo, data_preventivo, ditta, referente, note)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (num_prev.strip(), str(data_prev), ditta_prev.strip(), referente_prev.strip(), note_prev.strip()))
                        
                        prev_id = cur_p.lastrowid
                        
                        for _, row in edited_prev_df.iterrows():
                            desc = clean_val(row.get('descrizione', ''))
                            if desc:
                                qta = clean_int(row.get('quantita', 1))
                                prz = clean_float(row.get('prezzo', 0.0))
                                subtot = qta * prz
                                iva_p = clean_float(row.get('iva_perc', 22.0))
                                
                                cur_p.execute('''
                                    INSERT INTO preventivi_dettagli (preventivo_id, descrizione, quantita, prezzo, subtotale, iva_perc)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (prev_id, desc, qta, prz, subtot, iva_p))
                                
                        conn_p.commit()
                        conn_p.close()
                        st.success(f"✅ Preventivo #{prev_id} salvato con successo!")
                        st.rerun()

    with tab_modifica:
        conn_m = get_db_connection()
        df_m_prevs = pd.read_sql_query("SELECT id, numero_preventivo, ditta, data_preventivo FROM preventivi ORDER BY id DESC", conn_m)
        conn_m.close()
        
        if df_m_prevs.empty:
            st.warning("Nessun preventivo presente nel database da modificare.")
        else:
            mapping_m_prevs = {
                f"Preventivo #{row['id']} (N. {row['numero_preventivo'] or 'N/D'}) - {row['ditta']} ({row['data_preventivo']})": row['id']
                for _, row in df_m_prevs.iterrows()
            }
            scelta_m_prev = st.selectbox("Seleziona il preventivo da modificare:", options=list(mapping_m_prevs.keys()), key="select_mod_preventivo")
            
            if scelta_m_prev:
                m_prev_id = mapping_m_prevs[scelta_m_prev]
                
                conn_ed = get_db_connection()
                cur_ed = conn_ed.cursor()
                cur_ed.execute("SELECT * FROM preventivi WHERE id = ?", (m_prev_id,))
                p_data = cur_ed.fetchone()
                
                df_p_det_edit = pd.read_sql_query(
                    "SELECT descrizione, quantita, prezzo, iva_perc FROM preventivi_dettagli WHERE preventivo_id = ?",
                    conn_ed, params=(m_prev_id,)
                )
                conn_ed.close()
                
                if p_data:
                    try:
                        d_prev_val = date.fromisoformat(p_data['data_preventivo']) if p_data['data_preventivo'] else date.today()
                    except:
                        d_prev_val = date.today()
                        
                    if df_p_det_edit.empty:
                        df_p_edit_init = pd.DataFrame([{"descrizione": "", "quantita": 1, "prezzo": 0.0, "iva_perc": 22.0}])
                    else:
                        df_p_edit_init = df_p_det_edit.copy()

                    with st.form(key=f"form_modifica_preventivo_{m_prev_id}"):
                        c_m1, c_m2, c_m3 = st.columns(3)
                        with c_m1:
                            m_num = st.text_input("Numero Preventivo", value=p_data['numero_preventivo'] or "")
                            m_ditta = st.text_input("Ditta (Cliente)*", value=p_data['ditta'] or "")
                        with c_m2:
                            m_data = st.date_input("Data Preventivo", value=d_prev_val)
                            m_ref = st.text_input("Referente", value=p_data['referente'] or "")
                        with c_m3:
                            m_note = st.text_area("Note Aggiuntive", value=p_data['note'] or "", height=95)
                            
                        st.markdown("#### Voci e Servizi (Modificabili in tabella)")
                        edited_m_df = st.data_editor(
                            df_p_edit_init,
                            num_rows="dynamic",
                            use_container_width=True,
                            column_config={
                                "descrizione": st.column_config.TextColumn("Descrizione", required=True),
                                "quantita": st.column_config.NumberColumn("Quantità", min_value=1, step=1, required=True),
                                "prezzo": st.column_config.NumberColumn("Prezzo Unit. (€)", min_value=0.0, format="%.2f €", required=True),
                                "iva_perc": st.column_config.NumberColumn("IVA (%)", min_value=0.0, max_value=100.0, step=1.0, required=True)
                            },
                            key=f"editor_form_prev_{m_prev_id}"
                        )
                        
                        st.markdown("---")
                        submit_m_prev = st.form_submit_button("💾 SALVA MODIFICHE PREVENTIVO", use_container_width=True)
                        
                        if submit_m_prev:
                            if not m_ditta.strip():
                                st.error("⚠️ Il campo 'Ditta (Cliente)' è obbligatorio.")
                            else:
                                conn_ms = get_db_connection()
                                cur_ms = conn_ms.cursor()
                                
                                cur_ms.execute('''
                                    UPDATE preventivi 
                                    SET numero_preventivo = ?, data_preventivo = ?, ditta = ?, referente = ?, note = ?
                                    WHERE id = ?
                                ''', (m_num.strip(), str(m_data), m_ditta.strip(), m_ref.strip(), m_note.strip(), m_prev_id))
                                
                                cur_ms.execute("DELETE FROM preventivi_dettagli WHERE preventivo_id = ?", (m_prev_id,))
                                
                                for _, row in edited_m_df.iterrows():
                                    desc = clean_val(row.get('descrizione', ''))
                                    if desc:
                                        qta = clean_int(row.get('quantita', 1))
                                        prz = clean_float(row.get('prezzo', 0.0))
                                        subtot = qta * prz
                                        iva_p = clean_float(row.get('iva_perc', 22.0))
                                        
                                        cur_ms.execute('''
                                            INSERT INTO preventivi_dettagli (preventivo_id, descrizione, quantita, prezzo, subtotale, iva_perc)
                                            VALUES (?, ?, ?, ?, ?, ?)
                                        ''', (m_prev_id, desc, qta, prz, subtot, iva_p))
                                        
                                conn_ms.commit()
                                conn_ms.close()
                                st.success("✅ Preventivo modificato e salvato con successo!")
                                st.rerun()

    with tab_archivio:
        conn_a = get_db_connection()
        df_prevs = pd.read_sql_query("SELECT * FROM preventivi ORDER BY id DESC", conn_a)
        
        if df_prevs.empty:
            st.info("Nessun preventivo salvato nell'archivio.")
        else:
            prev_options = {f"Preventivo #{row['id']} (N. {row['numero_preventivo'] or 'N/D'}) - {row['ditta']} ({row['data_preventivo']})": row['id'] for _, row in df_prevs.iterrows()}
            selected_prev_label = st.selectbox("Seleziona Preventivo da consultare:", options=list(prev_options.keys()))
            
            if selected_prev_label:
                sel_prev_id = prev_options[selected_prev_label]
                cursor_a = conn_a.cursor()
                cursor_a.execute("SELECT * FROM preventivi WHERE id = ?", (sel_prev_id,))
                p_info = cursor_a.fetchone()
                
                df_p_det = pd.read_sql_query("SELECT descrizione, quantita, prezzo, subtotale, iva_perc FROM preventivi_dettagli WHERE preventivo_id = ?", conn_a, params=(sel_prev_id,))
                
                if p_info:
                    st.markdown(f"### Preventivo #{p_info['id']} - {p_info['ditta']}")
                    st.write(f"**N. Preventivo:** {p_info['numero_preventivo'] or 'N/D'} | **Data:** {p_info['data_preventivo']} | **Referente:** {p_info['referente']}")
                    if p_info['note']:
                        st.info(f"**Note:** {p_info['note']}")
                        
                    st.markdown("#### Voci:")
                    if not df_p_det.empty:
                        df_view = df_p_det.copy()
                        df_view['Subtotale (€)'] = df_view['quantita'] * df_view['prezzo']
                        st.dataframe(df_view[['descrizione', 'quantita', 'prezzo', 'Subtotale (€)', 'iva_perc']], use_container_width=True, hide_index=True)
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        try:
                            pdf_prev_data = generate_pdf_preventivo(p_info, df_p_det.to_dict(orient='records'))
                            st.download_button(
                                label="📄 Scarica PDF Preventivo Ufficiale",
                                data=pdf_prev_data,
                                file_name=f"Preventivo_{p_info['id']}_{p_info['ditta'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"dl_prev_{sel_prev_id}"
                            )
                        except Exception as e:
                            st.error(f"Errore generazione PDF Preventivo: {e}")
                    with col_dl2:
                        if st.button("🗑️ Elimina Preventivo", type="secondary", use_container_width=True, key=f"del_prev_{sel_prev_id}"):
                            cursor_a.execute("DELETE FROM preventivi WHERE id = ?", (sel_prev_id,))
                            cursor_a.execute("DELETE FROM preventivi_dettagli WHERE preventivo_id = ?", (sel_prev_id,))
                            conn_a.commit()
                            st.warning(f"Preventivo #{sel_prev_id} eliminato.")
                            st.rerun()
        conn_a.close()

# --- SCHERMATE ARCHIVIO (Consultazione, Stati, PDF, Filtri Data, Scadenze) ---
else:
    titoli_sezioni = {
        "📂 Tutti gli Ordini": ("Tutti gli Ordini", ['data_ordine', 'data_consegna', 'ditta', 'referente', 'stato', 'Stato Consegna'], None),
        "⏳ In arrivo": ("Ordini in Arrivo", ['numero_ordine', 'fornitore', 'data_consegna', 'ditta', 'referente', 'stato', 'Stato Consegna'], "In arrivo"),
        "🖨️ Mandati in stampa": ("Ordini Mandati in Stampa", ['numero_ordine', 'fornitore', 'data_consegna', 'referente', 'mandato_stampa_il', 'stato', 'Stato Consegna'], "Mandati in stampa"),
        "✅ Completati": ("Ordini Completati", ['numero_ordine', 'fornitore', 'data_consegna', 'ditta', 'referente', 'stato', 'Stato Consegna'], "Completati")
    }
    
    titolo_schermata, cols_to_show, filtro_stato = titoli_sezioni[sezione_corrente]
    st.title(f"📋 {titolo_schermata}")
    
    conn = get_db_connection()
    
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        filtro_cliente = st.text_input("🔍 Cerca per Ditta / Cliente / N. Ordine:", placeholder="Digita il testo da cercare...")
    with f_col2:
        data_da_filtro = st.date_input("Consegna da:", value=None)
    with f_col3:
        data_a_filtro = st.date_input("Consegna a:", value=None)
    
    base_query = "SELECT * FROM ordini"
    params = []
    conditions = []
    
    if filtro_cliente:
        conditions.append("(ditta LIKE ? OR numero_ordine LIKE ? OR fornitore LIKE ?)")
        params.extend([f"%{filtro_cliente}%", f"%{filtro_cliente}%", f"%{filtro_cliente}%"])
    if filtro_stato:
        conditions.append("stato = ?")
        params.append(filtro_stato)
        
    if data_da_filtro:
        conditions.append("data_consegna >= ?")
        params.append(str(data_da_filtro))
    if data_a_filtro:
        conditions.append("data_consegna <= ?")
        params.append(str(data_a_filtro))
        
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
        
    base_query += " ORDER BY data_consegna ASC, ditta ASC"
    
    df_ordini = pd.read_sql_query(base_query, conn, params=tuple(params))
    
    if df_ordini.empty:
        st.info("Nessun ordine trovato corrispondente ai filtri selezionati.")
    else:
        oggi_str = str(date.today())
        stati_scadenza = []
        for _, row in df_ordini.iterrows():
            st_ord = row['stato']
            cons = str(row['data_consegna'])
            if st_ord == 'Completati':
                stati_scadenza.append("✅ Completato")
            elif cons < oggi_str:
                stati_scadenza.append("🔴 SCADUTO")
            elif cons == oggi_str:
                stati_scadenza.append("🟡 IN SCADENZA OGGI")
            else:
                stati_scadenza.append("🟢 Regolare")
                
        df_ordini['Stato Consegna'] = stati_scadenza
        
        display_df = df_ordini[cols_to_show].copy()
        renames = {
            'data_ordine': 'Data',
            'data_consegna': 'Data Consegna',
            'ditta': 'Ditta',
            'referente': 'Referente',
            'stato': 'Stato',
            'numero_ordine': 'N. Ordine',
            'fornitore': 'Fornitore',
            'mandato_stampa_il': 'Mandato il'
        }
        display_df = display_df.rename(columns=renames)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
            
        st.markdown("---")
        st.subheader("⚙️ Gestione Ordine Selezionato (Stato, Allegati, PDF, Eliminazione)")
        
        ordini_disponibili = {f"Ordine #{row['id']} (N. Ord: {row['numero_ordine'] or 'N/D'}) - {row['ditta']} (Consegna: {row['data_consegna']})": row['id'] for index, row in df_ordini.iterrows()}
        
        selected_label = st.selectbox("Seleziona l'ordine da gestire:", options=list(ordini_disponibili.keys()), key="select_gestisci_ordine")
        
        if selected_label:
            selected_id = ordini_disponibili[selected_label]
            
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ordini WHERE id = ?", (selected_id,))
            ordine_info = cursor.fetchone()
            
            df_dettagli = pd.read_sql_query("SELECT articolo, quantita, descrizione, colore_articolo, colore_stampa, posizione_stampa, stampa, fornitore_articolo, numero_ordine_articolo FROM ordini_dettagli WHERE ordine_id = ?", conn, params=(selected_id,))
            
            if ordine_info:
                st.markdown(f"### 📌 ORDINE: \"{ordine_info['ditta'].upper()}\"")
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.write(f"**N. Ordine:** {ordine_info['numero_ordine'] or 'Non specificato'}")
                    st.write(f"**Fornitore:** {ordine_info['fornitore'] or 'Non specificato'}")
                    st.write(f"**Data Ordine:** {ordine_info['data_ordine']}")
                with col_info2:
                    st.write(f"**Ditta:** {ordine_info['ditta']}")
                    st.write(f"**Referente:** {ordine_info['referente']}")
                    st.write(f"**Data Consegna:** {ordine_info['data_consegna']}")
                with col_info3:
                    mandato_mostra = ordine_info['mandato_stampa_il'] if ordine_info['mandato_stampa_il'] else 'Non ancora inviato'
                    st.write(f"**Mandato in Stampa il:** {mandato_mostra}")
                    st.write(f"**Stato Attuale:** {ordine_info['stato']}")
                
                if ordine_info['note_stampa']:
                    st.info(f"📌 **Note di Stampa:** {ordine_info['note_stampa']}")
                
                if ordine_info['allegati']:
                    st.markdown(f"📎 **File Allegati dell'Ordine:** `{ordine_info['allegati']}`")
                    allegati_files = [a.strip() for a in ordine_info['allegati'].split(",") if a.strip()]
                    cols_all = st.columns(len(allegati_files) if len(allegati_files) <= 3 else 3)
                    for idx_a, fname in enumerate(allegati_files):
                        file_path = os.path.join("allegati", fname)
                        if os.path.exists(file_path):
                            with cols_all[idx_a % len(cols_all)]:
                                with open(file_path, "rb") as f_dl:
                                    st.download_button(
                                        label=f"📥 Scarica: {fname}",
                                        data=f_dl,
                                        file_name=fname,
                                        key=f"dl_file_{selected_id}_{idx_a}",
                                        use_container_width=True
                                    )
                        else:
                            st.warning(f"⚠️ File '{fname}' non trovato nella cartella allegati.")
                else:
                    st.write("📎 *Nessun allegato caricato per questo ordine.*")
                
                st.markdown("#### Articoli associati all'ordine:")
                if not df_dettagli.empty:
                    st.dataframe(df_dettagli, use_container_width=True, hide_index=True)
                else:
                    st.warning("Nessun articolo associato a questo ordine.")
                
                st.markdown("#### Azioni Disponibili:")
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    stati_possibili = ["In arrivo", "Mandati in stampa", "Completati"]
                    current_status_index = stati_possibili.index(ordine_info['stato']) if ordine_info['stato'] in stati_possibili else 0
                    nuovo_stato = st.selectbox("Modifica Stato:", options=stati_possibili, index=current_status_index, key=f"status_{selected_id}")
                    
                    data_mandato_stampa = None
                    if nuovo_stato == "Mandati in stampa":
                        default_date = date.today()
                        if ordine_info['mandato_stampa_il']:
                            try:
                                default_date = date.fromisoformat(ordine_info['mandato_stampa_il'])
                            except:
                                pass
                        data_mandato_stampa = st.date_input("Data Mandato in Stampa:", value=default_date, key=f"date_stampa_{selected_id}")

                    if st.button("Aggiorna Stato Ordine", use_container_width=True, key=f"btn_upd_status_{selected_id}"):
                        if nuovo_stato == "Mandati in stampa":
                            cursor.execute("UPDATE ordini SET stato = ?, mandato_stampa_il = ? WHERE id = ?", (nuovo_stato, str(data_mandato_stampa), selected_id))
                        else:
                            cursor.execute("UPDATE ordini SET stato = ? WHERE id = ?", (nuovo_stato, selected_id))
                        conn.commit()
                        st.success(f"Stato aggiornato a '{nuovo_stato}' con successo!")
                        st.rerun()
                
                with col_act2:
                    st.write("")
                    st.write("")
                    try:
                        dettagli_dict = df_dettagli.to_dict(orient='records')
                        pdf_data = generate_pdf_ordine(ordine_info, dettagli_dict)
                        st.download_button(
                            label="📄 Scarica PDF Ordine",
                            data=pdf_data,
                            file_name=f"Ordine_{ordine_info['id']}_{ordine_info['ditta'].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"dl_pdf_{selected_id}"
                        )
                    except Exception as e:
                        st.error(f"Errore generazione PDF Ordine: {e}")
                
                with col_act3:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Elimina Ordine", type="secondary", use_container_width=True, key=f"del_ord_{selected_id}"):
                        cursor.execute("DELETE FROM ordini WHERE id = ?", (selected_id,))
                        cursor.execute("DELETE FROM ordini_dettagli WHERE ordine_id = ?", (selected_id,))
                        conn.commit()
                        st.warning(f"Ordine #{selected_id} eliminato.")
                        st.rerun()

    conn.close()
