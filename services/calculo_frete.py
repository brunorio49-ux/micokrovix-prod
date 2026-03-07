# Motor de cálculo de frete do Micokrovix

def calcular_frete(km):

    preco_diesel = 6.0
    consumo_km_l = 3.0
    pedagio_por_km = 0.25
    lucro_por_km = 4.2

    custo_diesel = (km / consumo_km_l) * preco_diesel
    pedagio = km * pedagio_por_km
    lucro = km * lucro_por_km

    lucro_final = lucro - custo_diesel - pedagio

    return {
        "km": km,
        "diesel": round(custo_diesel,2),
        "pedagio": round(pedagio,2),
        "lucro_estimado": round(lucro_final,2)
    }


if __name__ == "__main__":

    km = int(input("Digite a distância da rota em km: "))

    resultado = calcular_frete(km)

    print("Distância:", resultado["km"])
    print("Custo diesel:", resultado["diesel"])
    print("Pedágio:", resultado["pedagio"])
    print("Lucro estimado:", resultado["lucro_estimado"])
