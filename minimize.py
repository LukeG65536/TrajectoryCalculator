import matplotlib
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
from trajectory_math import get_divergence,get_dist,get_optimal_from_dist
from scipy import optimize

row = 500
col = 500

t_min,t_max = .5,1.5
v_min,v_max = 6,15

line_res = 200

x_cords = np.linspace(t_min,t_max, row)
y_cords = np.linspace(v_min,v_max, col)

arr = np.zeros((row,col,2))

for i in range(row):
    for j in range(col):
        t = x_cords[i]
        v = y_cords[j]
        res = get_divergence(v,t)
        if res > 100:
            res = None
        arr[j][i][0] = res
        arr[j][i][1] = get_dist(v,t,-2)

dists = np.linspace(1,20,line_res)

X = np.zeros((line_res))
Y = np.zeros((line_res))

for i in range(line_res):
    res = get_optimal_from_dist(dists[i])
    X[i] = (res[1]-t_min)*(row/(t_max-t_min))
    Y[i] = (res[0]-v_min)*(col/(v_max-v_min))


fig, ax = plt.subplots()



        
img = plt.imshow(arr[:,:,0], norm='log', cmap='inferno', origin='lower')
plt.xlabel('initial angle radians')
plt.ylabel('initial velocity m/s')

ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * ((t_max-t_min)/row)+t_min)))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y * ((v_max-v_min)/row)+v_min)))

# CS = ax.contour(arr[:,:,1], 20, colors='black')
# plt.clabel(CS, inline=True, fontsize=10)
plt.plot(X,Y, color='red')




plt.show() 
