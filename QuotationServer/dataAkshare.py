import akshare as ak
import datetime
from decimal import *
import numpy as np
import progressBar
import time

def get_type(code):
    if code[0] == '6':
        return 'sh'
    else:
        return 'sz'

def _data_format(data):
    data = str(data).replace('↑', '')
    data = data.replace('↓', '')
    return data

def get_ticks(code, date: datetime.datetime):
    """
    获取指定股票指定交易日的全部tick，一个tick是一个集合，没有返回空列表
    """
    stock_zh_a_tick_tx_df = ak.stock_zh_a_tick_tx(code=get_type(code) + code, trade_date=date.strftime('%Y%m%d'))
    result = []
    for row in stock_zh_a_tick_tx_df.itertuples(index=False):
        buyorsell = 0
        if row[5] == '卖盘':
            buyorsell = 1
        elif row[5] == '中性盘':
            buyorsell = 2
        result.append({
                'code': code,
                'datetime': datetime.datetime.strptime(date.strftime('%Y%m%d') + ' ' + row[0], '%Y%m%d %H:%M:%S').strftime('%Y%m%d %H:%M:%S'),
                'price': row[1],
                'amount': float(row[4]),
                'buyorsell': buyorsell,
                'num': 0,
                'vol': float(row[3] * 100)
        })
    return result

def get_kline(code, start_date: datetime.date):
    """
    返回json数据，最新的日期在前面
    """
    result = []
    df = ak.stock_zh_a_daily(symbol=get_type(code) + code, adjust="hfq")
    # 腾讯，主要是使用amount字段
    dftx = ak.stock_zh_index_daily_tx(symbol=get_type(code) + code)
    if df is None or df.empty:
        return result
    if dftx is None or dftx.empty:
        return result
    for row in df.itertuples():
        w = {}
        w['datetime'] = getattr(row, 'Index')
        if w['datetime'] < start_date:
            continue
        w['open'] = getattr(row, 'open')
        w['high'] = getattr(row, 'high')
        w['low'] = getattr(row, 'low')
        w['close'] = getattr(row, 'close')
        w['volume'] = getattr(row, 'volume')
        result.append(w)
    return result

def jijin_cg(code):
    result = []
    df = ak.stock_fund_stock_holder(stock=code)
    if df is None or df.empty:
        return result
    spl_date = str(df.iloc[0]['截止日期']).replace('-', '')
    for row in df.itertuples(index=False):
        date = str(getattr(row, '截止日期')).replace('-', '')
        # 只获取一个阶段
        if date != spl_date:
            break
        result.append({
                'date': date,
                '基金名称': row[0],
                '持股数量': int(_data_format(row[2])),
                '持股比例': float(_data_format(row[3]))
        })
    return result

def jigou_cg(code, quarter):
    """
    机构持股一览表，quarter是年度和季度，注意要看当前季度有没有数据
    """
    result = []
    df = ak.stock_institute_hold_detail(stock=code, quarter=quarter)
    if df is None or df.empty:
        return result
    for row in df.itertuples(index=False):
        result.append({
                '持股机构简称': row[2],
                '持股数量': int(Decimal(_data_format(row[4])) * 10000),
                '持股比例': float(_data_format(row[6]))
        })
    return result

def liutong_gudong(code):
    """
    流通股东
    """
    result = []
    df = ak.stock_circulate_stock_holder(stock=code)
    if df is None or df.empty:
        return result
    spl_date = str(df.iloc[0]['截止日期']).replace('-', '')
    for row in df.itertuples(index=False):
        date = str(getattr(row, '截止日期')).replace('-', '')
        # 只获取一个阶段
        if date != spl_date:
            break
        cgs = row[4]
        if cgs is np.nan:
            continue
        result.append({
            '股东名称': row[3],
            '持股数量': int(_data_format(cgs)),
            '持股比例': float(_data_format(row[5]))
        })
    return result

def _get_detail_hangye(label):
    """
    获取行业详情，返回股票代码列表
    :param label:
    :return:
    """
    result = []
    df = ak.stock_sector_detail(sector=label)
    if df is None or df.empty:
        return result
    for row in df.itertuples():
        code = getattr(row, 'code')
        result.append(code)
    return result

def get_hangye(indicators):
    """
    读取全部行业信息，返回字典，{code: 行业}
    :return:
    """
    result = {}
    for indicator in indicators:
        df = ak.stock_sector_spot(indicator=indicator)
        if df is None or df.empty:
            continue
        bar = progressBar.progressbar()
        bar.start('获取行业信息（%s）' % indicator, len(df))
        for row in df.itertuples():
            bar.progress()
            time.sleep(3)
            label = getattr(row, 'label')
            bkname = getattr(row, '板块')
            codes = _get_detail_hangye(label)
            for c in codes:
                v = result.get(c, [])
                v.append(bkname)
                result[c] = v
    return result
