import matplotlib
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
from trajectory_math import *
from scipy import optimize

X = np.load('lines/X_5:1_Unscaled.npy')
Y = np.load('lines/Y_5:1_Unscaled.npy')

X = X/2.5
Y = Y/2.5

arr = np.load('1k_20:1.npy')

plt.plot(X,Y, color='white')

img = plt.imshow(arr, norm='linear', cmap='magma', origin='lower')

Y1 = np.argmax(arr, axis=0)
X1 = np.arange(0,1000)

plt.plot(X1,Y1, color='cyan')

plt.show()