from os import path
import time
import argparse

import config
import utils
import model

import tensorflow as tf
sess = tf.InteractiveSession()
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np


____section____ = utils.section_print()
mnist = input_data.read_data_sets(
    path.join(config.path_main, 'MNIST_data'), one_hot=True)

# Parse arguments
parser = argparse.ArgumentParser(description='MNIST bounding box parameters')
parser.add_argument('--batch-size', type=int, default=50, metavar='N',
                    help='input batch size for training (default: 50)')
parser.add_argument('--lr', type=float, default=0.001, metavar='LR',
                    help='learning rate (default: 0.001)')
parser.add_argument('--background-noise', action='store_true', default=False,
                    help='add randomnoise to background')
args = parser.parse_args()


____section____('Generate synthetic bounding boxes')

train = utils.reshape_to_img(mnist.train.images)
validation = utils.reshape_to_img(mnist.validation.images)
test = utils.reshape_to_img(mnist.test.images)

bounds_train = utils.get_data_to_box(train) * 1. / 28
bounds_validation = utils.get_data_to_box(validation) * 1. / 28
bounds_test = utils.get_data_to_box(test) * 1. / 28

bounding_box_grid_generated = utils.plot_bounding_grid(
    df=train,
    subplot_shape=(4, 6),
    bounding_boxes=bounds_train,
)
bounding_box_grid_generated.savefig(
    path.join(config.path_outputs, 'bounding_box_grid_generated.png'))


____section____('Gathering and formatting data')
if args.background_noise:
    print('Adding noise to background')
    X_test = utils.add_background_noise(mnist.test.images)
    X_train = utils.add_background_noise(mnist.train.images)
    X_validation = utils.add_background_noise(mnist.validation.images)
else:
    X_test = mnist.test.images
    X_train = mnist.train.images
    X_validation = mnist.validation.images

X_test = X_test.reshape((mnist.test.num_examples, 28, 28))
X_train = X_train.reshape((mnist.train.num_examples, 28, 28))
X_validation = X_validation.reshape((mnist.validation.num_examples, 28, 28))

batch_X_train = np.split(X_train, mnist.train.num_examples / args.batch_size)
batch_bounds_train = np.split(
    bounds_train, mnist.train.num_examples / args.batch_size)


____section____('Learn and predict bounding box')
start = time.time()
pred_validation = model.train_model(
    args.lr, batch_X_train, X_validation,
    batch_bounds_train, bounds_validation)
print('Training completed in {:.0f} seconds'.format(time.time() - start))

bounding_box_grid_estimated = utils.plot_bounding_grid(
    df=X_validation,
    subplot_shape=(4, 6),
    bounding_boxes=pred_validation,
)
bounding_box_grid_estimated.savefig(
    path.join(config.path_outputs, 'bounding_box_grid_estimated.png'))
