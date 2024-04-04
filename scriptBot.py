import requests
import hashlib
import hmac
import time
from binance.client import Client
from binance.enums import *





# moeda = 'BTCUSDT'
def continuar():
    cont = ""
    cont = input("Deseja continuar? Digite S para sim e N para não: ")
    cont = cont.lower()
    if cont == "s":
        menu()
    elif cont == "n":
        print("bye!")
    else:
        continuar()

def menu():
    acao = int(input("Digite qual será sua ação \n1 - Para consultar os preços \n2 - Para comprar ações\n3 - Para encerrar\nAção: "))
    if acao == 1:
        consultarPreco()
    elif acao == 2: 
        fazerSolicitacao()
    elif acao == 3:
        return
    else:
        menu()

def consultarPreco():
    ativos = 'BTCUSDT' 
    try:
        url = f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={ativos}"
        response = requests.get(url)
        data = response.json()
        precoVenda = float(data['askPrice'])
        print(f"O preço de venda para o par de ativos {ativos} é: {precoVenda}")  
    except Exception as e:
        print("Erro ao consultar o preço de venda:", e)
    continuar()
    

def consultaPrecoAtual(ativo):
    try:
        url = f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={ativo}"
        response = requests.get(url)
        data = response.json()
        precoVenda = float(data['askPrice']) 
        return precoVenda
    except Exception as e:
        return None

    
    
from binance.client import Client
import time

def fazerSolicitacao():
    api_key = input("Insira sua apikey: ")
    api_secret= input("insira sua apisecret: ")
    
    client = Client(api_key=api_key, api_secret=api_secret, testnet=True)
    moeda = input("Digite a moeda do seu ativo")
    moeda = moeda.upper()
    tipoDeOrdem = ""
    while tipoDeOrdem != "1" or tipoDeOrdem !="2":
        tipoDeOrdem = input("Digite 1, para compra \nou 2 para venda")
        if tipoDeOrdem == "1":
            tipoDeOrdem = SIDE_BUY
            break
        elif tipoDeOrdem == "2":
            tipoDeOrdem = SIDE_SELL
            break
        
    quantidade = float(input("digite a quantidade do ativo que você quer comprar"))
    print(f'O preço atual da moeda é: {consultaPrecoAtual(moeda)}\nE a quantidade que você quer comprar está custando: {consultaPrecoAtual(moeda)*quantidade}')
    
    order = client.create_test_order(
        symbol=moeda,
        side=tipoDeOrdem,
        type=ORDER_TYPE_MARKET,
        quantity=quantidade
        
    )

    if isinstance(order, dict) and 'code' in order:
        print("Erro na solicitação:", order['msg'])
    else:
        print("Solicitação bem-sucedida!")
        continuar()


    

menu()
    