import numpy as np
from scipy.misc import imread, imresize
import sys
from PyQt4 import QtGui
import os


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
        #
        '''
        placeholder_name = 'Placeholder'
        image_path = 'sample_images/Lenna.png'
        im = np.expand_dims(imresize(imresize(imread(image_path), (256, 256)), (224, 224)), axis = 0)
        '''
        
        self.feed_dict = {}
        self.placeholder_dict = placeholder_dict
        #self.feed_dict[placeholder_dict[placeholder_name]] = im

        #update configures
        '''
        self.config_dict['placeholder_name'] = placeholder_name
        self.config_dict['image_path'] = image_path
        '''
        #
        print(placeholder_dict)

    def show(self):
        if self.window is None:
            self.window = QtGui.QWidget()
            self.window.setGeometry(600, 50, 600, 400)
            self.window.setWindowTitle("Input Settings")

            self.window.chs_plahd = QtGui.QLabel(self.window)
            self.window.chs_plahd.setText('Choose a Placeholder: ')
            self.window.chs_plahd.move(20, 20)
            self.window.chs_plahd.setFont(QtGui.QFont("Times", 15))

            self.window.plahd_combo = QtGui.QComboBox(self.window)
            self.window.plahd_combo.move(220, 20)
            count = 0
            for item in self.placeholder_dict:
                self.window.plahd_combo.addItem(item)
                if count == 0:
                    self.feedkey = self.placeholder_dict[item]
                    count = 1     
            self.window.plahd_combo.activated[str].connect(self.prep_feedkey)

            self.window.button = QtGui.QPushButton("Picture Lib", self.window)
            self.window.button.setStyleSheet("color: blue; background-color: yellow; font: bold 14px")
            self.window.button.resize(85, 30)
            self.window.button.move(500, 15)
            self.window.button.clicked.connect(self.prep_feedvalue)

            print('11111111111111111111')
        self.window.show()        

    def prep_feedkey(self, placeholder):
        self.feedkey = self.placeholder_dict[placeholder]
        print('222222222222')

    def prep_feedvalue(self,):
        name = QtGui.QFileDialog.getOpenFileName(self.window, 'Choose Input Source')
        im = np.expand_dims(imresize(imresize(imread(name), (256, 256)), (224, 224)), axis = 0)
        self.feed_dict[self.feedkey] = im
        print('3333333333333333')

    def prepare_input(self):
        print('prepare_input.....................................')
        return self.feed_dict

    def get_config(self):
        return self.config_dict

