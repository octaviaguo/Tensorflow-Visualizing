import sys
from threading import Thread
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
if sys.version_info[0] < 3:
    import Queue
else:
    import queue as Queue


class PyQTWindowWrapper():
    def __init__(self, data_source):
        self.data_source = data_source
        print('11111')
        #print(self.data_source, len(self.data_source.data))
    def update_data(self):
        pass
    def close(self):
        pass
    def get_pos_size(self):
        x = self.win.pos().x()
        y = self.win.pos().y()
        w = self.win.size().width()
        h = self.win.size().height()
        #print(x,y,w,h)
        return (x,y,w,h)
    def set_pos_size(self, x, y, w, h):
        #print("=======================",x,y,w,h)
        self.win.resize(w,h)
        self.win.move(x,y)

class PyQTEnv():
    """
    create QApplication in a different thread from main() thread
    """
    def __init__(self):
        self.cmd_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.MAX_WIN_NUM = 100
        self.win_slots = [None]*self.MAX_WIN_NUM
        self.thread = Thread(target=self.__run, args=())
        self.thread.start()

    def __run(self):
        self.app = QtGui.QApplication([])

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timer_fun)
        self.timer.start(10)

        QtGui.QApplication.instance().exec_()

    def timer_fun(self):
        while self.cmd_queue.empty() is False:
            cmd = self.cmd_queue.get_nowait()
            if cmd[0] == 'run':
                fun = cmd[1]
                args = cmd[2]
                ret = fun(args)
                self.result_queue.put(ret)
            elif cmd[0] == 'create_window':
                new_cls = cmd[2]
                args = cmd[3]
                print("create_window", new_cls)
                self.win_slots[cmd[1]]=new_cls(args)
            elif cmd[0] == 'close':
                #print("close window", cmd[1])
                win=self.win_slots[cmd[1]]
                win.close()
                self.win_slots[cmd[1]]=None
            elif cmd[0] == 'set_win_pos_size':
                win=self.win_slots[cmd[1]]
                win.set_pos_size(cmd[2], cmd[3], cmd[4], cmd[5])

        for win in self.win_slots:
            if win is not None:
                win.update_data()

    def get_free_identity(self):
        for i in range(self.MAX_WIN_NUM):
            if self.win_slots[i] is None:
                self.win_slots[i] = 0
                return i
        print('get_free_identity error')

    def create_window(self, identity, cls, args):
        if identity < self.MAX_WIN_NUM:
            self.cmd_queue.put(('create_window', identity, cls, args))
            print('create window application')
        else:
            print("create_window Error")

    def get_window(self, identity):
        if identity < self.MAX_WIN_NUM:
            return self.win_slots[identity]
        return None

    def run(self, fun, args):
        self.cmd_queue.put(('run', fun, args))
        ret = self.result_queue.get()
        return ret

    def close(self, identity):
        if identity < self.MAX_WIN_NUM and self.win_slots[identity] is not None:
            self.cmd_queue.put(('close', identity))
        else:
            print("close Error")

    def quit(self):
        QtGui.QApplication.quit()

    def get_win_pos_size(self, i):
        return self.win_slots[i].get_pos_size()

    def set_win_pos_size(self, i, x, y, w, h):
        self.cmd_queue.put(('set_win_pos_size', i, x, y, w, h))
