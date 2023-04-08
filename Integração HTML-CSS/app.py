from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'uabjpsychoatendsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:wKzs7JlkXjVYpDq496aG@containers-us-west-119.railway.app:5622/railway'

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.String(80), unique=False, nullable=False)
    hora = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user= db.relationship('User', backref='agendamentos')

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'mostrarLogin'
login_manager.login_message = 'Você precisa estar logado para acessar essa página!'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # como o user_id é apenas a chave primária da tabela de usuários, use-o na consulta para encontrar o usuário
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/agendar', methods=['POST'])
@login_required
def agendar():
    user= current_user
    data = request.form['data']
    hora = request.form['hora']

    agendamento = Agendamento(data=data, hora=hora, user=user)
    db.session.add(agendamento)
    db.session.commit()

    flash('Agendamento realizado com sucesso!', 'success')
    return render_template('sucesso.html')

@app.route ('/agendamento')
@login_required
def cadastradosucesso():
    return render_template('formulario.html')

@app.route ('/historico')
@login_required
def historico():
    return render_template('historico.html')

@app.route ('/perfil')
@login_required
def mostrarPerfil():
    logout_user()
    return render_template('perfil.html')

@app.route("/acompanhamento")
@login_required
def acompanhamento():

    # Obter todos os agendamentos do banco de dados
    agendamentos = Agendamento.query.all()

    # Obter o usuário atualmente logado
    user = current_user

    # Renderizar a página de acompanhamento, passando a lista de agendamentos e o usuário atualmente logado
    return render_template('acompanhamento.html', agendamentos=agendamentos, user=user)

@app.route ('/login')
def mostrarLogin():
    return render_template('login.html')

@app.route('/login-db', methods=['POST'])
def login_db():
    # Obter o email e senha do formulário de login
    email = request.form.get('email')
    password = request.form.get('password')

    # Procurar o usuário no banco de dados pelo email fornecido
    user = User.query.filter_by(email=email).first()

    # Verificar se o usuário existe e se a senha fornecida está correta
    if not user or not check_password_hash(user.password, password):
        # Se o usuário não existir ou a senha estiver incorreta, redirecionar para a página de login e exibir uma mensagem de erro
        flash('Por favor, verifique suas informações de login e tente novamente.')
        return redirect(url_for('mostrarLogin'))

    # Se todas as verificações passarem, o usuário tem as credenciais corretas
    login_user(user)
    return redirect(url_for('mostrarPerfil'))

@app.route ('/register')
def mostrarCadastro():
    return render_template('cadastrar.html')

@app.route('/cadastro-db', methods=['POST'])
def register_db():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # se o email já existir, não deixa registrar

    if user: # se um usuário for encontrado, queremos redirecionar de volta para a página de inscrição para que o usuário possa tentar novamente
        flash('Email já cadastrado!')
        return redirect(url_for('mostrarCadastro'))

    # crie um novo usuário com os dados do formulário. Faça o hash da senha para que a versão em texto simples não seja salva.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # Adicione o novo usuário ao banco de dados
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('mostrarLogin'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(error):
    return str(error), 500

if __name__ == '__main__':
    app.run(debug=True)
