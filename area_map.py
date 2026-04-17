from matplotlib import pyplot as plt, ticker
import numpy as np

from trajectory_math import get_max_area_custom

class AreaMap:
    def __init__(self, y0 = -1.423, size = 200, t_range = (.5,1.5), v_range = (0,20), area_itr = 18) -> None:
        self.y0 = y0
        self.size = size
        self.t_min, self.t_max = t_range
        self.v_min, self.v_max = v_range
        self.area_itr = area_itr

        self.map = np.zeros((size,size))

        self.t_at_index = np.linspace(self.t_min,self.t_max, size)
        self.v_at_intex = np.linspace(self.v_min,self.v_max, size)

        self.T_line: np.ndarray | None = None
        self.V_line: np.ndarray | None = None
    

    def init_map(self):
        for i in range(self.size):
            print(i*100/self.size)
            for j in range(self.size):
                t = self.t_at_index[i]
                v = self.v_at_intex[j]
                res = get_max_area_custom(v, t, self.y0, 5, 1, self.area_itr)

                if res > 100:
                    res = 0
            
                self.map[j][i] = res
    

    def show_map(self):
        fig, ax = plt.subplots()


        img = plt.imshow(self.map, norm='linear', cmap='magma', origin='lower')
        plt.xlabel('initial angle radians')
        plt.ylabel('initial velocity m/s')

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * ((self.t_max - self.t_min)/self.size) + self.t_min)))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y * ((self.v_max - self.v_min)/self.size) + self.v_min)))

        if self.T_line is not None and self.V_line is not None:
            T_unscalled = np.interp(self.T_line, xp=(self.t_min, self.t_max), fp=(0,self.size-1)) 
            V_unscalled = np.interp(self.V_line, xp=(self.v_min, self.v_max), fp=(0,self.size-1)) 
            plt.plot(T_unscalled, V_unscalled)

        plt.xlim((0, self.size))
        plt.ylim((0, self.size))

        plt.show()

    def save_map(self, filepath:str):
        np.save(filepath, self.map)

    def load_map(self, filepath:str):
        self.map = np.load(filepath)

    def find_best_fit_line(self, t_cutoff = 0.9):
        V = np.argmax(self.map, axis=0)
        T = np.arange(0, self.size)

        V = np.interp(V, xp=(0,self.size-1), fp=(self.v_min, self.v_max))
        T = np.interp(T, xp=(0,self.size-1), fp=(self.t_min, self.t_max))

        T = T[T > t_cutoff]

        min_index = self.size - len(T)

        V = V[min_index:]

        self.T_line = T
        self.V_line = V
    


