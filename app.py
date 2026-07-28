from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessoes"

# Inicialização e atualização do Banco de Dados
def init_db():
    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS advertencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno TEXT NOT NULL,
            turma TEXT NOT NULL,
            professor TEXT NOT NULL,
            motivo TEXT NOT NULL,
            gravidade TEXT DEFAULT 'Média',
            data TEXT
        )
    ''')
    
    # Garante que a coluna gravidade exista
    try:
        cursor.execute("ALTER TABLE advertencias ADD COLUMN gravidade TEXT DEFAULT 'Média'")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()

init_db()

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    erro_usuario = None
    erro_senha = None

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        
        usuarios_validos = {
            'professor': '1223',
            'secretaria': 'admin123'
        }

        if usuario not in usuarios_validos:
            erro_usuario = "Usuário incorreto ou não encontrado."
        elif usuarios_validos[usuario] != senha:
            erro_senha = "Senha incorreta."
        else:
            if usuario == 'professor':
                session['user'] = 'professor'
                return redirect(url_for('painel_professor'))
            else:
                session['user'] = 'secretaria'
                return redirect(url_for('painel_secretaria'))

    return render_template('login.html', erro_usuario=erro_usuario, erro_senha=erro_senha)

# Painel do Professor (Salva Data/Hora do Brasil)
@app.route('/professor', methods=['GET', 'POST'])
def painel_professor():
    if session.get('user') != 'professor':
        return redirect(url_for('login'))

    if request.method == 'POST':
        aluno = request.form['aluno']
        turma = request.form['turma']
        professor = request.form['professor']
        motivo = request.form['motivo']
        gravidade = request.form.get('gravidade', 'Média')

        # Pega a Data e Hora atual exata do seu computador no formato Brasileiro (DD/MM/AAAA HH:MM)
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        conn = sqlite3.connect('escola.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO advertencias (aluno, turma, professor, motivo, gravidade, data) VALUES (?, ?, ?, ?, ?, ?)',
            (aluno, turma, professor, motivo, gravidade, data_atual)
        )
        conn.commit()
        conn.close()
        
        return render_template('professor.html', sucesso=True)

    return render_template('professor.html', sucesso=False)

# Painel da Secretaria
@app.route('/secretaria')
def painel_secretaria():
    if session.get('user') != 'secretaria':
        return redirect(url_for('login'))

    termo_busca = request.args.get('busca', '').strip()

    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()

    if termo_busca:
        cursor.execute('''
            SELECT id, aluno, turma, professor, motivo, data, gravidade 
            FROM advertencias 
            WHERE aluno LIKE ? OR turma LIKE ? 
            ORDER BY id DESC
        ''', (f'%{termo_busca}%', f'%{termo_busca}%'))
    else:
        cursor.execute('SELECT id, aluno, turma, professor, motivo, data, gravidade FROM advertencias ORDER BY id DESC')
    
    registros = cursor.fetchall()

    # Estatísticas
    cursor.execute('SELECT COUNT(*), SUM(CASE WHEN gravidade="Grave" THEN 1 ELSE 0 END) FROM advertencias')
    total_stats = cursor.fetchone()
    total_ocorrencias = total_stats[0] or 0
    total_graves = total_stats[1] or 0

    conn.close()

    return render_template('secretaria.html', 
                           advertencias=registros, 
                           busca=termo_busca,
                           total_ocorrencias=total_ocorrencias,
                           total_graves=total_graves)

# Excluir Advertência
@app.route('/excluir/<int:id>')
def excluir_advertencia(id):
    if session.get('user') != 'secretaria':
        return redirect(url_for('login'))

    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM advertencias WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('painel_secretaria'))

# Imprimir Advertência
@app.route('/imprimir/<int:id>')
def imprimir_advertencia(id):
    if session.get('user') != 'secretaria':
        return redirect(url_for('login'))

    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, aluno, turma, professor, motivo, data, gravidade FROM advertencias WHERE id = ?', (id,))
    item = cursor.fetchone()
    conn.close()

    if not item:
        return "Advertência não encontrada.", 404

    return render_template('imprimir.html', item=item)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
