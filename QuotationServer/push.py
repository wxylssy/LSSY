from QuotationServer import zbBase
from QuotationServer import zbStrategy
import redisRW

from decimal import *
import datetime

class Push:
    def __init__(self, commObj, xg_data):
        self.ticks = []
        self.xg_data = xg_data
        self.code = xg_data['code']
        self.name = xg_data['name']
        self.hangye = xg_data['hangye']
        self.chicang = xg_data['chicang']
        if self.chicang:
            self.chicang['datetime'] = datetime.datetime.strptime(self.chicang['datetime'], '%Y%m%d %H:%M:%S')
        self.bz = xg_data['bz']
        self.price_zs = xg_data['price_zs']
        self.price_zy = xg_data['price_zy']
        self.zs_date = xg_data['zs_date']
        self.zy_date = xg_data['zy_date']
        self.strategy = zbStrategy.Strategy(commObj)
        self.rdrealtimetick = redisRW.redisrw(redisRW.db_realtime_tick)
        self.rdmainquotation = redisRW.redisrw(redisRW.db_mainquotaion)
        self.history_data = zbBase.history_calculate_by_kline(xg_data)

    def push_tick(self, tick):
        self.ticks.insert(0, tick)
        zbBase.max_all(self.ticks, 'price', 'price_high')
        zbBase.min_all(self.ticks, 'price', 'price_low')
        zbBase.kline(self.ticks, 9)
        zbBase.count_all(self.ticks, 'vol', 'vols')
        zbBase.count_all(self.ticks, 'amount', 'amounts')
        zbBase.count_all(self.ticks, 'num', 'nums')
        zbBase.count_avg(self.ticks, 'vol', 'vol_avg', 20)
        zbBase.count_while(self.ticks, 'amount', 'buy_amounts', 'buyorsell', 0)
        zbBase.count_while(self.ticks, 'amount', 'sell_amounts', 'buyorsell', 1)
        zbBase.bi(self.ticks, 'buy_amounts', 'sell_amounts', 'bi_buy')
        zbBase.count_by_seconds_int(self.ticks, 'num', 'num_60s', 60)
        zbBase.count_by_seconds_dec(self.ticks, 'amount', 'amount_60s', 60)
        zbBase.bi_by_seconds(self.ticks, 'amount_60s', 'bi_amount_60s', 60)
        zbBase.bi_by_seconds(self.ticks, 'num_60s', 'bi_num_60s', 60)
        zbBase.bi_avg_by_seconds(self.ticks, 'amount', 'bi_amount_avg', 60)
        zbBase.open_record(self.ticks, 'datetime', 'datetime_open')
        zbBase.open_record(self.ticks, 'amount', 'amount_open')
        zbBase.open_record(self.ticks, 'price', 'price_open')
        zbBase.qx(self.ticks, 'qx')
        zbBase.merge_history_realtime_tick(self.ticks, self.history_data)
        zbBase.diff(self.ticks, 'zdf', 'zdf_diff')
        zbBase.count_continuity(self.ticks, 'zdf_diff', 'zdf_diff_count')
        zbBase.min_all(self.ticks, 'zdf', 'zdf_low')
        zbBase.speed_by_seconds(self.ticks, 'speed_60s', 60)
        zbBase.max_all(self.ticks, 'speed_60s', 'max_speed_60s')
        zbBase.ap_reversed(self.ticks, 'bi_amount_60s_1', 'amount_reversed')
        zbBase.count_all(self.ticks, 'amount_reversed', 'amount_reversed_total')
        zbBase.count_filter_avg(self.ticks, 'bi_amount_60s_1', 'bi_amount_60s_1_max_total', 'bi_amount_60s_1_max_num', 'bi_amount_60s_1_max_avg', 5)
        zbBase.max_all(self.ticks, 'amount_reversed', 'max_amount_reversed')
        self.ticks[0]['name'] = self.name
        self.ticks[0]['hangye'] = self.hangye
        self.ticks[0]['bz'] = self.bz
        self.ticks[0]['zs_date'] = self.zs_date
        self.ticks[0]['zy_date'] = self.zy_date
        self.ticks[0]['price_zs'] = self.price_zs
        self.ticks[0]['price_zy'] = self.price_zy
        self.ticks[0]['chicang'] = self.chicang
        self.strategy.entry(self.ticks, 'catch_zt')
        tick = self.rdrealtimetick.wirte_l_data(self.code, self.ticks[0])
        self.rdmainquotation.write_str(self.code, tick)
