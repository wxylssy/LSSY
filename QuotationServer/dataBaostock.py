import baostock as bs
import datetime
from decimal import *

lg = bs.login()

def get_type(code):
    if code[0] == 's':
        return ''
    if code[0] == '6' or code[0:3] in ['110', '113']:
        return 'sh.'
    else:
        return 'sz.'

def str_to_dec(s):
    if len(s) == 0:
        return Decimal(0)
    return Decimal(s).quantize(Decimal('0.01'), ROUND_HALF_UP)

def get_kline_from_start_date(code, start_date: datetime.date, frequency='d', adjustflag='2'):
    """
    返回json数据，最新的日期在前面（0索引）
    """
    rs = bs.query_history_k_data_plus(get_type(code) + code,
                                      "date,code,open,high,low,close,volume,amount,turn,pctChg",
                                      start_date=start_date.strftime('%Y-%m-%d'),
                                      frequency=frequency,
                                      adjustflag=adjustflag
                                      )
    if rs.error_code != '0':
        raise Exception('错误代码：' + rs.error_code)
    data_list = []
    while rs.next():
        d = {}
        r = rs.get_row_data()
        for i in range(len(r)):
            d[rs.fields[i]] = r[i]
        w = {}
        w['volume'] = str_to_dec(d['volume'])
        w['amount'] = str_to_dec(d['amount'])
        if w['volume'] == 0 or w['amount'] == 0:
            continue
        w['datetime'] = d['date'].replace('-', '')
        w['open'] = str_to_dec(d['open'])
        w['high'] = str_to_dec(d['high'])
        w['low'] = str_to_dec(d['low'])
        w['close'] = str_to_dec(d['close'])
        w['pctChg'] = str_to_dec(d['pctChg'])
        data_list.insert(0, w)
    return data_list

def get_kline_index_from_start_date(i_code, start_date: datetime.date):
    rs = bs.query_history_k_data_plus(i_code,
                                      "date,code,open,high,low,close,preclose,volume,amount,pctChg",
                                      start_date=start_date.strftime('%Y-%m-%d'), frequency="d")
    if rs.error_code != '0':
        raise Exception('错误代码：' + rs.error_code)
    data_list = []
    while rs.next():
        d = {}
        r = rs.get_row_data()
        for i in range(len(r)):
            d[rs.fields[i]] = r[i]
        w = {}
        w['volume'] = str_to_dec(d['volume'])
        if w['volume'] == 0:
            continue
        w['datetime'] = d['date'].replace('-', '')
        w['open'] = str_to_dec(d['open'])
        w['high'] = str_to_dec(d['high'])
        w['low'] = str_to_dec(d['low'])
        w['close'] = str_to_dec(d['close'])
        w['amount'] = str_to_dec(d['amount'])
        w['preclose'] = str_to_dec(d['preclose'])
        w['pctChg'] = str_to_dec(d['pctChg'])
        data_list.insert(0, w)
    return data_list

def qfq_adjust_factor(none_klines, qfq_klines):
    l = len(none_klines)
    if l != len(qfq_klines):
        raise Exception('数据长度不一致。')
    for i in range(l):
        factor = qfq_klines[i]['open'] / none_klines[i]['open']
        # 需要使用float，dec会被保留2位小数失去精度
        qfq_klines[i]['factor'] = float(factor.quantize(Decimal('0.000001'), ROUND_HALF_UP))

"""
def get_adjust_factor(code, start_date: datetime.date):
    #获取复权因子，最新的数据在前面（0索引）
    rs = bs.query_adjust_factor(code=get_type(code) + code, start_date=start_date.strftime('%Y-%m-%d'))
    if rs.error_code != '0':
        raise Exception('错误代码：' + rs.error_code)
    data_list = []
    while rs.next():
        d = {}
        r = rs.get_row_data()
        for i in range(len(r)):
            d[rs.fields[i]] = r[i]
        w = {}
        w['datetime'] = datetime.datetime.strptime(d['dividOperateDate'], '%Y-%m-%d')
        # 这里不能用dec类型，否则存储会被保留2位小数失去精度
        w['foreAdjustFactor'] = float(d['foreAdjustFactor'])
        w['backAdjustFactor'] = float(d['backAdjustFactor'])
        data_list.insert(0, w)
    return data_list
"""

def get_profit_from_start_year(code, start_year: int):
    """
    获取指定年度到现在的1,2,3,4季度
    """
    data_list = []
    for y in range(start_year, datetime.datetime.now().year + 1):
        for i in range(1, 5):
            rs = bs.query_profit_data(get_type(code) + code, year=y, quarter=i)
            while (rs.error_code == '0') & rs.next():
                d = {}
                r = rs.get_row_data()
                for k_i in range(len(r)):
                    d[rs.fields[k_i]] = r[k_i]
                d['statDate'] = datetime.datetime.strptime(d['statDate'], '%Y-%m-%d')
                for k in d.keys():
                    if k not in ['code', 'pubDate', 'statDate']:
                        d[k] = str_to_dec(d[k])
                data_list.insert(0, d)
    return data_list

def get_operation_from_start_year(code, start_year: int):
    """
    获取指定年度到现在的1,2,3,4季度
    """
    data_list = []
    for y in range(start_year, datetime.datetime.now().year + 1):
        for i in range(1, 5):
            rs = bs.query_operation_data(get_type(code) + code, year=y, quarter=i)
            while (rs.error_code == '0') & rs.next():
                d = {}
                r = rs.get_row_data()
                for k_i in range(len(r)):
                    d[rs.fields[k_i]] = r[k_i]
                d['statDate'] = datetime.datetime.strptime(d['statDate'], '%Y-%m-%d')
                for k in d.keys():
                    if k not in ['code', 'pubDate', 'statDate']:
                        d[k] = str_to_dec(d[k])
                data_list.insert(0, d)
    return data_list

def get_growth_from_start_year(code, start_year: int):
    """
    获取指定年度到现在的1,2,3,4季度
    """
    data_list = []
    for y in range(start_year, datetime.datetime.now().year + 1):
        for i in range(1, 5):
            rs = bs.query_growth_data(get_type(code) + code, year=y, quarter=i)
            while (rs.error_code == '0') & rs.next():
                d = {}
                r = rs.get_row_data()
                for k_i in range(len(r)):
                    d[rs.fields[k_i]] = r[k_i]
                d['statDate'] = datetime.datetime.strptime(d['statDate'], '%Y-%m-%d')
                for k in d.keys():
                    if k not in ['code', 'pubDate', 'statDate']:
                        d[k] = str_to_dec(d[k])
                data_list.insert(0, d)
    return data_list

def get_balance_from_start_year(code, start_year: int):
    """
    获取指定年度到现在的1,2,3,4季度
    """
    data_list = []
    for y in range(start_year, datetime.datetime.now().year + 1):
        for i in range(1, 5):
            rs = bs.query_balance_data(get_type(code) + code, year=y, quarter=i)
            while (rs.error_code == '0') & rs.next():
                d = {}
                r = rs.get_row_data()
                for k_i in range(len(r)):
                    d[rs.fields[k_i]] = r[k_i]
                d['statDate'] = datetime.datetime.strptime(d['statDate'], '%Y-%m-%d')
                for k in d.keys():
                    if k not in ['code', 'pubDate', 'statDate']:
                        d[k] = str_to_dec(d[k])
                data_list.insert(0, d)
    return data_list

def get_cash_flow_from_start_year(code, start_year: int):
    """
    获取指定年度到现在的1,2,3,4季度
    """
    data_list = []
    for y in range(start_year, datetime.datetime.now().year + 1):
        for i in range(1, 5):
            rs = bs.query_cash_flow_data(get_type(code) + code, year=y, quarter=i)
            while (rs.error_code == '0') & rs.next():
                d = {}
                r = rs.get_row_data()
                for k_i in range(len(r)):
                    d[rs.fields[k_i]] = r[k_i]
                d['statDate'] = datetime.datetime.strptime(d['statDate'], '%Y-%m-%d')
                for k in d.keys():
                    if k not in ['code', 'pubDate', 'statDate']:
                        d[k] = str_to_dec(d[k])
                data_list.insert(0, d)
    return data_list

def get_hangye():
    """
    获取行业信息，返回字典 {code: bkname, ...}
    :return:
    """
    rs = bs.query_stock_industry()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        d = {}
        r = rs.get_row_data()
        for k_i in range(len(r)):
            d[rs.fields[k_i]] = r[k_i]
        w = {}
        w['code'] = d['code'][3:]
        w['name'] = d['code_name']
        w['hangye'] = d['industry']
        data_list.append(w)
    return data_list