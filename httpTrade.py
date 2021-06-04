from xmlrpc.client import ServerProxy
import requests
import json
from decimal import *
import redisRW

url = 'http://127.0.0.1:8001'

def login():
    try:
        with ServerProxy(rpc_url) as proxy:
            result = proxy.login()
            return result
    except:
        pass
    return False

def get_ky_balance():
    try:
        r = requests.get(url + '/balance')
        if r.status_code == 200:
            return str(json.loads(r.text)['balance'])
    except:
        pass
    return '0'

def buy(code, name, price, tol):
    try:
        data = {'code': code, 'name': name, 'price': price, 'tol': tol}
        r = requests.post(url + '/buy', data=json.dumps(data, cls=redisRW.DecEncoder))
        if r.status_code == 200:
            return True
    except Exception as e:
        print(e)
    return False

def sell(code, name, price, tol):
    try:
        data = {'code': code, 'name': name, 'price': price, 'tol': tol}
        r = requests.post(url + '/sell', data=json.dumps(data, cls=redisRW.DecEncoder))
        if r.status_code == 200:
            return True
    except Exception as e:
        print(e)
    return False

def get_chicang():
    try:
        with ServerProxy(rpc_url) as proxy:
            result = proxy.get_chicang()
            return result
    except:
        pass

def get_chengjiao(ht_bh):
    try:
        with ServerProxy(rpc_url) as proxy:
            result = proxy.get_chengjiao(ht_bh)
            return result
    except:
        pass
    return {}

def get_weituo():
    try:
        with ServerProxy(rpc_url) as proxy:
            result = proxy.get_weituo()
            return result
    except:
        pass
    return {}

def cancel_oder_all():
    try:
        r = requests.get(url + '/cancel')
        if r.status_code == 200:
            return True
    except:
        pass
    return False

def kill():
    try:
        with ServerProxy(rpc_url) as proxy:
            result = proxy.kill()
            return result
    except:
        pass
    return False
