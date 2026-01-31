import matplotlib
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
from trajectory_math import *
from scipy import optimize

arr = np.load('maps/2.5k_5:1.npy')


fig, ax = plt.subplots()

col = 2500
row = 2500
t_min,t_max = .5,1.5
v_min,v_max = 6,15


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



# np.save('lines/X_5:1_Unscaled.npy',X)
# np.save('lines/Y_5:1_Unscaled.npy',Y)

T = ((t_max-t_min)/col)*X + t_min
V = ((v_max-v_min)/col)*Y + v_min

dist = get_dist(V,T,-2)

# dist_to_vel_constants = np.polyfit(dist,V,7)


# vel_ests = dist_to_vel_constants[7] + dist_to_vel_constants[6]*dist + dist_to_vel_constants[5]*dist**2 + dist_to_vel_constants[4]*dist**3 + dist_to_vel_constants[3]*dist**4 + dist_to_vel_constants[2]*dist**5 + dist_to_vel_constants[1]*dist**6 + dist_to_vel_constants[0]*dist**7



# plt.scatter(dist,V,s=.5)
# plt.scatter(dist,vel_ests,s=.5)


# print(dist_to_vel_constants)

T2 = T[::100]
V2 = V[::100]

with open('best_angles.txt','w') as file:
    file.write(f'double[][] optimalPoses = {{\n')
    for i in range(len(T2)):
        dist = get_dist(V2[i],T2[i],-2)
        file.write(f'{{{dist},{T2[i]},{V2[i]}}},\n')
    file.write(f'}};')

plt.plot(T,V)
plt.plot(T2,V2)

# coef = np.polyfit(dist,)

# plt.xlim((0,row))
# plt.ylim((0,col))

# np.save('2.5k_5:1', arr[:,:,0])


plt.show() 
