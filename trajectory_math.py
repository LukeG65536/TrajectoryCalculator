import numpy as np


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


def get(v,t):
    return (get_dtdx(v,t,-2)**2+get_dvdx(v,t,-2)**2)**.5

def get_dist(v,t,y0):
    g=-10.0
    a = get_a(v,t,g)
    b = get_b(t)
    c = y0
    u=get_u(a,b,c)

    return (-b-u**.5)*(.5)*(1/a)


