from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def calcular_frete(distancia, valor_frete, consumo, preco_combustivel, pedagio):

    litros = distancia / consumo
    custo_combustivel = litros * preco_combustivel

    custos = custo_combustivel + pedagio
    lucro = valor_frete - custos

    return {
        "distancia": distancia,
        "combustivel": round(custo_combustivel,2),
        "pedagio": pedagio,
        "lucro": round(lucro,2)
    }


@app.route("/")
def inicio():
    return redirect("/calculadora")


@app.route("/calculadora", methods=["GET","POST"])
def calculadora():

    if request.method == "POST":

        km = float(request.form["km"])
        valor_frete = float(request.form["valor_frete"])
        consumo = float(request.form["consumo"])
        preco_combustivel = float(request.form["preco_combustivel"])
        pedagio = float(request.form["pedagio"])

        resultado = calcular_frete(
            km,
            valor_frete,
            consumo,
            preco_combustivel,
            pedagio
        )

        return f"""
        <h1>Resultado do Frete</h1>

        Distância: {resultado['distancia']} km<br><br>

        Combustível: R$ {resultado['combustivel']}<br>
        Pedágio: R$ {resultado['pedagio']}<br><br>

        <b>Lucro estimado: R$ {resultado['lucro']}</b>

        <br><br>

        <a href="/calculadora">Calcular novamente</a>
        """

    return render_template("calculadora.html")


if __name__ == "__main__":
    app.run(debug=True)
