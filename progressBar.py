import sys
import datetime

class progressbar:
    def start(self, title, total):
        self.total = float(total)
        self.start_time = datetime.datetime.now()
        self.bar_len = 30
        self.cur_count = 0
        self.title = title

    def progress(self):
        self.cur_count += 1
        b = self.cur_count / self.total
        filled_len = int(self.bar_len * b)
        more_len = self.bar_len - filled_len
        percents = round(100.0 * b, 1)
        bar = '>' * filled_len + '.' * more_len
        # 已用时间
        lost_time = datetime.datetime.now() - self.start_time
        # 剩余时间
        more_time = datetime.timedelta(seconds=lost_time.total_seconds() / self.cur_count * (self.total - self.cur_count))
        sys.stdout.write('[%s] %s%s %s 剩余时间：%s\r' % (bar, percents, '%', self.title, more_time))
        sys.stdout.flush()
        if self.cur_count == self.total:
            sys.stdout.write('[%s] %s%s %s 用时：%s\n' % (bar, percents, '%', self.title, lost_time))

    def out_text(self, *args):
        sys.stdout.write('\n')
        print(*args)



