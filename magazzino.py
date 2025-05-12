from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify, make_response
from datetime import datetime, timedelta
import sqlite3
import os
import csv
from io import StringIO
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  
DATABASE = 'magazzino_pizzeria.db'

if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE prodotti (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT NOT NULL,
                 categoria TEXT NOT NULL,
                 quantita REAL NOT NULL,
                 um TEXT NOT NULL,
                 soglia_minima REAL DEFAULT 0,
                 data_scadenza TEXT,
                 note TEXT
                 )''')
    
    c.execute('''CREATE TABLE movimenti (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 prodotto_id INTEGER NOT NULL,
                 tipo TEXT NOT NULL,  # 'entrata' o 'uscita'
                 quantita REAL NOT NULL,
                 data TEXT NOT NULL,
                 motivo TEXT,
                 FOREIGN KEY (prodotto_id) REFERENCES prodotti (id)
                 )''')

    c.execute('''CREATE TABLE utenti (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 ruolo TEXT NOT NULL  # 'admin' o 'user'
                 )''')
    
    c.execute("INSERT INTO utenti (username, password, ruolo) VALUES (?, ?, ?)",
              ('admin', 'admin123', 'admin'))  
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Per favore, effettua il login per accedere a questa pagina.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'ruolo' not in session or session['ruolo'] != 'admin':
            flash('Accesso negato. Richiesti privilegi di amministratore.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def format_date(value, format='%d/%m/%Y'):
    if value is None:
        return ''
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

app.jinja_env.filters['date'] = format_date


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM utenti WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['ruolo'] = user['ruolo']
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username o password non validi', 'danger')
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="login-container">
            <h2>Login Magazzino</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Accedi</button>
            </form>
        </div>
        {% endblock %}
    ''')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Sei stato disconnesso con successo.', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    
    prodotti_esaurimento = conn.execute('''
        SELECT * FROM prodotti 
        WHERE quantita < soglia_minima AND quantita > 0
        ORDER BY quantita ASC
        LIMIT 5
    ''').fetchall()
    
    prodotti_terminati = conn.execute('''
        SELECT * FROM prodotti 
        WHERE quantita <= 0
        ORDER BY nome ASC
    ''').fetchall()

    totale_prodotti = conn.execute('SELECT COUNT(*) FROM prodotti').fetchone()[0]
    
    movimenti_recenti = conn.execute('''
        SELECT m.*, p.nome as prodotto_nome 
        FROM movimenti m
        JOIN prodotti p ON m.prodotto_id = p.id
        ORDER BY m.data DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="dashboard">
            <h2>Dashboard Magazzino</h2>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h3>Prodotti in Magazzino</h3>
                    <p>{{ totale_prodotti }}</p>
                </div>
                <div class="stat-card warning">
                    <h3>Prodotti in Esaurimento</h3>
                    <p>{{ prodotti_esaurimento|length }}</p>
                </div>
                <div class="stat-card danger">
                    <h3>Prodotti Terminati</h3>
                    <p>{{ prodotti_terminati|length }}</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col">
                    <h3>Prodotti in Esaurimento</h3>
                    {% if prodotti_esaurimento %}
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Prodotto</th>
                                    <th>Categoria</th>
                                    <th>Quantità</th>
                                    <th>Soglia Minima</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for p in prodotti_esaurimento %}
                                <tr>
                                    <td>{{ p['nome'] }}</td>
                                    <td>{{ p['categoria'] }}</td>
                                    <td class="warning">{{ p['quantita'] }} {{ p['um'] }}</td>
                                    <td>{{ p['soglia_minima'] }} {{ p['um'] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <p>Nessun prodotto in esaurimento</p>
                    {% endif %}
                </div>
                
                <div class="col">
                    <h3>Prodotti Terminati</h3>
                    {% if prodotti_terminati %}
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Prodotto</th>
                                    <th>Categoria</th>
                                    <th>Quantità</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for p in prodotti_terminati %}
                                <tr>
                                    <td>{{ p['nome'] }}</td>
                                    <td>{{ p['categoria'] }}</td>
                                    <td class="danger">{{ p['quantita'] }} {{ p['um'] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <p>Nessun prodotto terminato</p>
                    {% endif %}
                </div>
            </div>
            
            <h3>Movimenti Recenti</h3>
            {% if movimenti_recenti %}
                <table class="table">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Prodotto</th>
                            <th>Tipo</th>
                            <th>Quantità</th>
                            <th>Motivo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in movimenti_recenti %}
                        <tr>
                            <td>{{ m['data']|date }}</td>
                            <td>{{ m['prodotto_nome'] }}</td>
                            <td class="{{ 'success' if m['tipo'] == 'entrata' else 'danger' }}">
                                {{ 'Entrata' if m['tipo'] == 'entrata' else 'Uscita' }}
                            </td>
                            <td>{{ m['quantita'] }}</td>
                            <td>{{ m['motivo'] or '' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>Nessun movimento recente</p>
            {% endif %}
        </div>
        {% endblock %}
    ''', **locals())

@app.route('/prodotti')
@login_required
def lista_prodotti():
    conn = get_db()
    search = request.args.get('search', '')
    
    query = 'SELECT * FROM prodotti'
    params = []
    
    if search:
        query += ' WHERE nome LIKE ? OR categoria LIKE ?'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY nome ASC'
    prodotti = conn.execute(query, params).fetchall()
    
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="prodotti-container">
            <h2>Gestione Prodotti</h2>
            
            <div class="toolbar">
                <form method="GET" class="search-form">
                    <input type="text" name="search" placeholder="Cerca prodotto..." value="{{ search }}">
                    <button type="submit" class="btn btn-secondary">Cerca</button>
                </form>
                <a href="{{ url_for('aggiungi_prodotto') }}" class="btn btn-primary">Aggiungi Prodotto</a>
            </div>
            
            {% if prodotti %}
                <table class="table">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Categoria</th>
                            <th>Quantità</th>
                            <th>UM</th>
                            <th>Soglia Minima</th>
                            <th>Scadenza</th>
                            <th>Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in prodotti %}
                        <tr class="{{ 'warning' if p['quantita'] < p['soglia_minima'] and p['quantita'] > 0 else 'danger' if p['quantita'] <= 0 else '' }}">
                            <td>{{ p['nome'] }}</td>
                            <td>{{ p['categoria'] }}</td>
                            <td>{{ p['quantita'] }}</td>
                            <td>{{ p['um'] }}</td>
                            <td>{{ p['soglia_minima'] }}</td>
                            <td>{{ p['data_scadenza']|date if p['data_scadenza'] else '' }}</td>
                            <td class="actions">
                                <a href="{{ url_for('modifica_prodotto', id=p['id']) }}" class="btn btn-sm btn-info">Modifica</a>
                                <a href="{{ url_for('elimina_prodotto', id=p['id']) }}" class="btn btn-sm btn-danger" onclick="return confirm('Sei sicuro?')">Elimina</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>Nessun prodotto trovato</p>
            {% endif %}
        </div>
        {% endblock %}
    ''', **locals())

@app.route('/prodotti/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_prodotto():
    if request.method == 'POST':
        nome = request.form['nome']
        categoria = request.form['categoria']
        quantita = float(request.form['quantita'])
        um = request.form['um']
        soglia_minima = float(request.form.get('soglia_minima', 0))
        data_scadenza = request.form.get('data_scadenza')
        note = request.form.get('note', '')
        
        conn = get_db()
        conn.execute('''
            INSERT INTO prodotti (nome, categoria, quantita, um, soglia_minima, data_scadenza, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, categoria, quantita, um, soglia_minima, data_scadenza, note))
        conn.commit()
        conn.close()
        
        flash('Prodotto aggiunto con successo!', 'success')
        return redirect(url_for('lista_prodotti'))
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="form-container">
            <h2>Aggiungi Prodotto</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="nome">Nome Prodotto*</label>
                    <input type="text" id="nome" name="nome" required>
                </div>
                <div class="form-group">
                    <label for="categoria">Categoria*</label>
                    <input type="text" id="categoria" name="categoria" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="quantita">Quantità*</label>
                        <input type="number" step="0.01" id="quantita" name="quantita" required>
                    </div>
                    <div class="form-group">
                        <label for="um">Unità di Misura*</label>
                        <select id="um" name="um" required>
                            <option value="kg">kg</option>
                            <option value="g">g</option>
                            <option value="lt">lt</option>
                            <option value="ml">ml</option>
                            <option value="pz">pz</option>
                            <option value="lattine">lattine</option>
                            <option value="bottiglie">bottiglie</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="soglia_minima">Soglia Minima</label>
                    <input type="number" step="0.01" id="soglia_minima" name="soglia_minima" value="0">
                </div>
                <div class="form-group">
                    <label for="data_scadenza">Data di Scadenza</label>
                    <input type="date" id="data_scadenza" name="data_scadenza">
                </div>
                <div class="form-group">
                    <label for="note">Note</label>
                    <textarea id="note" name="note" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Salva Prodotto</button>
                <a href="{{ url_for('lista_prodotti') }}" class="btn btn-secondary">Annulla</a>
            </form>
        </div>
        {% endblock %}
    ''')

@app.route('/prodotti/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_prodotto(id):
    conn = get_db()
    prodotto = conn.execute('SELECT * FROM prodotti WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nome = request.form['nome']
        categoria = request.form['categoria']
        quantita = float(request.form['quantita'])
        um = request.form['um']
        soglia_minima = float(request.form.get('soglia_minima', 0))
        data_scadenza = request.form.get('data_scadenza')
        note = request.form.get('note', '')
        
        conn.execute('''
            UPDATE prodotti 
            SET nome = ?, categoria = ?, quantita = ?, um = ?, soglia_minima = ?, data_scadenza = ?, note = ?
            WHERE id = ?
        ''', (nome, categoria, quantita, um, soglia_minima, data_scadenza, note, id))
        conn.commit()
        conn.close()
        
        flash('Prodotto modificato con successo!', 'success')
        return redirect(url_for('lista_prodotti'))
    
    conn.close()
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="form-container">
            <h2>Modifica Prodotto</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="nome">Nome Prodotto*</label>
                    <input type="text" id="nome" name="nome" value="{{ prodotto['nome'] }}" required>
                </div>
                <div class="form-group">
                    <label for="categoria">Categoria*</label>
                    <input type="text" id="categoria" name="categoria" value="{{ prodotto['categoria'] }}" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="quantita">Quantità*</label>
                        <input type="number" step="0.01" id="quantita" name="quantita" value="{{ prodotto['quantita'] }}" required>
                    </div>
                    <div class="form-group">
                        <label for="um">Unità di Misura*</label>
                        <select id="um" name="um" required>
                            <option value="kg" {% if prodotto['um'] == 'kg' %}selected{% endif %}>kg</option>
                            <option value="g" {% if prodotto['um'] == 'g' %}selected{% endif %}>g</option>
                            <option value="lt" {% if prodotto['um'] == 'lt' %}selected{% endif %}>lt</option>
                            <option value="ml" {% if prodotto['um'] == 'ml' %}selected{% endif %}>ml</option>
                            <option value="pz" {% if prodotto['um'] == 'pz' %}selected{% endif %}>pz</option>
                            <option value="lattine" {% if prodotto['um'] == 'lattine' %}selected{% endif %}>lattine</option>
                            <option value="bottiglie" {% if prodotto['um'] == 'bottiglie' %}selected{% endif %}>bottiglie</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="soglia_minima">Soglia Minima</label>
                    <input type="number" step="0.01" id="soglia_minima" name="soglia_minima" value="{{ prodotto['soglia_minima'] }}">
                </div>
                <div class="form-group">
                    <label for="data_scadenza">Data di Scadenza</label>
                    <input type="date" id="data_scadenza" name="data_scadenza" value="{{ prodotto['data_scadenza'] or '' }}">
                </div>
                <div class="form-group">
                    <label for="note">Note</label>
                    <textarea id="note" name="note" rows="3">{{ prodotto['note'] or '' }}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Salva Modifiche</button>
                <a href="{{ url_for('lista_prodotti') }}" class="btn btn-secondary">Annulla</a>
            </form>
        </div>
        {% endblock %}
    ''', prodotto=prodotto)

@app.route('/prodotti/elimina/<int:id>')
@login_required
@admin_required
def elimina_prodotto(id):
    conn = get_db()
    conn.execute('DELETE FROM prodotti WHERE id = ?', (id,))
    conn.execute('DELETE FROM movimenti WHERE prodotto_id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Prodotto eliminato con successo!', 'success')
    return redirect(url_for('lista_prodotti'))


@app.route('/movimenti')
@login_required
def lista_movimenti():
    conn = get_db()
    
    tipo = request.args.get('tipo', '')
    prodotto_id = request.args.get('prodotto_id', '')
    data_inizio = request.args.get('data_inizio', '')
    data_fine = request.args.get('data_fine', '')
    
    query = '''
        SELECT m.*, p.nome as prodotto_nome 
        FROM movimenti m
        JOIN prodotti p ON m.prodotto_id = p.id
    '''
    params = []
    conditions = []
    
    if tipo:
        conditions.append('m.tipo = ?')
        params.append(tipo)
    
    if prodotto_id:
        conditions.append('m.prodotto_id = ?')
        params.append(prodotto_id)
    
    if data_inizio:
        conditions.append('m.data >= ?')
        params.append(data_inizio)
    
    if data_fine:
        conditions.append('m.data <= ?')
        params.append(data_fine)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY m.data DESC, m.id DESC'
    movimenti = conn.execute(query, params).fetchall()
    
    prodotti = conn.execute('SELECT id, nome FROM prodotti ORDER BY nome').fetchall()
    
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="movimenti-container">
            <h2>Movimenti Magazzino</h2>
            
            <div class="filtri">
                <form method="GET">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="tipo">Tipo</label>
                            <select id="tipo" name="tipo">
                                <option value="">Tutti</option>
                                <option value="entrata" {% if tipo == 'entrata' %}selected{% endif %}>Entrata</option>
                                <option value="uscita" {% if tipo == 'uscita' %}selected{% endif %}>Uscita</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="prodotto_id">Prodotto</label>
                            <select id="prodotto_id" name="prodotto_id">
                                <option value="">Tutti</option>
                                {% for p in prodotti %}
                                <option value="{{ p['id'] }}" {% if prodotto_id == p['id']|string %}selected{% endif %}>{{ p['nome'] }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="data_inizio">Da Data</label>
                            <input type="date" id="data_inizio" name="data_inizio" value="{{ data_inizio }}">
                        </div>
                        <div class="form-group">
                            <label for="data_fine">A Data</label>
                            <input type="date" id="data_fine" name="data_fine" value="{{ data_fine }}">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-secondary">Filtra</button>
                    <a href="{{ url_for('lista_movimenti') }}" class="btn btn-outline-secondary">Reset</a>
                </form>
            </div>
            
            <div class="toolbar">
                <a href="{{ url_for('nuovo_movimento') }}" class="btn btn-primary">Nuovo Movimento</a>
                <a href="{{ url_for('export_movimenti') }}?{{ request.query_string.decode() }}" class="btn btn-info">Esporta CSV</a>
            </div>
            
            {% if movimenti %}
                <table class="table">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Prodotto</th>
                            <th>Tipo</th>
                            <th>Quantità</th>
                            <th>Motivo</th>
                            <th>Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in movimenti %}
                        <tr>
                            <td>{{ m['data']|date }}</td>
                            <td>{{ m['prodotto_nome'] }}</td>
                            <td class="{{ 'success' if m['tipo'] == 'entrata' else 'danger' }}">
                                {{ 'Entrata' if m['tipo'] == 'entrata' else 'Uscita' }}
                            </td>
                            <td>{{ m['quantita'] }}</td>
                            <td>{{ m['motivo'] or '' }}</td>
                            <td class="actions">
                                <a href="{{ url_for('modifica_movimento', id=m['id']) }}" class="btn btn-sm btn-info">Modifica</a>
                                <a href="{{ url_for('elimina_movimento', id=m['id']) }}" class="btn btn-sm btn-danger" onclick="return confirm('Sei sicuro?')">Elimina</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>Nessun movimento trovato</p>
            {% endif %}
        </div>
        {% endblock %}
    ''', **locals())

@app.route('/movimenti/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_movimento():
    if request.method == 'POST':
        prodotto_id = request.form['prodotto_id']
        tipo = request.form['tipo']
        quantita = float(request.form['quantita'])
        motivo = request.form.get('motivo', '')
        data = request.form.get('data', datetime.now().strftime('%Y-%m-%d'))
        
        conn = get_db()
        
 
        if tipo == 'entrata':
            conn.execute('UPDATE prodotti SET quantita = quantita + ? WHERE id = ?', (quantita, prodotto_id))
        else:
            conn.execute('UPDATE prodotti SET quantita = quantita - ? WHERE id = ?', (quantita, prodotto_id))
        
        conn.execute('''
            INSERT INTO movimenti (prodotto_id, tipo, quantita, data, motivo)
            VALUES (?, ?, ?, ?, ?)
        ''', (prodotto_id, tipo, quantita, data, motivo))
        
        conn.commit()
        conn.close()
        
        flash('Movimento registrato con successo!', 'success')
        return redirect(url_for('lista_movimenti'))
    
    conn = get_db()
    prodotti = conn.execute('SELECT id, nome FROM prodotti ORDER BY nome').fetchall()
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="form-container">
            <h2>Nuovo Movimento</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="prodotto_id">Prodotto*</label>
                    <select id="prodotto_id" name="prodotto_id" required>
                        <option value="">Seleziona prodotto</option>
                        {% for p in prodotti %}
                        <option value="{{ p['id'] }}">{{ p['nome'] }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="tipo">Tipo*</label>
                    <select id="tipo" name="tipo" required>
                        <option value="entrata">Entrata</option>
                        <option value="uscita">Uscita</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="quantita">Quantità*</label>
                    <input type="number" step="0.01" min="0.01" id="quantita" name="quantita" required>
                </div>
                <div class="form-group">
                    <label for="data">Data</label>
                    <input type="date" id="data" name="data" value="{{ datetime.now().strftime('%Y-%m-%d') }}">
                </div>
                <div class="form-group">
                    <label for="motivo">Motivo</label>
                    <input type="text" id="motivo" name="motivo" placeholder="Opzionale">
                </div>
                <button type="submit" class="btn btn-primary">Registra Movimento</button>
                <a href="{{ url_for('lista_movimenti') }}" class="btn btn-secondary">Annulla</a>
            </form>
        </div>
        {% endblock %}
    ''', prodotti=prodotti, datetime=datetime)

@app.route('/movimenti/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_movimento(id):
    conn = get_db()
    movimento = conn.execute('''
        SELECT m.*, p.nome as prodotto_nome 
        FROM movimenti m
        JOIN prodotti p ON m.prodotto_id = p.id
        WHERE m.id = ?
    ''', (id,)).fetchone()
    
    if request.method == 'POST':
        prodotto_id = request.form['prodotto_id']
        tipo = request.form['tipo']
        quantita = float(request.form['quantita'])
        motivo = request.form.get('motivo', '')
        data = request.form.get('data', movimento['data'])
        
      
        if movimento['tipo'] == 'entrata':
            conn.execute('UPDATE prodotti SET quantita = quantita - ? WHERE id = ?', 
                         (movimento['quantita'], movimento['prodotto_id']))
        else:
            conn.execute('UPDATE prodotti SET quantita = quantita + ? WHERE id = ?', 
                         (movimento['quantita'], movimento['prodotto_id']))
        
    
        if tipo == 'entrata':
            conn.execute('UPDATE prodotti SET quantita = quantita + ? WHERE id = ?', (quantita, prodotto_id))
        else:
            conn.execute('UPDATE prodotti SET quantita = quantita - ? WHERE id = ?', (quantita, prodotto_id))
        
      
        conn.execute('''
            UPDATE movimenti 
            SET prodotto_id = ?, tipo = ?, quantita = ?, data = ?, motivo = ?
            WHERE id = ?
        ''', (prodotto_id, tipo, quantita, data, motivo, id))
        
        conn.commit()
        conn.close()
        
        flash('Movimento modificato con successo!', 'success')
        return redirect(url_for('lista_movimenti'))
    
    prodotti = conn.execute('SELECT id, nome FROM prodotti ORDER BY nome').fetchall()
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="form-container">
            <h2>Modifica Movimento</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="prodotto_id">Prodotto*</label>
                    <select id="prodotto_id" name="prodotto_id" required>
                        {% for p in prodotti %}
                        <option value="{{ p['id'] }}" {% if p['id'] == movimento['prodotto_id'] %}selected{% endif %}>{{ p['nome'] }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="tipo">Tipo*</label>
                    <select id="tipo" name="tipo" required>
                        <option value="entrata" {% if movimento['tipo'] == 'entrata' %}selected{% endif %}>Entrata</option>
                        <option value="uscita" {% if movimento['tipo'] == 'uscita' %}selected{% endif %}>Uscita</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="quantita">Quantità*</label>
                    <input type="number" step="0.01" min="0.01" id="quantita" name="quantita" value="{{ movimento['quantita'] }}" required>
                </div>
                <div class="form-group">
                    <label for="data">Data</label>
                    <input type="date" id="data" name="data" value="{{ movimento['data'] }}">
                </div>
                <div class="form-group">
                    <label for="motivo">Motivo</label>
                    <input type="text" id="motivo" name="motivo" value="{{ movimento['motivo'] or '' }}">
                </div>
                <button type="submit" class="btn btn-primary">Salva Modifiche</button>
                <a href="{{ url_for('lista_movimenti') }}" class="btn btn-secondary">Annulla</a>
            </form>
        </div>
        {% endblock %}
    ''', movimento=movimento, prodotti=prodotti)

@app.route('/movimenti/elimina/<int:id>')
@login_required
@admin_required
def elimina_movimento(id):
    conn = get_db()
    

    movimento = conn.execute('SELECT * FROM movimenti WHERE id = ?', (id,)).fetchone()
    

    if movimento['tipo'] == 'entrata':
        conn.execute('UPDATE prodotti SET quantita = quantita - ? WHERE id = ?', 
                     (movimento['quantita'], movimento['prodotto_id']))
    else:
        conn.execute('UPDATE prodotti SET quantita = quantita + ? WHERE id = ?', 
                     (movimento['quantita'], movimento['prodotto_id']))
    

    conn.execute('DELETE FROM movimenti WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    flash('Movimento eliminato con successo!', 'success')
    return redirect(url_for('lista_movimenti'))

@app.route('/movimenti/export')
@login_required
def export_movimenti():

    tipo = request.args.get('tipo', '')
    prodotto_id = request.args.get('prodotto_id', '')
    data_inizio = request.args.get('data_inizio', '')
    data_fine = request.args.get('data_fine', '')
    
    conn = get_db()
    
    query = '''
        SELECT m.data, p.nome as prodotto, m.tipo, m.quantita, p.um, m.motivo
        FROM movimenti m
        JOIN prodotti p ON m.prodotto_id = p.id
    '''
    params = []
    conditions = []
    
    if tipo:
        conditions.append('m.tipo = ?')
        params.append(tipo)
    
    if prodotto_id:
        conditions.append('m.prodotto_id = ?')
        params.append(prodotto_id)
    
    if data_inizio:
        conditions.append('m.data >= ?')
        params.append(data_inizio)
    
    if data_fine:
        conditions.append('m.data <= ?')
        params.append(data_fine)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY m.data DESC, m.id DESC'
    movimenti = conn.execute(query, params).fetchall()
    
    conn.close()
    

    output = StringIO()
    writer = csv.writer(output)
    

    writer.writerow(['Data', 'Prodotto', 'Tipo', 'Quantità', 'UM', 'Motivo'])
    

    for m in movimenti:
        writer.writerow([
            datetime.strptime(m['data'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            m['prodotto'],
            'Entrata' if m['tipo'] == 'entrata' else 'Uscita',
            m['quantita'],
            m['um'],
            m['motivo'] or ''
        ])
    

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=movimenti_magazzino.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response


@app.route('/utenti')
@login_required
@admin_required
def lista_utenti():
    conn = get_db()
    utenti = conn.execute('SELECT * FROM utenti ORDER BY username').fetchall()
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="utenti-container">
            <h2>Gestione Utenti</h2>
            
            <div class="toolbar">
                <a href="{{ url_for('aggiungi_utente') }}" class="btn btn-primary">Aggiungi Utente</a>
            </div>
            
            {% if utenti %}
                <table class="table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Ruolo</th>
                            <th>Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for u in utenti %}
                        <tr>
                            <td>{{ u['username'] }}</td>
                            <td>{{ 'Amministratore' if u['ruolo'] == 'admin' else 'Utente' }}</td>
                            <td class="actions">
                                <a href="{{ url_for('modifica_utente', id=u['id']) }}" class="btn btn-sm btn-info">Modifica</a>
                                {% if u['id'] != session['user_id'] %}
                                <a href="{{ url_for('elimina_utente', id=u['id']) }}" class="btn btn-sm btn-danger" onclick="return confirm('Sei sicuro?')">Elimina</a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>Nessun utente trovato</p>
            {% endif %}
        </div>
        {% endblock %}
    ''', utenti=utenti)

@app.route('/utenti/aggiungi', methods=['GET', 'POST'])
@login_required
@admin_required
def aggiungi_utente():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ruolo = request.form['ruolo']
        
        conn = get_db()
        
        try:
            conn.execute('INSERT INTO utenti (username, password, ruolo) VALUES (?, ?, ?)',
                        (username, password, ruolo))
            conn.commit()
            flash('Utente aggiunto con successo!', 'success')
            return redirect(url_for('lista_utenti'))
        except sqlite3.IntegrityError:
            flash('Username già esistente!', 'danger')
        finally:
            conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="form-container">
            <h2>Aggiungi Utente</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username*</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password*</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <div class="form-group">
                    <label for="ruolo">Ruolo*</label>
                    <select id="ruolo" name="ruolo" required>
                        <option value="user">Utente</option>
                        <option value="admin">Amministratore</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Salva Utente</button>
                <a href="{{ url_for('lista_utenti') }}" class="btn btn-secondary">Annulla</a>
            </form>
        </div>
        {% endblock %}
    ''')

@app.route('/utenti/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def modifica_utente(id):
    conn = get_db()
    utente = conn.execute('SELECT * FROM utenti WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ruolo = request.form['ruolo']
        
        try:
            if password:
                conn.execute('''
                    UPDATE utenti 
                    SET username = ?, password = ?, ruolo = ?
                    WHERE id = ?
                ''', (username, password, ruolo, id))
            else:
                conn.execute('''
                    UPDATE utenti 
                    SET username = ?, ruolo = ?
                    WHERE id = ?
                ''', (username, ruolo, id))
            
            conn.commit()
            flash('Utente modificato con successo!', 'success')
            return redirect(url_for('lista_utenti'))
        except sqlite3.IntegrityError:
            flash('Username già esistente!', 'danger')
        finally:
            conn.close()
    
    conn.close()
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="form-container">
            <h2>Modifica Utente</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username*</label>
                    <input type="text" id="username" name="username" value="{{ utente['username'] }}" required>
                </div>
                <div class="form-group">
                    <label for="password">Nuova Password</label>
                    <input type="password" id="password" name="password" placeholder="Lascia vuoto per non modificare">
                </div>
                <div class="form-group">
                    <label for="ruolo">Ruolo*</label>
                    <select id="ruolo" name="ruolo" required>
                        <option value="user" {% if utente['ruolo'] == 'user' %}selected{% endif %}>Utente</option>
                        <option value="admin" {% if utente['ruolo'] == 'admin' %}selected{% endif %}>Amministratore</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Salva Modifiche</button>
                <a href="{{ url_for('lista_utenti') }}" class="btn btn-secondary">Annulla</a>
            </form>
        </div>
        {% endblock %}
    ''', utente=utente)

@app.route('/utenti/elimina/<int:id>')
@login_required
@admin_required
def elimina_utente(id):
    if id == session['user_id']:
        flash('Non puoi eliminare il tuo account!', 'danger')
        return redirect(url_for('lista_utenti'))
    
    conn = get_db()
    conn.execute('DELETE FROM utenti WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Utente eliminato con successo!', 'success')
    return redirect(url_for('lista_utenti'))


@app.route('/report')
@login_required
def report():
    conn = get_db()
    
    totale_prodotti = conn.execute('SELECT COUNT(*) FROM prodotti').fetchone()[0]
    prodotti_in_esaurimento = conn.execute('SELECT COUNT(*) FROM prodotti WHERE quantita < soglia_minima AND quantita > 0').fetchone()[0]
    prodotti_terminati = conn.execute('SELECT COUNT(*) FROM prodotti WHERE quantita <= 0').fetchone()[0]
    
    data_30_giorni_fa = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    movimenti_30_giorni = conn.execute('''
        SELECT m.tipo, COUNT(*) as count, SUM(m.quantita) as quantita_totale
        FROM movimenti m
        WHERE m.data >= ?
        GROUP BY m.tipo
    ''', (data_30_giorni_fa,)).fetchall()
    
    categorie = conn.execute('''
        SELECT categoria, COUNT(*) as count 
        FROM prodotti 
        GROUP BY categoria 
        ORDER BY count DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template_string('''
        {% extends "base.html" %}
        {% block content %}
        <div class="report-container">
            <h2>Report Magazzino</h2>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h3>Prodotti Totali</h3>
                    <p>{{ totale_prodotti }}</p>
                </div>
                <div class="stat-card warning">
                    <h3>In Esaurimento</h3>
                    <p>{{ prodotti_in_esaurimento }}</p>
                </div>
                <div class="stat-card danger">
                    <h3>Terminati</h3>
                    <p>{{ prodotti_terminati }}</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col">
                    <h3>Movimenti Ultimi 30 Giorni</h3>
                    {% if movimenti_30_giorni %}
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Tipo</th>
                                    <th>Numero Movimenti</th>
                                    <th>Quantità Totale</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for m in movimenti_30_giorni %}
                                <tr>
                                    <td>{{ 'Entrate' if m['tipo'] == 'entrata' else 'Uscite' }}</td>
                                    <td>{{ m['count'] }}</td>
                                    <td>{{ m['quantita_totale'] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <p>Nessun movimento negli ultimi 30 giorni</p>
                    {% endif %}
                </div>
                
                <div class="col">
                    <h3>Categorie Prodotti</h3>
                    {% if categorie %}
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Categoria</th>
                                    <th>Numero Prodotti</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for c in categorie %}
                                <tr>
                                    <td>{{ c['categoria'] }}</td>
                                    <td>{{ c['count'] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <p>Nessuna categoria trovata</p>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endblock %}
    ''', **locals())

@app.route('/base')
def base():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Magazzino Pizzeria</title>
            <style>
                :root {
                    --primary: #007bff;
                    --secondary: #6c757d;
                    --success: #28a745;
                    --danger: #dc3545;
                    --warning: #ffc107;
                    --info: #17a2b8;
                    --light: #f8f9fa;
                    --dark: #343a40;
                }
                
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    background-color: #f5f5f5;
                    color: #333;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                header {
                    background-color: var(--dark);
                    color: white;
                    padding: 15px 0;
                    margin-bottom: 20px;
                }
                
                .header-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .logo {
                    font-size: 1.5rem;
                    font-weight: bold;
                }
                
                .nav-links {
                    display: flex;
                    gap: 20px;
                }
                
                .nav-links a {
                    color: white;
                    text-decoration: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                
                .nav-links a:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                
                .user-info {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .btn {
                    display: inline-block;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    text-decoration: none;
                    font-size: 0.9rem;
                    transition: all 0.3s ease;
                }
                
                .btn-sm {
                    padding: 5px 10px;
                    font-size: 0.8rem;
                }
                
                .btn-primary {
                    background-color: var(--primary);
                    color: white;
                }
                
                .btn-secondary {
                    background-color: var(--secondary);
                    color: white;
                }
                
                .btn-success {
                    background-color: var(--success);
                    color: white;
                }
                
                .btn-danger {
                    background-color: var(--danger);
                    color: white;
                }
                
                .btn-warning {
                    background-color: var(--warning);
                    color: black;
                }
                
                .btn-info {
                    background-color: var(--info);
                    color: white;
                }
                
                .btn-outline-secondary {
                    background-color: transparent;
                    border: 1px solid var(--secondary);
                    color: var(--secondary);
                }
                
                .btn:hover {
                    opacity: 0.9;
                    transform: translateY(-1px);
                }
                
                .table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                
                .table th, .table td {
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                
                .table th {
                    background-color: var(--dark);
                    color: white;
                }
                
                .table tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                
                .table tr:hover {
                    background-color: #e9e9e9;
                }
                
                .success {
                    color: var(--success);
                    font-weight: bold;
                }
                
                .danger {
                    color: var(--danger);
                    font-weight: bold;
                }
                
                .warning {
                    color: var(--warning);
                    font-weight: bold;
                }
                
                .info {
                    color: var(--info);
                    font-weight: bold;
                }
                
                .form-container {
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                
                .form-group {
                    margin-bottom: 20px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                
                .form-group input[type="text"],
                .form-group input[type="number"],
                .form-group input[type="date"],
                .form-group input[type="password"],
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 1rem;
                }
                
                .form-row {
                    display: flex;
                    gap: 20px;
                }
                
                .form-row .form-group {
                    flex: 1;
                }
                
                .toolbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                
                .search-form {
                    display: flex;
                    gap: 10px;
                }
                
                .search-form input {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                
                .actions {
                    white-space: nowrap;
                }
                
                .stats-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .stat-card {
                    flex: 1;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }
                
                .stat-card h3 {
                    color: var(--secondary);
                    margin-bottom: 10px;
                }
                
                .stat-card p {
                    font-size: 2rem;
                    font-weight: bold;
                    color: var(--dark);
                }
                
                .stat-card.warning {
                    border-top: 4px solid var(--warning);
                }
                
                .stat-card.danger {
                    border-top: 4px solid var(--danger);
                }
                
                .login-container {
                    max-width: 400px;
                    margin: 50px auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                
                .login-container h2 {
                    text-align: center;
                    margin-bottom: 20px;
                }
                
                .alert {
                    padding: 10px 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }
                
                .alert-success {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                
                .alert-danger {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                
                .alert-info {
                    background-color: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
                
                .row {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .col {
                    flex: 1;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                
                @media (max-width: 768px) {
                    .form-row, .stats-container, .row {
                        flex-direction: column;
                    }
                    
                    .header-container {
                        flex-direction: column;
                        gap: 15px;
                    }
                    
                    .nav-links {
                        flex-direction: column;
                        gap: 10px;
                    }
                }
            </style>
        </head>
        <body>
            <header>
                <div class="container header-container">
                    <div class="logo">Magazzino Pizzeria</div>
                    <nav class="nav-links">
                        <a href="{{ url_for('dashboard') }}">Dashboard</a>
                        <a href="{{ url_for('lista_prodotti') }}">Prodotti</a>
                        <a href="{{ url_for('lista_movimenti') }}">Movimenti</a>
                        <a href="{{ url_for('report') }}">Report</a>
                        {% if session.get('ruolo') == 'admin' %}
                        <a href="{{ url_for('lista_utenti') }}">Utenti</a>
                        {% endif %}
                    </nav>
                    <div class="user-info">
                        <span>Ciao, {{ session.get('username', 'Ospite') }}</span>
                        <a href="{{ url_for('logout') }}" class="btn btn-sm btn-danger">Logout</a>
                    </div>
                </div>
            </header>
            
            <main class="container">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </main>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
