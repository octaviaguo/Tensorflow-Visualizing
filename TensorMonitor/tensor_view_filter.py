import numpy as np
import pyqtgraph as pg
from pyqt_env import PyQTWindowWrapper

INSERT_BORDER = True

class TensorViewFilter(PyQTWindowWrapper):
    def __init__(self,args):
        PyQTWindowWrapper.__init__(self, args.get('data_source'))
        self.args = args

        self.win = pg.GraphicsLayoutWidget()
        self.win.show() 
        self.win.resize(1000,900)
        self.win.setWindowTitle(args.get('name'))
        self.view = self.win.addViewBox()
        
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)

    def update_data(self):
        global INSERT_BORDER
        if self.data_source.dirty:
            #print('the shape of filter:   '+self.args.get('shape'))
            np0 = self.data_source.data[-1]
            np1 = np.swapaxes(np0,0,3)
            np2 = np.swapaxes(np1,1,2)
            np3 = np.swapaxes(np2,2,3)
            #print('after three swaps, the shape of filter is:       ', np.shape(np3))

            if INSERT_BORDER:
                minval = np.amin(np0)
                w1 = int(np3.shape[2]/16) + 1
                w2 = int(np3.shape[3]/16) + 1
                if np3.shape[2]==3:
                    w1 = 2 #pyqtgraph bug workaround

                f1 = minval*np.ones((np3.shape[0],np3.shape[1],w1,np3.shape[3]))
                f2 = minval*np.ones((np3.shape[0],np3.shape[1],np3.shape[2]+w1,w2))
                #print(np3.shape, f1.shape, f2.shape)
                np3 = np.concatenate([np3, f1], axis=2)
                np3 = np.concatenate([np3, f2], axis=3)
                #print(np3.shape)
            
            create_list = []
            for i in range(np.shape(np3)[0]):
                todo = np.copy(np3[i])
                m = np.reshape(todo, (np.shape(todo)[0]*np.shape(todo)[1], np.shape(todo)[2]))
                create_list.append(m)
            showpic = np.concatenate(create_list, axis = 1)
            showpic2 = np.transpose(showpic)
            showpic3 = np.flip(showpic2, 1)

            self.img.setImage(showpic3)
            #print('finally:      ', np.shape(showpic3))
            self.data_source.clear_dirty()
      
    def close(self):
        self.win.hide()