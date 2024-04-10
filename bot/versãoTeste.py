from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
import hmac
import hashlib
import time
import requests

app = Flask(__name__)

# Configurações do banco de dados
conn = {
    "host": 'localhost',
    "user": 'root',
    "password": 'admin',
    "database": 'db_binance'
}

# Função para conectar ao banco de dados
def connect(conn):
    try:
        c = mysql.connector.connect(**conn)
        return c
    except Exception as e:
        print("Erro na conexão com o banco de dados" + str(e))
        return None

# Rota raiz
@app.route('/')
def index():
    return 'Olá, mundo!'

# Rota de cadastro de usuário
@app.route('/cadastro', methods=['POST'])
def Cadastro():
    dadosRegistro = request.get_json()
    
    if 'api_key' not in dadosRegistro or 'api_secret' not in dadosRegistro or 'email' not in dadosRegistro or 'password' not in dadosRegistro:
        return jsonify({'message': 'Dados incompletos'}), 400

    api_key = dadosRegistro['api_key']
    api_secret = dadosRegistro['api_secret']
    email = dadosRegistro['email']
    password = dadosRegistro['password']

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        c = connect(conn)
        if c:
            cursor = c.cursor()
            cursor.execute('INSERT INTO tbl_users (api_key, api_secret, email, pass) VALUES (%s, %s, %s, %s)', (api_key, api_secret, email, hashed_password))
            c.commit()
            novo_id = cursor.lastrowid
            c.close()
            return jsonify({'message': 'Cadastro feito com sucesso! O id do usuário é: ' + str(novo_id)}), 201
        else:
            return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    except Exception as e:
        return jsonify({'message': 'Erro de cadastro: ' + str(e)}), 500

# Rota para autenticar o usuário
@app.route('/login', methods=['POST'])
def login():
    dadosLogin = request.get_json()
    
    if 'email' not in dadosLogin or 'password' not in dadosLogin:
        return jsonify({'message': 'Dados incompletos'}), 400

    email = dadosLogin['email']
    password = dadosLogin['password']

    try:
        c = connect(conn)
        if c:
            cursor = c.cursor()
            cursor.execute('SELECT pass FROM tbl_users WHERE email = %s', (email,))
            user_data = cursor.fetchone()
            c.close()
            if user_data:
                hashed_password = user_data[0]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return jsonify({'message': 'Login realizado com sucesso'}), 200
                else:
                    return jsonify({'message': 'Login e(ou) Senha inválidos'}), 401
            else:
                return jsonify({'message': 'Usuário não encontrado'}), 404
        else:
            return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    except Exception as e:
        return jsonify({'message': 'Erro de autenticação: ' + str(e)}), 500

@app.route('/new-order-buy', methods=['POST'])
def newOrderBuy():
    dadosCompra = request.get_json()
    
    if 'par_ativos' not in dadosCompra or 'price' not in dadosCompra:
        return jsonify({'message': 'Os dados informados estão incorretos'}), 400
    
    try:
        c = connect(conn)
        if c:
            cursor = c.cursor()
            cursor.execute('SELECT API_KEY, API_SECRET FROM tbl_users')
            users = cursor.fetchall()
            
            success = False 
            dadosCompra['quantity'] = float(dadosCompra['valor_depositado'])/float(dadosCompra['price'])
            for user in users:
                API_KEY = user[0]
                API_SECRET = user[1]
                
                try:
                    value = float(dadosCompra['valor_depositado'])/float(dadosCompra['price'])
                      
                    if dadosCompra['stop_loss'] == None:
                        dadosCompra['stop_loss'] = 10
                    stopLoss = float(dadosCompra['price']) * ((100 - float(dadosCompra['stop_loss']))/100)
                    
                    params = {
                        'symbol': dadosCompra['par_ativos'],
                        'side': 'BUY',
                        'quantity': int(value),
                        'price': dadosCompra['price'],
                        'type': 'LIMIT',
                        'timeInForce': 'GTC',
                        'timestamp': int(time.time() * 1000)
                    }

                    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

                    signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

                    params['signature'] = signature

                    headers = {
                        'X-MBX-APIKEY': API_KEY
                    }

                    endpoint = 'https://testnet.binance.vision/api/v3/order/test'

                    response = requests.post(endpoint, headers=headers, data=params)
                    

                    if response.status_code == 200:
                        success = True 
                        response_json = response.json()
                        
                        if 'orderId' not in response_json:
                            response_json = "testnet"
                        try:
                            cursor.execute(f'Insert into tbl_order(api_key, ativo, tipo_de_ordem, valor_depositado, ultimo_alvo, ativa, order_id, quantidade_ativo, preco_parada, preco_entrada) values("{API_KEY}", "{dadosCompra['par_ativos']}", "BUY", {float(dadosCompra['valor_depositado'])}, {float(dadosCompra['ultimo_alvo'])}, "s", "{response_json}" , "{value}", {float(stopLoss)}, {float(dadosCompra['price'])})')
                            c.commit()
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue

            if success:
                c.close()
                return jsonify({'message': 'Requisição realizada com sucesso!'}), 200
                
            else:
                return jsonify({'message': 'Nenhuma ordem foi executada com sucesso para nenhum usuário.'}), 500

    except Exception as e:
        return jsonify({'message': 'Erro na requisição do banco de dados: ' + str(e)}), 500

# @app.route('/order-edit', methods=['PUT'])
# def orderEdit():
#     dadosEdicao = request.get_json()
    
#     if 'order_id' not in dadosEdicao or 'new_price' not in dadosEdicao or 'par_ativos' not in dadosEdicao:
#         return jsonify({'message': 'Os dados informados estão incorretos'}), 400
    
#     try:
#         c = connect(conn)
#         if c:
#             cursor = c.cursor()
#             cursor.execute(f'SELECT a.API_KEY, API_SECRET FROM tbl_users a inner join tbl_order b on a.api_key = b.api_key where ativa = "s" and ativo = {dadosEdicao['par_ativos']}')
#             users = cursor.fetchall()
#             for user in users:
            
            
#     except Exception as e:
        
            
            
@app.route('/new-order-sell', methods=['POST'])
def newOrderSell():
    dadosVenda = request.get_json()
    
    if 'par_ativos' not in dadosVenda or 'price' not in dadosVenda:
        return jsonify({'message': 'Os dados informados estão incorretos'}), 400
    
    try:
        c = connect(conn)
        if c:
            cursor = c.cursor()
            cursor.execute('SELECT API_KEY, API_SECRET FROM tbl_users')
            users = cursor.fetchall()
            
            success = False  
            for user in users:
                API_KEY = user[0]
                API_SECRET = user[1]
                
                value = float(dadosVenda['valor_depositado'])/float(dadosVenda['price'])
                if dadosVenda['stop_loss'] == None:
                    dadosVenda['stop_loss'] = 10
                stopLoss = float(dadosVenda['price']) * ((100 - float(dadosVenda['stop_loss']))/100)
                
                try:
                    params = {
                        'symbol': dadosVenda['par_ativos'],
                        'side': 'SELL',
                        'quantity': int(value),
                        'price': dadosVenda['price'],
                        'type': 'LIMIT',
                        'timeInForce': 'GTC',
                        'timestamp': int(time.time() * 1000)
                    }

                    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

                    signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

                    params['signature'] = signature

                    headers = {
                        'X-MBX-APIKEY': API_KEY
                    }

                    endpoint = 'https://testnet.binance.vision/api/v3/order/test'

                    response = requests.post(endpoint, headers=headers, data=params)

                    if response.status_code == 200:
                        success = True 
                        response_json = response.json()
                        
                        if 'orderId' not in response_json:
                            response_json = "testnet"
                            
                        try:
                            cursor.execute(f'Insert into tbl_order(api_key, ativo, tipo_de_ordem, valor_depositado, ultimo_alvo, ativa, order_id, quantidade_ativo, preco_parada, preco_entrada) values("{API_KEY}", "{dadosVenda['par_ativos']}", "SELL", {dadosVenda['valor_depositado']}, {float(dadosVenda['ultimo_alvo'])}, "s", "{response_json}" , {value}, {float(stopLoss)}, {float(dadosVenda['price'])})')
                            c.commit()
                        except Exception as e:
                            print(response.text)
                            continue
                except Exception as e:
                    jsonify({'message' : 'Requisição não realizada: ' + str(e)})
                    continue

            if success:
                return jsonify({'message': 'Requisição realizada com sucesso!'}), 200
                c.close()
            else:
                return jsonify({'message': 'Nenhuma ordem foi executada com sucesso para nenhum usuário.' + response.text}), 500

    except Exception as e:
        return jsonify({'message': 'Erro na requisição do banco de dados: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
