from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import sqlite3, bcrypt, os, secrets
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_urlsafe(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("ENV") == "production"

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def criar_banco():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY, email TEXT UNIQUE, senha_hash TEXT, 
            nome TEXT, is_pro INTEGER DEFAULT 0)''')
        db.execute('''CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY, usuario_id INTEGER, titulo TEXT, 
            status TEXT DEFAULT 'To Do')''')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with get_db() as db:
            user = db.execute('SELECT * FROM usuarios WHERE email=?', 
                            (form.email.data,)).fetchone()
            if user and bcrypt.checkpw(form.senha.data.encode(), user['senha_hash']):
                session['user_id'] = user['id']
                return redirect('/dashboard')
        flash('Erro no login')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        senha_hash = bcrypt.hashpw(form.senha.data.encode(), bcrypt.gensalt())
        try:
            with get_db() as db:
                db.execute('INSERT INTO usuarios (email, senha_hash, nome) VALUES (?, ?, ?)',
                          (form.email.data, senha_hash, 'User'))
                db.commit()
            return redirect('/')
        except:
            flash('Email existe')
    return render_template('register.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/')
    with get_db() as db:
        tasks = db.execute('SELECT * FROM tarefas WHERE usuario_id=?', 
                          (session['user_id'],)).fetchall()
    return f"Dashboard - {len(tasks)} tasks (templates depois)"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    criar_banco()
    app.run(host='0.0.0.0', port=5000, debug=False)
