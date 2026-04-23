from matplotlib import pyplot as plt, ticker
import numpy as np

# from app import MplCanvas
from trajectory_math import get_max_area_custom

class AreaMap:
    def __init__(self, y0 = -1.423, range = 0.595, size = 200, t_range = (.5,1.5), v_range = (0,20), area_itr = 18) -> None:
        self.y0 = y0
        self.range = range
        self.size = size
        self.t_min, self.t_max = t_range
        self.v_min, self.v_max = v_range
        self.area_itr = area_itr

        self.map = np.zeros((size,size))


        # create an array that maps from pixel space (x,y) to the actual map space of (t,v)
        self.t_at_index = np.linspace(self.t_min,self.t_max, size)
        self.v_at_intex = np.linspace(self.v_min,self.v_max, size)

        # sets up the line of best fit as null at first but still specify the future type
        self.T_line: np.ndarray | None = None
        self.V_line: np.ndarray | None = None
    

    def init_map(self):
        # for each pixel (i,j) 
        for i in range(self.size):
            print(i*100/self.size)
            for j in range(self.size):
                # Get the t and v values from the pixel -> position mapping
                t = self.t_at_index[i]
                v = self.v_at_intex[j]
                # get the rating of how good the shot is
                res = get_max_area_custom(v, t, self.y0, 5, 1, self.area_itr, self.range)


                if res > 100:
                    res = 0
            
                self.map[j][i] = res
# functin to render the current graph to a matplotlib axes object
    def render_to_axes(self, ax):

        ax.imshow(self.map, norm='linear', cmap='magma', origin='lower')
        ax.set_xlabel('initial angle radians')
        ax.set_ylabel('initial velocity m/s')


        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * ((self.t_max - self.t_min)/self.size) + self.t_min)))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y * ((self.v_max - self.v_min)/self.size) + self.v_min)))
        # if the line is defined then render else dont render them
        if self.T_line is not None and self.V_line is not None:
            T_unscalled = np.interp(self.T_line, xp=(self.t_min, self.t_max), fp=(0,self.size-1)) 
            V_unscalled = np.interp(self.V_line, xp=(self.v_min, self.v_max), fp=(0,self.size-1)) 
            ax.plot(T_unscalled, V_unscalled)

        ax.set_xlim((0, self.size))
        ax.set_ylim((0, self.size))


    def show_map(self):
        fig, ax = plt.subplots()

        self.render_to_axes(ax)

        plt.show()

    
# basic numpy built in save and load stuff
    def save_map(self, filepath:str):
        np.save(filepath, self.map)

    def load_map(self, filepath:str):
        self.map = np.load(filepath)



    def find_best_fit_line(self, t_cutoff = 0.9):
        # get the max value for each vertical row in the map, creating an array of V indexes 
        V = np.argmax(self.map, axis=0)
        # make an array of T values from 0,size
        T = np.arange(0, self.size)

        #scale each point (V,T) from pixel space into (theta,velocity) space
        V = np.interp(V, xp=(0,self.size-1), fp=(self.v_min, self.v_max))
        T = np.interp(T, xp=(0,self.size-1), fp=(self.t_min, self.t_max))

        # basic cutoff to trim the inconsistant data around the edge
        T = T[T > t_cutoff]
        min_index = self.size - len(T)
        V = V[min_index:]


        self.T_line = T
        self.V_line = V
    


