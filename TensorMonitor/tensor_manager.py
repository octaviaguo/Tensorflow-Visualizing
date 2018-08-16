import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import sys
import fnmatch
from control_panel import ControlPanel
import time
if sys.version_info[0] >= 3:
    from functools import reduce

class TensorMonitor(object):
    filter_types = [
        'USER_LIST',
        'TRAINABLE_VARIABLES',
        'ACTIVATIONS',
        'GLOBAL_VARIABLES',
        'ALL_OPS']
    user_tensor_list = []
    control_panel = None

    class Tensor:
        name = None
        shape = None
        op = None
        filter_str = None
        def __init__(cls, name, shape, op):
            cls.name = name
            cls.shape = shape
            cls.op = op

    @classmethod
    def __update_tensor_list(cls, session):
        cls.tensor_list = []
        cls.tensor_list_1 = []
        if cls.filter_type == 'USER_LIST':
            for t in cls.user_tensor_list:
                cls.tensor_list.append(t)
        elif cls.filter_type == 'TRAINABLE_VARIABLES':
            tensors = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            for t in tensors:
                #print(t.op.type)
                cls.tensor_list.append(cls.Tensor(t.name, t.get_shape(), t))
        elif cls.filter_type == 'GLOBAL_VARIABLES':
            tensors = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
            for t in tensors:
                cls.tensor_list.append(cls.Tensor(t.name, t.get_shape(), t))
        elif cls.filter_type == 'ACTIVATIONS':
            for t in tf.get_default_graph().get_operations():
                try:
                    tensor = t.values()[0]
                    #print(tensor.op.type)
                    if tensor.op.type in ('Relu', 'Softplus', 'Relu6', 'Tanh'):
                        cls.tensor_list.append(cls.Tensor(t.name, tensor.get_shape(), tensor))
                except:
                    continue
        else:
            for t in session.graph.get_operations():
                if cls.filter_str != '' and cls.filter_str in t.name:
                    try:
                        tensor = t.values()[0]
                        shape = tensor.get_shape()
                        if len(shape) > 0 or True:
                            cls.tensor_list.append(cls.Tensor(t.name, shape, tensor))
                    except:
                        continue
                if cls.filter_str == '':
                    try:
                        tensor = t.values()[0]
                        shape = tensor.get_shape()
                        if len(shape) > 0 or True:
                            cls.tensor_list.append(cls.Tensor(t.name, shape, tensor))
                    except:
                        continue
                        


    @classmethod
    def __init(cls, session, input_list):
        cls.filter_type = None
        cls.filter_str = ""
        cls.control_panel = ControlPanel(
            filter_type_list=cls.filter_types,
            input_list=input_list
            )

    @classmethod
    def __check(cls, session):
        (filter_type, filter_str) = cls.control_panel.get_filter_type()
        if (cls.filter_type != filter_type) or \
          (cls.filter_type=='ALL_OPS' and cls.filter_str != filter_str):
            cls.filter_type = filter_type
            cls.filter_str = filter_str
            cls.__update_tensor_list(session)
            cls.control_panel.update_tensor_list(tensor_list=[(t.name, t.shape, t.op) for t in cls.tensor_list])

    @classmethod
    def AddUserList(cls, **args):
        #print(args.keys())
        for name in args.keys():
            tensor = cls.Tensor(name, args[name].shape, args[name])
            #tensor = cls.Tensor(args[name].name, args[name].shape, args[name])
            cls.user_tensor_list.append(tensor)

    @classmethod
    def Beat(cls, session, **args):
        if cls.control_panel is None:
            cls.__init(session, args.keys())

        tensor_watch_list = cls.control_panel.get_tensor_watch_list()
        if len(tensor_watch_list) > 0:
            for placeholder_name in args.keys():
                tensor_list = [t for t in tensor_watch_list if t[4]==placeholder_name]
                ops = [t[2] for t in tensor_list]
                r = session.run(ops, feed_dict=args[placeholder_name])
                #print(r)
                for i,t in enumerate(tensor_list):
                    data_source = t[3]
                    data_source.set_data(r[i])

        cls.__check(session)
        quit = not cls.control_panel.beat(True)

        while cls.control_panel.is_pause():
            if cls.control_panel.is_step():
                break
            cls.__check(session)
            quit = not cls.control_panel.beat(False)
            time.sleep(0.1)
            if quit:
                break

        if quit:
            return 'quit'
        else:
            return cls.control_panel.get_console_command()
