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
        self.init_flag = False
        self.x_is_time = False

    def __set_data(self, data):
        self.curve.setData(np.reshape(data,(-1)))

    def update_data(self):
        if self.data_source.dirty:
            if self.init_flag is False:
                tot_dim = np.prod(self.data_source.data[-1].shape)
                print('tot dim is %d' %tot_dim)
                if tot_dim == 1:
                    self.x_is_time = True
                self.init_flag = True
            if self.x_is_time:
                self.__set_data([d.flatten()[0] for d in self.data_source.data])
            else:
                self.__set_data(self.data_source.data[-1])
            self.data_source.clear_dirty()

    def close(self):
        self.win.hide()
