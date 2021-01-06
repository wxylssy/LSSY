#! /usr/bin/python3
from QuotationServer import historyQuotation
from QuotationServer import comm
from QuotationServer import runQuotation
from QuotationServer import zbStrategy
from WebServer import runWeb
import redisRW
import rpcTrade

from multiprocessing import Process
import time
import datetime
from dateutil.relativedelta import relativedelta
import sys
from decimal import *

commobj = None

def update(rdinfo, date: datetime.datetime):
    # 3年历史数据
    back_y = 3
    historyQuotation.get_all_clear_finance_qfq_kline_from_start_date(date - relativedelta(years=back_y))
    rdinfo.write_json('update', {'datetime': date})
    print(date, '数据更新完毕，请进行今日复盘。')

def fupan():
    # 选股
    zbstrategy = zbStrategy.Strategy(None)
    zbstrategy.stock_select(redisRW.redisrw(redisRW.db_chicang))
    tk_date = datetime.datetime.now()
    # 获取最新一天的ticks，并启动回测
    commobj = comm.commObj(redisRW.redisrw(redisRW.db_backtest_chicang), 1, is_backtest=True)
    getticks = runQuotation.get_ticks_from_xg_and_start_backtest(commobj, tk_date)
    while not getticks:
        print(tk_date, '没有ticks，尝试前一天。')
        tk_date -= datetime.timedelta(days=1)
        getticks = runQuotation.get_ticks_from_xg_and_start_backtest(commobj, tk_date)
    print('策略提示', '将买入标记重点的股票。')
    return True

def start_loop():
    # 更新时间
    hour = 18
    rdinfo = redisRW.redisrw(redisRW.db_info)
    # 上次入库时间
    update_time = rdinfo.read_dec_datetime('update')
    if update_time is not None:
        last_up_date = update_time['datetime']
        now_date = datetime.datetime.now()
        diff_days = (now_date.date() - last_up_date.date()).days
        if diff_days > 1 or (diff_days == 1 and last_up_date.hour < hour):
            last_up_date = now_date
            update(rdinfo, last_up_date)
    else:
        last_up_date = datetime.datetime.now()
        update(rdinfo, last_up_date)
    while True:
        now_date = datetime.datetime.now()
        if now_date.hour >= hour:
            # 只有在今天指定时间更新才有效
            if last_up_date.date() < now_date.date() or last_up_date.hour < hour:
                last_up_date = now_date
                update(rdinfo, last_up_date)
        if comm.is_trade_time():
            global commobj
            print('登陆交易终端', rpcTrade.login())
            # 清空数据
            redisRW.redisrw(redisRW.db_backtest_chicang).del_db()
            redisRW.redisrw(redisRW.db_sell).del_db()
            runQuotation.start_quotation_process(commobj)
            print('结束交易终端', rpcTrade.kill())
        time.sleep(5)

def main():
    global commobj
    if len(sys.argv) > 1 and sys.argv[1] == 'b':
        commobj = comm.commObj(redisRW.redisrw(redisRW.db_backtest_chicang), Decimal('1000000'), is_backtest=True)
        print('进入回测系统。可用资金：', commobj.balance)
    else:
        commobj = comm.commObj(redisRW.redisrw(redisRW.db_chicang), Decimal(rpcTrade.get_ky_balance()),
                               is_backtest=False)
        print('进入实盘系统。可用资金：', commobj.balance)
    Process(target=runWeb.main, args=(commobj, )).start()
    start_loop()

if __name__ == "__main__":
    main()
