from xmlrpc.client import ServerProxy

rpc_url = 'http://192.168.122.122:8081/'

def login():
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.login()
            return result
        except:
            return False

def get_ky_balance():
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.get_ky_balance()
            return result
        except:
            return '0'

def buy(code, name, price: str, tol: int):
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.buy(code, name, price, tol)
            return result
        except Exception as e:
            print(e)
            return False

def sell(code, name, price: str, tol: int):
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.sell(code, name, price, tol)
            return result
        except Exception as e:
            print(e)
            return False

def get_chicang():
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.get_chicang()
            return result
        except:
            return None

def get_chengjiao(ht_bh):
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.get_chengjiao(ht_bh)
            return result
        except:
            return {}

def get_weituo():
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.get_weituo()
            return result
        except:
            return {}

def cancel_oder_all():
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.cancel_oder_all()
            return result
        except:
            return False

def kill():
    with ServerProxy(rpc_url) as proxy:
        try:
            result = proxy.kill()
            return result
        except:
            return False
