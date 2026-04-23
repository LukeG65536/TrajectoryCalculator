import unittest
from unittest.mock import patch
import numpy as np
from area_map import AreaMap
from trajectory_table import TrajectoryTable

class TestCalibration(unittest.TestCase):
    def test_calibration(self):
        area_map = AreaMap(size=50)
        area_map.init_map()
        area_map.find_best_fit_line()
        table = TrajectoryTable.from_areamap(area_map)
        original = table.vels
        table.calibrate_vels(table)
        for orig, cal in zip(original, table.vels):
            self.assertAlmostEqual(orig, cal, places=2)

    def test_csv_roundtrip(self):
        original = TrajectoryTable([1.5, 2.5], [0.9, 1.1], [6.0, 9.0])
        original.save_table("/tmp/test_table.csv")
        loaded = TrajectoryTable.from_file("/tmp/test_table.csv")
        for o, l in zip(original.dists, loaded.dists):
            self.assertAlmostEqual(o, l, places=5)

unittest.main()