import math
import numpy as np
from scipy import optimize


def get_du(a,b,c,da,db,dc):
    return 2*b*db-4*(a*dc+c*da)

def get_u(a,b,c):
    return b**2-4*a*c

def get_dx(a,b,c,da,db,dc):
    u=get_u(a,b,c)
    du=get_du(a,b,c,da,db,dc)
    top = 2*a*(-db-.5*(u**-.5)*du)-(-b-u**.5)*2*da
    return top * (1/4) * (1/(a**2)) 

def get_a(v,t,g):
    return (g/2)*((np.cos(t)*v)**-2)

def get_da(v,t,dv,dt,g):
    return -g*((np.cos(t)*v)**-3)*(np.cos(t)*dv-np.sin(t)*dt*v)

def get_b(t):
    return np.tan(t)

def get_db(t):
    return (1/np.cos(t))**2

# def get_ball_shadow_width(t_f):
#     return - (1/np.sin(t_f))

def get_ball_shadow_width(v,t,y0):
    dydx = get_a(v,t,-10)*2*get_dist(v,t,y0) + np.tan(t)
    return -(1)/(np.sin(np.atan(dydx)))


def get_dvdx(v,t,y0):
    g=-10.0
    a = get_a(v,t,g)
    b = get_b(t)
    c = y0
    da = get_da(v,t,1,0,g)
    # db = get_db(t)
    return get_dx(a,b,c,da,0,0)


def get_dtdx(v,t,y0):
    g=-10.0
    a = get_a(v,t,g)
    b = get_b(t)
    c = y0
    da = get_da(v,t,0,1,g)
    db = get_db(t)
    return get_dx(a,b,c,da,db,0)


def get_divergence(v,t):
    return (get_dtdx(v,t,-2)**2+get_dvdx(v,t,-2)**2)**.5

# def get_divergence_window(v,t):
#     width = get_ball_shadow_width(v,t,-2)
#     return ((get_dtdx(v,t,-2)*width)**2+(get_dvdx(v,t,-2)*width)**2)**.5

def get_error(input):
    v,t,dist = input
    res = get_divergence(v,t) + (dist - get_dist(v,t,-2))**2
    if math.isnan(res): return 10000
    return res


# def get_window_error(input):
#     v,t,target_dist = input
#     res = get_divergence_window(v,t)
#     if math.isnan(res): return 10000
#     return res

def get_dist(v,t,y0):
    g=-10.0
    a = get_a(v,t,g)
    b = get_b(t)
    c = y0
    u=get_u(a,b,c)

    return (-b-u**.5)*(.5)*(1/a)

def get_area(v,t,y0,dv,dt,target_dist,max_dx):
    dists = []
    # print(dv)
    dists.append(get_dist(v+dv,t+dt,y0))
    dists.append(get_dist(v+dv,t-dt,y0))
    dists.append(get_dist(v-dv,t+dt,y0))
    dists.append(get_dist(v-dv,t-dt,y0))
    for dist in dists:
        error = np.abs(target_dist-dist)
        if np.isnan(error):
            return 1000
        if error > max_dx:
            return -error
        
    return dv*dt

def get_max_area_custom(v,t,y0,dv_multi,dt_multi,iter):
    current_best = 0
    current_step = 1
    target_dist = get_dist(v,t,y0)

    for i in range(iter):
        test = current_best + current_step
        dv = test * dv_multi
        dt = test * dt_multi
        if goes_in_worst_case(v, t, y0, dv, dt, target_dist):
            current_best = test
            continue
        current_step = current_step/2
        
    return current_best
        

def goes_in_worst_case(v,t,y0,dv,dt, dist):
    return goes_in(v+dv, t+dt, y0, dist, 0.595) and goes_in(v-dv, t+dt, y0, dist, 0.595) and goes_in(v+dv, t-dt, y0, dist, 0.595) and goes_in(v-dv, t-dt, y0, dist, 0.595)

def goes_in(v,t,y0,target_dist,max_dx):
    error = np.abs(target_dist-get_dist(v,t,y0))
    return error < max_dx


def get_max_area(v,t,y0,dv_multi,dt_multi):
    target = get_dist(v,t,y0)
    init_guess = 0
    options = {'maxiter':500}
    to_min = lambda x: -get_area(v,t,y0,x[0]*dv_multi, x[0]*dt_multi, target, 0.595)
    res = optimize.minimize(to_min,init_guess,method='Nelder-Mead',options=options)
    return res.x
    

def get_optimal_from_dist(dist):
    init_guess = (10,1,0)
    options = {'maxiter':1000}
    to_min = lambda x: -get_area(x[0],x[1],-2,x[2]*1, x[2]*.5, dist, 0.595)
    res = optimize.minimize(to_min,init_guess,options=options)
    return res.x


def get_optimal_from_dist_old(dist):
    init_guess = (15,.7,dist)
    bounds = ((6,20),(.5,1.5),(dist,dist))
    res = optimize.minimize(get_error,init_guess,bounds=bounds)
    # print(res)
    return res.x