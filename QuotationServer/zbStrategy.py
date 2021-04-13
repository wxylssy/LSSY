from Strategy import StrategyDefault
from QuotationServer import comm
import httpTrade
import redisRW

from decimal import *
import datetime
import time
import threading

class Strategy:
    def __init__(self, common_):
        self.common = common_
        # 具体策略类
        self.strategy = StrategyDefault.Strategy(common_)

    def entry(self, data_list, new_key):
        """
        策略入口
        :param data_list:
        :param new_key:
        :return:
        """
        if len(data_list) > 1:
            # 取原来的标记
            dict_val = data_list[1][new_key]
            # 已经标记过
            if dict_val:
                data_list[0][new_key] = dict_val
                return
        data_list[0][new_key] = {}
        # 调用的具体策略
        # 持仓
        chicang = data_list[0]['chicang']
        if chicang and chicang['status'] == 0:
            if self.strategy.sell_strategy(data_list):
                # 卖出
                self.sell(data_list[0])
        fg_data = self.strategy.buy_strategy(data_list)
        if fg_data:
            # 买入
            self.buy(data_list[0], fg_data)

    def stock_select(self, is_backtest, codes_bk, date: datetime.datetime = None):
        self.strategy.stock_select(is_backtest, codes_bk, date)

    def buy(self, tick, fg_data):
        if not self.common['lock'].acquire(timeout=0.1):
            return False
        if self.common['b']:
            rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
        else:
            rdchicang = redisRW.redisrw(redisRW.db_chicang)
        try:
            cc_tol = 0
            cc_amount = Decimal(0)
            cc_price = Decimal(0)
            code = tick['code']
            tick_chicang = tick['chicang']
            trade_date = tick['datetime']
            price = tick['price']
            cangwei = fg_data['cangwei']
            cc_max = fg_data['cc_max']
            # 加仓
            cc_data = rdchicang.read_dec(code)
            # 新开仓
            if not cc_data:
                if len(rdchicang.read_codes()) >= cc_max:
                    return False
            buy_tol = comm.buy_tol_from_money(code, self.common['balance'], price, cangwei)
            if buy_tol is None:
                #print('余额不足。')
                return False
            cc_price = price
            cc_tol = buy_tol
            cc_amount = comm.sell_money_from_tol(code, cc_price, cc_tol, False)
            if not self.common['b']:
                r = httpTrade.buy(code, tick['name'], price, buy_tol)
                if r:
                    print('买入下单成功')
            if cc_tol > 0:
                # 可用金额
                self.common['balance'] -= cc_amount
                chicang = {
                    'code': code,
                    'datetime': trade_date,
                    'price': cc_price,
                    'tol': cc_tol,
                    'marketValue': cc_amount,
                    'status': 0
                }
                # 加仓
                if cc_data:
                    c = cc_data['chicang']
                    all_tol = c['tol'] + cc_tol
                    chicang['price'] = ((c['price'] * c['tol'] + cc_tol * cc_price) / all_tol).quantize(Decimal('0.01'), ROUND_HALF_UP)
                    chicang['tol'] = all_tol
                    chicang['marketValue'] = comm.sell_money_from_tol(code, chicang['price'], chicang['tol'], False)
                    if not rdchicang.delete(code):
                        print(code, '删除持仓数据错误。')
                for k in fg_data.keys():
                    if k not in ['cangwei', 'price_buy']:
                        chicang[k] = fg_data[k]
                for k in chicang.keys():
                    tick_chicang[k] = chicang[k]
                r_data = comm.xg_data(code, tick['name'], chicang)
                rdchicang.write_json(code, r_data)
                return True
        finally:
            self.common['lock'].release()

    def sell(self, tick):
        if not self.common['lock'].acquire(timeout=0.1):
            return False
        if self.common['b']:
            rdchicang = redisRW.redisrw(redisRW.db_backtest_chicang)
        else:
            rdchicang = redisRW.redisrw(redisRW.db_chicang)
        cc_tol = 0
        cc_amount = Decimal(0)
        cc_price = Decimal(0)
        try:
            rdsell = redisRW.redisrw(redisRW.db_sell)
            code = tick['code']
            tick_chicang = tick['chicang']
            trade_date = tick['datetime']
            price = tick['price']

            cc_tol = tick_chicang['tol']
            cc_price = price
            cc_amount = comm.sell_money_from_tol(code, cc_price, cc_tol)
            if not self.common['b']:
                r = httpTrade.sell(code, tick['name'], price, tick_chicang['tol'])
                if r:
                    print('卖出下单成功')
            if cc_tol > 0:
                # 可用金额
                self.common['balance'] += cc_amount
                tick_chicang['tol'] -= cc_tol
                if tick_chicang['tol'] == 0:
                    tick_chicang['status'] = 1
                    tick_chicang['sell_price'] = cc_price

                    zdf = (cc_price / tick_chicang['price'] - 1) * 100
                    if not rdchicang.delete(code):
                        print(code, '删除持仓数据错误。')
                    rdsell.write_json(code, {
                        'code': code,
                        'datetime': trade_date,
                        'price': cc_price,
                        'money': cc_amount,
                        'zdf': zdf
                    })
                    return True
        finally:
            self.common['lock'].release()
