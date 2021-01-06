import requests
import json
import datetime
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}

def _eastmoney_ann_detail(url):
    r = requests.get(url, headers=headers, timeout=3)
    if r.status_code == 200:
        text = r.text
        flag = 'id="notice_content"'
        i = text.find(flag)
        text = text[i:]
        i = text.find('</div>')
        text = text[0: i]
        if text.find('实施完毕') > -1:
            return True

def eastmoney_jianchi(code, date):
    i = 0
    while True:
        i += 1
        if i > 3:
            print(code, '访问错误。')
            return
        try:
            r = requests.get('http://data.eastmoney.com/notices/stock/{}.html'.format(code), headers=headers, timeout=3)
            break
        except:
            time.sleep(1)
    if r.status_code == 200:
        text = r.text
        flag = 'var dataObj = '
        i = text.find(flag)
        text = text[i + len(flag):]
        i = text.find('};')
        text = text[:i + 1]
        js = json.loads(text)
        for ann in js['data']:
            notice_date = datetime.datetime.strptime(ann['notice_date'], '%Y-%m-%d %H:%M:%S')
            art_code = ann['art_code']
            title = ann['title']
            if title.find('减持') > -1 and \
                    title.find('不减持') < 0 and \
                    title.find('届满') < 0 and \
                    title.find('结果') < 0 and \
                    title.find('完毕') < 0 and \
                    title.find('完成') < 0 and \
                    title.find('终止') < 0:
                url = 'http://data.eastmoney.com/notices/detail/{}/{}.html'.format(code, art_code)
                if (date - notice_date).days < 180:
                    #print(notice_date, title, url)
                    return True

