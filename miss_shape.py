import matplotlib
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
from trajectory_math import *
from scipy import optimize

row = 400
col = 400

t_min,t_max = -.7,.7
v_min,v_max = 0,100

line_res = 200

x_cords = np.linspace(t_min,t_max, row)
y_cords = np.linspace(v_min,v_max, col)

v_innit = 9-.7
t_innit = np.pi/4+.25

arr = np.zeros((row,col,2))
dist = get_dist(v_innit,t_innit,-2)

for i in range(row):
    print(i*100/row)
    
    for j in range(col):
        t = x_cords[i]
        v = y_cords[j]
        # res = get_divergence(v,t)
        # res = get_error((v,t,0))
        # res = get_ball_shadow_width(v,t,-2)
        # res = get_max_area_custom(v,t,-2,.001,1,20)
        res = 0
        if goes_in(v_innit+v,t_innit+t,-2,dist,1.19/2):
            res = 1


        if res > 100:
            res = 0
     
        arr[j][i][0] = res
        arr[j][i][1] = get_dist(v,t,-2)

dists = np.linspace(0.1,22,line_res)

X1 = np.zeros((line_res))
Y1 = np.zeros((line_res))
X2 = np.zeros((line_res))
Y2 = np.zeros((line_res))

# for i in range(line_res):
#     res = get_optimal_from_dist_old(dists[i])
#     X1[i] = (res[1]-t_min)*(row/(t_max-t_min))
#     Y1[i] = (res[0]-v_min)*(col/(v_max-v_min))

# for i in range(line_res):
#     res = get_optimal_from_dist(dists[i])
#     X2[i] = (res[1]-t_min)*(row/(t_max-t_min))
#     Y2[i] = (res[0]-v_min)*(col/(v_max-v_min))


fig, ax = plt.subplots()



        
img = plt.imshow(arr[:,:,0], norm='linear', cmap='magma', origin='lower')
plt.xlabel('initial angle radians')
plt.ylabel('initial velocity m/s')

ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * ((t_max-t_min)/row)+t_min)))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y * ((v_max-v_min)/row)+v_min)))

# CS = ax.contour(arr[:,:,1], 10, colors='blue')
# plt.clabel(CS, inline=True, fontsize=10)
# plt.plot(X1,Y1, color='blue')
# plt.plot(X1,Y1, color='blue')


plt.xlim((0,row))
plt.ylim((0,col))

# np.save('.5k_1:1000', arr[:,:,0])


plt.show() 
