import math

from area_map import AreaMap
from trajectory_table import TrajectoryTable


calculated_table = TrajectoryTable.from_file("tables/hi.csv")

manual_table = TrajectoryTable.from_file("tables/manual2.csv")

calculated_table.calibrate_vels(manual_table)

calculated_table.save_table("tables/calculated_calibrated.csv")

calculated_table.export_java_arr("hi.txt")