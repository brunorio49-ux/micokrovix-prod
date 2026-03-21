from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Caminho do banco dentro da pasta do projeto
DB_PATH = '/data/data/com.termux/files/home/micokrovix/temp/micokrovix.db'

# =========================
# BASE DE PEDÁGIOS
# =========================
PEDAGIOS = {
    # Dutra (SP - RJ)
    'dutra': [
        {'km': 150, 'nome': 'São José dos Campos', 'valor': 18.50},
        {'km': 210, 'nome': 'Guararema', 'valor': 18.50},
        {'km': 320, 'nome': 'Itatiaia', 'valor': 18.50},
        {'km': 380, 'nome': 'Resende', 'valor': 18.50},
    ],
    # Fernão Dias (SP - BH)
    'fernao_dias': [
        {'km': 50, 'nome': 'Atibaia', 'valor': 16.50},
        {'km': 120, 'nome': 'Bragança', 'valor': 16.50},
        {'km': 200, 'nome': 'Extrema', 'valor': 16.50},
        {'km': 280, 'nome': 'Vargem', 'valor': 16.50},
        {'km': 360, 'nome': 'Pouso Alegre', 'valor': 16.50},
    ],
    # Anhanguera (SP - Interior)
    'anhanguera': [
        {'km': 50, 'nome': 'Jundiaí', 'valor': 15.20},
        {'km': 110, 'nome': 'Campinas', 'valor': 15.20},
        {'km': 180, 'nome': 'Limeira', 'valor': 15.20},
        {'km': 240, 'nome': 'Ribeirão Preto', 'valor': 15.20},
    ],
    # Bandeirantes (SP - Interior)
    'bandeirantes': [
        {'km': 60, 'nome': 'Jundiaí', 'valor': 22.50},
        {'km': 130, 'nome': 'Campinas', 'valor': 22.50},
        {'km': 200, 'nome': 'Americana', 'valor': 22.50},
    ],
    # BR-040 (RJ - BH)
    'br040': [
        {'km': 80, 'nome': 'Petrópolis', 'valor': 22.00},
        {'km': 180, 'nome': 'Juiz de Fora', 'valor': 22.00},
        {'km': 280, 'nome': 'Barbacena', 'valor': 22.00},
        {'km': 380, 'nome': 'Congonhas', 'valor': 22.00},
    ],
    # Castelo Branco (SP - Interior)
    'castelo': [
        {'km': 70, 'nome': 'Barueri', 'valor': 18.90},
        {'km': 140, 'nome': 'Sorocaba', 'valor': 18.90},
        {'km': 220, 'nome': 'Itapetininga', 'valor': 18.90},
    ],
    # Régis Bittencourt (SP - PR)
    'regis': [
        {'km': 100, 'nome': 'Miracatu', 'valor': 19.50},
        {'km': 200, 'nome': 'Registro', 'valor': 19.50},
        {'km': 300, 'nome': 'Jacupiranga', 'valor': 19.50},
    ],
    # Washington Luís (SP - MG)
    'washington': [
        {'km': 80, 'nome': 'São José do Rio Preto', 'valor': 17.80},
        {'km': 160, 'nome': 'Mirassol', 'valor': 17.80},
    ]
}

def calcular_pedagio_auto(origem, destino, distancia):
    """Calcula pedágio baseado na origem/destino"""
    texto = (origem + destino).lower()
    total_pedagio = 0
    rodovia_usada = None
    
    # Identificar rodovia baseada no texto
    if 'rio' in destino and 'sao paulo' in origem or 'sp' in origem:
        rodovia_usada = 'dutra'
        total_pedagio = 74.00  # 4 pedágios na Dutra
    elif 'belo horizonte' in destino or 'bh' in destino:
        if 'sao paulo' in origem or 'sp' in origem:
            rodovia_usada = 'fernao_dias'
            total_pedagio = 82.50  # 5 pedágios
        elif 'rio' in origem:
            rodovia_usada = 'br040'
            total_pedagio = 88.00  # 4 pedágios
    elif 'campinas' in destino or 'interior' in destino:
        if 'sao paulo' in origem:
            rodovia_usada = 'bandeirantes'
            total_pedagio = 67.50  # 3 pedágios
    elif 'curitiba' in destino:
        rodovia_usada = 'regis'
        total_pedagio = 58.50  # 3 pedágios
    else:
        # Estimativa baseada na distância
        total_pedagio = round(distancia * 0.35, 2)  # R$0,35 por km estimado
    
    return total_pedagio, rodovia_usada

# =========================
# BANCO DE DADOS
# =========================
def init_db():
    os.makedirs('/data/data/com.termux/files/home/micokrovix/temp', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem TEXT,
            destino TEXT,
            distancia REAL,
            valor_frete REAL,
            combustivel REAL,
            pedagio REAL,
            manutencao REAL,
            custo_total REAL,
            lucro REAL,
            margem REAL,
            status TEXT,
            rodovia TEXT,
            data TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# FUNÇÕES AUXILIARES
# =========================
def parse_br(valor_str):
    """Converte string BR (1.234,56) para float"""
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
    """Formata float para padrão BR (1.234,56)"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calculate_trip(origem, destino, distancia, valor_frete, consumo, preco_diesel, pedagio, rodovia):
    litros = distancia / consumo if consumo > 0 else 1
    custo_combustivel = litros * preco_diesel
    custo_manutencao = distancia * 0.35
    custo_total = custo_combustivel + pedagio + custo_manutencao
    lucro = valor_frete - custo_total
    margem = (lucro / valor_frete * 100) if valor_frete > 0 else 0
    
    if margem >= 30:
        status = '🟢 VALE MUITO A PENA!'
        status_class = 'good'
        mensagem = f'Excelente negócio, irmão! {format_br(lucro)} de lucro! Aceita sem medo!'
    elif margem >= 15:
        status = '🟡 ACEITÁVEL - NEGOCIA MAIS'
        status_class = 'medium'
        mensagem = f'Dá pra fazer, {format_br(lucro)} de lucro. Tenta negociar um pouco mais!'
    else:
        status = '🔴 NÃO COMPENSA, IRMÃO!'
        status_class = 'bad'
        mensagem = f'Melhor esperar outra oportunidade. Esse frete vai dar {format_br(abs(lucro))} de prejuízo!'
    
    return {
        'distancia': round(distancia, 1),
        'combustivel': round(custo_combustivel, 2),
        'manutencao': round(custo_manutencao, 2),
        'pedagio': pedagio,
        'custo_total': round(custo_total, 2),
        'lucro': round(lucro, 2),
        'margem': round(margem, 1),
        'status': status,
        'status_class': status_class,
        'mensagem': mensagem,
        'rodovia': rodovia
    }

@app.route('/')
def index():
    return render_template('calculadora.html')

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    data = request.json
    
    origem = data.get('origem', '')
    destino = data.get('destino', '')
    distancia = float(data.get('distancia', 0))
    valor_frete = parse_br(data.get('valor_frete', 0))
    consumo = float(data.get('consumo', 3.0))
    preco_diesel = parse_br(data.get('preco_diesel', 6.09))
    pedagio_manual = parse_br(data.get('pedagio', 0))
    
    if distancia == 0:
        distancia = max(50, (len(origem) + len(destino)) * 12)
    
    # Calcular pedágio automático se não foi informado manualmente
    if pedagio_manual == 0:
        pedagio, rodovia = calcular_pedagio_auto(origem, destino, distancia)
    else:
        pedagio = pedagio_manual
        rodovia = 'informado manualmente'
    
    resultado = calculate_trip(origem, destino, distancia, valor_frete, 
                               consumo, preco_diesel, pedagio, rodovia)
    
    # Salvar no banco
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO trips (origem, destino, distancia, valor_frete, 
                             combustivel, pedagio, manutencao, custo_total, 
                             lucro, margem, status, rodovia, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (origem, destino, resultado['distancia'], valor_frete,
              resultado['combustivel'], pedagio, resultado['manutencao'],
              resultado['custo_total'], resultado['lucro'], 
              resultado['margem'], resultado['status'], rodovia, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'Erro ao salvar: {e}')
    
    return jsonify(resultado)

@app.route('/api/history')
def api_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT origem, destino, distancia, lucro, margem, status, rodovia, data 
        FROM trips ORDER BY data DESC LIMIT 20
    ''')
    trips = c.fetchall()
    conn.close()
    
    return jsonify([{
        'origem': t[0],
        'destino': t[1],
        'distancia': t[2],
        'lucro': t[3],
        'margem': t[4],
        'status': t[5],
        'rodovia': t[6],
        'data': t[7]
    } for t in trips])

@app.route('/api/fair_price', methods=['POST'])
def fair_price():
    data = request.json
    origem = data.get('origem', '')
    destino = data.get('destino', '')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT AVG(valor_frete), AVG(lucro), AVG(margem) 
        FROM trips 
        WHERE origem LIKE ? OR destino LIKE ?
        ORDER BY data DESC LIMIT 10
    ''', (f'%{origem[:3]}%', f'%{destino[:3]}%'))
    avg = c.fetchone()
    conn.close()
    
    if avg and avg[0]:
        return jsonify({
            'avg_price': round(avg[0], 2),
            'avg_profit': round(avg[1], 2),
            'avg_margin': round(avg[2], 1),
            'message': f'Na média, essa rota paga {format_br(avg[0])}'
        })
    else:
        return jsonify({
            'avg_price': None,
            'message': 'Ainda sem dados suficientes nessa rota, irmão!'
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'🚛 Micokrovix rodando em http://localhost:{port}')
    print(f'📍 Pedágio automático ativo para SP, RJ, BH, Campinas, Curitiba')
    app.run(host='0.0.0.0', port=port, debug=False)
