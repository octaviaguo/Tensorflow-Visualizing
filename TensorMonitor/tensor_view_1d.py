import pyqtgraph as pg
import numpy as np
from pyqt_env import PyQTWindowWrapper

class TensorView1D(PyQTWindowWrapper):
    def __init__(self, args):
        PyQTWindowWrapper.__init__(self, args.get('data_source'))

        self.win = pg.GraphicsLayoutWidget(show=True, title=args.get('name'))
        self.win.resize(600,390)
        self.win.show()

        self.p1 = self.win.addPlot(title="1-D Plot")
        self.curve = self.p1.plot(pen='y')

    def __set_data(self, data):
        self.curve.setData(np.reshape(data,(-1)))

    def update_data(self):
        if self.data_source.dirty:
            self.__set_data(self.data_source.data[-1])
            self.data_source.clear_dirty()

    def close(self):
        self.win.hide()
