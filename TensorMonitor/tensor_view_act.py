import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqt_env import PyQTWindowWrapper

class TensorViewAct(PyQTWindowWrapper):
    def __init__(self,args):
        PyQTWindowWrapper.__init__(self, args.get('data_source'))
        self.args = args

        class MyWindow(pg.GraphicsLayoutWidget):
            KeyPressed = QtCore.pyqtSignal(object)

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.KeyPressed.connect(self.pressKey)
                self.roi = pg.ROI([0, 0], [1,1])
                self.posx = 0
                self.posy = 0
                self.h = 0
                self.w = 0
                self.c = 0

            def keyPressEvent(self, ev):
                self.scene().keyPressEvent(ev)
                self.KeyPressed.emit(ev)

            def pressKey(self, eventQKeyEvent):
                key = eventQKeyEvent.key()
                if key == QtCore.Qt.Key_Up:
                    print("Up")
                    self.posy = self.posy+self.h
                    self.roi.setPos([self.posx, self.posy])
                elif key == QtCore.Qt.Key_Down:
                    print("Down")
                    self.posy = self.posy-self.h
                    self.roi.setPos([self.posx, self.posy])
                elif key == QtCore.Qt.Key_Right:
                    print("Right")
                    self.posx = self.posx+self.w
                    self.roi.setPos([self.posx, self.posy])
                elif key == QtCore.Qt.Key_Left:
                    print("Left")
                    self.posx = self.posx-self.w
                    self.roi.setPos([self.posx, self.posy])


        self.win = MyWindow()
        self.win.show() 
        self.win.resize(1300,1000)
        self.win.setWindowTitle(args.get('name'))
        self.view = self.win.addViewBox()
        
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)

        self.win.nextColumn()
        self.view2 = self.win.addViewBox()
        self.view2.setAspectLocked(True)
        self.img2 = pg.ImageItem(border='w')
        self.view2.addItem(self.img2)
        #maybe add a title for img2

        self.count_upd = 0

    def update_data(self):
        if self.data_source.dirty:
            print('the shape of activation:   '+self.args.get('shape'))
            np0 = self.data_source.data[-1]
            self.win.h = np.shape(np0)[1]
            self.win.w = np.shape(np0)[2]
            self.win.c = np.shape(np0)[3]
            np1 = np.swapaxes(np0,1,3)
            np2 = np.swapaxes(np1,2,3)
    
            create_list = []
            for i in range(np.shape(np2)[0]):
                todo = np.copy(np2[i])
                m = np.reshape(todo,(np.shape(todo)[0]*np.shape(todo)[1], np.shape(todo)[2]))
                create_list.append(m)
            showpic = np.concatenate(create_list, axis = 1)
            showpic2 = np.transpose(showpic)
            showpic3 = np.flip(showpic2, 1)
            
            self.img.setImage(showpic3)
            print('finally:     ', np.shape(showpic3))

            if self.count_upd == 0:
                self.win.roi.setPos([0, self.win.h*(self.win.c-1)])
                self.win.roi.setSize([self.win.w, self.win.h])
                self.win.posx = 0
                self.win.posy = self.win.h*(self.win.c-1)
                self.view.addItem(self.win.roi)
                self.win.roi.setZValue(10)     
                self.count_upd = 1

            def update_frame():
                selected = self.win.roi.getArrayRegion(showpic3, self.img)
                self.img2.setImage(selected)

            update_frame()
            self.win.roi.sigRegionChanged.connect(update_frame)

            self.data_source.clear_dirty()



    def close(self):
        self.win.hide()
