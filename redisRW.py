import redis
import json
import datetime
from decimal import *

db_kline = 0
db_realtime_tick = 1
db_backtest_tick = 2
db_mainquotaion = 3
db_baseinfo = 4
db_hangye = 5
db_finance = 6
db_xg = 7
db_chicang = 8
db_sell = 9
db_adjust_factor = 10
db_info = 11
db_index = 12
db_kline_week = 13
db_backtest_chicang = 14
db_day_sell = 15

class DecEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y%m%d %H:%M:%S')
        elif isinstance(obj, Decimal):
            return float(obj.quantize(Decimal('0.01'), ROUND_HALF_UP))
        else:
            return json.JSONEncoder.default(self, obj)

class redisrw:
    def __init__(self, db):
        self.client = redis.StrictRedis(host='127.0.0.1', port=6379, db=db, decode_responses=True)

    def read_codes(self):
        return self.client.keys()

    def write_str(self, code, str_data):
        """
        写字符串
        """
        return self.client.set(code, str_data)

    def write_json(self, code, d_json):
        """
        写入单个json数据
        """
        return self.client.set(code, json.dumps(d_json, cls=DecEncoder))

    def read_str(self, code):
        """
        读取字符串，没有返回None
        """
        return self.client.get(code)

    def read_dec(self, code):
        """
        读取单个数据，返回dec的json，没有返回None
        """
        d = self.client.get(code)
        if d is None:
            return d
        d = json.loads(d, parse_float=Decimal)
        return d

    def read_dec_datetime(self, key):
        """
        返回json对象并将datetime字段转化为datetime类型，没有返回None
        :param code:
        :return:
        """
        d = self.client.get(key)
        if d is None:
            return d
        d = json.loads(d, parse_float=Decimal)
        d['datetime'] = datetime.datetime.strptime(d['datetime'], '%Y%m%d %H:%M:%S')
        return d

    def read_all(self):
        """
        读取全部数据，返回的是字符串数组，没有返回空数组[]
        :return:
        """
        result = []
        for k in self.client.keys():
            d = self.client.get(k)
            if d is not None:
                result.append(d)
        return result

    def read_all_dec(self):
        """
        读取全部数据，返回数组，没有返回空数组[]
        """
        result = []
        for k in self.client.keys():
            d = self.read_dec(k)
            if d is not None:
                result.append(d)
        return result

    def wirte_l_datas(self, code, dict_list):
        """
        写入数组，在原数组的后面添加，返回写入后的总数组长度
        datas 必须是一个dict列表 [{},{}]
        """
        count = 0
        for d in dict_list:
            v = json.dumps(d, cls=DecEncoder)
            count = self.client.rpush(code, v)
        return count

    def wirte_l_data(self, code, dict_data):
        """
        在原列表添加一条数据，dict类型，返回dict转换的字符串数据
        """
        d_json = json.dumps(dict_data, cls=DecEncoder)
        self.client.rpush(code, d_json)
        return d_json

    def read_l_str(self, code, start, end):
        """
        读取指定索引数据，返回的是字符串数组，没有返回空数组[]，end -1 表示最后
        """
        return self.client.lrange(code, start, end)

    def read_l_dec(self, code, start, end):
        """
        读取列表数据，返回的是dict数组，float数据会转换为Decimal，没有返回空数组[]
        """
        result = []
        v = self.client.lrange(code, start, end)
        for d in v:
            d_json = json.loads(d, parse_float=Decimal)
            result.append(d_json)
        return result

    def read_l_date_dec_json(self, code, start, end):
        """
        读取列表数据，返回的是dict数组，float数据会转换为Decimal，datetime会转为日期，没有返回空数组[]
        """
        result = []
        v = self.client.lrange(code, start, end)
        for d in v:
            d_json = json.loads(d, parse_float=Decimal)
            d_json['datetime'] = datetime.datetime.strptime(d_json['datetime'], '%Y%m%d %H:%M:%S')
            result.append(d_json)
        return result

    def get_adjust_factor(self, code, date: datetime.datetime):
        """
        获取复权因子
        :param code:
        :param date:
        :return:
        """
        for i in range(self.client.llen(code)):
            v = self.client.lindex(code, i)
            v_json = json.loads(v, parse_float=Decimal)
            if datetime.datetime.strptime(v_json['datetime'], '%Y%m%d').date() == date.date():
                return v_json['factor']

    def read_klines_from_before_date_count_dec(self, code, date: datetime.datetime, count):
        """
        读取指定日期之前的N个k线，不包含指定日期，没有返回空数组[]
        """
        result = []
        add_count = 0
        list_count = self.client.llen(code)
        for i in range(list_count):
            v = self.client.lindex(code, i)
            v_json = json.loads(v, parse_float=Decimal)
            if datetime.datetime.strptime(v_json['datetime'], '%Y%m%d').date() < date.date():
                result.append(v_json)
                add_count += 1
                if add_count == count:
                    break
        return result

    def read_klines_from_start_end_date_dec(self, code, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        读取开始日期到结束之间的k线，包含开始日期，但不包含结束日期，没有返回空数组[]
        """
        result = []
        list_count = self.client.llen(code)
        for i in range(list_count):
            v = self.client.lindex(code, i)
            v_json = json.loads(v, parse_float=Decimal)
            v_json['datetime'] = datetime.datetime.strptime(v_json['datetime'], '%Y%m%d')
            if end_date.date() > v_json['datetime'].date() >= start_date.date():
                result.append(v_json)
        return result

    def read_klines_from_date_dec(self, code, date: datetime.datetime):
        """
        获取指定日期的k线，没有返回[]
        :param code:
        :param date:
        :return:
        """
        result = []
        list_count = self.client.llen(code)
        for i in range(list_count):
            v = self.client.lindex(code, i)
            v_json = json.loads(v, parse_float=Decimal)
            v_json['datetime'] = datetime.datetime.strptime(v_json['datetime'], '%Y%m%d')
            if date.date() == v_json['datetime'].date():
                result.append(v_json)
                break
        return result

    def read_klines_from_count_dec(self, code, count):
        """
        读取指定个k线，没有返回空数组[]
        """
        result = []
        if count <= 0:
            raise Exception('参数错误。')
        v = self.client.lrange(code, 0, count - 1)
        for k in v:
            k_json = json.loads(k, parse_float=Decimal)
            result.append(k_json)
        return result

    def delete(self, code):
        return self.client.delete(code)

    def del_db(self):
        return self.client.flushdb()
