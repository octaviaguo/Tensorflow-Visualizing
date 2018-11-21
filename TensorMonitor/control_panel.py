import os
import sys
import copy as copy

from tensor_view_1d import TensorView1D
from tensor_view_2d import TensorView2D
from tensor_view_act import TensorViewAct
from tensor_view_filter import TensorViewFilter
from tensor_data import TensorData
import inspect
from PyQt4 import QtGui, QtCore
from pyqt_env import PyQTEnv
import xml.etree.ElementTree as ET

TEST_WATERFALL_VIEW = False

gui_root_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

class MainWindow(QtGui.QMainWindow):
    def __init__(self, args):
        super(MainWindow, self).__init__()
        self.setGeometry(1400,70,600,370)
        self.setWindowTitle("VISUALIZATION")
        self.action_cb = args
        #self.tensor_input_list = args['tensor_input_list']

        quitAction = QtGui.QAction('Quit', self)
        quitAction.triggered.connect(self.close_application)

        saveAction = QtGui.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.save_WatchList)

        loadAction = QtGui.QAction('Open File...', self)
        loadAction.setShortcut('Ctrl+O')
        loadAction.triggered.connect(self.action_cb['load_WatchList'])

        input_file = QtGui.QAction('Open input file', self)
        input_file.setShortcut('Ctrl+I')
        input_file.triggered.connect(self.open_input_file)

        menu = self.menuBar()
        filemenu = menu.addMenu('&File')
        filemenu.addAction(saveAction)
        filemenu.addAction(loadAction)
        filemenu.addAction(input_file)
    
        self.toolBar = self.addToolBar("ToolBar")
        self.toolBar.addAction(quitAction)

        self.create_sub_windows()

    def create_sub_windows(self):
        pausecheck = QtGui.QCheckBox('Pause', self)
        pausecheck.move(520,120)
        pausecheck.toggle()
        pausecheck.stateChanged.connect(self.action_cb['on_pause'])

        self.step_btn = QtGui.QPushButton("Step",self)
        self.step_btn.setStyleSheet("color: blue; font: bold 14px")
        self.step_btn.resize(50,25)
        self.step_btn.move(520,80)
        self.step_btn.clicked.connect(self.action_cb['on_step'])
        
        self.watch_com = QtGui.QLabel(self)
        self.watch_com.setText('Watch :')
        self.watch_com.move(520,244)
        self.watch_com.setFont(QtGui.QFont("Times",13,weight=QtGui.QFont.Bold))
        
        self.watch_choice = QtGui.QComboBox(self)
        self.watch_choice.setStyleSheet("font: bold 14px")
        self.watch_choice.move(520,280)
        self.watch_choice.addItem('1-DIM')
        self.watch_choice.addItem('2-DIM')
        self.watch_choice.addItem('Activation')
        self.watch_choice.addItem('Filter')
        self.watch_choice.resize(70,30)
        self.watch_choice.show()
        self.watch_choice.activated[str].connect(self.action_cb['on_add_watch'])
        
        self.showbtn = QtGui.QCheckBox('Show',self)
        self.showbtn.move(520,195)
        self.showbtn.toggle()
        self.showbtn.hide()
        self.showbtn.stateChanged.connect(self.action_cb['on_set_show'])

        self.show_remove_btn = QtGui.QPushButton("Remove",self)
        self.show_remove_btn.setStyleSheet("color: red; font: bold 14px")
        self.show_remove_btn.resize(70,30)
        self.show_remove_btn.move(520,240)
        self.show_remove_btn.hide()
        self.show_remove_btn.clicked.connect(self.action_cb['on_remove_watch'])
          
        self.hd_all_btn = QtGui.QPushButton("Hide All",self)
        self.hd_all_btn.setStyleSheet("color: red; font: bold 14px")
        self.hd_all_btn.resize(84,30)
        self.hd_all_btn.move(510,280)
        self.hd_all_btn.hide()        
        self.hd_all_btn.clicked.connect(self.action_cb['on_hide_all'])
        
        self.tensor_label = QtGui.QLabel(self)
        self.tensor_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tensor_label.setGeometry(QtCore.QRect(80,180,200,20))
        self.tensor_label.setFont(QtGui.QFont("Times",12,weight=QtGui.QFont.Bold))

        self.tensor_reshape_label = QtGui.QLabel(self)
        self.tensor_reshape_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tensor_reshape_label.setGeometry(QtCore.QRect(80,220,200,20))
        self.tensor_reshape_label.setFont(QtGui.QFont("Times",12,weight=QtGui.QFont.Bold))

        self.reshape_inlb = QtGui.QLabel(self)
        self.reshape_inlb.move(80,220)
        self.reshape_inlb.setText('Reshape: ')
        self.reshape_inlb.setFont(QtGui.QFont('Times',12,weight=QtGui.QFont.Bold))

        self.tensor_shape_input = QtGui.QLineEdit(self)
        self.tensor_shape_input.textChanged.connect(self.action_cb['on_tensor_shape_input'])
        self.tensor_shape_input.move(160,220)
        
        self.sourceInput_list = QtGui.QComboBox(self)
        self.sourceInput_list.move(160,270)
        self.sourceInput_list.activated[str].connect(self.action_cb['on_input_select'])

        listcombo = QtGui.QComboBox(self)
        listcombo.addItem("Select List")
        listcombo.addItem("Watch List")
        listcombo.move(50,100)
        
        subcombo = QtGui.QComboBox(self)
        subcombo.addItem('USER_LIST')
        subcombo.addItem('TRAINABLE_VARIABLES')
        subcombo.addItem('ACTIVATIONS')
        subcombo.addItem('GLOBAL_VARIABLES')
        subcombo.addItem('ALL_OPS')
        subcombo.move(180,100)

        listcombo.activated[str].connect(self.action_cb['on_list_type_select'])
        subcombo.activated[str].connect(self.action_cb['on_filter_type_select'])

        self.create_list_view()
        
        fontset = QtGui.QFont()
        fontset.setPointSize(12)

        self.filter_comment = QtGui.QLabel(self)
        self.filter_comment.setText('Search Only in  ALL_OPS:')
        self.filter_comment.setGeometry(QtCore.QRect(100,34,180,25))  
        self.filter_comment.setFont(fontset)

        self.filter_in = QtGui.QLineEdit(self)
        self.filter_in.textChanged.connect(self.action_cb['on_filter_str_input'])
        self.filter_in.move(290,30)
        self.filter_in.resize(190,40)

        self.show()

    def create_list_view(self):
        self.list_view=QtGui.QListView(self)
        self.list_view.main = self
        self.list_view.setEditTriggers(QtGui.QListView.NoEditTriggers)
        self.list_view.setMouseTracking(True)
        self.list_model = QtGui.QStandardItemModel()
        self.list_view.setModel(self.list_model)
        entries = [str(i) for i in range(50)]
        for i in entries:
            item = QtGui.QStandardItem(i)
            self.list_model.appendRow(item)

        self.list_view.setMinimumSize(170,200)
        self.list_view.move(310,130)
        self.list_view.clicked.connect(self.action_cb['on_tensor_select'])

    def close_application(self):
        choice = QtGui.QMessageBox.question(self, 'Warning',
                                            "Do you want to quit?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            self.action_cb['on_close']()
        else:
            pass

    def save_WatchList(self):
        choice = QtGui.QMessageBox.question(self, '',
                                            "Do you want to save the watch_list?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            self.action_cb['on_save']()
        else:
            pass

    def update_tensor_list(self, list_type, list, pos, reset_pos):
        items_str = [t.disp_name for t in list]
        self.list_model.clear()
        for text in items_str:
            item = QtGui.QStandardItem(text)
            self.list_model.appendRow(item)

    def open_input_file(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open input file')
        input_file = open(name, 'r')
        DIYname = QtGui.QInputDialog.getText(self, 'Name your input choice', None)
        save_name = DIYname[0]
        self.action_cb['add_input'](save_name, input_file.name)

    def update_input_list(self, input_list):
        self.sourceInput_list.clear()
        for item in input_list:
            self.sourceInput_list.addItem(item.name)

    def enable_filter_input(self, enable):
        if enable is False:
            self.filter_in.setDisabled(True)
        else:
            self.filter_in.setDisabled(False)

class TensorItem(object):
    def __init__(self, name, shape, op, input_name):
        self.name = name
        self.op = op
        self.input_name = input_name
        #self.data_source = TensorData(start_step=ControlPanel.step_count)
        self.disp_name = name
        try:
            shape_str = '(' + ', '.join(map(str, shape)) + ')'
            self.shape_str = shape_str
            self.reshape = []
        except: #TypeError: #fix for python3 
            self.shape_str = ""
            self.reshape = []

        ####
        #self.pyqt_window_id = None
        #self.view = None
    def copy(self, obj):
        self.name = copy.copy(obj.name)
        self.input_name = copy.copy(obj.input_name)
        self.op = obj.op
        self.disp_name = copy.copy(obj.disp_name)
        self.shape_str = copy.copy(obj.shape_str)
        self.reshape = copy.copy(obj.reshape)

    def get_reshape_str(self):
        return ', '.join(map(str, self.reshape))

class ControlPanel(object):
    quit = False
    pause = True
    single_step_flag = False
    step_count = 0

    cur_list_type = 0
    cur_filter_type_index = 0

    tensor_select_list = []
    select_list_cur_pos = 0
  
    tensor_watch_list = []
    watch_list_cur_pos = 0

    tensor_input_list = []

    console_cmd_list = []
    pyqt_env = None


    class TensorSelectItem(TensorItem):
        def __init__(self, name, shape, op, input_name):
            TensorItem.__init__(self, name, shape, op, input_name)

    class TensorWatchItem(TensorItem):
        def __init__(self, tensor_select_item):
            self.showstate = True
            self.copy(tensor_select_item)
            self.data_source = TensorData(start_step=ControlPanel.step_count)
            self.pyqt_window_id = None
            self.picDIM = '1-DIM'

    class TensorInputItem(object):
        def __init__(self, name, input_obj):
            self.name = name
            self.input_obj = input_obj

    """
    tensor panel
    """
    def __open_tensor_view(self, index, text):
        tensor_item = self.tensor_watch_list[index]
        tensor_item.pyqt_window_id = self.pyqt_env.get_free_identity()
        if text == '2-DIM':
            self.pyqt_env.create_window(tensor_item.pyqt_window_id, TensorView2D,
                {'data_source':tensor_item.data_source, 'name':tensor_item.name, 'shape':tensor_item.shape_str, 'reshape':tensor_item.reshape})
            self.tensor_watch_list[index].picDIM = '2-DIM'
        elif text == '1-DIM':
            self.pyqt_env.create_window(tensor_item.pyqt_window_id, TensorView1D,
                {'data_source':tensor_item.data_source, 'name':tensor_item.name})
            self.tensor_watch_list[index].picDIM = '1-DIM'
        elif text == 'Activation':
            self.pyqt_env.create_window(tensor_item.pyqt_window_id, TensorViewAct,
                {'data_source':tensor_item.data_source, 'name':tensor_item.name, 'shape':tensor_item.shape_str, 'reshape':tensor_item.reshape})
            self.tensor_watch_list[index].picDIM = 'Activation'
        elif text == 'Filter':
            self.pyqt_env.create_window(tensor_item.pyqt_window_id, TensorViewFilter,
                {'data_source':tensor_item.data_source, 'name':tensor_item.name, 'shape':tensor_item.shape_str, 'reshape':tensor_item.reshape})  
            self.tensor_watch_list[index].picDIM = 'Filter'

    def __close_tensor_view(self, index):
        tensor_item = self.tensor_watch_list[index]
        if tensor_item.pyqt_window_id is not None:
            self.pyqt_env.close(tensor_item.pyqt_window_id)
            
            tensor_item.pyqt_window_id = None

    def __close_all_tensor_views(self):
        for i in range(len(self.tensor_watch_list)):
            self.__close_tensor_view(i)

    def __on_tensor_shape_input(self, text):
        titem = self.tensor_select_list[self.select_list_cur_pos]
        dims = text.split(',')
        titem.reshape = []
        for dim in dims:
            try:
                titem.reshape.append(int(dim))
            except ValueError:
                pass

    def __on_add_watch(self, text):
            titem = self.tensor_select_list[self.select_list_cur_pos]
            new_titem = self.TensorWatchItem(titem)
            
            """
            new_titem = copy.copy(titem) #shallow copy
            new_titem.reshape = copy.copy(titem.reshape)
            """
            self.tensor_watch_list.append(new_titem)
            index = len(self.tensor_watch_list)-1
            self.__open_tensor_view(index,text)

    def __on_remove_watch(self):
        self.__close_tensor_view(self.watch_list_cur_pos)
        del self.tensor_watch_list[self.watch_list_cur_pos]
        item_num = len(self.tensor_watch_list)
        if self.watch_list_cur_pos >= item_num and item_num > 0:
            self.watch_list_cur_pos = item_num-1
        if self.cur_list_type==0:
            list = self.tensor_select_list
            pos = self.select_list_cur_pos
        else:
            list = self.tensor_watch_list
            pos = self.watch_list_cur_pos
        self.main_window.update_tensor_list(list_type=self.cur_list_type, list=list, pos=pos, reset_pos=False)

    def __on_set_show(self, state):
        if state == QtCore.Qt.Checked and self.tensor_watch_list[self.watch_list_cur_pos].showstate == False:
            self.__open_tensor_view(self.watch_list_cur_pos, self.tensor_watch_list[self.watch_list_cur_pos].picDIM)
            self.tensor_watch_list[self.watch_list_cur_pos].showstate = True
        if state != QtCore.Qt.Checked and self.tensor_watch_list[self.watch_list_cur_pos].showstate == True:
            self.__close_tensor_view(self.watch_list_cur_pos)
            self.tensor_watch_list[self.watch_list_cur_pos].showstate = False

    def __on_input_select(self, text):
        titem = self.tensor_select_list[self.select_list_cur_pos]
        titem.input_name = text
        input_obj = self.__get_input_obj(text)
        if input_obj is not None:
            input_obj.show()

    def __on_tensor_select(self, index):
        index = index.row()
        if self.cur_list_type == 0:
            self.select_list_cur_pos = index
            list = self.tensor_select_list
            print(list[index].shape_str)
        else:
            self.watch_list_cur_pos = index
            list = self.tensor_watch_list
            if self.tensor_watch_list[index].showstate == False:
                self.main_window.showbtn.setChecked(False)
            else:
                self.main_window.showbtn.setChecked(True)   
            self.main_window.tensor_reshape_label.setText('Reshape:   ('+str(list[index].get_reshape_str())+')')
        self.main_window.tensor_label.setText('Shape:  '+list[index].shape_str)

    """
    global control
    """

    def __on_list_type_select(self, text):
        if text == 'Select List':
            index = 0
        else:
            index = 1
            
        if index != self.cur_list_type:
            if index == 0:
                self.main_window.enable_filter_input(True)
            else:
                self.main_window.enable_filter_input(False)
            self.cur_list_type = index
        self.on_switch_btn(self.cur_list_type)
        if self.cur_list_type == 0:
            pos = self.select_list_cur_pos
            self.main_window.update_tensor_list(list_type=self.cur_list_type, list=self.tensor_select_list, pos=pos, reset_pos=False)
        else:
            pos = self.watch_list_cur_pos
            self.main_window.update_tensor_list(list_type=self.cur_list_type, list=self.tensor_watch_list, pos=pos, reset_pos=False)
    
    def on_switch_btn(self,index):
        if index == 0:
            self.main_window.watch_choice.show()
            self.main_window.show_remove_btn.hide()
            self.main_window.hd_all_btn.hide()
            self.main_window.showbtn.hide()
            self.main_window.watch_com.show()
            self.main_window.tensor_label.show()
            self.main_window.tensor_label.setText('Shape:  '+self.tensor_select_list[0].shape_str)
            self.main_window.tensor_shape_input.show()
            self.main_window.reshape_inlb.show()
            self.main_window.tensor_shape_input.clear()
            self.main_window.tensor_reshape_label.hide()
        else:
            self.main_window.watch_choice.hide()
            self.main_window.show_remove_btn.show()
            self.main_window.hd_all_btn.show()
            self.main_window.watch_com.hide()
            self.main_window.tensor_shape_input.hide()
            if self.tensor_watch_list != []:
                self.main_window.showbtn.show()
                self.main_window.tensor_label.show()
                self.main_window.tensor_reshape_label.show()                
                self.main_window.tensor_label.setText('Shape:  '+self.tensor_watch_list[0].shape_str)
                self.main_window.tensor_reshape_label.setText('Reshape:   ('+str(self.tensor_watch_list[0].get_reshape_str())+')')
                if self.tensor_watch_list[0].showstate == True:
                    self.main_window.showbtn.setChecked(True)
                else:
                    self.main_window.showbtn.setChecked(False)
            else:
                self.main_window.showbtn.hide()
                self.main_window.tensor_label.hide()
                self.main_window.tensor_reshape_label.hide()
            self.main_window.reshape_inlb.hide()

    def __on_filter_type_select(self, text):
        pwd = {'USER_LIST':0, 'TRAINABLE_VARIABLES':1, 'ACTIVATIONS':2, 'GLOBAL_VARIABLES':3, 'ALL_OPS':4 }
        self.cur_filter_type_index = pwd[text]
        if pwd[text] == 2:
            pass
        else:
            pass
    
    def __on_filter_str_input(self, text):
        text = str(text)
        self.filter_str = text.strip()

    def __on_pause(self, state):
        if state == QtCore.Qt.Checked:
            self.pause = True
        else:
            self.pause = False
        print(self.pause)
     
    def __on_step(self):
        self.pause = True
        self.single_step_flag = True

    def __on_hide_all(self):
        self.__close_all_tensor_views()
        self.main_window.showbtn.hide()
    
    def __on_console_str_input(self):
        return

        cmd = copy.copy(text.strip())
        self.console_cmd_list.append(cmd)

    def __on_close(self):
        self.quit = True

    def __on_save(self):
        NoWatchItem = len(self.tensor_watch_list)
        watchlist = [None]*NoWatchItem

        root = ET.Element('root')
        for i in range(NoWatchItem):
            watchlist[i] = ET.SubElement(root, 'Item'+str(i+1))
            name = ET.SubElement(watchlist[i], 'name')
            shape = ET.SubElement(watchlist[i], 'shape')
            reshape = ET.SubElement(watchlist[i], 'reshape')
            visType = ET.SubElement(watchlist[i], 'visType')

            name.text = self.tensor_watch_list[i].name
            shape.text = self.tensor_watch_list[i].shape_str
            reshape.text = self.tensor_watch_list[i].reshape
            visType.text = self.tensor_watch_list[i].picDIM

        my = ET.tostring(root)
        myfile = open('Saved_WatchList.xml', 'wb')
        myfile.write(my)

    def __load_WatchList(self):
        tree = ET.parse('Saved_WatchList.xml')
        root = tree.getroot()
        count = len(self.tensor_watch_list)
        print(count)
        for elem in root:
            n = elem[0].text
            for t in self.all_ops:
                if t.name == n:
                    tem_select = self.TensorSelectItem(t.name, t.shape, t.op, self.tensor_input_list[0].name)
                    new = self.TensorWatchItem(tem_select)
                    self.tensor_watch_list.append(new)
                    print('now',len(self.tensor_watch_list), 'but count: ', count)
                    self.__open_tensor_view(count, elem[3].text)
                    break
            count += 1
                    
    def __create_main_window(self, args):
        self.main_window = MainWindow(
            {
             'filter_type_list':self.filter_type_list,
             'tensor_input_list': self.tensor_input_list,
             'on_close':self.__on_close,
             'on_save':self.__on_save,
             # global control
             'on_pause':self.__on_pause,
             'on_step':self.__on_step,
             'on_hide_all':self.__on_hide_all,
             'on_console_str_input':self.__on_console_str_input,
             'on_filter_type_select':self.__on_filter_type_select,
             'on_filter_str_input':self.__on_filter_str_input,
             'on_list_type_select':self.__on_list_type_select,
             ##
             'on_tensor_select':self.__on_tensor_select,
             # tensor select panel
             'on_tensor_shape_input':self.__on_tensor_shape_input,
             'on_input_select':self.__on_input_select,
             # tensor watch panel
             'on_remove_watch':self.__on_remove_watch,
             'on_add_watch':self.__on_add_watch,
             'on_set_show':self.__on_set_show,

             'load_WatchList':self.__load_WatchList,
             'add_input':self.__add_input
             }
            )
        return None

    def __init__(self, filter_type_list, input_list, loaded_list):
        for input_name in input_list:
            self.tensor_input_list.append(self.TensorInputItem(input_name, None))
        self.filter_str = ""
        self.filter_type_list = filter_type_list

        self.pyqt_env = PyQTEnv()

        self.pyqt_env.run(self.__create_main_window, None)
        
        self.main_window.update_input_list(self.tensor_input_list)

        print('control_panel _init')
        self.all_ops = loaded_list

        ### add_input test
        #for test/alexnet
        #self.__add_input('img_input')
        #for test/basic_test
        #self.__add_input('test_input')
        #self.pyqt_env.run(self.__load_input, None)
    '''
    def __load_input(self, args):
        ### add_input test
        #for test/alexnet
        self.__add_input('my_img_input', '../alexnet/img_input.py')
        #for test/basic_test
        self.__add_input('test_input', '../basic_test/test_input.py')
    '''

    def __get_input_obj(self, name):
        for input_item in self.tensor_input_list:
            if input_item.name == name:
                return input_item.input_obj
        return None

    def __add_input(self, input_name, filename, config_dict={}):
        import importlib
        try:
            placeholder_dict={}
            for t in self.all_ops:
                if t.op.op.type == 'Placeholder':
                    placeholder_dict[t.name] = t.op 
            names = os.path.split(os.path.abspath(filename))
            path = names[0]
            module_name = names[1].split('.')[-2]
            print('* input_name is: %s, filename is: %s'%(input_name, filename))
            print('* config_dict is:', config_dict)
            print('* module path is: %s, name is: %s'%(path, module_name))
            #add module search path
            sys.path.append(path)
            
            temp_module = importlib.import_module(module_name)
            input_obj = temp_module.TensorInput(placeholder_dict, config_dict)
            input_obj.show()

            input_item = self.TensorInputItem(input_name, input_obj)
            self.tensor_input_list.append(input_item)
            self.main_window.update_input_list(self.tensor_input_list)
        except Exception as e: 
            print('Add_input error:', e)

    """
    public methods
    """
    def update_tensor_list(self, tensor_list):
        self.tensor_select_list = []
        for t in tensor_list:
            if len(self.tensor_input_list)>0:
                input_name = self.tensor_input_list[0].name
            else:
                input_name = ''
            self.tensor_select_list.append(self.TensorSelectItem(t[0], t[1], t[2], input_name))
        if self.cur_list_type == 0:
            self.select_list_cur_pos = 0
            self.main_window.update_tensor_list(list_type=self.cur_list_type, list=self.tensor_select_list, pos=0, reset_pos=True)

    def get_tensor_watch_list(self):
        dict = {}
        for input_item in self.tensor_input_list:
            list = []
            for t in self.tensor_watch_list:
                if t.pyqt_window_id is not None and input_item.name == t.input_name:
                    list.append((t.name, t.reshape, t.op, t.data_source, t.input_name))
            if len(list)>0:
                dict[input_item] = list
        return dict

    def beat(self, update_step_flag):
        if update_step_flag:
            self.single_step_flag = False
            ControlPanel.step_count += 1
        if self.quit:
            self.pyqt_env.quit()
        return not self.quit

    def is_pause(self):
        return self.pause

    def is_step(self):
        return self.single_step_flag

    def get_filter_type(self):
        return [self.filter_type_list[self.cur_filter_type_index], self.filter_str]

    def get_console_command(self):
        if len(self.console_cmd_list)>0:
            cmd = self.console_cmd_list.pop()
            return cmd
