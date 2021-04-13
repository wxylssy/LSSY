#! /usr/bin/python3
from QuotationServer import runQuotation
from QuotationServer import comm
import redisRW

import sys
import datetime
from decimal import *

def run(common, start_date, end_date):
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except:
        print('日期格式错误')
        return
    runQuotation.backtest_start(common, start_date, end_date)

if __name__ == '__main__':
    pass

