import redisRW

import os
import shutil
import json

class TickFile:
    def __init__(self):
        current_path = os.path.dirname(__file__)
        self.dir = os.path.join(current_path, 'ticks')
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def _check_code_to_filename(self, code):
        try:
            ts = int(code)
            code = str(ts)
            return os.path.join(self.dir, code)
        except:
            pass
        return ''

    def write(self, code, tick):
        data_str = json.dumps(tick, cls=redisRW.DecEncoder)
        with open(os.path.join(self.dir, code), mode='a') as f:
            f.write(data_str)
            f.write('\n')
        return data_str

    def read(self, code, index):
        result = []
        i = 0
        fname = self._check_code_to_filename(code)
        if os.path.exists(fname):
            with open(fname, mode='r') as f:
                for line in f.read().splitlines():
                    if i < index:
                        continue
                    result.append(line)
                    i += 1
        return result

    def delete(self, code):
        fname = self._check_code_to_filename(code)
        if os.path.exists(fname):
            os.remove(fname)

    def clear(self):
        shutil.rmtree(self.dir)
        os.makedirs(self.dir)