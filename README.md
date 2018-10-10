# Tensorflow-Visualizing
Wait for me to upload...
## Tensorflow Visualizing Tool
This is a tensorflow visualization tool that helps monitor the real-time data in TensorFlow programs. It is a general tool not only for CNN visualization, but also for some other deep learning code. By adding a few lines in the code, user can watch most of tensors they are interested in. It could help people debug the code and check if the code is learning the certain features, and gain a better insight of the neural network. 

The idea comes from the Deep Visualization Toolbox for Caffe (https://github.com/yosinski/deep-visualization-toolbox) and  the work of https://github.com/InFoCusp/tf_cnnvis. We want to build a general tool that implements some visualization functions of TensorBoard, but with simple APIs and easy setup. Moreover, with the help of high performance of pyqtgraph, this tool can render the real-time data during the training. 
Extensibility is also our consideration. For now, we provide 1-dimensional and 2-dimensional visualization, particularly for activations and filters of CNN. More types of visualization will be supported in the future.
