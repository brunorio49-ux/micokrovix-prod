from flask import Flask, render_template, request, redirect
import sqlite3
import sys
import os

# permite acessar a pasta services
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from services.calculo_frete import calcular_frete

app = Flask(__name__)


def moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():
    with get_db() as db:

        db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            senha TEXT
        )
        """)

        db.execute("""
        CREATE TABLE IF NOT EXISTS fretes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            km INTEGER,
            diesel REAL,
            pedagio REAL,
            lucro REAL
        )
        """)


@app.route("/")
def login():
    return """
<h1>Login</h1>

<a href="/register">Registrar</a><br><br>

<a href="/calculadora">Calculadora de Frete</a>
"""


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        with get_db() as db:
            db.execute(
                "INSERT INTO usuarios (email, senha) VALUES (?,?)",
                (email, senha)
            )

        return redirect("/")

    return render_template("register.html")


@app.route("/calculadora", methods=["GET", "POST"])
def calculadora():

    if request.method == "POST":

        km = int(request.form["km"])

        resultado = calcular_frete(km)

        with get_db() as db:
            db.execute(
                "INSERT INTO fretes (km, diesel, pedagio, lucro) VALUES (?,?,?,?)",
                (
                    resultado["km"],
                    resultado["diesel"],
                    resultado["pedagio"],
                    resultado["lucro_estimado"]
                )
            )

        return f"""
<h1>Resultado do Frete</h1>

Distância: {resultado['km']} km<br>

Diesel: R$ {moeda(resultado['diesel'])}<br>

Pedágio: R$ {moeda(resultado['pedagio'])}<br>

Lucro estimado: R$ {moeda(resultado['lucro_estimado'])}<br><br>

<a href="/calculadora">Calcular novamente</a>
"""

    return render_template("calculadora.html")


if __name__ == "__main__":
    criar_banco()
    app.run(host="0.0.0.0", port=5000)

