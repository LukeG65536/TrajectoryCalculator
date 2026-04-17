from __future__ import annotations

import csv
from typing import List

from area_map import AreaMap
from trajectory_math import get_dist




class TrajectoryTable:
    def __init__(self, dists: List[float], thetas: List[float], vels: List[float]):
        self.dists = dists
        self.thetas = thetas
        self.vels = vels

    
    @classmethod
    def from_areamap(cls, area_map: AreaMap, stepsize: int = 1):
        if area_map.T_line is None or area_map.V_line is None:
            raise ValueError("Line not found yet.")
        T = area_map.T_line.tolist()
        V = area_map.V_line.tolist()
        D = []

        for t, v in list(zip(T, V))[::stepsize]:
            D.append(get_dist(v, t, area_map.y0))
        
        return cls(D, T, V)
    

    @classmethod
    def from_file(cls, filepath:str):
        D = T = V = []

        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                D.append(float(row[0]))
                T.append(float(row[1]))
                V.append(float(row[2]))
        return cls(D, T, V)


    def save_table(self, filepath:str):
        data = zip(self.dists, self.thetas, self.vels)

        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    # def calibrate_vels(self, other: TrajectoryTable):
        
