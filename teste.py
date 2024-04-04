import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
from binance.client import Client
from binance.enums import *
from telegram import *
from telegram import Bot
import re
import mysql.connector


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


conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'admin',
    database = 'db_binance'
)

if conn.is_connected():
    print("Estamos conectados ao banco de dados")
    

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = 'SEU_TOKEN'

BINANCE_API_KEY = 'zy6W4shF0DK3xhtf1Y4ijbcGhqgKHdbsXRJMdWyiZ2a41SJMn5zItGBWbwq1O2TP'
BINANCE_API_SECRET = '8E1p3Cq8Q5kG8uPsbNAf0bp6NCvwSppw9Wmq9snNOxAa2L6xyXjzSj7iXAUeRkJr'
client = Client(BINANCE_API_KEY,BINANCE_API_SECRET,testnet=True)

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
    api = conn.cursor()
    if re.search(padraoEntrada, texto): 
        padrao_par = r'([A-Za-z0-9/]+)USDT\b'
        padrao_alvos = r'\d+\.\d+'
        padrao_stop = r'\d+% do Preço'
        re1 = r'\bVenda\b'
        side = ""
        if re.search(re1, texto):
            side = SIDE_SELL
        else:
            side = SIDE_BUY
        
        par_search = re.search(padrao_par, texto)
        
        print(par_search) 
        if par_search:
            par = par_search.group()
            par = par.split('/')
            print(par)
            par = ''.join(par)
            print(par)
        else:
            await bot.send_message(chat_id=update.effective_chat.id, text="Erro: Par de ativos não encontrado.")
            return
        
        alvos = re.findall(padrao_alvos, texto)

        stop = re.search(padrao_stop, texto)

        numero_alvos = len(alvos)
        entrada = ""
        print(par, alvos, side, numero_alvos, stop, entrada)
        par = par
        
        try:
            if side == 'BUY':
                order = client.create_test_order(symbol=par, side=Client.SIDE_BUY, type=Client.ORDER_TYPE_LIMIT, timeInForce=Client.TIME_IN_FORCE_GTC, quantity=10, price=float(alvos[1]))
            else:
                order = client.create_test_order(symbol=par, side=Client.SIDE_SELL, type=Client.ORDER_TYPE_LIMIT,timeInForce=Client.TIME_IN_FORCE_GTC, quantity=10, price=float(alvos[1]))
            
            await bot.send_message(chat_id=update.effective_chat.id, text=f"Ordem executada com sucesso:\n{order}")
            
            try:
                api.execute(f"Insert into tbl_order(api_key, ativo, tipo_de_ordem, valor_depositado ,ultimo_alvo, ativa) values('{BINANCE_API_KEY}','{par}', '{side.upper()}', {alvos[1]}, {alvos[len(alvos)-1]}, 's')")
                print("Insert feito")
                conn.commit()
                    
            except Exception as e:
                    print("Erro ao executar no banco de dados" + str(e))
                    
        except Exception as e:
            await bot.send_message(chat_id=update.effective_chat.id, text=f"Erro ao executar a ordem: {e}")
   
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
            api.execute(f"select ultimo_alvo from tbl_order where ativo = '{par_ativos}' and ativa = 's';")
            ultimo_alvo = api.fetchone()
            # order_id = int(api.execute(f"select id from tbl_order where ativo = '{par_ativos}' and ativa = 's'; "))
            
            print(ultimo_alvo)
            
            print("Select feito" + ultimo_alvo)
            
            
        except Exception as e:
            print("Erro ao executar no banco de dados" + str(e))
        if preco == preco:
            try:
                new_stop_loss = calc_70_porcento(float(preco))
                result = client.oco(
                    symbol=par_ativos,
                    orderId= order_id,
                    side=Client.SIDE_BUY,
                    stopPrice=new_stop_loss,
                    newOrderRespType=ORDER_RESP_TYPE_RESULT
                )
                
                print("order alterada." + result)
            except Exception as e:
                print("Erro ao alterar a order: " + str(e))
        
        
application = ApplicationBuilder().token('7167225065:AAEbguGVG10yHcSKGjgskwbrHswI-QHTDyw').build()
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
message_handler = MessageHandler(filters.ALL, message_handler)
application.add_handler(message_handler)

application.run_polling()


