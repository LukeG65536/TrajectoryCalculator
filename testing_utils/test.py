from trajectory_math import *

v,t,y0 = 9,1,-2


to_min = lambda x: -get_area(v,t,-2,x*1, x*.1, get_dist(v,t,-2), 0.595)

# better = to_min(.292)

res = get_max_area(v,t,y0,1,.1)
res2 = get_max_area_custom(v,t,y0,1,.1,15)

print(f'{res} and {res2} diff {res-res2}')