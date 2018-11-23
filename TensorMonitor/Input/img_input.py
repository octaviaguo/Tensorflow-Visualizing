import numpy as np
from scipy.misc import imread, imresize
import sys
from PyQt4 import QtGui
import os
import pyqtgraph as pg


"""
add_input('input.img_input',placeholder='Placeholder',image='sample_images/ManCoffee.jpeg')
"""

class TensorInput():
    def __init__(self, placeholder_dict, config_dict):
        self.window = None
        
        #get configures
        self.config_dict = {}
        for config_name in config_dict.keys():
            self.config_dict[config_name] = config_dict[config_name]
        
        self.feed_dict = {}
        self.placeholder_dict = placeholder_dict

        #update configures
        '''
        self.config_dict['placeholder_name'] = placeholder_name
        self.config_dict['image_path'] = image_path
        '''
        #
        print(placeholder_dict)

    def show(self):
        if self.window is None:
            self.window = QtGui.QMainWindow()
            self.window.setGeometry(700, 50, 800, 600)
            self.window.setWindowTitle("Input Settings")

            self.window.chs_plahd = QtGui.QLabel(self.window)
            self.window.chs_plahd.setText('Choose a Placeholder: ')
            self.window.chs_plahd.setFont(QtGui.QFont("Times", 14))

            self.window.plahd_combo = QtGui.QComboBox(self.window)
            count = 0
            for item in self.placeholder_dict:
                self.window.plahd_combo.addItem(item)
                if count == 0:
                    self.feedkey = self.placeholder_dict[item]
                    count = 1     
            self.window.plahd_combo.activated[str].connect(self.prep_feedkey)

            self.window.frame_pmt = QtGui.QLabel(self.window)
            self.window.frame_pmt.setText('Choose Content of ROI: ')
            self.window.frame_pmt.setFont(QtGui.QFont("Times", 14))

            self.window.frame = QtGui.QComboBox(self.window)
            self.window.frame.addItem('Closed')
            self.window.frame.addItem('Included')
            self.window.frame.addItem('Excluded')
            self.window.frame.activated[str].connect(self.select_frame)
            self.frame = 'Closed'

            self.window.button = QtGui.QPushButton("Picture Lib", self.window)
            self.window.button.setStyleSheet("color: blue; background-color: yellow; font: bold 14px")
            self.window.button.clicked.connect(self.prep_feedvalue)

            self.window.pw1 = pg.GraphicsLayoutWidget()
            self.window.pw1.show()
            self.window.view = self.window.pw1.addViewBox()
            self.window.view.setAspectLocked(True)
            self.window.img = pg.ImageItem(border='w')
            self.window.view.addItem(self.window.img)
            self.window.img.setImage(np.random.randint(10, size=(100,100)))

            cw = QtGui.QWidget()
            self.window.setCentralWidget(cw)
            layout = QtGui.QGridLayout()
            cw.setLayout(layout)
            layout.addWidget(self.window.chs_plahd, 0, 0, 1, 1)
            layout.addWidget(self.window.plahd_combo, 1, 0, 1, 1)
            layout.addWidget(self.window.button, 3, 0, 1, 1)
            layout.addWidget(self.window.frame_pmt, 5, 0)
            layout.addWidget(self.window.frame, 6, 0)
            layout.addWidget(self.window.pw1, 0, 2, 15, 20)

            self.window.pw1.roi = pg.ROI([0, 0], [20, 20])
            self.window.view.addItem(self.window.pw1.roi)
            self.window.pw1.roi.addScaleHandle([0.5, 1], [0.5, 0.5])
            self.window.pw1.roi.addScaleHandle([0, 0.5], [0.5, 0.5])
            self.window.pw1.roi.hide()
            self.window.pw1.roi.sigRegionChanged.connect(self.update_frame)

        self.window.show()        

    def prep_feedkey(self, placeholder):
        self.feedkey = self.placeholder_dict[placeholder]
        print(self.feedkey.shape[0],self.feedkey.shape[1],self.feedkey.shape[2],self.feedkey.shape[3])
        dem = len(self.feedkey.shape)
        if dem==4:
            self.depth = int(self.feedkey.shape[3])
            if self.depth==1 or self.depth==3: #(batch, width, height, depth)
                self.width = int(self.feedkey.shape[1])
                self.height = int(self.feedkey.shape[2])
            else:
                print('error')
        elif dem==3:
            self.depth = int(self.feedkey.shape[2])
            if self.depth==1 or self.depth==3: #(width, height, depth)
                self.width = int(self.feedkey.shape[0])
                self.height = int(self.feedkey.shape[1])
            else: #(batch, width, height)
                self.depth=1
                self.width = int(self.feedkey.shape[2])
                self.height = int(self.feedkey.shape[2])
        elif dem==2:
            self.depth = 1
            self.width = int(self.feedkey.shape[0])
            self.height = int(self.feedkey.shape[1])
        else:
            print('error')
        print('width %d height %d depth %d'%(self.width,self.height,self.depth))

    def prep_feedvalue(self):
        name = QtGui.QFileDialog.getOpenFileName(self.window, 'Choose Input Source')
        self.window.im0 = imresize(imread(name), (self.width, self.height))
        im1 = np.transpose(self.window.im0, (1, 0, 2))
        self.window.im2 = np.flip(im1, 1)
        self.window.img.setImage(self.window.im2)

        im = np.expand_dims(self.window.im0, axis = 0)
        self.feed_dict[self.feedkey] = im

    def select_frame(self, text):
        self.frame = text
        if self.frame == 'Closed':
            self.window.pw1.roi.hide()
        else:
            self.window.pw1.roi.show()

    def update_frame(self):
        if self.frame == 'Closed':
            pass

        width = int(self.window.pw1.roi.size()[0])
        height = int(self.window.pw1.roi.size()[1])
        x0 = int(self.window.pw1.roi.pos()[0])
        y0 = int(self.window.pw1.roi.pos()[1])
        
        if self.frame == 'Included':
            n0 = np.zeros(self.window.im2.shape)
            for i in range(width):
                for j in range(height):
                    n0[self.height-(y0+j)][x0+i]= self.window.im0[self.height-(y0+j)][x0+i]
            im = np.expand_dims(n0, axis = 0)
            self.feed_dict[self.feedkey] = im
        else:
            n1 = np.array(self.window.im0)
            for i in range(width):
                for j in range(height):
                    n1[self.height-(y0+j)][x0+i] = 0
            im = np.expand_dims(n1, axis = 0)
            self.feed_dict[self.feedkey] = im

    def prepare_input(self):
        return self.feed_dict

    def get_config(self):
        return self.config_dict