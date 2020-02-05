from bfxapi import Client, Order
import datetime
import time
import math
import asyncio
import os
import sys
import json
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s : %(message)s', 
                    filename='auto_lend.log')


with open('config.json' , 'r') as reader:
    config = json.loads(reader.read())

bfx = Client(config['API_KEY'], config['API_SECRET'], logLevel='DEBUG')
now = int(round(time.time() * 1000))
then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago

async def wallet_available_balance():
    try:
        balance = await bfx.rest.get_available_balance('fUSD', 1, 800, 'FUNDING')
        return round(balance[0]*(-1),3)-0.001
    except Exception as e:
        logging.error(e)
        return 0

async def get_books():
    try:
        books = await bfx.rest.get_public_books('fUSD','R0',25)
    except Exception as e:
        logging.error(e)
        return 0
    max_funding_rate_want_borrow = books[0][2]
    max_funding_rate_want_days = books[0][1]
    tmp = 0
    money = 0
    for book in books:
        if book[3] > 0:
            tmp += book[2] * book[3]
            money += book[3] 
    funding_rate = round(tmp / money, 8)
    if max_funding_rate_want_borrow > funding_rate and max_funding_rate_want_days == 2:
        return max_funding_rate_want_borrow
    else:
        return funding_rate

async def wallet_funding_balance():
    try:
        amounts = await bfx.rest.get_wallets()
    except Exception as e:
        logging.error(e)
        return 0
    for amount in amounts:
        if amount.__dict__['key'] == 'funding_USD':            
            balance = math.ceil(amount.__dict__['unsettled_interest']*100)/100
    return balance

async def create_funding_order(funding_rate, balance, day):
    try:
        resp = await bfx.rest.submit_funding_offer("fUSD", balance, funding_rate, day)
        logging.info(resp)
    except Exception as e:
        logging.error(e)

async def check_offer():
    try:
        offers = await bfx.rest.get_funding_offers('fUSD')
    except Exception as e:
        logging.error(e)
        return 
    for offer in offers:
        offer_data = offer.__dict__
        now = math.ceil(time.time()*1000)
        if now - offer_data["mts_create"] > 1000*60*2:
            try:
                resp = await bfx.rest.submit_cancel_funding_offer(offer_data['id'])
                logging.info(resp)
            except Exception as e:
                logging.error(e)

async def run():
    await check_offer()
    balance = await wallet_available_balance()
    funding_rate = await get_books()
    funding_rate_year = round(math.pow(1 + funding_rate, 365) - 1, 4)
    logging.info("Balance: %.2f, Rate: %.8f, Year: %.4f", balance, funding_rate, funding_rate_year)
    if balance > 50:
        if funding_rate > config['RATE_THEADHOLD_HIGH']:
            await create_funding_order(funding_rate, balance, 30)
        else: 
            await create_funding_order(funding_rate, balance, 2)
while 1 :
    t = asyncio.ensure_future(run())
    asyncio.get_event_loop().run_until_complete(t)
    time.sleep(10)