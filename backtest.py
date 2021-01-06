#! /usr/bin/python3
from QuotationServer import runQuotation
import datetime

def run(commobj, start_date, end_date):
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except:
        return
    runQuotation.backtest_start(commobj, start_date, end_date)

if __name__ == '__main__':
    pass

