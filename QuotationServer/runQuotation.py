from QuotationServer import comm
from QuotationServer import dataTdx
from QuotationServer import push
from QuotationServer import backTest
from QuotationServer import zbStrategy
from QuotationServer import dataAkshare
from WebServer import ply
import progressBar
import redisRW
import tickFile

from multiprocessing import Process
import threading
import datetime
import math
import traceback
import os
import time
from decimal import *
import numpy as np

current_path = os.path.dirname(__file__)

def th_tdx_run(lockobj, ip, port, xg_data, sleep_time_connect):
    try:
        p = push.Push(lockobj, xg_data)
    except:
        print(traceback.print_exc())
        return
    tdx = dataTdx.DataTdx(ip=ip, port=port, push=p, sleep_time_connect=sleep_time_connect)
    tdx.loop_get_realtime_tick(xg_data['code'])

def c_ths_tdx(lockobj, addrs_list_info, xg_data_list):
    ths_list = []
    addr_ky_count = len(addrs_list_info)
    addrs_sleep_time = {}
    for ad in addrs_list_info:
        addrs_sleep_time[ad[1]] = 0.0
    rdkline = redisRW.redisrw(redisRW.db_kline)
    addr_index = 0
    for xg_data in xg_data_list:
        # 把K线合并到选股数据中
        code = xg_data['code']
        klines = rdkline.read_l_dec(code, 0, 0)
        if len(klines) == 0:
            continue
        xg_data['kline'] = klines[0]
        ip = addrs_list_info[addr_index][1]
        port = addrs_list_info[addr_index][2]
        th = threading.Thread(target=th_tdx_run, args=(lockobj,
                                                       ip,
                                                       port,
                                                       xg_data,
                                                       addrs_sleep_time[ip]))
        ths_list.append(th)
        addr_index += 1
        if addr_index >= addr_ky_count:
            addr_index = 0
        addrs_sleep_time[ip] += 0.5
    for th in ths_list:
        th.start()
    m = sorted(addrs_sleep_time.items(), key=lambda x: x[1], reverse=True)
    print('任务报告', os.getpid(), len(ths_list), '个线程启动完毕。最后开始时间', m[0][1], '秒。')
    for th in ths_list:
        th.join()

def th_back_test_run(lockobj, xg_data):
    try:
        p = push.Push(lockobj, xg_data)
    except:
        print(traceback.print_exc())
        return
    bk = backTest.BackTest(p, xg_data['code'])
    bk.start()

def c_ths_back_test(lockobj, back_test_date, xg_data_list):
    ths_list = []
    rdkline = redisRW.redisrw(redisRW.db_kline)
    for xg_data in xg_data_list:
        # 把K线合并到选股数据中
        code = xg_data['code']
        klines = rdkline.read_klines_from_before_date_count_dec(code, back_test_date, 1)
        if len(klines) == 0:
            continue
        xg_data['kline'] = klines[0]
        th = threading.Thread(target=th_back_test_run, args=(lockobj, xg_data))
        ths_list.append(th)
        #break
    for th in ths_list:
        th.start()
    print('任务报告', os.getpid(), len(ths_list), '个线程启动完毕。')
    for th in ths_list:
        th.join()

def wait_trade_time_end():
    # 在交易时间就等待交易时间结束
    while comm.is_trade_time():
        time.sleep(10)

def get_ticks_from_xg_and_start_backtest(common, back_test_date: datetime.datetime):
    """
    回测初始化
    """
    rdbacktest = redisRW.redisrw(redisRW.db_backtest_tick)
    rdbacktest.del_db()
    rdxg = redisRW.redisrw(redisRW.db_xg)
    rdkline = redisRW.redisrw(redisRW.db_kline)
    xg_codes = rdxg.read_codes()
    if len(xg_codes) == 0:
        print(back_test_date, '没有选股数据。')
        return True
    # 存储当天tick数据
    bar = progressBar.progressbar()
    bar.start('存储tick数据', len(xg_codes))
    for code in xg_codes:
        bar.progress()
        if not common['ticktest']:
            ticks = rdkline.read_klines_from_date_dec(code, back_test_date)
        else:
            ticks = dataAkshare.get_ticks(code, back_test_date)
        if len(ticks) == 0:
            continue
        if not common['ticktest']:
            ticks[0]['code'] = code
            ticks[0]['price'] = ticks[0]['open']
            ticks[0]['buyorsell'] = 0
            ticks[0]['num'] = 0
            ticks[0]['vol'] = ticks[0]['volume']
            ticks.append(ticks[0].copy())
            ticks[1]['price'] = ticks[1]['close']
            ticks[1]['vol'] = 0
            ticks[1]['amount'] = 0
            date_time = ticks[0]['datetime']
            ticks[0]['datetime'] = datetime.datetime(date_time.year, date_time.month, date_time.day, 9, 25)
            ticks[1]['datetime'] = datetime.datetime(date_time.year, date_time.month, date_time.day, 15)
        else:
            # 复权
            factor = rdkline.get_adjust_factor(code, back_test_date)
            for tk in ticks:
                tk['price'] = Decimal(tk['price'])
                tk['price'] = (tk['price'] * factor).quantize(Decimal('0.01'), ROUND_HALF_UP)
        rdbacktest.wirte_l_datas(code, ticks)
    if len(rdbacktest.read_codes()) == 0:
        print(back_test_date, '没有tick数据')
        return
    print('回测日期', back_test_date)
    start_quotation_process(common, back_test_date)

    rddaysell = redisRW.redisrw(redisRW.db_day_sell)
    rdsell = redisRW.redisrw(redisRW.db_sell)
    # 简单统计
    sell_count = 0
    sz_count = 0
    xd_count = 0
    for d in rdsell.read_all_dec():
        sell_count += 1
        zdf = d['zdf']
        if zdf > 0:
            sz_count += 1
        else:
            xd_count += 1
    if common['b']:
        rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
    else:
        rdchicang = redisRW.redisrw(redisRW.db_chicang)
    # 持仓市值
    market_value = 0
    for d in rdchicang.read_all_dec():
        market_value += d['chicang']['marketValue']
    zc = common['balance'] + market_value
    zyk = (zc / common['init_balance'] - 1) * 100
    zyk = zyk.quantize(Decimal('0.01'), ROUND_HALF_UP)
    rddaysell.wirte_l_data('daysell', {
        'datetime': back_test_date,
        'zyk': zyk,
        'sell_count': sell_count,
        'sz': sz_count,
        'xd': xd_count,
        'zc': zc
    })
    print('卖出数量', sell_count, '上涨', sz_count, '下跌', xd_count,
          '可用余额', common['balance'], '持仓市值', market_value, '总资产', zc, '总盈亏', zyk)
    return True

def backtest_start(common, start_date: datetime.datetime, end_date: datetime.datetime):
    """
    回测
    """
    rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
    rdchicang.del_db()
    rddaysell = redisRW.redisrw(redisRW.db_day_sell)
    rddaysell.del_db()
    codes_bk = comm.get_codes_bk()
    if not codes_bk:
        print('股票代码列表获取失败。')
        return
    zbstrategy = zbStrategy.Strategy(None)
    while start_date.date() <= end_date.date():
        if start_date.weekday() in range(5):
            # 选股
            zbstrategy.stock_select(common['b'], codes_bk, start_date)
            get_ticks_from_xg_and_start_backtest(common, start_date)
            #input('按任意键继续...')
        start_date += datetime.timedelta(days=1)
    ex_sz_count = 0
    ex_xd_count = 0
    ex_sell_count = 0
    datas = []
    zyk_list = []
    max_huice = 0
    max_zc = None
    day_sz_count = 0
    day_xd_count = 0
    last_zc = common['init_balance']
    for d in rddaysell.read_l_date_dec_json('daysell', 0, -1):
        ex_sell_count += d['sell_count']
        ex_sz_count += d['sz']
        ex_xd_count += d['xd']
        zyk_list.append(d['zyk'])
        if max_zc is None:
            max_zc = d['zc']
        max_zc = max(max_zc, d['zc'])
        max_huice = max(max_huice, (1 - d['zc'] / max_zc) * 100)
        if d['zc'] < last_zc:
            day_sz_count += 1
        else:
            day_xd_count += 1
        last_zc = d['zc']
        datas.append({
            'datetime': d['datetime'],
            'ex_sell_count': ex_sell_count,
            'ex_sz_count': ex_sz_count,
            'ex_xd_count': ex_xd_count,
            'day_sz_count': day_sz_count,
            'day_xd_count': day_xd_count,
            'zc': float(str(d['zc'])),
        })
    if len(datas) == 0:
            print('没有交易数据')
            return
    zyk_std = float(str(np.std(zyk_list)))
    m_data = datas[len(datas) - 1]
    tol_days = (m_data['datetime'] - datas[0]['datetime']).days
    tol_days = max(1, tol_days)
    annualized = float(str(d['zyk'])) / tol_days * 365
    sharperatio = 0
    if zyk_std > 0:
        sharperatio = annualized / zyk_std
    ply.write_html_tol(os.path.join(current_path, '..', 'WebServer', 'html', 'charts.html'), datas, float(str(d['zyk'])), max_huice, annualized, sharperatio)
    #input('回测完成，按任意键继续...')

def start_quotation_process(common, back_test_date: datetime.datetime=None, process_count=3):
    rdxg = redisRW.redisrw(redisRW.db_xg)
    rdsell = redisRW.redisrw(redisRW.db_sell)
    rdsell.del_db()
    # 读取选股数据
    xg_data_list = rdxg.read_all_dec()
    if len(xg_data_list) == 0:
        print('没有选股数据')
        wait_trade_time_end()
        return
    # 清空数据
    tickFile.TickFile().clear()
    rdmainquotation = redisRW.redisrw(redisRW.db_mainquotaion)
    rdmainquotation.del_db()
    # 数据分块
    bk = math.ceil(len(xg_data_list) / process_count)
    bk_data_list = []
    temp = []
    p_list = []
    for i in range(len(xg_data_list)):
        if i > 0 and i % bk == 0:
            bk_data_list.append(temp)
            temp = []
        temp.append(xg_data_list[i])
    if len(temp) > 0:
        bk_data_list.append(temp)
    if back_test_date is None:
        tdx = dataTdx.DataTdx()
        # 可用服务器
        addrs_list_info = tdx.get_sort_address_info()
        addr_ky_count = len(addrs_list_info)
        if addr_ky_count == 0:
            print('没有可用服务器。')
            wait_trade_time_end()
            return
        print('可用服务器', addr_ky_count, '最大延时', addrs_list_info[addr_ky_count - 1][3], 'ms')
        # 启动通达信实时行情进程
        for b in bk_data_list:
            p = Process(target=c_ths_tdx, args=(common, addrs_list_info, b))
            p_list.append(p)
            p.start()
    else:
        # 启动回测行情模拟进程
        for b in bk_data_list:
            p = Process(target=c_ths_back_test, args=(common, back_test_date, b))
            p_list.append(p)
            p.start()
    print('行情服务已启动，选股数量', len(xg_data_list))
    for p in p_list:
        p.join()
    print('行情服务结束。')

if __name__ == "__main__":
    pass
