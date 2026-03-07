from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def calcular_frete(distancia, valor_frete):

    diesel = distancia * 2
    pedagio = distancia * 0.25

    custos = diesel + pedagio
    lucro = valor_frete - custos

    return {
        "km": distancia,
        "diesel": diesel,
        "pedagio": pedagio,
        "lucro": lucro
    }


@app.route("/")
def inicio():
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():

    with get_db() as db:
        fretes = db.execute("SELECT * FROM fretes").fetchall()

    total_fretes = len(fretes)
    diesel_total = sum(f["diesel"] for f in fretes) if fretes else 0
    pedagio_total = sum(f["pedagio"] for f in fretes) if fretes else 0
    lucro_medio = sum(f["lucro"] for f in fretes) / total_fretes if fretes else 0

    return render_template(
        "dashboard.html",
        total_fretes=total_fretes,
        diesel_total=diesel_total,
        pedagio_total=pedagio_total,
        lucro_medio=lucro_medio,
        fretes=fretes
    )


@app.route("/calculadora", methods=["GET", "POST"])
def calculadora():

    if request.method == "POST":

        km = int(request.form["km"])
        valor_frete = float(request.form["valor_frete"])

        resultado = calcular_frete(km, valor_frete)

        with get_db() as db:

            db.execute(
                "INSERT INTO fretes (km, diesel, pedagio, lucro) VALUES (?, ?, ?, ?)",
                (
                    resultado["km"],
                    resultado["diesel"],
                    resultado["pedagio"],
                    resultado["lucro"]
                )
            )

            db.commit()

        return f"""
        <h1>Resultado do Frete</h1>

        Distância: {resultado['km']} km<br><br>

        Diesel: R$ {resultado['diesel']:.2f}<br>
        Pedágio: R$ {resultado['pedagio']:.2f}<br>

        <b>Lucro estimado: R$ {resultado['lucro']:.2f}</b>

        <br><br>

        <a href="/calculadora">Calcular novamente</a><br><br>
        <a href="/historico">Ver histórico</a><br><br>
        <a href="/dashboard">Ir para dashboard</a>
        """

    return render_template("calculadora.html")


@app.route("/historico")
def historico():

    with get_db() as db:
        fretes = db.execute("SELECT * FROM fretes ORDER BY id DESC").fetchall()

    return render_template("historico.html", fretes=fretes)


if __name__ == "__main__":
    app.run(debug=True)

