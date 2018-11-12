import numpy as np


"""
add_input('test_input')
"""

class TensorInput():
    def __init__(self, placeholder_dict, options_dict):
        self.feed_dict = {}
        self.placeholder_dict = placeholder_dict
        self.mu = 0
        self.sigma = 100
        print(placeholder_dict)

    def show(self):
        pass

    def prepare_input(self):
        N_A = 30
        a = np.linspace(-3.14,3.14,N_A)
        self.mu += 0.1
        self.sigma += 1
        self.feed_dict[self.placeholder_dict['A']] = a[np.newaxis,:]
        self.feed_dict[self.placeholder_dict['mu']] = np.array([self.mu])
        self.feed_dict[self.placeholder_dict['sigma']] = np.array([self.sigma])
        return self.feed_dict

    def get_config(self):
        config_dict = {}
        return config_dict