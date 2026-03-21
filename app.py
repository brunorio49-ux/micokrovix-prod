from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Banco no Render usa /tmp (espaço temporário)
DB_PATH = '/tmp/micokrovix.db'

# =========================
# BASE DE PEDÁGIOS
# =========================
def calcular_pedagio_auto(origem, destino, distancia):
    origem_lower = origem.lower()
    destino_lower = destino.lower()
    
    # SP ↔ RJ (Dutra)
    if ('rio' in destino_lower and ('sao paulo' in origem_lower or 'sp' in origem_lower)) or \
       ('rio' in origem_lower and ('sao paulo' in destino_lower or 'sp' in destino_lower)):
        return 74.00, 'Dutra (BR-116): 4 pedágios'
    
    # SP ↔ BH (Fernão Dias)
    if ('belo horizonte' in destino_lower or 'bh' in destino_lower) and ('sao paulo' in origem_lower or 'sp' in origem_lower):
        return 82.50, 'Fernão Dias (BR-381): 5 pedágios'
    
    # RJ ↔ BH (BR-040)
    if ('belo horizonte' in destino_lower or 'bh' in destino_lower) and 'rio' in origem_lower:
        return 88.00, 'BR-040: 4 pedágios'
    
    # SP ↔ Campinas (Bandeirantes)
    if 'campinas' in destino_lower and ('sao paulo' in origem_lower or 'sp' in origem_lower):
        return 67.50, 'Bandeirantes (SP-348): 3 pedágios'
    
    # SP ↔ Curitiba (Régis)
    if 'curitiba' in destino_lower and ('sao paulo' in origem_lower or 'sp' in origem_lower):
        return 58.50, 'Régis Bittencourt (BR-116): 3 pedágios'
    
    # Estimativa padrão
    return round(distancia * 0.40, 2), f'Estimado: R$ 0,40/km'

# =========================
# BANCO DE DADOS
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem TEXT, destino TEXT, distancia REAL,
            valor_frete REAL, combustivel REAL, pedagio REAL,
            manutencao REAL, custo_total REAL, lucro REAL,
            margem REAL, status TEXT, rodovia TEXT, data TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# FUNÇÃO DE VALIDAÇÃO
# =========================
def validar_entrada(origem, destino, valor_frete, consumo, preco_diesel):
    erros = []
    if not origem or len(origem.strip()) < 3:
        erros.append("📍 Origem precisa ter pelo menos 3 caracteres.")
    if not destino or len(destino.strip()) < 3:
        erros.append("🎯 Destino precisa ter pelo menos 3 caracteres.")
    if not valor_frete or valor_frete <= 0:
        erros.append("💰 Valor do frete deve ser maior que zero.")
    if consumo <= 0 or consumo > 20:
        erros.append("📊 Consumo deve estar entre 1 e 20 km/L.")
    if preco_diesel <= 0 or preco_diesel > 10:
        erros.append("⛽ Preço do diesel deve estar entre R$1 e R$10.")
    return erros

# =========================
# FUNÇÕES AUXILIARES
# =========================
def parse_br(valor_str):
    if isinstance(valor_str, (int, float)):
        return float(valor_str)
    if not valor_str:
        return 0.0
    valor_str = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(valor_str)
    except:
        return 0.0

def format_br(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# =========================
# CÁLCULO PRINCIPAL
# =========================
def calculate_trip(origem, destino, distancia, valor_frete, consumo, preco_diesel, pedagio, rodovia):
    litros = distancia / consumo if consumo > 0 else 1
    custo_combustivel = litros * preco_diesel
    custo_manutencao = distancia * 0.35
    custo_total = custo_combustivel + pedagio + custo_manutencao
    lucro = valor_frete - custo_total
    margem = (lucro / valor_frete * 100) if valor_frete > 0 else 0
    
    if margem >= 30:
        status = '🟢 VALE MUITO A PENA!'
    elif margem >= 15:
        status = '🟡 ACEITÁVEL - NEGOCIA MAIS'
    else:
        status = '🔴 NÃO COMPENSA, IRMÃO!'
    
    return {
        'distancia': round(distancia, 1),
        'custo_combustivel': round(custo_combustivel, 2),
        'custo_manutencao': round(custo_manutencao, 2),
        'pedagio': pedagio,
        'custo_total': round(custo_total, 2),
        'lucro': round(lucro, 2),
        'margem': round(margem, 1),
        'status': status,
        'rodovia': rodovia
    }

# =========================
# ROTAS
# =========================
@app.route('/')
def index():
    return render_template('calculadora.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    
    origem = data.get('origem', '').strip()
    destino = data.get('destino', '').strip()
    valor_frete = parse_br(data.get('receita', 0))
    consumo = parse_br(data.get('consumo', 3.0))
    preco_diesel = parse_br(data.get('preco_combustivel', 6.09))
    pedagio_manual = parse_br(data.get('pedagio', 0))
    
    erros = validar_entrada(origem, destino, valor_frete, consumo, preco_diesel)
    if erros:
        return jsonify({'erros': erros}), 400
    
    distancia = max(50, (len(origem) + len(destino)) * 12)
    
    if pedagio_manual == 0:
        pedagio, rodovia = calcular_pedagio_auto(origem, destino, distancia)
    else:
        pedagio = pedagio_manual
        rodovia = 'Informado manualmente'
    
    resultado = calculate_trip(origem, destino, distancia, valor_frete, 
                               consumo, preco_diesel, pedagio, rodovia)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO trips VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (None, origem, destino, resultado['distancia'], valor_frete,
                   resultado['custo_combustivel'], pedagio, resultado['custo_manutencao'],
                   resultado['custo_total'], resultado['lucro'], resultado['margem'],
                   resultado['status'], rodovia, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    
    return jsonify(resultado)

@app.route('/historico')
def historico():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT origem, destino, distancia, lucro, margem, status, rodovia, data FROM trips ORDER BY data DESC LIMIT 20')
    trips = c.fetchall()
    conn.close()
    return jsonify([{
        'origem': t[0], 'destino': t[1], 'distancia': t[2],
        'lucro': t[3], 'margem': t[4], 'status': t[5],
        'rodovia': t[6], 'data': t[7]
    } for t in trips])

@app.route('/api/fair_price', methods=['POST'])
def fair_price():
    data = request.json
    origem = data.get('origem', '').strip()
    destino = data.get('destino', '').strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT AVG(valor_frete), AVG(lucro), AVG(margem) FROM trips WHERE origem LIKE ? AND destino LIKE ? LIMIT 10', 
              (f'%{origem[:3]}%', f'%{destino[:3]}%'))
    avg = c.fetchone()
    conn.close()
    if avg and avg[0]:
        return jsonify({
            'avg_price': round(avg[0], 2),
            'avg_profit': round(avg[1], 2),
            'avg_margin': round(avg[2], 1),
            'message': f'Média: {format_br(avg[0])}'
        })
    return jsonify({
        'avg_price': None,
        'message': 'Ainda sem dados suficientes nessa rota, irmão!'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
