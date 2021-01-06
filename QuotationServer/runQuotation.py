from QuotationServer import comm
from QuotationServer import dataTdx
from QuotationServer import push
from QuotationServer import backTest
from QuotationServer import zbStrategy
from QuotationServer import dataAkshare
from WebServer import ply
import progressBar
import redisRW

from multiprocessing import Process
import threading
import datetime
import math
import traceback
import os
import time
from decimal import *

def th_tdx_run(lockobj, ip, port, xg_data, sleep_time_connect):
    try:
        p = push.Push(lockobj, xg_data)
    except:
        print(traceback.print_exc())
        return
    tdx = dataTdx.DataTdx(ip=ip, port=port, push=p, sleep_time_connect=sleep_time_connect)
    tdx.loop_get_realtime_tick(xg_data['code'])

def c_ths_tdx(lockobj, addrs_list_info, xg_data_list):
    tdx = dataTdx.DataTdx()
    tdx.select_fast_addr()
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
        # 前一天ticks
        data_ticks = tdx.get_history_ticks(code, datetime.datetime.strptime(klines[0]['datetime'], '%Y%m%d'))
        ticks_len = len(data_ticks)
        if (data_ticks is None) or ticks_len == 0:
            print('前一天tick获取错误。', code)
            continue
        close_tick = data_ticks[ticks_len - 1]
        xg_data['amount_open'] = Decimal(str(close_tick['amount_open']))
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
    tdx = dataTdx.DataTdx()
    tdx.select_fast_addr()
    ths_list = []
    rdkline = redisRW.redisrw(redisRW.db_kline)
    for xg_data in xg_data_list:
        # 把K线合并到选股数据中
        code = xg_data['code']
        klines = rdkline.read_klines_from_before_date_count_dec(code, back_test_date, 1)
        if len(klines) == 0:
            continue
        xg_data['kline'] = klines[0]
        data_ticks = tdx.get_history_ticks(code, datetime.datetime.strptime(klines[0]['datetime'], '%Y%m%d'))
        ticks_len = len(data_ticks)
        if (data_ticks is None) or ticks_len == 0:
            return
        close_tick = data_ticks[ticks_len - 1]
        xg_data['amount_open'] = Decimal(str(close_tick['amount_open']))
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

def get_ticks_from_xg_and_start_backtest(commobj, back_test_date: datetime.datetime):
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
        if commobj.testbar:
            ticks = rdkline.read_klines_from_date_dec(code, back_test_date)
        else:
            ticks = dataAkshare.get_ticks(code, back_test_date)
        if len(ticks) == 0:
            continue
        if commobj.testbar:
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
                tk['price'] = (tk['price'] * factor).quantize(Decimal('0.01'), ROUND_HALF_UP)
        rdbacktest.wirte_l_datas(code, ticks)
    if len(rdbacktest.read_codes()) == 0:
        print(back_test_date, '没有tick数据')
        return
    print('回测日期', back_test_date)
    start_quotation_process(commobj, back_test_date)

    rddaysell = redisRW.redisrw(redisRW.db_day_sell)
    rdsell = redisRW.redisrw(redisRW.db_sell)
    # 简单统计
    buy_count = 0
    zdf_count = Decimal(0)
    sz_count = 0
    xd_count = 0
    for d in rdsell.read_all_dec():
        buy_count += 1
        zdf = d['zdf']
        if zdf > 0:
            sz_count += 1
        else:
            xd_count += 1
        zdf_count += zdf
    if buy_count == 0:
        return
        # 持仓市值
    market_value = 0
    for d in commobj.rdchicang.read_all_dec():
        market_value += d['chicang']['marketValue']
    zc = commobj.balance + market_value
    zyk = (zc / commobj.init_balance - 1) * 100
    zyk = zyk.quantize(Decimal('0.01'), ROUND_HALF_UP)
    rddaysell.wirte_l_data('daysell', {
        'datetime': back_test_date,
        'ex_zdf_count': zdf_count,
        'sj_zdf_count': (zdf_count / buy_count),
        'zyk': zyk,
        'buy_count': buy_count,
        'sz': sz_count,
        'xd': xd_count
    })
    print('卖出数量', buy_count, '上涨', sz_count, '下跌', xd_count, '盈利',
          (zdf_count / buy_count).quantize(Decimal('0.01'), ROUND_HALF_UP),
          '可用余额', commobj.balance, '持仓市值', market_value, '总资产', zc, '总盈亏', zyk)
    return True

def backtest_start(commobj, start_date: datetime.datetime, end_date: datetime.datetime):
    """
    回测
    """
    rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
    rdchicang.del_db()
    rddaysell = redisRW.redisrw(redisRW.db_day_sell)
    rddaysell.del_db()
    # 日线回测
    commobj.testbar = True
    zbstrategy = zbStrategy.Strategy(None)
    while start_date.date() <= end_date.date():
        if start_date.weekday() in range(5):
            # 选股
            zbstrategy.stock_select(rdchicang, start_date)
            get_ticks_from_xg_and_start_backtest(commobj, start_date)
            #input('按任意键继续...')
        start_date += datetime.timedelta(days=1)
    ex_buy_count = 0
    day_sj_zdf_count = Decimal(0)
    ex_zdf_count = Decimal(0)
    sz_count = 0
    xd_count = 0
    ex_sz_count = 0
    ex_xd_count = 0
    datas = []
    max_zyk = None
    max_huice = None
    for d in rddaysell.read_l_date_dec_json('daysell', 0, -1):
        ex_buy_count += d['buy_count']
        ex_sz_count += d['sz']
        ex_xd_count += d['xd']
        zdf = d['sj_zdf_count']
        if (max_zyk is None) or d['zyk'] > max_zyk:
            max_zyk = d['zyk']
        huice = d['zyk'] - max_zyk
        if (max_huice is None) or huice < max_huice:
            max_huice = huice
        if zdf > 0:
            sz_count += 1
        else:
            xd_count += 1
        day_sj_zdf_count += zdf
        ex_zdf_count += d['ex_zdf_count']
        datas.append({
            'datetime': d['datetime'],
            'ex_buy_count': ex_buy_count,
            'ex_zdf_count': float(str(ex_zdf_count.quantize(Decimal('0.01'), ROUND_HALF_UP))),
            'day_sj_zdf_count': float(str(day_sj_zdf_count.quantize(Decimal('0.01'), ROUND_HALF_UP))),
            'zyk': float(str(d['zyk'].quantize(Decimal('0.01'), ROUND_HALF_UP))),
            'day_sz': sz_count,
            'day_xd': xd_count,
            'ex_sz_count': ex_sz_count,
            'ex_xd_count': ex_xd_count
        })
    ply.write_html_tol('./WebServer/html/charts.html', datas, max_huice)
    #input('回测完成，按任意键继续...')

def start_quotation_process(commobj, back_test_date: datetime.datetime=None, process_count=3):
    # 交易时间不允许回放行情
    if commobj.is_backtest and comm.is_trade_time():
        return
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
    redisRW.redisrw(redisRW.db_realtime_tick).del_db()
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
            p = Process(target=c_ths_tdx, args=(commobj, addrs_list_info, b))
            p_list.append(p)
            p.start()
    else:
        # 启动回测行情模拟进程
        for b in bk_data_list:
            p = Process(target=c_ths_back_test, args=(commobj, back_test_date, b))
            p_list.append(p)
            p.start()
    print('行情服务已启动，选股数量', len(xg_data_list))
    for p in p_list:
        p.join()
    print('行情服务结束。')

if __name__ == "__main__":
    pass
