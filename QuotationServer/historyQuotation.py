from QuotationServer import dataTdx
from QuotationServer import zbKline
from QuotationServer import dataBaostock
from QuotationServer import dataAkshare
from QuotationServer import comm
import progressBar
import redisRW

import datetime
import time
import json

def count_cg(data_list):
    tol = 0
    for d in data_list:
        tol += d['持股数量']
    return tol

def _get_baseinfo(code):
    time.sleep(3)
    jgcg = dataAkshare.jigou_cg(code, '20201')
    time.sleep(3)
    jijincg = dataAkshare.jijin_cg(code)
    time.sleep(3)
    ltgd = dataAkshare.liutong_gudong(code)
    result = []
    result.append({'name': '机构持股', 'value': count_cg(jgcg)})
    result.append({'name': '基金持股', 'value': count_cg(jijincg)})
    result.append({'name': '流通股东', 'value': count_cg(ltgd)})
    return result

def _get_sz_index_kline(start_date: datetime.date):
    rdindex = redisRW.redisrw(redisRW.db_index)
    rdindex.delete(comm.index_sz_code)
    klines = dataBaostock.get_kline_index_from_start_date(comm.index_sz_code, start_date)
    k_len = len(klines)
    if k_len == 0:
        raise Exception('指数K线获取错误。')
    # 计算
    zbKline.klines_calculate(comm.index_sz_code, klines)
    if k_len != rdindex.wirte_l_datas(comm.index_sz_code, klines):
        raise Exception('指数K线存储错误。')

def get_all_clear_finance_qfq_kline_from_start_date(start_date: datetime.date):
    rdkline = redisRW.redisrw(redisRW.db_kline)
    rdkline_week = redisRW.redisrw(redisRW.db_kline_week)
    rdbaseinfo = redisRW.redisrw(redisRW.db_baseinfo)
    rdhangye = redisRW.redisrw(redisRW.db_hangye)
    rdfinance = redisRW.redisrw(redisRW.db_finance)
    # 清空数据
    rdkline.del_db()
    rdkline_week.del_db()
    # 3年的财务信息
    cw_start_year = datetime.datetime.now().year - 3
    # 获取指数
    _get_sz_index_kline(start_date)
    # 实例化通达信对象
    tdx = dataTdx.DataTdx()
    tdx.select_fast_addr()
    # 没有行业信息则更新
    if len(rdhangye.read_codes()) == 0:
        hy = dataBaostock.get_hangye()
        for h in hy:
            rdhangye.write_json(h['code'], h)
    # 读取市场股票
    codes_info = tdx.get_szsh_a_codes()
    bar = progressBar.progressbar()
    bar.start('存储%s至今历史数据' % start_date.strftime('%Y%m%d'), len(codes_info))
    for d in codes_info:
        bar.progress()
        code = d['code']
        if comm.is_kzz(code):
            klines = tdx.get_kline_from_count(code, 800)
            none_klines = tdx.get_kline_from_count(code, 800)
            k_len = len(klines)
            if k_len == 0:
                bar.out_text(code, '没有K线数据。')
                continue
            # 复权因子
            dataBaostock.qfq_adjust_factor(none_klines, klines)
            zbKline.klines_calculate(code, klines)
            if k_len != rdkline.wirte_l_datas(code, klines):
                bar.out_text(code, '历史K线数据存储错误。')
                continue
            continue
        # 前复权k线
        klines = dataBaostock.get_kline_from_start_date(code, start_date)
        # 不复权k线
        none_klines = dataBaostock.get_kline_from_start_date(code, start_date, adjustflag='3')
        #klines = akshareData.get_kline(code, start_date)
        k_len = len(klines)
        if k_len == 0:
            bar.out_text(code, '没有K线数据。')
            continue
        # 复权因子
        dataBaostock.qfq_adjust_factor(none_klines, klines)
        # 前复权周k线
        klines_week = dataBaostock.get_kline_from_start_date(code, start_date, frequency='w')
        # 计算
        zbKline.klines_calculate(code, klines_week)
        zbKline.klines_calculate(code, klines)
        if k_len != rdkline.wirte_l_datas(code, klines) or \
            len(klines_week) != rdkline_week.wirte_l_datas(code, klines_week):
            bar.out_text(code, '历史K线数据存储错误。')
            continue
        # 没有财务数据则更新
        if rdfinance.read_str(code) is None:
            # 财务信息
            finance_data = {'code': code,
                            'profit': dataBaostock.get_profit_from_start_year(code, cw_start_year),
                            'balance': dataBaostock.get_balance_from_start_year(code, cw_start_year),
                            'cash_flow': dataBaostock.get_cash_flow_from_start_year(code, cw_start_year),
                            'growth': dataBaostock.get_growth_from_start_year(code, cw_start_year),
                            'operation': dataBaostock.get_operation_from_start_year(code, cw_start_year)
                            }
            if not rdfinance.write_json(code, finance_data):
                bar.out_text(code, '财务信息存储错误。')
        # 没有基本信息则更新
        if len(rdbaseinfo.read_l_str(code, 0, 0)) == 0:
            rdbaseinfo.wirte_l_datas(code, _get_baseinfo(code))
            gbchg = tdx.get_liutong(code)
            rdbaseinfo.wirte_l_data(code, {'name': '流通股本', 'value': gbchg[0]['liutong'] * 10000})
