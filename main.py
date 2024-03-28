import requests
import hashlib
import hmac
import time

moeda = 'BTCUSDT'
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

    
    
def fazerSolicitacao():
    try:
        timestamp = int(time.time() * 1000)
        timestamp_str = str(timestamp)
        api_key = "AIyD6xqJH8TM3LV2IEIJup5VxBrlnNuo9eCenvLnzmvbbp3KBx4cIYMK3kbJ83Za"
        api_secret = "OpRJ6SyS8EvstHUIXxvIlHacNbZ4Lv6gOUQJS6CFSpiA00FOjr9Pf6DHZc49RCs1"
        url = "https://testnet.binance.vision/api/v3/order/test"
        moeda = input("Digite o par de moedas para a transação (ex: BTCUSDT): ").upper()
        moeda = 'BTCUSDT'  
        precoMoeda = consultaPrecoAtual(moeda)
        quantity = float(input("Digite a quantidade do ativo que deseja comprar/vender: "))
        price = round(precoMoeda * quantity, 2)
        print(f'O preço atual da quantidade do ativo que você quer comprar é: {precoMoeda}')
        print(f'O preço total da compra para {quantity} {moeda} é: {price}')
        params = {
            'symbol': moeda,
            'side': 'BUY', 
            'type': 'LIMIT',  
            'quantity': quantity,
            'price': price,  
            'timeInForce': 'GTC', 
            'timestamp': timestamp_str,
            'recvWindow': 60000  
        }
        query_string = '&'.join([f"{key}={params[key]}" for key in params])
        signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params['signature'] = signature

        headers = {'X-MBX-APIKEY': api_key}
        response = requests.post(url, headers=headers, params=params)
        print(response.json())

    except ValueError as ve:
        print("Erro: Valor inválido inserido.", ve)
    except requests.exceptions.RequestException as re:
        print("Erro de solicitação:", re)
    except Exception as e:
        print("Erro desconhecido:", e)

    
print(consultaPrecoAtual("BTCUSDT"))
menu()
    