import matplotlib
import scipy
matplotlib.use('QtAgg')
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
from trajectory_math import *
from scipy.optimize import minimize_scalar




def get_vel(t, dist, y0 = (-2+.577)):
    def f(x):
        f = 100
        try:
            f = get_dist(x, t, y0) - dist
        except Exception:
            pass
        return f
    
    minimize_scalar(f, bounds=((1,10)))

print(get_vel(0.7, 3))