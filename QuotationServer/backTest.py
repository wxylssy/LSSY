from decimal import Decimal
import datetime
from decimal import *
import time

import redisRW

class BackTest:
    def __init__(self, push, code):
        self.push = push
        self.rdbacktest = redisRW.redisrw(redisRW.db_backtest_tick)
        self.rdmainquotation = redisRW.redisrw(redisRW.db_mainquotaion)
        self.code = code

    def _get_min_time(self):
        """
        获取tick中最小的，便于同步
        :return:
        """
        m = None
        for d in self.rdmainquotation.read_all_dec():
            tm = datetime.datetime.strptime(d['datetime'], '%Y%m%d %H:%M:%S')
            if m is None:
                m = tm
                continue
            if tm < m:
                m = tm
        return m

    def start(self):
        ticks = self.rdbacktest.read_l_date_dec_json(self.code, 0, -1)
        for tk in ticks:
            self.push.push_tick(tk)
            """
            # 超过指定时间不执行同步
            if tk['datetime'].hour > 9:
                continue
            # 同步
            while True:
                time.sleep(0.1)
                min_time = self._get_min_time()
                if (tk['datetime'] - min_time).total_seconds() < 10:
                    break
            """


