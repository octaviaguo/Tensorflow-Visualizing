import tensorflow as tf
import numpy as np
import sys
sys.path.append("../../")
from TensorMonitor.tensor_manager import TensorMonitor

N_A = 30
step_count = 0
mu = tf.placeholder(tf.float32, [1], 'mu')
sigma = tf.placeholder(tf.float32, [1], 'sigma')
s = tf.placeholder(tf.float32, [None, N_A], 'A')
normal_dist = tf.distributions.Normal(mu, sigma)

prob = normal_dist.prob(s)
log_prob = normal_dist.log_prob(s)
#sample = tf.squeeze(normal_dist.sample(10000), axis=0)

TensorMonitor.AddUserList(
    mu=mu,
    sigma=sigma,
    prob_a = prob,
    log_prob_a = log_prob
    )

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init)

    while True:
        a = np.linspace(-3.14,3.14,N_A)
        cmd = TensorMonitor.Beat(sess, input1={s:a[np.newaxis,:], mu:np.array([0]), sigma:np.array([100])},input2={s:a[np.newaxis,:], mu:np.array([0]), sigma:np.array([100])})
        step_count += 1
        print('step %d'%step_count)
        if cmd == 'quit':
            break

print('quit done')
sys.exit(0)