'''
@Author: John
@Date: 2020-03-04 15:19:27
@LastEditors: John
@LastEditTime: 2020-03-04 15:37:47
@Description: 
'''

import multiprocessing
import multiprocessing.pool


class DaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return True

    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


class DaemonProcessPool(multiprocessing.pool.Pool):
    Process = DaemonProcess
