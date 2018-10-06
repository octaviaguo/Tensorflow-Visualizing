import numpy as np
import pyqtgraph as pg
from pyqt_env import PyQTWindowWrapper

class TensorView2D(PyQTWindowWrapper):
    def __init__(self,args):
        PyQTWindowWrapper.__init__(self, args.get('data_source'))
        self.args = args

        self.win = pg.GraphicsLayoutWidget()
        self.win.show() 
        self.win.setWindowTitle(args.get('name'))
        self.view = self.win.addViewBox()

        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)

    def update_data(self):
        if self.data_source.dirty:
            if self.args.get('reshape') != []:
                np1 = np.reshape(self.data_source.data[-1],self.args.get('reshape'))
                np2 = np.transpose(np1)
                self.img.setImage(np.flip(np2,1))
            else:
                self.img.setImage(self.data_source.data[-1])
            self.data_source.clear_dirty()
        
    def close(self):
        self.win.hide()