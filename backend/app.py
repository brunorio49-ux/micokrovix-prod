from flask import Flask, render_template, request, redirect
import sqlite3
import sys
import os

# permitir acessar pasta services
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from services.calculo_frete import calcular_frete

app = Flask(__name__)


# -------------------------------
# formatação moeda brasileira
# -------------------------------

def moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# -------------------------------
# conexão banco
# -------------------------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# criar banco
# -------------------------------

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


# -------------------------------
# página inicial
# -------------------------------

@app.route("/")
def inicio():

    return redirect("/dashboard")


# -------------------------------
# registro
# -------------------------------

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


# -------------------------------
# calculadora
# -------------------------------

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

        Distância: {resultado["km"]} km<br><br>

        Diesel: R$ {moeda(resultado["diesel"])}<br>
        Pedágio: R$ {moeda(resultado["pedagio"])}<br>
        Lucro estimado: R$ {moeda(resultado["lucro_estimado"])}<br><br>

        <a href="/calculadora">Calcular novamente</a><br><br>

        <a href="/historico">Ver histórico</a><br><br>

        <a href="/dashboard">Ir para dashboard</a>

        """

    return render_template("calculadora.html")


# -------------------------------
# histórico
# -------------------------------

@app.route("/historico")
def historico():

    with get_db() as db:

        fretes = db.execute(
            "SELECT * FROM fretes ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "historico.html",
        fretes=fretes,
        moeda=moeda
    )


# -------------------------------
# dashboard
# -------------------------------

@app.route("/dashboard")
def dashboard():

    with get_db() as db:

        total = db.execute("SELECT COUNT(*) FROM fretes").fetchone()[0]

        diesel_total = db.execute(
            "SELECT SUM(diesel) FROM fretes"
        ).fetchone()[0] or 0

        pedagio_total = db.execute(
            "SELECT SUM(pedagio) FROM fretes"
        ).fetchone()[0] or 0

        lucro_medio = db.execute(
            "SELECT AVG(lucro) FROM fretes"
        ).fetchone()[0] or 0

        fretes = db.execute(
            "SELECT id, lucro FROM fretes ORDER BY id"
        ).fetchall()

    labels = [f"Frete {f['id']}" for f in fretes]
    valores = [f["lucro"] for f in fretes]

    return render_template(
        "dashboard.html",
        total_fretes=total,
        diesel_total=moeda(diesel_total),
        pedagio_total=moeda(pedagio_total),
        lucro_medio=moeda(lucro_medio),
        labels=labels,
        valores=valores
    )


# -------------------------------
# iniciar app
# -------------------------------

if __name__ == "__main__":

    criar_banco()

    app.run(host="0.0.0.0", port=5000)
