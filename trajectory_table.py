from __future__ import annotations

import csv
import re
from typing import List

import numpy as np

from area_map import AreaMap
from trajectory_math import get_dist, get_vel




class TrajectoryTable:
    def __init__(self, dists: List[float], thetas: List[float], vels: List[float], y0 = -1.423):
        self.dists = dists
        self.thetas = thetas
        self.vels = vels
        self.y0 = y0

    
    @classmethod
    def from_areamap(cls, area_map: AreaMap, stepsize: int = 1, y0 = -1.423):
        if area_map.T_line is None or area_map.V_line is None:
            raise ValueError("Line not found yet.")
        T = area_map.T_line.tolist()
        V = area_map.V_line.tolist()
        D = []

        for t, v in list(zip(T, V))[::stepsize]:
            D.append(get_dist(v, t, area_map.y0))
        
        return cls(D, T, V, y0)
    

    @classmethod
    def from_file(cls, filepath:str, y0 = -1.423):
        D = []
        T = []
        V = []

        def check_row(row: List[str]):
            num = r"-?\d+\.\d+"
            space = r"\s*"
            pattern = f"^{space}{num}{space}$"
            for item in row:
                if not bool(re.match(pattern, item)):
                    return False
            return True

        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

                if not check_row(row):
                    continue

                D.append(float(row[0]))
                T.append(float(row[1]))
                V.append(float(row[2]))
        return cls(D, T, V, y0)


    def save_table(self, filepath:str):
        data = list(zip(self.dists, self.thetas, self.vels))

        print(f"dists {self.dists} thetas {self.thetas}")

        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def calibrate_vels(self, other: TrajectoryTable):
        commanded_vels = []
        actual_vels = []

        for i,val in enumerate(other.vels):
            commanded_vels.append(val)

            actual_vels.append(get_vel(other.thetas[i], other.dists[i], other.y0))

        slope, intercept = np.polyfit(np.asarray(actual_vels), np.asarray(commanded_vels), 1)

        for i,val in enumerate(self.vels):
            self.vels[i] = val * slope + intercept
    
    def export_java_arr(self, filepath:str):
        with open(filepath, 'w') as file:
            file.write(f" = {{\n")

            for dist, theta, vel in zip(self.dists, self.thetas, self.vels):
                file.write(f"\t{{{dist}, {theta}, {vel}}},\n")

            file.write(f'}};')


