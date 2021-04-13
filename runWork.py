#! /usr/bin/python3
from QuotationServer import historyQuotation
from QuotationServer import comm
from QuotationServer import runQuotation
from QuotationServer import zbStrategy
from WebServer import runWeb
import redisRW
import backtest
import httpTrade

from multiprocessing import Process, Queue, Manager, Lock
import time
import datetime
from dateutil.relativedelta import relativedelta
import sys
from decimal import *

fupaned = False

def update(rdinfo, date: datetime.datetime):
    #return False
    # 3年历史数据
    back_y = 3
    historyQuotation.get_all_clear_finance_qfq_kline_from_start_date(date - relativedelta(years=back_y))
    rdinfo.write_json('update', {'datetime': date})
    print(date, '数据更新完毕。')
    global fupaned
    fupaned = False
    fupan()

def fupan():
    global fupaned
    if fupaned:
        return False
    fupaned = True
    codes_bk = comm.get_codes_bk()
    # 选股
    zbstrategy = zbStrategy.Strategy(None)
    m = Manager()
    common = m.dict()
    common['lock'] = m.Lock()
    common['b'] = True
    common['ticktest'] = False
    common['balance'] = Decimal('1')
    common['init_balance'] = common['balance']
    zbstrategy.stock_select(False, codes_bk)
    tk_date = datetime.datetime.now()
    # 获取最新一天的ticks，并启动回测
    getticks = runQuotation.get_ticks_from_xg_and_start_backtest(common, tk_date)
    while not getticks:
        print(tk_date, '没有ticks，尝试前一天。')
        tk_date -= datetime.timedelta(days=1)
        getticks = runQuotation.get_ticks_from_xg_and_start_backtest(common, tk_date)
    print('策略提示', '将买入标记重点的股票。')
    
    return True

def start_loop(common, queue):
    # 更新时间
    hour = 17
    rdinfo = redisRW.redisrw(redisRW.db_info)
    while True:
        # 上次入库时间
        update_time = rdinfo.read_dec_datetime('update')
        now_date = datetime.datetime.now()
        if update_time is not None:
            last_up_date = update_time['datetime']
            diff_days = (now_date.date() - last_up_date.date()).days
            if diff_days > 1 or (diff_days == 1 and last_up_date.hour < hour):
                last_up_date = now_date
                update(rdinfo, last_up_date)
        else:
            last_up_date = now_date
            update(rdinfo, last_up_date)
        if now_date.hour >= hour:
            # 只有在今天指定时间更新才有效
            if last_up_date.date() < now_date.date() or last_up_date.hour < hour:
                last_up_date = now_date
                update(rdinfo, last_up_date)
        if comm.is_trade_time() and (not common['b']):
            # 清空数据
            redisRW.redisrw(redisRW.db_backtest_chicang).del_db()
            redisRW.redisrw(redisRW.db_sell).del_db()
            runQuotation.start_quotation_process(common)
        else:
            if queue.full():
                if queue.get() == 0:
                    backtest.run(common, queue.get(), queue.get())
                else:
                    queue.get()
                    queue.get()
                    fupan()
        time.sleep(3)

def main():
    m = Manager()
    common = m.dict()
    common['lock'] = m.Lock()
    common['ticktest'] = False
    queue = Queue(3)
    if len(sys.argv) > 1 and sys.argv[1] == 'b':
        common['b'] = True
        common['balance'] = Decimal('1000000')
        print('进入回测系统。可用资金：', common['balance'])
    else:
        common['b'] = False
        common['balance'] = Decimal(httpTrade.get_ky_balance())
        print('进入实盘系统。可用资金：', common['balance'])
    common['init_balance'] = common['balance']
    Process(target=runWeb.main, args=(common, queue)).start()
    start_loop(common, queue)

if __name__ == "__main__":
    main()
