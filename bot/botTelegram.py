import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
from telegram import *
from telegram import Bot
import re
import requests
import json


endpoint = "http://127.0.0.1:5000/"


def calcular_lucro_prejuizo(preco_atual, preco_inicial, valor_entrada):
    lucro_prejuizo = (preco_atual - preco_inicial) * valor_entrada
    return lucro_prejuizo

def calcular_70_porcento(preco_atual, preco_inicial, valor_entrada):
    lucro_prejuizo = calcular_lucro_prejuizo(preco_atual, preco_inicial, valor_entrada)
    setenta_porcento = 0.7 * abs(lucro_prejuizo)  
    return setenta_porcento

def calc_70_porcento(preco):
    setenta_porcento = 0.7 * abs(preco)
    return setenta_porcento





    

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = 'SEU_TOKEN'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou o seu bot de negociação. Envie uma mensagem com as informações da sua ordem.")
    

async def message_handler(update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    
    await execute_order(message_text, context.bot, update)

async def execute_order(message_text, bot, update):
    n = 0
    x = 0
    texto = message_text    
    padraoEntrada = r'\bEntrada Agendada\b'
    padraoAlvo = r'\bAlvo Atingido\b'
    par = ""
    if re.search(padraoEntrada, texto): 
        padrao_par = r'([A-Za-z0-9/]+)USDT\b'
        padrao_alvos = r'\d+\.\d+'
        padrao_stop = r'\d+% do Preço'
        re1 = r'\bVenda\b'
        re2 = r'\bCompra\b'
        side = ""
        if re.search(re1, texto):
            side = "SELL"
        elif re.search(re2, texto):
            side = "BUY"
        
        par_search = re.search(padrao_par, texto)
        
        print(par_search) 
        if par_search:
            par = par_search.group()
            par = par.split('/')
            print(par)
            par = ''.join(par)
            print(par)
        else:
            print("Erro: Par de ativos não encontrado.")
            return
        
        alvos = re.findall(padrao_alvos, texto)

        stop = re.search(padrao_stop, texto)

        numero_alvos = len(alvos)
        entrada = ""
        print(par, alvos, side, numero_alvos, stop, entrada)
        par = par
        
        try:
            if side == 'BUY':
                dadosCompra = {
                    "par_ativos" : par,
                    "valor_depositado" : str(50),
                    'price' : str(alvos[0]),
                    'ultimo_alvo' : str(alvos[numero_alvos - 1]),
                    "stop_loss" : stop
                }
                try:
                    response = requests.post((endpoint+'new-order-buy'), json=dadosCompra)
                
                
                    if response.status_code == 200:
                        print(f"Ordem executada com sucesso {response.text}")
                    else: 
                        print(f"Order não realizada, veja {response.text}")
                except Exception as e:
                    print(f"Erro na order: {e}")

            else:
                dadosCompra = {
                    "par_ativos" : par,
                    "valor_depositado" : 50,
                    'price' : alvos[0],
                    'ultimo_alvo' : alvos[numero_alvos-1],
                    "stop_loss" : stop
                }
                try:
                    response = requests.post((endpoint+'new-order-sell'), json=dadosCompra)
                
                
                    if response.status_code == 200:
                        print("Order realizada com sucesso!")
                    else: 
                        print(response.text)
                except Exception as e:
                    print(f"Erro na order: {str(e)}")

                    
        except Exception as e:
            print(f"Erro ao executar a ordem: {e}")
            
    
    elif re.search(padraoAlvo, texto):
        padrao_ativos = r'([A-Z0-9]+/[A-Z0-9]+)'
        padrao_preco = r'Preço: (\d+\.\d+)'
        padrao_stoploss = r'A Mover (?:o )?Stop para (\d+(?:\.\d+)?)%'
        par_ativos = re.search(padrao_ativos, texto).group()
        preco = re.search(padrao_preco, texto).group(1)
        stoploss = re.search(padrao_stoploss, texto).group(1)
        par_ativos = par_ativos.split('/')
        par_ativos = ''.join(par_ativos)
        print(par_ativos, preco, stoploss)
        order_id = ""
        id = 0
        ultimo_alvo = 0
        try:
            # id = api.execute(f"select id from tbl_order where ativo = '{par_ativos}' and ativa = 's'; ")
            # api.execute(f"select ultimo_alvo from tbl_order where ativo = '{par_ativos}' and ativa = 's';")
            # ultimo_alvo = api.fetchone()
            # order_id = int(api.execute(f"select id from tbl_order where ativo = '{par_ativos}' and ativa = 's'; "))
            
            print(ultimo_alvo)
            
            print("Select feito" + ultimo_alvo)
            
            
            
        except Exception as e:
            print("Erro ao executar no banco de dados" + str(e))
        # if preco == preco:
        #     # try:
        #     #     new_stop_loss = calc_70_porcento(float(preco))
        #     #     result = client.oco(
        #     #         symbol=par_ativos,
        #     #         orderId= order_id,
        #     #         side=Client.SIDE_BUY,
        #     #         stopPrice=new_stop_loss,
        #     #         newOrderRespType=ORDER_RESP_TYPE_RESULT
        #     #     )
                
        #         print("order alterada.")
        #     except Exception as e:
        #         print("Erro ao alterar a requisição: " + str(e))
        
        
application = ApplicationBuilder().token('7167225065:AAEbguGVG10yHcSKGjgskwbrHswI-QHTDyw').build()
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
message_handler = MessageHandler(filters.ALL, message_handler)
application.add_handler(message_handler)

application.run_polling()


