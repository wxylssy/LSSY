from decimal import *
from QuotationServer import comm

def count_by_seconds_int(data_list, key, new_key, seconds):
    last_time = data_list[0]['datetime']
    tols = 0
    for d in data_list:
        if (last_time - d['datetime']).total_seconds() > seconds:
            break
        tols += d[key]
    data_list[0][new_key] = tols

def count_by_seconds_dec(data_list, key, new_key, seconds):
    last_time = data_list[0]['datetime']
    tols = Decimal(0)
    for d in data_list:
        if (last_time - d['datetime']).total_seconds() > seconds:
            break
        tols += d[key]
    data_list[0][new_key] = tols

def count_avg(data_list, key, new_key, num):
    tols = Decimal(0)
    if len(data_list) > num:
        for i in range(1, num + 1):
            tols += data_list[i][key]
        tols /= Decimal(num)
    data_list[0][new_key] = tols

def count_all(data_list, key, new_key):
    if len(data_list) > 1:
        data_list[0][new_key] = data_list[1][new_key] + data_list[0][key]
    else:
        data_list[0][new_key] = data_list[0][key]

def count_while(data_list, key, new_key, while_key, while_val):
    if len(data_list) > 1:
        if data_list[0][while_key] == while_val:
            data_list[0][new_key] = data_list[1][new_key] + data_list[0][key]
        else:
            data_list[0][new_key] = data_list[1][new_key]
    else:
        if data_list[0][while_key] == while_val:
            data_list[0][new_key] = data_list[0][key]
        else:
            data_list[0][new_key] = 0

def count_continuity(data_list, key, new_key):
    if len(data_list) > 1:
        if (data_list[0][key] >= 0 and data_list[1][key] >= 0) or (data_list[0][key] <= 0 and data_list[1][key] <= 0):
            data_list[0][new_key] = data_list[1][new_key] + data_list[0][key]
        else:
            data_list[0][new_key] = data_list[0][key]
    else:
        data_list[0][new_key] = data_list[0][key]

def count_filter_avg(data_list, key, new_key, new_key_num, new_key_avg, filter_val):
    if len(data_list) > 1:
        if data_list[0][key] >= filter_val:
            data_list[0][new_key] = data_list[1][new_key] + data_list[0][key]
            data_list[0][new_key_num] = data_list[1][new_key_num] + 1
            data_list[0][new_key_avg] = data_list[0][new_key] / data_list[0][new_key_num]
        else:
            data_list[0][new_key] = data_list[1][new_key]
            data_list[0][new_key_num] = data_list[1][new_key_num]
            data_list[0][new_key_avg] = data_list[1][new_key_avg]
    else:
        if data_list[0][key] >= filter_val:
            data_list[0][new_key] = data_list[0][key]
            data_list[0][new_key_num] = 1
            data_list[0][new_key_avg] = data_list[0][key]
        else:
            data_list[0][new_key] = 0
            data_list[0][new_key_num] = 0
            data_list[0][new_key_avg] = 0

def min_all(data_list, key, new_key):
    if len(data_list) > 1:
        if data_list[0][key] < data_list[1][new_key]:
            data_list[0][new_key] = data_list[0][key]
        else:
            data_list[0][new_key] = data_list[1][new_key]
    else:
        data_list[0][new_key] = data_list[0][key]

def max_all(data_list, key, new_key):
    if len(data_list) > 1:
        if data_list[0][key] > data_list[1][new_key]:
            data_list[0][new_key] = data_list[0][key]
        else:
            data_list[0][new_key] = data_list[1][new_key]
    else:
        data_list[0][new_key] = data_list[0][key]

def kline(data_list, count):
    low_price = data_list[0]['price']
    high_price = low_price
    d_price = high_price
    i = 0
    for d in data_list:
        i += 1
        if i > count:
            break
        d_price = d['price']
        if d_price > high_price:
            high_price = d_price
        if d_price < low_price:
            low_price = d_price
    data_list[0]['open'] = d_price
    data_list[0]['low'] = low_price
    data_list[0]['high'] = high_price
    data_list[0]['close'] = data_list[0]['price']

def ap_reversed(data_list, key, newkey):
    if len(data_list) > 1:
        flag = data_list[1][newkey]
        if data_list[0][key] <= data_list[1][key] and data_list[0]['amount'] >= 100000:
            if data_list[0]['price'] > data_list[1]['price']:
                flag += 2
            elif data_list[0]['price'] == data_list[1]['price']:
                flag += 1
            else:
                flag = 0
        else:
            flag = 0
        data_list[0][newkey] = flag
    else:
        data_list[0][newkey] = 0

def bi(data_list, key1, key2, new_key):
    if data_list[0][key2] == 0:
        data_list[0][new_key] = Decimal('0')
        return
    data_list[0][new_key] = data_list[0][key1] / data_list[0][key2]

def bi_by_seconds(data_list, key, new_key, seconds):
    last_time = data_list[0]['datetime']
    last_val = data_list[0][key]
    for d in data_list:
        if (last_time - d['datetime']).total_seconds() > seconds:
            break
        if d[key] > 0:
            last_val = d[key]
    if last_val > 0:
        data_list[0][new_key] = Decimal(data_list[0][key]) / Decimal(last_val)
    else:
        data_list[0][new_key] = Decimal(0)

def bi_avg_by_seconds(data_list, key, new_key, seconds):
    """
    当前的价格除以过去一分钟的（不包含当前）平均价格
    :param data_list:
    :param key:
    :param new_key:
    :param seconds:
    :return:
    """
    last_time = data_list[0]['datetime']
    tols = Decimal(0)
    i = 1
    for i in range(1, len(data_list)):
        if (last_time - data_list[i]['datetime']).total_seconds() > seconds:
            break
        tols += data_list[i][key]
    i = Decimal(str(i))
    avg = tols / i
    if avg > 0:
        bi = data_list[0][key] / avg
    else:
        bi = Decimal(0)
    data_list[0][new_key] = bi

def speed_by_seconds(data_list, new_key, seconds):
    last_time = data_list[0]['datetime']
    new_price = data_list[0]['price']
    low = new_price
    high = new_price
    for d in data_list:
        if (last_time - d['datetime']).total_seconds() > seconds:
            break
        if d['price'] < low:
            low = d['price']
        if d['price'] > high:
            high = d['price']
    if new_price > low:
        dec_div = (new_price / low - 1) * 100
    else:
        dec_div = (new_price / high - 1) * 100
    data_list[0][new_key] = dec_div

def qx(data_list, new_key):
    if len(data_list) > 1:
        if data_list[0]['datetime'].hour > 9:
            data_list[0][new_key] = data_list[1][new_key]
            return
    v = 0
    if data_list[0]['price'] > data_list[0]['price_open']:
        v = 1
    data_list[0][new_key] = v

def open_record(data_list, key, new_key):
    if len(data_list) > 1:
        data_list[0][new_key] = data_list[1][new_key]
    else:
        data_list[0][new_key] = data_list[0][key]

def diff(data_list, key, new_key):
    if len(data_list) > 1:
        data_list[0][new_key] = data_list[0][key] - data_list[1][key]
    else:
        data_list[0][new_key] = 0

def history_calculate_by_kline(xg_data):
    # 开盘到收盘的分钟数
    kline = xg_data['kline']
    open_lost_time = Decimal('245')
    r_data = {
        'last_price': kline['close'],
        'last_amount_m': kline['amount'] / open_lost_time,
        'last_amount_open': xg_data['amount_open'],
        'zt_price': kline['zt_price'],
        'dt_price': kline['dt_price'],
        'zt_chg': kline['zt_chg'],
        'dt_chg': kline['dt_chg']
    }
    return r_data

def merge_history_realtime_tick(data_list, history_data):
    # 开盘到现在的分钟数
    open_lost_time = comm.get_lost_time_minute(data_list[0]['datetime_open'], data_list[0]['datetime'])
    data_list[0]['zdf'] = ((data_list[0]['price'] / history_data['last_price'] - 1) * 100)
    data_list[0]['zdf_open'] = ((data_list[0]['price_open'] / history_data['last_price'] - 1) * 100)
    data_list[0]['bi_amount'] = data_list[0]['amounts'] / open_lost_time / history_data['last_amount_m']
    data_list[0]['bi_amount_open'] = data_list[0]['amount_open'] / history_data['last_amount_m']
    data_list[0]['bi_amount_open_last'] = data_list[0]['amount_open'] / history_data['last_amount_open']
    data_list[0]['bi_amount_60s_1'] = data_list[0]['amount_60s'] / history_data['last_amount_m']
    data_list[0]['zt_price'] = history_data['zt_price']
    data_list[0]['dt_price'] = history_data['dt_price']
    data_list[0]['zt_chg'] = history_data['zt_chg']
    data_list[0]['dt_chg'] = history_data['dt_chg']
