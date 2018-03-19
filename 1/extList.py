# -*- coding: utf-8 -*-
#
""" 扩展列表
"""

from gevent import monkey
monkey.patch_all()
import gevent
import gevent.pool
try:
    from gevent.coros import BoundedSemaphore
except:
    from gevent.lock import BoundedSemaphore

import sys
import time
import random
import traceback
from libs.core.log import getLogger
from libs.core.utils import syncGeventLock
from libs.core._signal import initGeventSignal

# 日志
log = getLogger("TEST")
#设定对共享资源的访问数量
sem = BoundedSemaphore(1)
signal_stop = False

class StatList(list):

    @syncGeventLock(sem)
    def appends(self, ident, cid, count=1, points=1):
        T = time.strftime("%Y-%m-%d")
        for stat in self:
            if stat["date"] == T and stat["ident"] == ident and stat["cid"] == cid:
                stat["count_send"] += count
                stat["points"] += points
                log.info('-----1------:{}'.format(stat))
                break
        else:
            stat = {"date": T, "ident": ident, "cid": cid, "count_send": count, "points": points,}
            self.append(stat)
            log.info('-----2------:{}'.format(stat))

    @syncGeventLock(sem)
    def pops(self):
        while self:
            d = self.pop()
            log.info('-----3------:{}'.format(d))
        log.info(self)

SL = StatList()

def lappend():
    idents = ["aa", "bb", "cc"]
    cids = ["12", "13", "14"]
    while True:
        if signal_stop: break
        SL.appends(random.choice(idents), random.choice(cids))
        gevent.sleep(1)

def lpop():
    while True:
        if signal_stop: break
        SL.pops()
        gevent.sleep(30)

######################################################
# 信号量处理
def signalHandle(mode):
    log.info(u"catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

# 结束
def finish():
    log.info('finish...')
    SL.pops()

######################################################
def main():
    gevent.joinall([
        gevent.spawn(lappend),
        gevent.spawn(lpop),
    ])

if __name__ == '__main__':
    log.info("program start...")
    initGeventSignal(signalHandle)
    EXIT_CODE = 0
    try:
        main()
    except KeyboardInterrupt:
        signalHandle('sigint')
    except:
        log.error(traceback.format_exc())
        EXIT_CODE = 1
    finally:
        finish()
    log.info("program quit...")
    sys.exit(EXIT_CODE)
