import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

class TensorData(object):
    def __init__(self, start_step=0):
        self.data = []
        self.data_shape = []
        self.dirty = False
        self.__start_step = start_step

    def set_data(self, data):
        self.data_shape.append(data.shape)
        self.data.append(data)
        self.dirty = True

    """
    index: index of data
          -1 is for last step
    return simulation step
    """
    """
    def get_index(self, step):
        return step - self.__start_step

    def get_step(self, index):
        if index == -1:
            step = len(self.data) - 1
        else:
            step = index
        return self.__start_step + step
    """

    def get_steps(self):
        return np.arange(self.__start_step, self.__start_step + len(self.data))

    def get_step_range(self):
        return [self.__start_step, self.__start_step + len(self.data)]

    def get_data(self, step):
        if step==-1:
            index = -1
        else:
            index = step - self.__start_step
        return self.data[index]

    def clear_dirty(self):
        self.dirty = False
