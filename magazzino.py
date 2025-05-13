finiscilo e poi dimmi come caricarlo su github e farlo funzionare import json
import os
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, messagebox, filedialog

class MagazzinoPizzeria:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestione Magazzino Pizzeria")
        self.root.geometry("1200x700")
        
        # Inizializza i dati
        self.prodotti = []
        self.categorie = ["Farina e Lieviti", "Condimenti", "Formaggi", "Salumi", "Verdure", "Bevande", "Altro"]
        self.unita_misura = ["kg", "g", "l", "ml", "pz"]
        self.fornitori = []
        self.ordini = []
        
        # Carica i dati esistenti
        self.carica_dati()
        
        # Crea le schede
        self.crea_interfaccia()
    
    def crea_interfaccia(self):
        # Notebook (schede)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Scheda Prodotti
        self.crea_scheda_prodotti()
        
        # Scheda Inventario
        self.crea_scheda_inventario()
        
        # Scheda Ordini
        self.crea_scheda_ordini()
        
        # Scheda Scadenze
        self.crea_scheda_scadenze()
        
        # Scheda Statistiche
        self.crea_scheda_statistiche()
        
        # Scheda Fornitori
        self.crea_scheda_fornitori()
        
        # Barra dei menu
        self.crea_menu()
    
    def crea_scheda_prodotti(self):
        # Frame prodotti
        frame_prodotti = Frame(self.notebook)
        self.notebook.add(frame_prodotti, text="Prodotti")
        
        # Pannello sinistro (lista prodotti)
        panel_sx = Frame(frame_prodotti)
        panel_sx.pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # Lista prodotti
        self.lista_prodotti = ttk.Treeview(panel_sx, columns=("ID", "Nome", "Categoria", "Quantità", "UM"), show="headings")
        self.lista_prodotti.heading("ID", text="ID")
        self.lista_prodotti.heading("Nome", text="Nome")
        self.lista_prodotti.heading("Categoria", text="Categoria")
        self.lista_prodotti.heading("Quantità", text="Quantità")
        self.lista_prodotti.heading("UM", text="UM")
        self.lista_prodotti.column("ID", width=50)
        self.lista_prodotti.column("Nome", width=150)
        self.lista_prodotti.column("Categoria", width=120)
        self.lista_prodotti.column("Quantità", width=80)
        self.lista_prodotti.column("UM", width=50)
        self.lista_prodotti.pack(fill=BOTH, expand=True)
        self.lista_prodotti.bind("<<TreeviewSelect>>", self.seleziona_prodotto)
        
        # Pulsanti prodotti
        btn_frame = Frame(panel_sx)
        btn_frame.pack(fill=X, pady=5)
        
        btn_aggiungi = Button(btn_frame, text="Aggiungi", command=self.aggiungi_prodotto)
        btn_aggiungi.pack(side=LEFT, padx=2)
        
        btn_modifica = Button(btn_frame, text="Modifica", command=self.modifica_prodotto)
        btn_modifica.pack(side=LEFT, padx=2)
        
        btn_elimina = Button(btn_frame, text="Elimina", command=self.elimina_prodotto)
        btn_elimina.pack(side=LEFT, padx=2)
        
        # Pannello destro (dettaglio prodotto)
        panel_dx = Frame(frame_prodotti)
        panel_dx.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Form dettaglio prodotto
        Label(panel_dx, text="ID:").grid(row=0, column=0, sticky=W, pady=2)
        self.prod_id = Entry(panel_dx)
        self.prod_id.grid(row=0, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Nome:").grid(row=1, column=0, sticky=W, pady=2)
        self.prod_nome = Entry(panel_dx)
        self.prod_nome.grid(row=1, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Categoria:").grid(row=2, column=0, sticky=W, pady=2)
        self.prod_categoria = ttk.Combobox(panel_dx, values=self.categorie)
        self.prod_categoria.grid(row=2, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Quantità:").grid(row=3, column=0, sticky=W, pady=2)
        self.prod_quantita = Entry(panel_dx)
        self.prod_quantita.grid(row=3, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Unità di misura:").grid(row=4, column=0, sticky=W, pady=2)
        self.prod_um = ttk.Combobox(panel_dx, values=self.unita_misura)
        self.prod_um.grid(row=4, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Prezzo unitario (€):").grid(row=5, column=0, sticky=W, pady=2)
        self.prod_prezzo = Entry(panel_dx)
        self.prod_prezzo.grid(row=5, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Fornitore principale:").grid(row=6, column=0, sticky=W, pady=2)
        self.prod_fornitore = ttk.Combobox(panel_dx, values=[f['nome'] for f in self.fornitori])
        self.prod_fornitore.grid(row=6, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Giacenza minima:").grid(row=7, column=0, sticky=W, pady=2)
        self.prod_giacenza_min = Entry(panel_dx)
        self.prod_giacenza_min.grid(row=7, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Scadenza (gg):").grid(row=8, column=0, sticky=W, pady=2)
        self.prod_scadenza = Entry(panel_dx)
        self.prod_scadenza.grid(row=8, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Note:").grid(row=9, column=0, sticky=NW, pady=2)
        self.prod_note = Text(panel_dx, height=5, width=30)
        self.prod_note.grid(row=9, column=1, sticky=EW, pady=2)
        
        # Pulsanti salva/annulla
        btn_salva = Button(panel_dx, text="Salva", command=self.salva_prodotto)
        btn_salva.grid(row=10, column=1, sticky=E, pady=5)
        
        btn_annulla = Button(panel_dx, text="Annulla", command=self.annulla_prodotto)
        btn_annulla.grid(row=10, column=0, sticky=W, pady=5)
        
        # Aggiorna lista prodotti
        self.aggiorna_lista_prodotti()
    
    def crea_scheda_inventario(self):
        frame_inventario = Frame(self.notebook)
        self.notebook.add(frame_inventario, text="Inventario")
        
        # Filtri
        filtro_frame = Frame(frame_inventario)
        filtro_frame.pack(fill=X, padx=5, pady=5)
        
        Label(filtro_frame, text="Categoria:").pack(side=LEFT)
        self.inv_categoria = ttk.Combobox(filtro_frame, values=["Tutte"] + self.categorie)
        self.inv_categoria.pack(side=LEFT, padx=5)
        self.inv_categoria.set("Tutte")
        
        Label(filtro_frame, text="Scorte basse:").pack(side=LEFT, padx=(10,0))
        self.inv_scorte_basse = IntVar()
        Checkbutton(filtro_frame, variable=self.inv_scorte_basse).pack(side=LEFT)
        
        Button(filtro_frame, text="Filtra", command=self.filtra_inventario).pack(side=LEFT, padx=10)
        Button(filtro_frame, text="Esporta CSV", command=self.esporta_csv).pack(side=RIGHT)
        
        # Lista inventario
        self.lista_inventario = ttk.Treeview(frame_inventario, columns=("ID", "Nome", "Categoria", "Quantità", "UM", "Giacenza Min", "Stato"), show="headings")
        self.lista_inventario.heading("ID", text="ID")
        self.lista_inventario.heading("Nome", text="Nome")
        self.lista_inventario.heading("Categoria", text="Categoria")
        self.lista_inventario.heading("Quantità", text="Quantità")
        self.lista_inventario.heading("UM", text="UM")
        self.lista_inventario.heading("Giacenza Min", text="Giacenza Min")
        self.lista_inventario.heading("Stato", text="Stato")
        
        self.lista_inventario.column("ID", width=50)
        self.lista_inventario.column("Nome", width=150)
        self.lista_inventario.column("Categoria", width=120)
        self.lista_inventario.column("Quantità", width=80)
        self.lista_inventario.column("UM", width=50)
        self.lista_inventario.column("Giacenza Min", width=80)
        self.lista_inventario.column("Stato", width=100)
        
        self.lista_inventario.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Pulsanti inventario
        btn_frame = Frame(frame_inventario)
        btn_frame.pack(fill=X, pady=5)
        
        btn_entrata = Button(btn_frame, text="Registra Entrata", command=self.registra_entrata)
        btn_entrata.pack(side=LEFT, padx=5)
        
        btn_uscita = Button(btn_frame, text="Registra Uscita", command=self.registra_uscita)
        btn_uscita.pack(side=LEFT, padx=5)
        
        # Aggiorna lista inventario
        self.aggiorna_lista_inventario()
    
    def crea_scheda_ordini(self):
        frame_ordini = Frame(self.notebook)
        self.notebook.add(frame_ordini, text="Ordini")
        
        # Lista ordini
        self.lista_ordini = ttk.Treeview(frame_ordini, columns=("ID", "Fornitore", "Data", "Stato", "Totale"), show="headings")
        self.lista_ordini.heading("ID", text="ID")
        self.lista_ordini.heading("Fornitore", text="Fornitore")
        self.lista_ordini.heading("Data", text="Data")
        self.lista_ordini.heading("Stato", text="Stato")
        self.lista_ordini.heading("Totale", text="Totale (€)")
        
        self.lista_ordini.column("ID", width=50)
        self.lista_ordini.column("Fornitore", width=150)
        self.lista_ordini.column("Data", width=100)
        self.lista_ordini.column("Stato", width=100)
        self.lista_ordini.column("Totale", width=80)
        
        self.lista_ordini.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.lista_ordini.bind("<<TreeviewSelect>>", self.seleziona_ordine)
        
        # Pulsanti ordini
        btn_frame = Frame(frame_ordini)
        btn_frame.pack(fill=X, pady=5)
        
        btn_nuovo = Button(btn_frame, text="Nuovo Ordine", command=self.nuovo_ordine)
        btn_nuovo.pack(side=LEFT, padx=5)
        
        btn_modifica = Button(btn_frame, text="Modifica", command=self.modifica_ordine)
        btn_modifica.pack(side=LEFT, padx=5)
        
        btn_elimina = Button(btn_frame, text="Elimina", command=self.elimina_ordine)
        btn_elimina.pack(side=LEFT, padx=5)
        
        btn_conferma = Button(btn_frame, text="Conferma Ricezione", command=self.conferma_ricezione)
        btn_conferma.pack(side=LEFT, padx=5)
        
        # Dettaglio ordine
        self.dettaglio_ordine_frame = Frame(frame_ordini)
        self.dettaglio_ordine_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Aggiorna lista ordini
        self.aggiorna_lista_ordini()
    
    def crea_scheda_scadenze(self):
        frame_scadenze = Frame(self.notebook)
        self.notebook.add(frame_scadenze, text="Scadenze")
        
        # Filtri
        filtro_frame = Frame(frame_scadenze)
        filtro_frame.pack(fill=X, padx=5, pady=5)
        
        Label(filtro_frame, text="Mostra scadenze entro:").pack(side=LEFT)
        self.scadenza_giorni = ttk.Combobox(filtro_frame, values=[7, 15, 30, 60, 90])
        self.scadenza_giorni.pack(side=LEFT, padx=5)
        self.scadenza_giorni.set(30)
        
        Button(filtro_frame, text="Aggiorna", command=self.aggiorna_scadenze).pack(side=LEFT, padx=5)
        
        # Lista scadenze
        self.lista_scadenze = ttk.Treeview(frame_scadenze, columns=("Prodotto", "Lotto", "Scadenza", "Giorni Rimanenti", "Quantità"), show="headings")
        self.lista_scadenze.heading("Prodotto", text="Prodotto")
        self.lista_scadenze.heading("Lotto", text="Lotto")
        self.lista_scadenze.heading("Scadenza", text="Scadenza")
        self.lista_scadenze.heading("Giorni Rimanenti", text="Giorni Rimanenti")
        self.lista_scadenze.heading("Quantità", text="Quantità")
        
        self.lista_scadenze.column("Prodotto", width=150)
        self.lista_scadenze.column("Lotto", width=100)
        self.lista_scadenze.column("Scadenza", width=100)
        self.lista_scadenze.column("Giorni Rimanenti", width=100)
        self.lista_scadenze.column("Quantità", width=80)
        
        self.lista_scadenze.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Aggiorna lista scadenze
        self.aggiorna_scadenze()
    
    def crea_scheda_statistiche(self):
        frame_statistiche = Frame(self.notebook)
        self.notebook.add(frame_statistiche, text="Statistiche")
        
        # Frame superiore (grafici)
        top_frame = Frame(frame_statistiche)
        top_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Frame inferiore (statistiche)
        bottom_frame = Frame(frame_statistiche)
        bottom_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Statistiche di consumo
        Label(bottom_frame, text="Statistiche di Consumo", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W)
        
        # Lista prodotti più consumati
        Label(bottom_frame, text="Prodotti più consumati:").grid(row=1, column=0, sticky=W)
        self.lista_consumi = ttk.Treeview(bottom_frame, columns=("Prodotto", "Quantità", "UM"), show="headings")
        self.lista_consumi.heading("Prodotto", text="Prodotto")
        self.lista_consumi.heading("Quantità", text="Quantità")
        self.lista_consumi.heading("UM", text="UM")
        self.lista_consumi.grid(row=2, column=0, sticky=NSEW, padx=5, pady=5)
        
        # Statistiche costi
        Label(bottom_frame, text="Costi per Categoria", font=('Arial', 12, 'bold')).grid(row=0, column=1, sticky=W)
        
        self.lista_costi = ttk.Treeview(bottom_frame, columns=("Categoria", "Costo Mensile", "Costo Annuale"), show="headings")
        self.lista_costi.heading("Categoria", text="Categoria")
        self.lista_costi.heading("Costo Mensile", text="Costo Mensile (€)")
        self.lista_costi.heading("Costo Annuale", text="Costo Annuale (€)")
        self.lista_costi.grid(row=1, column=1, rowspan=2, sticky=NSEW, padx=5, pady=5)
        
        # Configura griglia
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(2, weight=1)
        
        # Aggiorna statistiche
        self.aggiorna_statistiche()
    
    def crea_scheda_fornitori(self):
        frame_fornitori = Frame(self.notebook)
        self.notebook.add(frame_fornitori, text="Fornitori")
        
        # Pannello sinistro (lista fornitori)
        panel_sx = Frame(frame_fornitori)
        panel_sx.pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # Lista fornitori
        self.lista_fornitori = ttk.Treeview(panel_sx, columns=("ID", "Nome", "Telefono", "Email"), show="headings")
        self.lista_fornitori.heading("ID", text="ID")
        self.lista_fornitori.heading("Nome", text="Nome")
        self.lista_fornitori.heading("Telefono", text="Telefono")
        self.lista_fornitori.heading("Email", text="Email")
        self.lista_fornitori.column("ID", width=50)
        self.lista_fornitori.column("Nome", width=150)
        self.lista_fornitori.column("Telefono", width=100)
        self.lista_fornitori.column("Email", width=150)
        self.lista_fornitori.pack(fill=BOTH, expand=True)
        self.lista_fornitori.bind("<<TreeviewSelect>>", self.seleziona_fornitore)
        
        # Pulsanti fornitori
        btn_frame = Frame(panel_sx)
        btn_frame.pack(fill=X, pady=5)
        
        btn_aggiungi = Button(btn_frame, text="Aggiungi", command=self.aggiungi_fornitore)
        btn_aggiungi.pack(side=LEFT, padx=2)
        
        btn_modifica = Button(btn_frame, text="Modifica", command=self.modifica_fornitore)
        btn_modifica.pack(side=LEFT, padx=2)
        
        btn_elimina = Button(btn_frame, text="Elimina", command=self.elimina_fornitore)
        btn_elimina.pack(side=LEFT, padx=2)
        
        # Pannello destro (dettaglio fornitore)
        panel_dx = Frame(frame_fornitori)
        panel_dx.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Form dettaglio fornitore
        Label(panel_dx, text="ID:").grid(row=0, column=0, sticky=W, pady=2)
        self.forn_id = Entry(panel_dx)
        self.forn_id.grid(row=0, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Nome:").grid(row=1, column=0, sticky=W, pady=2)
        self.forn_nome = Entry(panel_dx)
        self.forn_nome.grid(row=1, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Indirizzo:").grid(row=2, column=0, sticky=W, pady=2)
        self.forn_indirizzo = Entry(panel_dx)
        self.forn_indirizzo.grid(row=2, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Telefono:").grid(row=3, column=0, sticky=W, pady=2)
        self.forn_telefono = Entry(panel_dx)
        self.forn_telefono.grid(row=3, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Email:").grid(row=4, column=0, sticky=W, pady=2)
        self.forn_email = Entry(panel_dx)
        self.forn_email.grid(row=4, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Prodotti forniti:").grid(row=5, column=0, sticky=W, pady=2)
        self.forn_prodotti = Text(panel_dx, height=5, width=30)
        self.forn_prodotti.grid(row=5, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Tempi consegna:").grid(row=6, column=0, sticky=W, pady=2)
        self.forn_tempi = Entry(panel_dx)
        self.forn_tempi.grid(row=6, column=1, sticky=EW, pady=2)
        
        Label(panel_dx, text="Note:").grid(row=7, column=0, sticky=NW, pady=2)
        self.forn_note = Text(panel_dx, height=5, width=30)
        self.forn_note.grid(row=7, column=1, sticky=EW, pady=2)
        
        # Pulsanti salva/annulla
        btn_salva = Button(panel_dx, text="Salva", command=self.salva_fornitore)
        btn_salva.grid(row=8, column=1, sticky=E, pady=5)
        
        btn_annulla = Button(panel_dx, text="Annulla", command=self.annulla_fornitore)
        btn_annulla.grid(row=8, column=0, sticky=W, pady=5)
        
        # Aggiorna lista fornitori
        self.aggiorna_lista_fornitori()
    
    def crea_menu(self):
        menubar = Menu(self.root)
        
        # Menu File
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuovo", command=self.nuovo_file)
        file_menu.add_command(label="Apri...", command=self.apri_file)
        file_menu.add_command(label="Salva", command=self.salva_file)
        file_menu.add_command(label="Salva con nome...", command=self.salva_con_nome)
        file_menu.add_separator()
        file_menu.add_command(label="Esporta Inventario...", command=self.esporta_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Menu Strumenti
        tools_menu = Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Genera Ordine Automatico", command=self.genera_ordine_automatico)
        tools_menu.add_command(label="Controlla Scorte", command=self.controlla_scorte)
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        
        self.root.config(menu=menubar)
    
    # Metodi per la gestione dei prodotti
    def aggiorna_lista_prodotti(self):
        self.lista_prodotti.delete(*self.lista_prodotti.get_children())
        for prodotto in self.prodotti:
            self.lista_prodotti.insert("", "end", values=(
                prodotto['id'],
                prodotto['nome'],
                prodotto['categoria'],
                prodotto['quantita'],
                prodotto['unita_misura']
            ))
    
    def seleziona_prodotto(self, event):
        selected = self.lista_prodotti.focus()
        if not selected:
            return
            
        values = self.lista_prodotti.item(selected, 'values')
        prodotto = next((p for p in self.prodotti if str(p['id']) == values[0]), None)
        
        if prodotto:
            self.prod_id.delete(0, END)
            self.prod_id.insert(0, prodotto['id'])
            
            self.prod_nome.delete(0, END)
            self.prod_nome.insert(0, prodotto['nome'])
            
            self.prod_categoria.set(prodotto['categoria'])
            
            self.prod_quantita.delete(0, END)
            self.prod_quantita.insert(0, prodotto['quantita'])
            
            self.prod_um.set(prodotto['unita_misura'])
            
            self.prod_prezzo.delete(0, END)
            self.prod_prezzo.insert(0, prodotto.get('prezzo_unitario', ''))
            
            self.prod_fornitore.set(prodotto.get('fornitore_principale', ''))
            
            self.prod_giacenza_min.delete(0, END)
            self.prod_giacenza_min.insert(0, prodotto.get('giacenza_minima', ''))
            
            self.prod_scadenza.delete(0, END)
            self.prod_scadenza.insert(0, prodotto.get('giorni_scadenza', ''))
            
            self.prod_note.delete(1.0, END)
            self.prod_note.insert(1.0, prodotto.get('note', ''))
    
    def aggiungi_prodotto(self):
        self.prod_id.delete(0, END)
        self.prod_nome.delete(0, END)
        self.prod_categoria.set('')
        self.prod_quantita.delete(0, END)
        self.prod_um.set('')
        self.prod_prezzo.delete(0, END)
        self.prod_fornitore.set('')
        self.prod_giacenza_min.delete(0, END)
        self.prod_scadenza.delete(0, END)
        self.prod_note.delete(1.0, END)
        
        # Genera nuovo ID
        nuovo_id = max([p['id'] for p in self.prodotti], default=0) + 1
        self.prod_id.insert(0, nuovo_id)
    
    def modifica_prodotto(self):
        selected = self.lista_prodotti.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un prodotto da modificare")
            return
        
        self.seleziona_prodotto(None)
    
    def elimina_prodotto(self):
        selected = self.lista_prodotti.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un prodotto da eliminare")
            return
            
        values = self.lista_prodotti.item(selected, 'values')
        prodotto_id = int(values[0])
        
        if messagebox.askyesno("Conferma", "Eliminare il prodotto selezionato?"):
            self.prodotti = [p for p in self.prodotti if p['id'] != prodotto_id]
            self.aggiorna_lista_prodotti()
            self.aggiorna_lista_inventario()
            self.salva_dati()
    
    def salva_prodotto(self):
        try:
            prodotto = {
                'id': int(self.prod_id.get()),
                'nome': self.prod_nome.get(),
                'categoria': self.prod_categoria.get(),
                'quantita': float(self.prod_quantita.get()),
                'unita_misura': self.prod_um.get(),
                'prezzo_unitario': float(self.prod_prezzo.get()) if self.prod_prezzo.get() else 0.0,
                'fornitore_principale': self.prod_fornitore.get(),
                'giacenza_minima': float(self.prod_giacenza_min.get()) if self.prod_giacenza_min.get() else 0.0,
                'giorni_scadenza': int(self.prod_scadenza.get()) if self.prod_scadenza.get() else 0,
                'note': self.prod_note.get(1.0, END).strip()
            }
            
            # Verifica se è un nuovo prodotto o una modifica
            existing = next((p for p in self.prodotti if p['id'] == prodotto['id']), None)
            
            if existing:
                # Aggiorna prodotto esistente
                index = self.prodotti.index(existing)
                self.prodotti[index] = prodotto
            else:
                # Aggiungi nuovo prodotto
                self.prodotti.append(prodotto)
            
            self.aggiorna_lista_prodotti()
            self.aggiorna_lista_inventario()
            self.salva_dati()
            
            messagebox.showinfo("Successo", "Prodotto salvato con successo")
        except ValueError as e:
            messagebox.showerror("Errore", f"Dati non validi: {str(e)}")
    
    def annulla_prodotto(self):
        self.seleziona_prodotto(None)
    
    # Metodi per la gestione dell'inventario
    def aggiorna_lista_inventario(self):
        self.lista_inventario.delete(*self.lista_inventario.get_children())
        for prodotto in self.prodotti:
            stato = "OK"
            if 'giacenza_minima' in prodotto and prodotto['quantita'] <= prodotto['giacenza_minima']:
                stato = "SCORTE BASSE"
            elif prodotto['quantita'] <= 0:
                stato = "ESAURITO"
                
            self.lista_inventario.insert("", "end", values=(
                prodotto['id'],
                prodotto['nome'],
                prodotto['categoria'],
                prodotto['quantita'],
                prodotto['unita_misura'],
                prodotto.get('giacenza_minima', ''),
                stato
            ), tags=(stato,))
        
        # Configura colori per gli stati
        self.lista_inventario.tag_configure("SCORTE BASSE", background='#FFFACD')
        self.lista_inventario.tag_configure("ESAURITO", background='#FFCCCB')
    
    def filtra_inventario(self):
        categoria = self.inv_categoria.get()
        scorte_basse = self.inv_scorte_basse.get()
        
        self.lista_inventario.delete(*self.lista_inventario.get_children())
        
        for prodotto in self.prodotti:
            # Filtra per categoria
            if categoria != "Tutte" and prodotto['categoria'] != categoria:
                continue
                
            # Filtra per scorte basse
            if scorte_basse and ('giacenza_minima' not in prodotto or prodotto['quantita'] > prodotto['giacenza_minima']):
                continue
                
            stato = "OK"
            if 'giacenza_minima' in prodotto and prodotto['quantita'] <= prodotto['giacenza_minima']:
                stato = "SCORTE BASSE"
            elif prodotto['quantita'] <= 0:
                stato = "ESAURITO"
                
            self.lista_inventario.insert("", "end", values=(
                prodotto['id'],
                prodotto['nome'],
                prodotto['categoria'],
                prodotto['quantita'],
                prodotto['unita_misura'],
                prodotto.get('giacenza_minima', ''),
                stato
            ), tags=(stato,))
    
    def registra_entrata(self):
        selected = self.lista_inventario.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un prodotto dall'inventario")
            return
            
        values = self.lista_inventario.item(selected, 'values')
        prodotto_id = int(values[0])
        
        # Finestra per inserire i dettagli dell'entrata
        dialog = Toplevel(self.root)
        dialog.title("Registra Entrata")
        dialog.geometry("400x300")
        
        Label(dialog, text="Quantità:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        quantita = Entry(dialog)
        quantita.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Lotto:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        lotto = Entry(dialog)
        lotto.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Data scadenza (GG/MM/AAAA):").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        scadenza = Entry(dialog)
        scadenza.grid(row=2, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Prezzo unitario (€):").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        prezzo = Entry(dialog)
        prezzo.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Fornitore:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        fornitore = ttk.Combobox(dialog, values=[f['nome'] for f in self.fornitori])
        fornitore.grid(row=4, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Note:").grid(row
# Aggiungi questa parte finale al tuo codice
        def conferma():
            try:
                qta = float(quantita.get())
                if qta <= 0:
                    raise ValueError("La quantità deve essere positiva")
                
                prodotto = next(p for p in self.prodotti if p['id'] == prodotto_id)
                prodotto['quantita'] += qta
                
                # Aggiungi alla cronologia movimenti
                movimento = {
                    'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'tipo': 'entrata',
                    'quantita': qta,
                    'prodotto_id': prodotto_id,
                    'prodotto_nome': prodotto['nome'],
                    'lotto': lotto.get(),
                    'scadenza': scadenza.get(),
                    'prezzo': float(prezzo.get()) if prezzo.get() else 0.0,
                    'fornitore': fornitore.get(),
                    'note': note.get("1.0", END).strip()
                }
                
                if 'movimenti' not in prodotto:
                    prodotto['movimenti'] = []
                prodotto['movimenti'].append(movimento)
                
                self.aggiorna_lista_inventario()
                self.salva_dati()
                dialog.destroy()
                messagebox.showinfo("Successo", "Entrata registrata con successo")
            except ValueError as e:
                messagebox.showerror("Errore", f"Dati non validi: {str(e)}")
        
        Label(dialog, text="Note:").grid(row=5, column=0, padx=5, pady=5, sticky=NW)
        note = Text(dialog, height=4, width=30)
        note.grid(row=5, column=1, padx=5, pady=5, sticky=EW)
        
        btn_frame = Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        Button(btn_frame, text="Conferma", command=conferma).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side=LEFT, padx=5)
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def registra_uscita(self):
        selected = self.lista_inventario.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un prodotto dall'inventario")
            return
            
        values = self.lista_inventario.item(selected, 'values')
        prodotto_id = int(values[0])
        prodotto = next(p for p in self.prodotti if p['id'] == prodotto_id)
        
        # Finestra per inserire i dettagli dell'uscita
        dialog = Toplevel(self.root)
        dialog.title("Registra Uscita")
        dialog.geometry("400x250")
        
        Label(dialog, text=f"Prodotto: {prodotto['nome']}").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=W)
        Label(dialog, text=f"Quantità disponibile: {prodotto['quantita']} {prodotto['unita_misura']}").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=W)
        
        Label(dialog, text="Quantità da prelevare:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        quantita = Entry(dialog)
        quantita.grid(row=2, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Motivo:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        motivo = ttk.Combobox(dialog, values=["Uso in cucina", "Vendita", "Spreco", "Altro"])
        motivo.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        
        Label(dialog, text="Note:").grid(row=4, column=0, padx=5, pady=5, sticky=NW)
        note = Text(dialog, height=4, width=30)
        note.grid(row=4, column=1, padx=5, pady=5, sticky=EW)
        
        def conferma():
            try:
                qta = float(quantita.get())
                if qta <= 0:
                    raise ValueError("La quantità deve essere positiva")
                if qta > prodotto['quantita']:
                    raise ValueError("Quantità insufficiente in magazzino")
                
                prodotto['quantita'] -= qta
                
                # Aggiungi alla cronologia movimenti
                movimento = {
                    'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'tipo': 'uscita',
                    'quantita': qta,
                    'prodotto_id': prodotto_id,
                    'prodotto_nome': prodotto['nome'],
                    'motivo': motivo.get(),
                    'note': note.get("1.0", END).strip()
                }
                
                if 'movimenti' not in prodotto:
                    produto['movimenti'] = []
                prodotto['movimenti'].append(movimento)
                
                self.aggiorna_lista_inventario()
                self.salva_dati()
                dialog.destroy()
                messagebox.showinfo("Successo", "Uscita registrata con successo")
            except ValueError as e:
                messagebox.showerror("Errore", f"Dati non validi: {str(e)}")
        
        btn_frame = Frame(dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        Button(btn_frame, text="Conferma", command=conferma).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side=LEFT, padx=5)
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def esporta_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["ID", "Nome", "Categoria", "Quantità", "UM", "Giacenza Minima", "Stato"])
                
                for prodotto in self.prodotti:
                    stato = "OK"
                    if 'giacenza_minima' in prodotto and prodotto['quantita'] <= prodotto['giacenza_minima']:
                        stato = "SCORTE BASSE"
                    elif prodotto['quantita'] <= 0:
                        stato = "ESAURITO"
                        
                    writer.writerow([
                        prodotto['id'],
                        prodotto['nome'],
                        prodotto['categoria'],
                        prodotto['quantita'],
                        prodotto['unita_misura'],
                        prodotto.get('giacenza_minima', ''),
                        stato
                    ])
                    
            messagebox.showinfo("Successo", f"Inventario esportato in {file_path}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile esportare: {str(e)}")
    
    # Metodi per la gestione degli ordini
    def aggiorna_lista_ordini(self):
        self.lista_ordini.delete(*self.lista_ordini.get_children())
        for ordine in self.ordini:
            self.lista_ordini.insert("", "end", values=(
                ordine['id'],
                ordine['fornitore'],
                ordine['data'],
                ordine['stato'],
                f"{ordine['totale']:.2f}"
            ))
    
    def seleziona_ordine(self, event):
        selected = self.lista_ordini.focus()
        if not selected:
            return
            
        # Pulisci il frame dei dettagli
        for widget in self.dettaglio_ordine_frame.winfo_children():
            widget.destroy()
            
        values = self.lista_ordini.item(selected, 'values')
        ordine = next((o for o in self.ordini if str(o['id']) == values[0]), None)
        
        if ordine:
            # Mostra i dettagli dell'ordine
            Label(self.dettaglio_ordine_frame, text=f"Ordine n. {ordine['id']}", font=('Arial', 12, 'bold')).pack(anchor=W)
            
            # Dettagli generali
            info_frame = Frame(self.dettaglio_ordine_frame)
            info_frame.pack(fill=X, pady=5)
            
            Label(info_frame, text=f"Fornitore: {ordine['fornitore']}").grid(row=0, column=0, sticky=W)
            Label(info_frame, text=f"Data: {ordine['data']}").grid(row=0, column=1, sticky=W)
            Label(info_frame, text=f"Stato: {ordine['stato']}").grid(row=0, column=2, sticky=W)
            Label(info_frame, text=f"Totale: € {ordine['totale']:.2f}").grid(row=0, column=3, sticky=W)
            
            # Lista prodotti ordinati
            tree_frame = Frame(self.dettaglio_ordine_frame)
            tree_frame.pack(fill=BOTH, expand=True)
            
            columns = ("Prodotto", "Quantità", "UM", "Prezzo Unitario", "Totale")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            tree.column("Prodotto", width=200)
            
            for item in ordine['dettagli']:
                tree.insert("", "end", values=(
                    item['prodotto'],
                    item['quantita'],
                    item['unita_misura'],
                    f"€ {item['prezzo_unitario']:.2f}",
                    f"€ {item['quantita'] * item['prezzo_unitario']:.2f}"
                ))
            
            tree.pack(fill=BOTH, expand=True)
            
            # Note
            note_frame = Frame(self.dettaglio_ordine_frame)
            note_frame.pack(fill=X, pady=5)
            
            Label(note_frame, text="Note:").pack(side=LEFT)
            note_text = Text(note_frame, height=3, width=50)
            note_text.pack(fill=X, expand=True)
            note_text.insert(END, ordine.get('note', ''))
            note_text.config(state=DISABLED)
    
    def nuovo_ordine(self):
        dialog = Toplevel(self.root)
        dialog.title("Nuovo Ordine")
        dialog.geometry("800x600")
        
        # Frame superiore (dati ordine)
        top_frame = Frame(dialog)
        top_frame.pack(fill=X, padx=5, pady=5)
        
        Label(top_frame, text="Fornitore:").grid(row=0, column=0, sticky=W)
        fornitore = ttk.Combobox(top_frame, values=[f['nome'] for f in self.fornitori])
        fornitore.grid(row=0, column=1, sticky=EW, padx=5)
        
        Label(top_frame, text="Data consegna prevista:").grid(row=1, column=0, sticky=W)
        data_consegna = Entry(top_frame)
        data_consegna.grid(row=1, column=1, sticky=EW, padx=5)
        
        Label(top_frame, text="Note:").grid(row=2, column=0, sticky=NW)
        note = Text(top_frame, height=3, width=30)
        note.grid(row=2, column=1, sticky=EW, padx=5)
        
        # Frame centrale (prodotti disponibili)
        center_frame = Frame(dialog)
        center_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Lista prodotti disponibili
        Label(center_frame, text="Prodotti disponibili:").pack(anchor=W)
        available_tree = ttk.Treeview(center_frame, columns=("ID", "Nome", "Categoria", "Quantità", "UM"), show="headings")
        available_tree.heading("ID", text="ID")
        available_tree.heading("Nome", text="Nome")
        available_tree.heading("Categoria", text="Categoria")
        available_tree.heading("Quantità", text="Quantità")
        available_tree.heading("UM", text="UM")
        available_tree.column("ID", width=50)
        available_tree.column("Nome", width=150)
        available_tree.column("Categoria", width=120)
        available_tree.column("Quantità", width=80)
        available_tree.column("UM", width=50)
        available_tree.pack(fill=BOTH, expand=True)
        
        # Popola la lista dei prodotti
        for prodotto in self.prodotti:
            available_tree.insert("", "end", values=(
                prodotto['id'],
                prodotto['nome'],
                prodotto['categoria'],
                prodotto['quantita'],
                prodotto['unita_misura']
            ))
        
        # Frame inferiore (prodotti ordinati)
        bottom_frame = Frame(dialog)
        bottom_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        Label(bottom_frame, text="Prodotti da ordinare:").pack(anchor=W)
        order_tree = ttk.Treeview(bottom_frame, columns=("Prodotto", "Quantità", "UM", "Prezzo Unitario"), show="headings")
        order_tree.heading("Prodotto", text="Prodotto")
        order_tree.heading("Quantità", text="Quantità")
        order_tree.heading("UM", text="UM")
        order_tree.heading("Prezzo Unitario", text="Prezzo Unitario")
        order_tree.column("Prodotto", width=200)
        order_tree.column("Quantità", width=80)
        order_tree.column("UM", width=50)
        order_tree.column("Prezzo Unitario", width=100)
        order_tree.pack(fill=BOTH, expand=True)
        
        # Pulsanti
        btn_frame = Frame(dialog)
        btn_frame.pack(fill=X, pady=5)
        
        def aggiungi_prodotto():
            selected = available_tree.focus()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona un prodotto da aggiungere")
                return
                
            values = available_tree.item(selected, 'values')
            prodotto_id = int(values[0])
            prodotto = next(p for p in self.prodotti if p['id'] == prodotto_id)
            
            # Finestra per inserire quantità e prezzo
            item_dialog = Toplevel(dialog)
            item_dialog.title("Aggiungi prodotto")
            item_dialog.geometry("300x200")
            
            Label(item_dialog, text=f"Prodotto: {prodotto['nome']}").pack(pady=5)
            
            Label(item_dialog, text="Quantità:").pack()
            qta = Entry(item_dialog)
            qta.pack()
            
            Label(item_dialog, text="Prezzo unitario (€):").pack()
            prezzo = Entry(item_dialog)
            prezzo.pack()
            
            def conferma_aggiunta():
                try:
                    quantita = float(qta.get())
                    prezzo_unitario = float(prezzo.get())
                    
                    if quantita <= 0 or prezzo_unitario <= 0:
                        raise ValueError("I valori devono essere positivi")
                        
                    order_tree.insert("", "end", values=(
                        prodotto['nome'],
                        quantita,
                        prodotto['unita_misura'],
                        prezzo_unitario
                    ))
                    
                    item_dialog.destroy()
                except ValueError as e:
                    messagebox.showerror("Errore", f"Dati non validi: {str(e)}")
            
            Button(item_dialog, text="Aggiungi", command=conferma_aggiunta).pack(pady=10)
        
        Button(btn_frame, text="Aggiungi Prodotto", command=aggiungi_prodotto).pack(side=LEFT, padx=5)
        
        def rimuovi_prodotto():
            selected = order_tree.focus()
            if selected:
                order_tree.delete(selected)
        
        Button(btn_frame, text="Rimuovi Prodotto", command=rimuovi_prodotto).pack(side=LEFT, padx=5)
        
        def conferma_ordine():
            if not fornitore.get():
                messagebox.showerror("Errore", "Seleziona un fornitore")
                return
                
            if not order_tree.get_children():
                messagebox.showerror("Errore", "Aggiungi almeno un prodotto all'ordine")
                return
                
            # Calcola il totale
            totale = 0.0
            dettagli = []
            
            for item in order_tree.get_children():
                values = order_tree.item(item, 'values')
                quantita = float(values[1])
                prezzo_unitario = float(values[3])
                totale += quantita * prezzo_unitario
                
                dettagli.append({
                    'prodotto': values[0],
                    'quantita': quantita,
                    'unita_misura': values[2],
                    'prezzo_unitario': prezzo_unitario
                })
            
            # Crea il nuovo ordine
            nuovo_id = max([o['id'] for o in self.ordini], default=0) + 1
            nuovo_ordine = {
                'id': nuovo_id,
                'fornitore': fornitore.get(),
                'data': datetime.now().strftime("%d/%m/%Y"),
                'data_consegna_prevista': data_consegna.get(),
                'stato': "In attesa",
                'totale': totale,
                'dettagli': dettagli,
                'note': note.get("1.0", END).strip()
            }
            
            self.ordini.append(nuovo_ordine)
            self.aggiorna_lista_ordini()
            self.salva_dati()
            dialog.destroy()
            messagebox.showinfo("Successo", "Ordine creato con successo")
        
        Button(btn_frame, text="Conferma Ordine", command=conferma_ordine).pack(side=RIGHT, padx=5)
        Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side=RIGHT, padx=5)
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def modifica_ordine(self):
        selected = self.lista_ordini.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un ordine da modificare")
            return
            
        values = self.lista_ordini.item(selected, 'values')
        ordine = next((o for o in self.ordini if str(o['id']) == values[0]), None)
        
        if ordine and ordine['stato'] != "In attesa":
            messagebox.showwarning("Attenzione", "Solo gli ordini 'In attesa' possono essere modificati")
            return
            
        # Implementazione simile a nuovo_ordine ma con dati precompilati
        # (omessa per brevità, ma dovrebbe aprire una finestra simile a nuovo_ordine con i dati esistenti)
    
    def elimina_ordine(self):
        selected = self.lista_ordini.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un ordine da eliminare")
            return
            
        values = self.lista_ordini.item(selected, 'values')
        ordine_id = int(values[0])
        ordine = next((o for o in self.ordini if o['id'] == ordine_id), None)
        
        if ordine and ordine['stato'] != "In attesa":
            messagebox.showwarning("Attenzione", "Solo gli ordini 'In attesa' possono essere eliminati")
            return
            
        if messagebox.askyesno("Conferma", "Eliminare l'ordine selezionato?"):
            self.ordini = [o for o in self.ordini if o['id'] != ordine_id]
            self.aggiorna_lista_ordini()
            self.salva_dati()
    
    def conferma_ricezione(self):
        selected = self.lista_ordini.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un ordine da confermare")
            return
            
        values = self.lista_ordini.item(selected, 'values')
        ordine_id = int(values[0])
        ordine = next((o for o in self.ordini if o['id'] == ordine_id), None)
        
        if not ordine or ordine['stato'] != "In attesa":
            messagebox.showwarning("Attenzione", "Solo gli ordini 'In attesa' possono essere confermati")
            return
            
        # Finestra di conferma ricezione
        dialog = Toplevel(self.root)
        dialog.title("Conferma Ricezione Ordine")
        dialog.geometry("400x300")
        
        Label(dialog, text=f"Conferma ricezione ordine n. {ordine_id}").pack(pady=5)
        
        Label(dialog, text="Data effettiva consegna:").pack()
        data_consegna = Entry(dialog)
        data_consegna.pack()
        data_consegna.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        Label(dialog, text="Note:").pack()
        note = Text(dialog, height=5, width=40)
        note.pack(fill=BOTH, expand=True)
        
        def conferma():
            # Aggiorna lo stato dell'ordine
            ordine['stato'] = "Consegnato"
            ordine['data_consegna_effettiva'] = data_consegna.get()
            ordine['note_ricezione'] = note.get("1.0", END).strip()
            
            # Aggiorna le quantità in magazzino
            for item in ordine['dettagli']:
                prodotto = next((p for p in self.prodotti if p['nome'] == item['prodotto']), None)
                if prodotto:
                    prodotto['quantita'] += item['quantita']
                    
                    # Aggiungi movimento
                    movimento = {
                        'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'tipo': 'entrata',
                        'quantita': item['quantita'],
                        'prodotto_id': prodotto['id'],
                        'prodotto_nome': prodotto['nome'],
                        'lotto': f"ORDINE {ordine_id}",
                        'prezzo': item['prezzo_unitario'],
                        'fornitore': ordine['fornitore'],
                        'note': f"Ricezione ordine n. {ordine_id}"
                    }
                    
                    if 'movimenti' not in prodotto:
                        prodotto['movimenti'] = []
                    prodotto['movimenti'].append(movimento)
            
            self.aggiorna_lista_ordini()
            self.aggiorna_lista_inventario()
            self.salva_dati()
            dialog.destroy()
            messagebox.showinfo("Successo", "Ordine confermato e magazzino aggiornato")
        
        Button(dialog, text="Conferma", command=conferma).pack(side=LEFT, padx=20, pady=10)
        Button(dialog, text="Annulla", command=dialog.destroy).pack(side=RIGHT, padx=20, pady=10)
    
    # Metodi per la gestione delle scadenze
    def aggiorna_scadenze(self):
        self.lista_scadenze.delete(*self.lista_scadenze.get_children())
        giorni = int(self.scadenza_giorni.get())
        data_limite = datetime.now() + timedelta(days=giorni)
        
        for prodotto in self.prodotti:
            if 'movimenti' not in prodotto:
                continue
                
            for movimento in prodotto['movimenti']:
                if movimento['tipo'] == 'entrata' and 'scadenza' in movimento and movimento['scadenza']:
                    try:
                        data_scadenza = datetime.strptime(movimento['scadenza'], "%d/%m/%Y")
                        if data_scadenza <= data_limite:
                            giorni_rimanenti = (data_scadenza - datetime.now()).days
                            self.lista_scadenze.insert("", "end", values=(
                                prodotto['nome'],
                                movimento.get('lotto', ''),
                                movimento['scadenza'],
                                giorni_rimanenti,
                                movimento['quantita']
                            ), tags=("scaduto" if giorni_rimanenti < 0 else "in_scadenza"))
                    except ValueError:
                        continue
        
        # Configura colori per le scadenze
        self.lista_scadenze.tag_configure("scaduto", background='#FFCCCB')
        self.lista_scadenze.tag_configure("in_scadenza", background='#FFFACD')
    
    # Metodi per la gestione delle statistiche
    def aggiorna_statistiche(self):
        # Prodotti più consumati (ultimi 30 giorni)
        self.lista_consumi.delete(*self.lista_consumi.get_children())
        
        consumi = {}
        trenta_giorni_fa = datetime.now() - timedelta(days=30)
        
        for prodotto in self.prodotti:
            if 'movimenti' not in prodotto:
                continue
                
            for movimento in prodotto['movimenti']:
                if movimento['tipo'] == 'uscita':
                    try:
                        data_movimento = datetime.strptime(movimento['data'], "%d/%m/%Y %H:%M")
                        if data_movimento >= trenta_giorni_fa:
                            if prodotto['nome'] not in consumi:
                                consumi[prodotto['nome']] = 0.0
                            consumi[prodotto['nome']] += movimento['quantita']
                    except ValueError:
                        continue
        
        # Ordina per quantità consumata
        prodotti_consumati = sorted(consumi.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for nome, quantita in prodotti_consumati:
            prodotto = next((p for p in self.prodotti if p['nome'] == nome), None)
            if prodotto:
                self.lista_consumi.insert("", "end", values=(
                    nome,
                    quantita,
                    prodotto['unita_misura']
                ))
        
        # Costi per categoria (ultimi 30 giorni)
        self.lista_costi.delete(*self.lista_costi.get_children())
        
        costi_mensili = {categoria: 0.0 for categoria in self.categorie}
        costi_annuali = {categoria: 0.0 for categoria in self.categorie}
        
        for prodotto in self.prodotti:
            if 'movimenti' not in prodotto:
                continue
                
            for movimento in prodotto['movimenti']:
                if movimento['tipo'] == 'entrata' and 'prezzo' in movimento:
                    try:
                        data_movimento = datetime.strptime(movimento['data'], "%d/%m/%Y %H:%M")
                        costo = movimento['quantita'] * movimento['prezzo']
                        
                        if data_movimento >= trenta_giorni_fa:
                            costi_mensili[prodotto['categoria']] += costo
                        
                        if data_movimento >= datetime.now() - timedelta(days=365):
                            costi_annuali[prodotto['categoria']] += costo
                    except ValueError:
                        continue
        
        for categoria in self.categorie:
            if costi_mensili[categoria] > 0 or costi_annuali[categoria] > 0:
                self.lista_costi.insert("", "end", values=(
                    categoria,
                    f"{costi_mensili[categoria]:.2f}",
                    f"{costi_annuali[categoria]:.2f}"
                ))
    
    # Metodi per la gestione dei fornitori
    def aggiorna_lista_fornitori(self):
        self.lista_fornitori.delete(*self.lista_fornitori.get_children())
        for fornitore in self.fornitori:
            self.lista_fornitori.insert("", "end", values=(
                fornitore['id'],
                fornitore['nome'],
                fornitore.get('telefono', ''),
                fornitore.get('email', '')
            ))
    
    def seleziona_fornitore(self, event):
        selected = self.lista_fornitori.focus()
        if not selected:
            return
            
        values = self.lista_fornitori.item(selected, 'values')
        fornitore = next((f for f in self.fornitori if str(f['id']) == values[0]), None)
        
        if fornitore:
            self.forn_id.delete(0, END)
            self.forn_id.insert(0, fornitore['id'])
            
            self.forn_nome.delete(0, END)
            self.forn_nome.insert(0, fornitore['nome'])
            
            self.forn_indirizzo.delete(0, END)
            self.forn_indirizzo.insert(0, fornitore.get('indirizzo', ''))
            
            self.forn_telefono.delete(0, END)
            self.forn_telefono.insert(0, fornitore.get('telefono', ''))
            
            self.forn_email.delete(0, END)
            self.forn_email.insert(0, fornitore.get('email', ''))
            
            self.forn_prodotti.delete(1.0, END)
            self.forn_prodotti.insert(1.0, fornitore.get('prodotti_forniti', ''))
            
            self.forn_tempi.delete(0, END)
            self.forn_tempi.insert(0, fornitore.get('tempi_consegna', ''))
            
            self.forn_note.delete(1.0, END)
            self.forn_note.insert(1.0, fornitore.get('note', ''))
    
    def aggiungi_fornitore(self):
        self.forn_id.delete(0, END)
        self.forn_nome.delete(0, END)
        self.forn_indirizzo.delete(0, END)
        self.forn_telefono.delete(0, END)
        self.forn_email.delete(0, END)
        self.forn_prodotti.delete(1.0, END)
        self.forn_tempi.delete(0, END)
        self.forn_note.delete(1.0, END)
        
        # Genera nuovo ID
        nuovo_id = max([f['id'] for f in self.fornitori], default=0) + 1
        self.forn_id.insert(0, nuovo_id)
    
    def modifica_fornitore(self):
        selected = self.lista_fornitori.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un fornitore da modificare")
            return
        
        self.seleziona_fornitore(None)
    
    def elimina_fornitore(self):
        selected = self.lista_fornitori.focus()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un fornitore da eliminare")
            return
            
        values = self.lista_fornitori.item(selected, 'values')
        fornitore_id = int(values[0])
        
        # Verifica se il fornitore è associato a prodotti
        prodotti_associati = [p for p in self.prodotti if p.get('fornitore_principale') == values[1]]
        
        if prodotti_associati:
            messagebox.showerror("Errore", f"Impossibile eliminare: {len(prodotti_associati)} prodotti associati a questo fornitore")
            return
            
        if messagebox.askyesno("Conferma", "Eliminare il fornitore selezionato?"):
            self.fornitori = [f for f in self.fornitori if f['id'] != fornitore_id]
            self.aggiorna_lista_fornitori()
            self.salva_dati()
    
    def salva_fornitore(self):
        try:
            fornitore = {
                'id': int(self.forn_id.get()),
                'nome': self.forn_nome.get(),
                'indirizzo': self.forn_indirizzo.get(),
                'telefono': self.forn_telefono.get(),
                'email': self.forn_email.get(),
                'prodotti_forniti': self.forn_prodotti.get(1.0, END).strip(),
                'tempi_consegna': self.forn_tempi.get(),
                'note': self.forn_note.get(1.0, END).strip()
            }
            
            # Verifica se è un nuovo fornitore o una modifica
            existing = next((f for f in self.fornitori if f['id'] == fornitore['id']), None)
            
            if existing:
                # Aggiorna fornitore esistente
                index = self.fornitori.index(existing)
                self.fornitori[index] = fornitore
            else:
                # Aggiungi nuovo fornitore
                self.fornitori.append(fornitore)
            
            self.aggiorna_lista_fornitori()
            
            # Aggiorna anche la lista fornitori nella scheda prodotti
            self.prod_fornitore['values'] = [f['nome'] for f in self.fornitori]
            
            self.salva_dati()
            
            messagebox.showinfo("Successo", "Fornitore salvato con successo")
        except ValueError as e:
            messagebox.showerror("Errore", f"Dati non validi: {str(e)}")
    
    def annulla_fornitore(self):
        self.seleziona_fornitore(None)
    
    # Metodi per la gestione dei file
    def carica_dati(self):
        try:
            if os.path.exists("magazzino_data.json"):
                with open("magazzino_data.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.prodotti = data.get('prodotti', [])
                    self.fornitori = data.get('fornitori', [])
                    self.ordini = data.get('ordini', [])
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare i dati: {str(e)}")
    
    def salva_dati(self):
        try:
            data = {
                'prodotti': self.prodotti,
                'fornitori': self.fornitori,
                'ordini': self.ordini
            }
            
            with open("magazzino_data.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare i dati: {str(e)}")
    
    def nuovo_file(self):
        if messagebox.askyesno("Conferma", "Creare un nuovo file? Tutti i dati non salvati andranno persi."):
            self.prodotti = []
            self.fornitori = []
            self.ordini = []
            
            self.aggiorna_lista_prodotti()
            self.aggiorna_lista_inventario()
            self.aggiorna_lista_ordini()
            self.aggiorna_lista_fornitori()
            self.aggiorna_scadenze()
            self.aggiorna_statistiche()
            
            self.salva_dati()
    
    def apri_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.prodotti = data.get('prodotti', [])
                    self.fornitori = data.get('fornitori', [])
                    self.ordini = data.get('ordini', [])
                
                self.aggiorna_lista_prodotti()
                self.aggiorna_lista_inventario()
                self.aggiorna_lista_ordini()
                self.aggiorna_lista_fornitori()
                self.aggiorna_scadenze()
                self.aggiorna_statistiche()
                
                messagebox.showinfo("Successo", "File caricato con successo")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile aprire il file: {str(e)}")

    def salva_file(self):
        try:
            self.salva_dati()
            messagebox.showinfo("Successo", "Dati salvati con successo")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare i dati: {str(e)}")

    def salva_con_nome(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                data = {
                    'prodotti': self.prodotti,
                    'fornitori': self.fornitori,
                    'ordini': self.ordini
                }
                
                with open(file_path, "w", encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Successo", f"File salvato come {file_path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile salvare il file: {str(e)}")

    def genera_ordine_automatico(self):
        # Identifica prodotti con scorte basse
        prodotti_scorte_basse = [
            p for p in self.prodotti 
            if 'giacenza_minima' in p and p['quantita'] <= p['giacenza_minima']
        ]
        
        if not prodotti_scorte_basse:
            messagebox.showinfo("Info", "Nessun prodotto con scorte basse da ordinare")
            return
            
        # Raggruppa per fornitore
        ordini_per_fornitore = {}
        
        for prodotto in prodotti_scorte_basse:
            fornitore = prodotto.get('fornitore_principale')
            if not fornitore:
                continue
                
            if fornitore not in ordini_per_fornitore:
                ordini_per_fornitore[fornitore] = []
                
            quantita_da_ordinare = prodotto['giacenza_minima'] * 2 - prodotto['quantita']
            ordini_per_fornitore[fornitore].append({
                'prodotto': prodotto['nome'],
                'quantita': quantita_da_ordinare,
                'unita_misura': prodotto['unita_misura'],
                'prezzo_unitario': prodotto.get('prezzo_unitario', 0)
            })
        
        # Crea gli ordini
        for fornitore, prodotti in ordini_per_fornitore.items():
            nuovo_id = max([o['id'] for o in self.ordini], default=0) + 1
            totale = sum(p['quantita'] * p['prezzo_unitario'] for p in prodotti)
            
            nuovo_ordine = {
                'id': nuovo_id,
                'fornitore': fornitore,
                'data': datetime.now().strftime("%d/%m/%Y"),
                'stato': "In attesa",
                'totale': totale,
                'dettagli': prodotti,
                'note': "Ordine generato automaticamente dal sistema"
            }
            
            self.ordini.append(nuovo_ordine)
        
        self.aggiorna_lista_ordini()
        self.salva_dati()
        messagebox.showinfo("Successo", f"Generati {len(ordini_per_fornitore)} ordini automatici")

    def controlla_scorte(self):
        prodotti_scorte_basse = [
            p for p in self.prodotti 
            if 'giacenza_minima' in p and p['quantita'] <= p['giacenza_minima']
        ]
        
        if prodotti_scorte_basse:
            message = "Prodotti con scorte basse:\n\n"
            for p in prodotti_scorte_basse:
                message += f"- {p['nome']} ({p['quantita']}/{p['giacenza_minima']} {p['unita_misura']})\n"
            
            message += "\nVuoi generare ordini automatici per questi prodotti?"
            
            if messagebox.askyesno("Scorte Basse", message):
                self.genera_ordine_automatico()
        else:
            messagebox.showinfo("Info", "Nessun prodotto con scorte basse")

# Avvio dell'applicazione
if __name__ == "__main__":
    root = Tk()
    app = MagazzinoPizzeria(root)
    root.mainloop()
