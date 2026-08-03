from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para gerenciar sessões/mensagens

# 1. ROTA RAIZ (Redireciona direto para o login)
@app.route('/')
def index():
    return redirect(url_for('login'))

# 2. ROTA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro_usuario = None
    erro_senha = None

    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # Exemplo simples de validação (substitua pelas suas credenciais reais se necessário)
        if usuario == "admin" and senha == "1234":
            return redirect(url_for('professor'))
        else:
            if usuario != "admin":
                erro_usuario = "Usuário incorreto"
            if senha != "1234":
                erro_senha = "Senha incorreta"

    return render_template('login.html', erro_usuario=erro_usuario, erro_senha=erro_senha)

# 3. ROTA DO FORMULÁRIO DOS PROFESSORES
@app.route('/professor')
def professor():
    return render_template('professor.html')

# 4. ROTA QUE PROCESSA A ADVERTÊNCIA (Evita Not Found e Internal Server Error)
@app.route('/gerar_advertencia', methods=['POST'])
def gerar_advertencia():
    try:
        # Pega os dados dos campos de texto
        estudante = request.form.get('estudante', '').strip()
        turma = request.form.get('turma', '').strip()
        disciplina = request.form.get('disciplina', '').strip()
        data_ocorrencia = request.form.get('data_ocorrencia', '').strip()
        
        # Pega a lista com todos os checkboxes marcados
        motivos_selecionados = request.form.getlist('motivo')
        motivo_outro = request.form.get('motivo_outro', '').strip()

        # Se a opção 'Outros:' foi marcada e o professor escreveu o complemento
        if "Outros:" in motivos_selecionados and motivo_outro:
            motivos_selecionados.remove("Outros:")
            motivos_selecionados.append(f"Outros: {motivo_outro}")

        # Formata os motivos em tópicos para exibição
        if motivos_selecionados:
            motivos_formatados = "".join([f"<li class='list-group-item bg-transparent'>• {m}</li>" for m in motivos_selecionados])
        else:
            motivos_formatados = "<li class='list-group-item bg-transparent text-muted'>Nenhum motivo selecionado</li>"

        # Retorna a confirmação formatada em HTML direto
        return f'''
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Advertência Gerada</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body class="bg-light d-flex align-items-center justify-content-center min-vh-100 p-3">
            <div class="card border-0 shadow-lg rounded-5 p-4 text-center" style="max-width: 520px; width: 100%;">
                
                <div class="mb-3 text-success">
                    <i class="bi bi-check-circle-fill display-2"></i>
                </div>
                
                <h3 class="fw-bold mb-1">Advertência Registrada!</h3>
                <p class="text-secondary small mb-4">E. E. Mestra Hercília — Registro Digital</p>

                <div class="card bg-body-tertiary border-0 rounded-4 text-start p-3 mb-4">
                    <p class="mb-1"><strong>Estudante:</strong> {estudante}</p>
                    <p class="mb-1"><strong>Turma:</strong> {turma}</p>
                    <p class="mb-1"><strong>Disciplina:</strong> {disciplina}</p>
                    <p class="mb-3"><strong>Data da Ocorrência:</strong> {data_ocorrencia}</p>
                    
                    <h6 class="fw-bold text-secondary small mb-2">FALTA(S) REGISTRADA(S):</h6>
                    <ul class="list-group list-group-flush small rounded-3 overflow-hidden">
                        {motivos_formatados}
                    </ul>
                </div>

                <div class="d-grid gap-2">
                    <button onclick="window.print()" class="btn btn-outline-secondary rounded-4 fw-bold">
                        <i class="bi bi-printer me-2"></i>Imprimir / Salvar PDF
                    </button>
                    <a href="/professor" class="btn btn-primary rounded-4 fw-bold py-2">
                        <i class="bi bi-arrow-left me-2"></i>Nova Advertência
                    </a>
                </div>

            </div>
        </body>
        </html>
        '''
    except Exception as erro:
        # Se ocorrer qualquer falha interna, mostra a mensagem legível em vez da tela preta/branca do Erro 500
        return f"""
        <div style="font-family: sans-serif; padding: 20px; text-align: center;">
            <h2>Ops! Algo deu errado ao processar a advertência.</h2>
            <p style="color: red;"><strong>Erro:</strong> {str(erro)}</p>
            <a href="/professor">Voltar para a página anterior</a>
        </div>
        """, 500

if __name__ == '__main__':
    app.run(debug=True)
