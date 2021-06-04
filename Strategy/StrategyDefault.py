from QuotationServer import comm
from QuotationServer import dataTdx
import redisRW

from decimal import *
import datetime
import time
import math
from multiprocessing import Process

class Strategy:
    """
    默认策略
    """
    def __init__(self, common_):
        self.common = common_

    def buy_strategy(self, data_list):
        """
        买入策略
        返回 {} 类型，可携带自定义数据，空表示不买入，买入 cangwei, cc_max 字段必须加上，携带数据全部加入 chicang 对象
        """
        # 已经持仓不买入
        chicang = data_list[0]['chicang']
        if chicang:
            return
        # 涨跌幅大于3不买入
        if data_list[0]['zdf'] > 3:
            return
        # cc_max 最大持仓数
        r_data = {'cc_max': 100, 'cangwei': Decimal('10000')}
        return r_data

    def sell_strategy(self, data_list):
        # k线，第二个是收盘价
        if (not self.common['ticktest']) and len(data_list) < 2:
            return
        chicang = data_list[0]['chicang']
        trade_date = data_list[0]['datetime']
        # T + 1
        days = (trade_date.date() - chicang['datetime'].date()).days
        if days < 1:
            return
        yl = (data_list[0]['price'] / chicang['price'] - 1) * 100
        if yl > 2 or yl < -1:
            return True

    def _stock_select(self, is_backtest, codes_info, date: datetime = None):
        """
        选股
        date 从指定日期开始选股，不指定则为最新
        """
        # 分析的历史根数
        count_week = 1
        count = 2
        count_short = 15
        rdkline = redisRW.redisrw(redisRW.db_kline)
        rdfinance = redisRW.redisrw(redisRW.db_finance)
        rdxg = redisRW.redisrw(redisRW.db_xg)
        rdindex = redisRW.redisrw(redisRW.db_index)
        if is_backtest:
            rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
        else:
            rdchicang = redisRW.redisrw(redisRW.db_chicang)
        for d in codes_info:
            code = d['code']
            if date is not None:
                klines = rdkline.read_klines_from_before_date_count_dec(code, date, count)
            else:
                klines = rdkline.read_klines_from_count_dec(code, count)
            # 持仓
            cc_data = rdchicang.read_dec(d['code'])
            if cc_data:
                # 重设价格
                #price = rdkline.read_klines_from_date_dec(code, datetime.datetime.strptime(cc_data['chicang']['datetime'], '%Y%m%d %H:%M:%S'))[0]['open']
                #cc_data['chicang']['price'] = price
                # 更新市值
                cc_data['chicang']['marketValue'] = comm.sell_money_from_tol(code, klines[0]['close'], cc_data['chicang']['tol'])
                rdchicang.delete(d['code'])
                rdchicang.write_json(d['code'], cc_data)
                continue
            if len(klines) == 0:
                continue
            tj = (klines[0]['dif_c_dea'] == 1 and
                 klines[0]['ma_5'] > klines[1]['ma_5'])
            if not tj:
                continue
            r_data = comm.xg_data(code, d['name'])
            if not rdxg.write_json(code, r_data):
                print(code, '选股数据写入错误。')

    def stock_select(self, is_backtest, codes_bk, date: datetime = None):
        rdxg = redisRW.redisrw(redisRW.db_xg)
        rdxg.del_db()
        p_list = []
        for b in codes_bk:
            p = Process(target=self._stock_select, args=(is_backtest, b, date))
            p_list.append(p)
            p.start()
        tm = datetime.datetime.now()
        print('正在选股...')
        for p in p_list:
            p.join()
        if is_backtest:
            rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
        else:
            rdchicang = redisRW.redisrw(redisRW.db_chicang)
        # 持仓
        for d in rdchicang.read_all_dec():
            rdxg.write_json(d['code'], d)
        print(datetime.datetime.now() - tm)
        print('被选股票', len(rdxg.read_codes()), '其中持仓', len(rdchicang.read_codes()))
