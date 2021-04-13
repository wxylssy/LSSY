from decimal import *
from QuotationServer import comm

decimal_zero = Decimal('0')
decimal_one = Decimal('1')

def sum_list(vals):
    s = 0
    for val in vals:
        s += val
    return s

def max_list(vals):
    m = vals[0]
    for val in vals:
        if val > m:
            m = val
    return m

def min_list(vals):
    m = vals[0]
    for val in vals:
        if val < m:
            m = val
    return m

def max_a(a1, a2):
    if a1 > a2:
        return a1
    else:
        return a2

def avg_list(vals):
    s = sum_list(vals)
    a = s / len(vals)
    return a

# 指定列n日最高值
def EX_high(data_iterator, key, newkey, n):
    i = 0
    vals = []
    for data in data_iterator:
        i += 1
        vals.append(data[key])
        if i < n:
            data[newkey] = decimal_zero
            continue
        m = max_list(vals)
        data[newkey] = m
        vals.pop(0)

# 指定列n日最低值
def EX_low(data_iterator, key, newkey, n):
    i = 0
    vals = []
    for data in data_iterator:
        i += 1
        vals.append(data[key])
        if i < n:
            data[newkey] = decimal_zero
            continue
        m = min_list(vals)
        data[newkey] = m
        vals.pop(0)

def EX_amount_ratio(data_iterator, newkey, n):
    i = 0
    amos = []
    for data in data_iterator:
        a = data['amount']
        i += 1
        #量比不包括本行
        if i <= n:
            data[newkey] = decimal_zero
            amos.append(a)
            continue
        data[newkey] = a / avg_list(amos)
        amos.pop(0)
        amos.append(a)

def EX_kdj(data_iterator, n):
    i = 0
    lows = []
    highs = []
    last_k = 50
    last_d = 50
    for data in data_iterator:
        lows.append(data['low'])
        highs.append(data['high'])
        i += 1
        if i < n:
            data['kdj_k'] = 0
            data['kdj_d'] = 0
            data['kdj_j'] = 0
            continue
        l_min = min_list(lows)
        nd = (data['close'] - l_min)
        if nd == 0:
            rsv = Decimal('0')
        else:
            rsv = (data['close'] - l_min) / (max_list(highs) - l_min) * 100
        k = Decimal("2") / Decimal("3") * last_k + Decimal("1") / Decimal("3") * rsv
        d = Decimal("2") / Decimal("3") * last_d + Decimal("1") / Decimal("3") * k
        j = 3 * k - 2 * d
        last_k = k
        last_d = d
        lows.pop(0)
        highs.pop(0)
        data['kdj_k'] = k
        data['kdj_d'] = d
        data['kdj_j'] = j

def EX_macd(data_iterator, short_: Decimal, mid_: Decimal, long_: Decimal):
    last_dea = 0
    last_sema = 0
    last_lema = 0
    for data in data_iterator:
        c = data["close"]
        s_ema = last_sema * (short_ - 1) / (short_ + 1) + c * 2 / (short_ + 1)
        l_ema = last_lema * (long_ - 1) / (long_ + 1) + c * 2 / (long_ + 1)
        dif = s_ema - l_ema
        dea = last_dea * (mid_ - 1) / (mid_ + 1) + dif * 2 / (mid_ + 1)
        bar = 2 * (dif - dea)
        last_dea = dea
        last_sema = s_ema
        last_lema = l_ema
        data['macd_dif'] = dif
        data['macd_dea'] = dea
        data['macd_bar'] = bar
        #data['macd_sema'] = s_ema
        #data['macd_lema'] = l_ema

def EX_ma(data_iterator, key, newkey, n):
    i = 0
    vals = []
    for data in data_iterator:
        vals.append(data[key])
        i += 1
        if i < n:
            data[newkey] = decimal_zero
            continue
        data[newkey] = sum_list(vals) / n
        vals.pop(0)

def EX_cr(data_iterator, newkey, n):
    # https://wiki.mbalib.com/wiki/CR%E6%8C%87%E6%A0%87
    i = 0
    p1 = []
    p2 = []
    ym = None
    cr = None
    for data in data_iterator:
        i += 1
        # YM 是前一天，这里小于等于
        if i <= n:
            if ym is not None:
                up = data['high'] - ym
                if up < 0:
                    up = decimal_zero
                p1.append(up)
                dn = ym - data['low']
                if dn < 0:
                    dn = decimal_zero
                p2.append(dn)
            ym = (data['high'] + data['low']) / 2
            data[newkey] = decimal_zero
            continue
        up = data['high'] - ym
        if up < 0:
            up = decimal_zero
        p1.append(up)
        dn = ym - data['low']
        if dn < 0:
            dn = decimal_zero
        p2.append(dn)
        df = sum_list(p1)
        kf = sum_list(p2)
        if kf == 0 or df == 0:
            data[newkey] = cr
        else:
            cr = df / kf * 100
            data[newkey] = cr
        p1.pop(0)
        p2.pop(0)
        ym = (data['high'] + data['low']) / 2

def EX_atr(data_iterator, newkey, n):
    i = 0
    trs = []
    lastc = None
    for data in data_iterator:
        i += 1
        if i < n:
            if lastc is None:
                lastc = data['close']
                trs.append(decimal_zero)
                data[newkey] = decimal_zero
                continue
            tr = max_a(max_a(data['high'] - data['low'], abs(lastc - data['high'])), abs(lastc - data['low']))
            trs.append(tr)
            data[newkey] = decimal_zero
            continue
        tr = max_a(max_a(data['high'] - data['low'], abs(lastc - data['high'])), abs(lastc - data['low']))
        trs.append(tr)
        data[newkey] = avg_list(trs)
        lastc = data['close']

def zdt(klines, zdt_range):
    for i in range(len(klines)):
        last_price = Decimal(str(klines[i]['close']))
        zdt_p = last_price * zdt_range
        # 涨跌停价和幅度
        zt_price = (last_price + zdt_p).quantize(Decimal('0.01'), ROUND_HALF_UP)
        dt_price = (last_price - zdt_p).quantize(Decimal('0.01'), ROUND_HALF_UP)
        klines[i]['zt_price'] = zt_price
        klines[i]['dt_price'] = dt_price
        klines[i]['zt_chg'] = ((zt_price / last_price - 1) * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
        klines[i]['dt_chg'] = ((dt_price / last_price - 1) * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)

def cross_upo_down(data_iterator, key1, key2, newkey):
    """
    key1上穿key2结果为1
    key1下穿key2结果为2
    否则为0
    :param data_iterator:
    :param key1:
    :param key2:
    :param newkey:
    :return:
    """
    last_data = None
    for data in data_iterator:
        if last_data is None:
            last_data = data
            data[newkey] = 0
            continue
        up = last_data[key1] < last_data[key2] and data[key1] > data[key2]
        down = last_data[key1] > last_data[key2] and data[key1] < data[key2]
        if up:
            data[newkey] = 1
        elif down:
            data[newkey] = 2
        else:
            data[newkey] = 0
        last_data = data

def klines_calculate(code, klines):
    """
    K先是从最新到旧排列
    """
    zdt_range = Decimal('0.1')
    if code[:3] == '300':
        zdt_range = Decimal('0.2')
    elif comm.is_kzz(code):
        zdt_range = Decimal('0.3')
    zdt(klines, zdt_range)

    EX_ma(reversed(klines), 'close', 'ma_5', 5)
    EX_ma(reversed(klines), 'close', 'ma_10', 10)
    EX_ma(reversed(klines), 'close', 'ma_20', 20)
    EX_ma(reversed(klines), 'close', 'ma_55', 55)
    EX_ma(reversed(klines), 'close', 'ma_60', 60)
    EX_ma(reversed(klines), 'close', 'ma_120', 120)
    EX_ma(reversed(klines), 'close', 'ma_240', 240)

    EX_ma(reversed(klines), 'close', 'ma_50', 50)
    EX_ma(reversed(klines), 'close', 'ma_150', 150)
    EX_ma(reversed(klines), 'close', 'ma_200', 200)
    EX_ma(reversed(klines), 'close', 'ma_8', 8)
    EX_ma(reversed(klines), 'close', 'ma_40', 40)
    cross_upo_down(reversed(klines), 'ma_8', 'ma_40', 'm8_c_m40')

    EX_amount_ratio(reversed(klines), 'amount_ratio_5', 5)

    EX_low(reversed(klines), 'amount', 'amount_low', 60)
    EX_high(reversed(klines), 'amount', 'amount_high', 60)

    EX_cr(reversed(klines), 'cr', 9)
    EX_macd(reversed(klines), Decimal(12), Decimal(9), Decimal(26))
    EX_kdj(reversed(klines), 9)

    EX_atr(reversed(klines), 'atr', 20)

    #cross(reversed(klines), 'macd_dif', 'macd_dea', 'dif_c_dea')
    cross_upo_down(reversed(klines), 'macd_dif', 'macd_dea', 'dif_c_dea')
    cross_upo_down(reversed(klines), 'kdj_j', 'kdj_k', 'j_c_k')
