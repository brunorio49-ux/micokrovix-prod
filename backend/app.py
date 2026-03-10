from flask import Flask, render_template, request, redirect
import sqlite3
app = Flask(__name__)
def criar_banco():

    conn = sqlite3.connect("fretes.db")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS fretes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        distancia REAL,
        valor_frete REAL,
        combustivel REAL,
        pedagio REAL,
        lucro REAL
    )
    """)

    conn.commit()
    conn.close()
def calcular_frete(distancia, valor_frete, consumo, preco_combustivel, pedagio):

    if consumo == 0:
        consumo = 1

    litros = distancia / consumo
    custo_combustivel = litros * preco_combustivel

    custos = custo_combustivel + pedagio
    lucro = valor_frete - custos

    return {
        "distancia": distancia,
        "combustivel": round(custo_combustivel, 2),
        "pedagio": pedagio,
        "lucro": round(lucro, 2)
    }


@app.route("/")
def inicio():
    return render_template("dashboard.html")


@app.route("/calculadora", methods=["GET", "POST"])
def calculadora():

    if request.method == "POST":

        km = float(request.form.get("km", 0))
        valor_frete = float(request.form.get("valor_frete", 0))
        consumo = float(request.form.get("consumo", 0))
        preco_combustivel = float(request.form.get("preco_combustivel", 0))
        pedagio = float(request.form.get("pedagio", 0))

        resultado = calcular_frete(
            km,
            valor_frete,
            consumo,
            preco_combustivel,
            pedagio
        )

        return f"""
        <h1>Resultado do Frete</h1>

        Distância: {resultado["distancia"]} km<br><br>

        Combustível: R$ {resultado["combustivel"]}<br>
        Pedágio: R$ {resultado["pedagio"]}<br><br>

        <b>Lucro estimado: R$ {resultado["lucro"]}</b>

        <br><br>
        <a href="/calculadora">Calcular novamente</a>
        """

    return render_template("calculadora.html")


if __name__ == "__main__":
    criar_banco()
    app.run(host="0.0.0.0", port=5000)
