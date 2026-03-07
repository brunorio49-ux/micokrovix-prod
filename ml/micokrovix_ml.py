import pandas as pd
from sklearn.linear_model import LinearRegression

# dados simples de exemplo
dados = {
    "rota_km": [100,200,300,400,500,600,700,800],
    "lucro": [500,900,1300,1700,2100,2600,3000,3500]
}

df = pd.DataFrame(dados)

modelo = LinearRegression()
modelo.fit(df[['rota_km']], df['lucro'])

def prever_lucro(km):
    previsao = modelo.predict([[km]])
    return round(previsao[0],2)


if __name__ == "__main__":
    km = int(input("Digite a distância da rota em km: "))
    lucro = prever_lucro(km)
    print(f"Lucro estimado: R$ {lucro}")
