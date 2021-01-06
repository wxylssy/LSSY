import datetime
from decimal import *
from multiprocessing import Lock, Manager
import redisRW

# 上证指数代码
index_sz_code = 'sh.000001'

class commObj:
    def __init__(self, rdchicang, balance, is_backtest):
        self.lock = Lock()
        self.is_backtest = is_backtest
        self.init_balance = balance
        self.testbar = False
        self.__values = Manager().dict()
        self.__values['balance'] = balance
        self.rdchicang = rdchicang

    @property
    def balance(self):
        return self.__values['balance']

    @balance.setter
    def balance(self, v):
        self.__values['balance'] = v

def is_trade_time():
    """
    是否为交易时间

    :return:
        True 或 False
    """
    return False
    now_date = datetime.datetime.now()
    if not now_date.weekday() in range(5):
        return False
    # 中午不能退出，因为实时行情本地列表退出就不存在了
    if now_date.hour in [10, 11, 12, 13, 14]:
        return True
    # 启动过早可能通达信的昨日数据还未清除
    if now_date.hour == 9 and now_date.minute >= 15:
        return True
    if now_date.hour == 15 and now_date.minute <= 3:
        return True
    return False

def is_kzz(code):
    if code[0:3] in ['127', '128', '123']:
        return 1
    elif code[:3] in ['110', '113']:
        return 2
    return False

def get_lost_time_minute(opentime, nowtime):
    t = Decimal(str((nowtime - opentime).total_seconds())) / Decimal('60')
    t = t.quantize(Decimal('0.01'), ROUND_HALF_UP)
    if nowtime.hour > 12:
        t -= Decimal('90')
    if t <= 0:
        t = Decimal('1')
    if t < 0:
        raise Exception('时间错误。', t, opentime, nowtime)
    return t


def get_xdxr_row(xdxr_datas, date: datetime.datetime):
    for d in xdxr_datas:
        if d['name'] != '除权除息':
            continue
        if d['datetime'].year == date.year and d['datetime'].month == date.month and d['datetime'].day == date.day:
            return d


def find_zt(klines, count):
    """
    寻找count天内是否有涨停
    """
    i = 0
    for k in klines:
        i += 1
        if i > count:
            break
        if k['close'] == klines[i]['zt_price']:
            return True
    return False


def check_up(klines, max_ma_5):
    last_k = None
    for k in klines:
        if k['ma_5'] == max_ma_5:
            break
        if last_k is None:
            last_k = k
            continue
        if k['ma_5'] < last_k['ma_5']:
            return True


def xg_data(code, name, avg_line_zdf, zs_date, zy_date, price_zs, price_zy, chicang={}):
    # 行业信息
    rdhangye = redisRW.redisrw(redisRW.db_hangye)
    hy = rdhangye.read_dec(code)
    if hy is None:
        hy = {'hangye': ''}
    return {
        'code': code,
        'name': name,
        'hangye': hy['hangye'],
        'avg_line_zdf': avg_line_zdf,
        'chicang': chicang,
        'bz': 0,
        'zs_date': zs_date,
        'zy_date': zy_date,
        'price_zy': price_zy,
        'price_zs': price_zs
    }


def get_index_from_datetime(klines, date: str):
    i = 0
    d = datetime.datetime.strptime(date, '%Y%m%d')
    for k in klines:
        if datetime.datetime.strptime(k['datetime'], '%Y%m%d').date() == d.date():
            return i
        i += 1


def get_price_zs(p: Decimal):
    # 误差
    fp = p * Decimal('0.003')
    zs = (p - fp).quantize(Decimal('0.01'), ROUND_HALF_UP)
    return zs

def get_max_from_count(klines, key, skip, count):
    """
    跳过skip个到count个k线中获取最大key值
    """
    i = 0
    result = klines[skip][key]
    for k in klines:
        i += 1
        if i <= skip:
            continue
        if i > count:
            break
        if k[key] > result:
            result = k[key]
    return result


def get_min_from_count(klines, key, skip, count):
    """
    跳过skip个到count个k线中获取最小key值
    """
    i = 0
    index = skip
    result = klines[skip][key]
    for k in klines:
        i += 1
        if i <= skip:
            continue
        if i > count:
            break
        if k[key] == 0:
            continue
        if k[key] < result:
            result = k[key]
            index = i - 1
    return result, index


def find_cross(klines, start, key):
    """
    从start(0开始)开始查找交点
    :param klines:
    :param start:
    :param key:
    :return:
    """
    i = 0
    for k in klines:
        i += 1
        if i <= start:
            continue
        if k[key] != 0:
            return k[key], i - 1
    return None, None


def trade_fee(m):
    gh_free = (m * Decimal('0.00002')).quantize(Decimal('0.01'), ROUND_HALF_UP)
    if gh_free < 1:
        gh_free = Decimal('1')
    fee = (m * Decimal('0.0002')).quantize(Decimal('0.01'), ROUND_HALF_UP)
    if fee < 5:
        fee = Decimal('5')
    return fee + gh_free


def buy_tol_from_money(code, balance, price, cangwei: str):
    """
    根据金额和仓位计算买入数量
    :param mbalance:
    :param price:
    :param cangwei:
    :return:
    """
    cangwei = Decimal(cangwei)
    if cangwei <= 1:
        jy_m = balance * cangwei
    else:
        jy_m = cangwei
    if jy_m > balance:
        jy_m = balance
    fee = trade_fee(jy_m)
    jy_m -= fee
    result = None
    if is_kzz(code) == 1:
        tol = int(jy_m // price // Decimal('10') * Decimal('10'))
        if tol < 10:
            return result
    elif is_kzz(code) == 2:
        tol = int(jy_m // price // Decimal('10') * Decimal('10') // Decimal('10'))
        if tol < 1:
            return result
    else:
        tol = int(jy_m // price // Decimal('100') * Decimal('100'))
        if tol < 100:
            return result
    result = tol
    return result

def sell_money_from_tol(code, price, tol):
    """
    根据数量计算卖出后的金额
    :param code:
    :param price:
    :param tol:
    :return:
    """
    if is_kzz(code) == 1:
        m = tol * price
    elif is_kzz(code) == 2:
        m = tol * Decimal('10') * price
    else:
        m = tol * price
    fee = trade_fee(m)
    m -= fee
    return m

