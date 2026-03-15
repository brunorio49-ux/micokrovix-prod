from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# =========================
# BANCO DE DADOS
# =========================
def criar_banco():
    conn = sqlite3.connect("/tmp/fretes.db")

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

# =========================
# CÁLCULO DO FRETE
# =========================
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

# =========================
# ROTA DASHBOARD (CORRIGIDA)
# =========================
@app.route("/")
def inicio():
    return render_template(
        "dashboard.html",
        total_fretes=0,
        diesel_total=0,
        pedagio_total=0,
        lucro_medio=0,
        labels=[],
        valores=[]
    )

# =========================
# CALCULADORA (CORRIGIDA)
# =========================
@app.route("/calculadora", methods=["GET", "POST"])
def calculadora():

    if request.method == "POST":

        km = float(request
