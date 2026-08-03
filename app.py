from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Banco de dados temporário em memória para contar advertências por aluno
HISTORICO_ADVERTENCIAS = []

# 1. ROTA RAIZ
@app.route('/')
def index():
    return redirect(url_for('login'))

# 2. ROTA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro_usuario = None
    erro_senha = None

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()

        if usuario == "professor" and senha == "1234":
            session['usuario'] = usuario
            return redirect(url_for('professor'))
        elif usuario in ["secretaria", "admin"] and senha == "1234":
            session['usuario'] = usuario
            return redirect(url_for('secretaria'))
        else:
            erro_usuario = "Usuário ou senha incorretos"
            erro_senha = "Verifique suas credenciais"

    return render_template('login.html', erro_usuario=erro_usuario, erro_senha=erro_senha)

# 3. ROTA DE LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 4. ROTA DO PROFESSOR
@app.route('/professor')
def professor():
    return render_template('professor.html')

# 5. ROTA DA SECRETARIA
@app.route('/secretaria')
def secretaria():
    total_ocorrencias = len(HISTORICO_ADVERTENCIAS)
    total_graves = sum(1 for item in HISTORICO_ADVERTENCIAS if item.get('gravidade') == 'Grave')
    busca = request.args.get('busca', '').strip().lower()

    if busca:
        advertencias_filtradas = [
            item for item in HISTORICO_ADVERTENCIAS 
            if busca in item['estudante'].lower() or busca in item['turma'].lower()
        ]
    else:
        advertencias_filtradas = HISTORICO_ADVERTENCIAS

    return render_template(
        'secretaria.html', 
        advertencias=advertencias_filtradas, 
        total_ocorrencias=total_ocorrencias, 
        total_graves=total_graves,
        busca=busca
    )

# 6. PROCESSAR E GERAR ADVERTÊNCIA (Com alerta de 3ª Advertência e sem botão de imprimir)
@app.route('/gerar_advertencia', methods=['POST'])
def gerar_advertencia():
    try:
        estudante = request.form.get('estudante', '').strip()
        turma = request.form.get('turma', '').strip()
        disciplina = request.form.get('disciplina', '').strip()
        data_ocorrencia = request.form.get('data_ocorrencia', '').strip()
        
        motivos_selecionados = request.form.getlist('motivo')
        motivo_outro = request.form.get('motivo_outro', '').strip()

        if "Outros:" in motivos_selecionados and motivo_outro:
            motivos_selecionados.remove("Outros:")
            motivos_selecionados.append(f"Outros: {motivo_outro}")

        # Contagem de advertências prévias para o mesmo estudante
        nome_normalizado = estudante.lower()
        contagem_aluno = sum(1 for item in HISTORICO_ADVERTENCIAS if item['estudante'].lower() == nome_normalizado) + 1

        # Salva no histórico
        nova_adv = {
            'id': len(HISTORICO_ADVERTENCIAS) + 1,
            'estudante': estudante,
            'turma': turma,
            'disciplina': disciplina,
            'data': data_ocorrencia,
            'motivos': motivos_selecionados,
            'gravidade': 'Grave' if len(motivos_selecionados) > 2 else 'Média'
        }
        HISTORICO_ADVERTENCIAS.append(nova_adv)

        # Formatação visual dos motivos
        if motivos_selecionados:
            motivos_formatados = "".join([f"<li class='list-group-item bg-transparent border-0 ps-0 text-start'>• {m}</li>" for m in motivos_selecionados])
        else:
            motivos_formatados = "<li class='list-group-item bg-transparent border-0 ps-0 text-muted'>Nenhum motivo selecionado</li>"

        # Bloco de alerta para pais se atingir 3 advertências ou mais
        alerta_pais_html = ""
        if contagem_aluno >= 3:
            alerta_pais_html = f'''
            <div class="alert alert-danger border-0 rounded-4 shadow-sm mb-4 text-start p-3">
                <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-exclamation-octagon-fill fs-3 me-2 text-danger"></i>
                    <h5 class="fw-bold mb-0 text-danger">ATENÇÃO: NOTIFICAÇÃO AOS PAIS NECESSÁRIA!</h5>
                </div>
                <p class="mb-0 small text-dark">
                    O(a) estudante <strong>{estudante}</strong> atingiu a marca de <strong>{contagem_aluno} advertências</strong> registradas no sistema. 
                    É obrigatório comunicar a família/responsáveis para o acompanhamento pedagógico e disciplinar.
                </p>
            </div>
            '''

        return f'''
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Advertência Registrada</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body class="bg-light d-flex align-items-center justify-content-center min-vh-100 p-3">
            <div class="card border-0 shadow-lg rounded-5 p-4 text-center" style="max-width: 540px; width: 100%;">
                
                <div class="mb-3 text-success">
                    <i class="bi bi-check-circle-fill display-3"></i>
                </div>
                
                <h3 class="fw-bold mb-1">Advertência Registrada!</h3>
                <p class="text-secondary small mb-3">E. E. Mestra Hercília — Registro Digital</p>

                {alerta_pais_html}

                <div class="card bg-white border border-light-subtle rounded-4 text-start p-3 mb-4 shadow-sm">
                    <p class="mb-1"><strong>Estudante:</strong> {estudante}</p>
                    <p class="mb-1"><strong>Turma:</strong> {turma}</p>
                    <p class="mb-1"><strong>Componente Curricular:</strong> {disciplina}</p>
                    <p class="mb-3"><strong>Data da Ocorrência:</strong> {data_ocorrencia}</p>
                    
                    <h6 class="fw-bold text-secondary small mb-2 text-uppercase">Falta(s) Registrada(s):</h6>
                    <ul class="list-group list-group-flush small">
                        {motivos_formatados}
                    </ul>
                </div>

                <div class="d-grid">
                    <a href="/professor" class="btn btn-primary rounded-4 fw-bold py-2 shadow-sm">
                        <i class="bi bi-plus-circle me-2"></i>Registrar Nova Advertência
                    </a>
                </div>

            </div>
        </body>
        </html>
        '''
    except Exception as erro:
        return f"""
        <div style="font-family: sans-serif; padding: 20px; text-align: center;">
            <h2>Ops! Algo deu errado ao processar a advertência.</h2>
            <p style="color: red;"><strong>Erro:</strong> {str(erro)}</p>
            <a href="/professor">Voltar para a página anterior</a>
        </div>
        """, 500

if __name__ == '__main__':
    app.run(debug=True)
