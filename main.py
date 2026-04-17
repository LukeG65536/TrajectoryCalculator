import math

from area_map import AreaMap
from trajectory_table import TrajectoryTable


calculated_table = TrajectoryTable.from_file("tables/hi.csv")

manual_table = TrajectoryTable.from_file("tables/manual.csv")

for i,val in enumerate(manual_table.thetas):
    rad = 2*math.pi*val / 12
    manual_table.thetas[i] = 1.39626 - rad

manual_table.save_table("tables/manual2.csv")