import numpy as np
import pyqtgraph as pg
from pyqt_env import PyQTWindowWrapper

COL_NUM = 16
INSERT_BORDER = True

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

    def draw_grid_img(self, data): #[batch, with, height, c]
        global COL_NUM, INSERT_BORDER
        shape = data.shape
        #print(shape)
        real_col = COL_NUM
        if shape[0]<COL_NUM:
            real_col = shape[0]

        if INSERT_BORDER:
            w1 = int(shape[2]/16) + 1
            w2 = int(shape[1]/16) + 1
            bval = np.amax(data) #for mono image
            b1 = bval*np.ones((shape[1],w1,shape[3]))
            b2 = bval*np.ones((w2,(shape[2]+w1)*real_col+w1,shape[3]))
            if shape[-1]!=1:
                #for color image
                b1[:,:,0:1]=b2[:,:,0:1]=np.amin(data)

        np2_list = []

        resi_col = (shape[0]%COL_NUM)
        if shape[0]>COL_NUM and resi_col != 0:
            padding_col = COL_NUM-resi_col
            padding_shape = np.copy(shape)
            padding_shape[0] = padding_col
            padding = np.zeros(padding_shape)
            np1 = np.concatenate([data, padding])
        else:
            np1 = data

        #print(padding_col,np1.shape)
        for j in range(0,shape[0],COL_NUM):
            if INSERT_BORDER:
                np1_list = [b1]
                for i in range(real_col):
                    np1_list.extend([np.flip(np1[j+i,:,:,:],axis=0),b1])
                np2 = np.concatenate(np1_list, axis=1)
            else:
                np2 = np.concatenate([np.flip(np1[j+i,:,:,:],axis=0) for i in range(real_col)], axis=1)
            if INSERT_BORDER:
                np2_list = [np.copy(np2), b2] + np2_list
            else:
                np2_list = [np.copy(np2)] + np2_list

        if INSERT_BORDER:
            np2_list = [b2] + np2_list
        np3 = np.concatenate(np2_list,axis=0)
        # setImage: 3D (width, height, RGBa)
        self.img.setImage(np.transpose(np3,[1,0,2]), axes={'x':0, 'y':1, 'c':2})


    def update_data(self):
        global COL_NUM
        if self.data_source.dirty:
            if self.args.get('reshape') != []:
                np1 = np.reshape(self.data_source.data[-1],self.args.get('reshape'))
            else:
                np1 = self.data_source.data[-1]

            shape = np1.shape
            #print(shape)
            if len(shape) == 2: #[width, height]
                np1 = np.expand_dims(np1, axis=2) #convert to [width,height,1]
                shape = np1.shape

            if shape[-1] == 3 or shape[-1] == 1:
                if len(shape) == 3: #[width, height, c]
                    self.draw_grid_img(np.expand_dims(np1, axis=0))
                elif len(shape) == 4: #[batch, width, height, c]
                    self.draw_grid_img(np1)
            elif len(shape) == 3: #[batch, width, height]
                self.draw_grid_img(np.expand_dims(np1, axis=3))

            self.data_source.clear_dirty()
        
    def close(self):
        self.win.hide()