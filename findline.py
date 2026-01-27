import matplotlib
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
from trajectory_math import *
from scipy import optimize

arr = np.load('2.5k_5:1.npy')


fig, ax = plt.subplots()

col = 2500
row = 2500
t_min,t_max = .5,1.5
v_min,v_max = 6,15

 
img = plt.imshow(arr, norm='linear', cmap='magma', origin='lower')
plt.xlabel('initial angle radians')
plt.ylabel('initial velocity m/s')


Y1 = np.argmax(arr, axis=0)
X1 = np.arange(1250,row)

Y1 = Y1[1250:]
X1 = X1[::-1]
Y1 = Y1[::-1]

X2 = np.argmax(arr, axis=1)
X2 = X2[X2 < 1250]
X2 = X2[10 < X2]
# X2 = X2[::-1]
Y2 = np.arange(row-1782,row)

X = np.concatenate((X1,X2))
Y = np.concatenate((Y1,Y2))

np.save('lines/X_5:1_Unscaled.npy',X)
np.save('lines/Y_5:1_Unscaled.npy',Y)

T = ((t_max-t_min)/col)*X + t_min
V = ((v_max-v_min)/col)*Y + v_min


ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * ((t_max-t_min)/row)+t_min)))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y * ((v_max-v_min)/row)+v_min)))

# plt.plot(X1,Y1,color='cyan')
plt.scatter(X,Y,c=get_dist(V,T,-2),s=.5)


plt.xlim((0,row))
plt.ylim((0,col))

# np.save('2.5k_5:1', arr[:,:,0])


plt.show() 
