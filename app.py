from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "micokrovix_secret"

# ------------------------
# Banco de dados
# ------------------------

def conectar():
    return sqlite3.connect("database.db")

def criar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        senha TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS fretes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        valor REAL,
        origem TEXT,
        destino TEXT,
        data TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tipo TEXT,
        valor REAL,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

# ------------------------
# Rotas
# ------------------------

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/registrar", methods=["POST"])
def registrar():
    conn = conectar()
    try:
        conn.execute(
            "INSERT INTO usuarios (username, senha) VALUES (?, ?)",
            (request.form["username"], request.form["senha"])
        )
        conn.commit()
    except:
        pass
    conn.close()
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    conn = conectar()
    user = conn.execute(
        "SELECT * FROM usuarios WHERE username=? AND senha=?",
        (request.form["username"], request.form["senha"])
    ).fetchone()
    conn.close()

    if user:
        session["user_id"] = user[0]
        return redirect("/dashboard")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html")

@app.route("/financeiro")
def financeiro():
    if "user_id" not in session:
        return redirect("/")

    conn = conectar()

    fretes = conn.execute(
        "SELECT * FROM fretes WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    despesas = conn.execute(
        "SELECT * FROM despesas WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    total_fretes = sum(f[2] for f in fretes)
    total_despesas = sum(d[2] for d in despesas)
    lucro = total_fretes - total_despesas

    conn.close()

    return render_template(
        "financeiro.html",
        fretes=fretes,
        despesas=despesas,
        total_fretes=round(total_fretes,2),
        total_despesas=round(total_despesas,2),
        lucro=round(lucro,2)
    )

@app.route("/add_frete", methods=["POST"])
def add_frete():
    valor = request.form["valor"].replace(",", ".")
    conn = conectar()
    conn.execute(
        "INSERT INTO fretes (user_id, valor, origem, destino, data) VALUES (?, ?, ?, ?, ?)",
        (
            session["user_id"],
            float(valor),
            request.form["origem"],
            request.form["destino"],
            request.form["data"]
        )
    )
    conn.commit()
    conn.close()
    return redirect("/financeiro")

@app.route("/add_despesa", methods=["POST"])
def add_despesa():
    valor = request.form["valor"].replace(",", ".")
    conn = conectar()
    conn.execute(
        "INSERT INTO despesas (user_id, tipo, valor, data) VALUES (?, ?, ?, ?)",
        (
            session["user_id"],
            request.form["tipo"],
            float(valor),
            request.form["data"]
        )
    )
    conn.commit()
    conn.close()
    return redirect("/financeiro")

@app.route("/deletar_frete/<int:id>")
def deletar_frete(id):
    conn = conectar()
    conn.execute(
        "DELETE FROM fretes WHERE id=? AND user_id=?",
        (id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect("/financeiro")

@app.route("/deletar_despesa/<int:id>")
def deletar_despesa(id):
    conn = conectar()
    conn.execute(
        "DELETE FROM despesas WHERE id=? AND user_id=?",
        (id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect("/financeiro")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    criar_banco()
    app.run(host="0.0.0.0", port=5000)
