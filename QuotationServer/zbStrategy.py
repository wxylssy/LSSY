from QuotationServer import zbStrategyMACD
from QuotationServer import comm
import rpcTrade
import redisRW

from decimal import *
import datetime
import time
import threading

class Strategy:
    def __init__(self, commobj):
        self.commobj = commobj
        # 具体策略类
        self.strategy = zbStrategyMACD.StrategyMACD(commobj)

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
            if self.strategy.sell_strategy(chicang, data_list):
                # 卖出
                if not self.commobj.is_backtest:
                    threading.Thread(target=self.sell, args=(data_list[0],)).start()
                else:
                    self.sell(data_list[0])
            return
        if self.strategy.buy_strategy(data_list, new_key):
            # 买入
            if not self.commobj.is_backtest:
                threading.Thread(target=self.buy, args=(data_list[0],)).start()
            else:
                self.buy(data_list[0])

    def stock_select(self, rdchicang, date: datetime.datetime = None):
        self.strategy.stock_select(rdchicang, date)

    def buy(self, tick):
        if not self.commobj.lock.acquire(timeout=0.1):
            return False
        try:
            cc_tol = 0
            cc_amount = Decimal(0)
            cc_price = Decimal(0)
            code = tick['code']
            tick_chicang = tick['chicang']
            price = tick['price']
            trade_date = tick['datetime']
            if redisRW.redisrw(redisRW.db_sell).read_str(code):
                return
            # 限定持仓数量
            # if len(self.commobj.rdchicang.read_codes()) >= 1:
            #    return False
            cangwei = '10000'
            """elif cc_tol == 1:
                cangwei = '0.6'
            elif cc_tol == 2:
                cangwei = '0.9'"""
            buy_tol = comm.buy_tol_from_money(code, self.commobj.balance, price, cangwei)
            if buy_tol is None:
                # print('余额不足。。')
                return False
            if not self.commobj.is_backtest:
                ht_bh = rpcTrade.buy(code, tick['name'], str(price), buy_tol)
                print('买入合同编号：', ht_bh)
                if ht_bh:
                    tm = datetime.datetime.now()
                    e = False
                    while not cc_tol == buy_tol:
                        time.sleep(0.5)
                        if (datetime.datetime.now() - tm).total_seconds() > 10:
                            # 撤单
                            rpcTrade.cancel_oder_all()
                            time.sleep(6)
                            e = True
                        cj_list = rpcTrade.get_chengjiao(ht_bh)
                        if cj_list:
                            cc_tol = 0
                            cc_amount = Decimal(0)
                            cc_price = Decimal(0)
                            for cj in cj_list:
                                cc_tol += cj['tol']
                                cc_price += Decimal(str(cj['price']))
                                cc_amount += Decimal(str(cj['amount']))
                            cc_price /= Decimal(len(cj_list))
                        if e:
                            print('已撤')
                            break
                    if cc_tol > 0:
                        print('已成交：', cc_tol, cc_price, cc_amount)
            else:
                cc_price = price
                cc_tol = buy_tol
                cc_amount = comm.sell_money_from_tol(code, cc_price, cc_tol)
            if cc_tol > 0:
                # 可用金额
                self.commobj.balance -= cc_amount + comm.trade_fee(cc_amount)
                chicang = {
                    'code': code,
                    'datetime': trade_date,
                    'price': cc_price,
                    'base_price': tick['price_low'],
                    'r_price': cc_price,
                    'sell_price': 0,
                    'tol': cc_tol,
                    'marketValue': cc_amount,
                    'status': 0
                }
                for k in chicang.keys():
                    tick_chicang[k] = chicang[k]
                r_data = comm.xg_data(code, tick['name'], None, tick['zs_date'], tick['zy_date'], tick['price_zs'], tick['price_zy'], chicang)
                self.commobj.rdchicang.write_json(code, r_data)
                return True
        finally:
            self.commobj.lock.release()

    def sell(self, tick):
        if not self.commobj.lock.acquire(timeout=0.1):
            return False
        cc_tol = 0
        cc_amount = Decimal(0)
        cc_price = Decimal(0)
        try:
            rdsell = redisRW.redisrw(redisRW.db_sell)
            code = tick['code']
            tick_chicang = tick['chicang']
            trade_date = tick['datetime']
            price = tick['price']
            if not self.commobj.is_backtest:
                ht_bh = rpcTrade.sell(code, tick['name'], str(price), tick_chicang['tol'])
                print('卖出合同编号：', ht_bh)
                if ht_bh:
                    tm = datetime.datetime.now()
                    e = False
                    while not cc_tol == tick_chicang['tol']:
                        time.sleep(0.5)
                        if (datetime.datetime.now() - tm).total_seconds() > 30:
                            # 撤单
                            rpcTrade.cancel_oder_all()
                            time.sleep(6)
                            e = True
                        cj_list = rpcTrade.get_chengjiao(ht_bh)
                        if cj_list:
                            cc_tol = 0
                            cc_amount = Decimal(0)
                            cc_price = Decimal(0)
                            for cj in cj_list:
                                cc_tol += cj['tol']
                                cc_price += Decimal(str(cj['price']))
                                cc_amount += Decimal(str(cj['amount']))
                            cc_price /= Decimal(len(cj_list))
                        if e:
                            print('已撤')
                            break
                    if cc_tol > 0:
                        print('已成交：', cc_tol, cc_price, cc_amount)
            else:
                cc_tol = tick_chicang['tol']
                cc_price = price
                cc_amount = comm.sell_money_from_tol(code, cc_price, cc_tol)
            if cc_tol > 0:
                # 可用金额
                self.commobj.balance += cc_amount
                tick_chicang['tol'] -= cc_tol
                if tick_chicang['tol'] == 0:
                    tick_chicang['status'] = 1
                    tick_chicang['sell_price'] = cc_price

                    zdf = (cc_price / tick_chicang['price'] - 1) * 100
                    if not self.commobj.rdchicang.delete(code):
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
            self.commobj.lock.release()
