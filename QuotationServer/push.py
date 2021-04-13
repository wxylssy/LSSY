from QuotationServer import zbBase
from QuotationServer import zbStrategy
import redisRW
import tickFile

from decimal import *
import datetime

class Push:
    def __init__(self, common, xg_data):
        self.ticks = []
        self.xg_data = {}
        for k in xg_data.keys():
            if k != 'kline':
                self.xg_data[k] = xg_data[k]
        self.code = xg_data['code']
        if self.xg_data['chicang']:
            self.xg_data['chicang']['datetime'] = datetime.datetime.strptime(self.xg_data['chicang']['datetime'], '%Y%m%d %H:%M:%S')
        self.common = common
        self.strategy = zbStrategy.Strategy(common)
        self.tickfile = tickFile.TickFile()
        self.rdmainquotation = redisRW.redisrw(redisRW.db_mainquotaion)
        self.history_data = zbBase.history_calculate_by_kline(xg_data)

    def push_tick(self, tick):
        if len(self.ticks) > 40:
            self.ticks.pop()
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
        for k in self.xg_data.keys():
            self.ticks[0][k] = self.xg_data[k]
        self.strategy.entry(self.ticks, 'catch_zt')
        tick = self.tickfile.write(self.code, self.ticks[0])
        self.rdmainquotation.write_str(self.code, tick)
