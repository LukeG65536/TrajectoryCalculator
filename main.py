import math
import matplotlib
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import trajectory_math

row = 1000
col = 1000

t_min,t_max = .5,1.5
v_min,v_max = 6,12

x_cords = np.linspace(t_min,t_max, row)
y_cords = np.linspace(v_min,v_max, col)

plt.xlim((t_max,t_max))
plt.ylim((v_min,v_max))

arr = np.zeros((row,col,2))

# input = np.meshgrid(x_cords, y_cords)

# arr = np.fromfunction(lambda: trajectory_math.get, (row,col), dtype=float)


for i in range(row):
    for j in range(col):
        t = x_cords[i]
        v = y_cords[j]
        res = trajectory_math.get(v,t)
        if res > 100:
            res = None
        arr[j][i][0] = res
        arr[j][i][1] = trajectory_math.get_dist(v,t,-2)


fig, ax = plt.subplots()

        
img = plt.imshow(arr[:,:,0], norm='log', cmap='plasma', origin='lower')
plt.xlabel('initial angle radians')
plt.ylabel('initial velocity m/s')

ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * ((t_max-t_min)/row)+t_min)))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y * ((v_max-v_min)/row)+v_min)))


# plt.imshow(arr[:,:,1], norm='log', cmap='plasma')

# plt.colorbar()


# plt.contour(arr[:,:,0], 20, colors='red')
CS = plt.contour(arr[:,:,1], 20, colors='black')
# plt.clabel(CS, inline=True, fontsize=10)
# plt.clabel(CS, CS.levels, fontsize=10)


plt.show() 
