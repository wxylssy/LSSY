from QuotationServer import comm
from QuotationServer import dataTdx
import redisRW

import datetime
import math
from multiprocessing import Process

class StrategyMACD:
    """
    MACD
    """
    def __init__(self, commobj):
        self.commobj = commobj

    def buy_strategy(self, data_list, new_key):
        if data_list[0]['zdf'] > 3:
            return
        return True

    def sell_strategy(self, chicang, data_list):
        if len(data_list) < 2:
            return
        trade_date = data_list[0]['datetime']
        days = (trade_date.date() - chicang['datetime'].date()).days
        if days < 1:
            return
        return True

    def _xg_hot_p(self, rdchicang, codes_info, date: datetime = None):
        """
        选股-热点股票
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
                price = rdkline.read_klines_from_date_dec(code, datetime.datetime.strptime(cc_data['chicang']['datetime'], '%Y%m%d %H:%M:%S'))[0]['open']
                cc_data['chicang']['price'] = price
                # 更新市值
                cc_data['chicang']['marketValue'] = comm.sell_money_from_tol(code, klines[0]['close'], cc_data['chicang']['tol'])
                rdchicang.delete(d['code'])
                rdchicang.write_json(d['code'], cc_data)
                continue
            if len(klines) == 0:
                continue
            tj = klines[0]['pctChg'] > 0.1 and \
                 klines[0]['ma_5'] > klines[1]['ma_5']
            if not tj:
                continue
            r_data = comm.xg_data(code, d['name'], 0, None, None, None, None)
            if r_data and (rdxg.read_str(code) is None):
                if not rdxg.write_json(code, r_data):
                    print(code, '选股数据写入错误。')

    def stock_select(self, rdchicang, date: datetime = None):
        rdxg = redisRW.redisrw(redisRW.db_xg)
        rdxg.del_db()
        # 实例化通达信对象
        tdx = dataTdx.DataTdx()
        tdx.select_fast_addr()
        # 读取市场股票
        codes_info = tdx.get_szsh_a_codes()
        # 数据分块
        process_count = 4
        bk = math.ceil(len(codes_info) / process_count)
        bk_data_list = []
        temp = []
        p_list = []
        for i in range(len(codes_info)):
            if i > 0 and i % bk == 0:
                bk_data_list.append(temp)
                temp = []
            temp.append(codes_info[i])
        if len(temp) > 0:
            bk_data_list.append(temp)
        for b in bk_data_list:
            p = Process(target=self._xg_hot_p, args=(rdchicang, b, date))
            p_list.append(p)
            p.start()
        tm = datetime.datetime.now()
        print('正在选股...')
        for p in p_list:
            p.join()
        # 只选择3只
        """top_xg = []
        for d in rdxg.read_all_dec():
            top_xg.append(d)
            rdxg.delete(d['code'])
        top_xg = sorted(top_xg, key=lambda x: x['avg_line_zdf'], reverse=False)
        cc_len = len(rdchicang.read_codes())
        i = 0
        for d in top_xg:
            if not rdxg.write_json(d['code'], d):
                print(d['code'], '选股数据写入错误。')
            i += 1
            # 只选择3只
            if i == 3 - cc_len:
                break"""
        # 持仓
        for d in rdchicang.read_all_dec():
            rdxg.write_json(d['code'], d)
        print(datetime.datetime.now() - tm)
        print('被选股票', len(rdxg.read_codes()), '其中持仓', len(rdchicang.read_codes()))
