from __future__ import annotations
import os
import platform
import sys

os.environ["QT_API"] = "PyQt6"

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QDoubleSpinBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QProgressBar,
    QGroupBox, QFormLayout, QMessageBox, QFrame, QHeaderView,
    QScrollArea,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from area_map import AreaMap
from trajectory_table import TrajectoryTable

# Basic helper functions
def divider() -> QFrame:
    f = QFrame()
    f.setProperty("role", "divider")
    f.setFrameShape(QFrame.Shape.HLine)
    f.setMaximumHeight(1)
    return f

def tag(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("tag")
    return l

def head(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("head")
    return l

def dim(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("dim")
    l.setWordWrap(True)
    return l

# Matplotlib custom canvas object for rendering the maps
class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def refresh_style(self):
        self.draw()

# MapWorker Object that just takes an area_map and initializes that. 
class MapWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, area_map: AreaMap):
        super().__init__()
        self.area_map = area_map

    def run(self):
        try:
            from trajectory_math import get_max_area_custom
            m = self.area_map
            for i in range(m.size):
                for j in range(m.size):
                    t   = m.t_at_index[i]
                    v   = m.v_at_intex[j]
                    res = get_max_area_custom(v, t, m.y0, 5, 1, m.area_itr, m.range)
                    m.map[j][i] = 0 if res > 100 else res
                self.progress.emit(int((i + 1) * 100 / m.size))
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# Page 1 setup stuff __________________________________________________________________
class SetupPage(QWidget):
    proceed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        inner = QWidget()
        root = QVBoxLayout(inner)

        root.addWidget(head("Robot Setup"))
        root.addWidget(divider())

        phys = QGroupBox("Physical Setup")
        f = QFormLayout(phys)
        f.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.y0 = QDoubleSpinBox()
        self.y0.setRange(-10, 10)
        self.y0.setValue(-1.423)
        self.y0.setDecimals(2)
        self.y0.setSingleStep(0.1)


        self.range = QDoubleSpinBox()
        self.range.setRange(0, 5)
        self.range.setValue(0.595)
        self.range.setDecimals(2)
        self.range.setSingleStep(0.1)

        f.addRow("Shooter Height (m):", self.y0)
        f.addRow("Target Range (m):", self.range)
        
        root.addWidget(phys)

        rng = QGroupBox("Search Ranges")
        rf = QFormLayout(rng)
        rf.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def range_row(min_val, max_val, lo, hi):
            row = QHBoxLayout()
            lo_spin = QDoubleSpinBox()
            lo_spin.setRange(min_val, max_val)
            lo_spin.setValue(lo)
            hi_spin = QDoubleSpinBox()
            hi_spin.setRange(min_val, max_val)
            hi_spin.setValue(hi)
            row.addWidget(lo_spin)
            row.addWidget(hi_spin)
            return row, lo_spin, hi_spin

        a_row, self.t_min, self.t_max = range_row(0, 3.14, 0.5, 1.5)
        rf.addRow("Angle range (rad):", a_row)

        v_row, self.v_min, self.v_max = range_row(0, 200, 0.0, 20.0)
        rf.addRow("Velocity range (m/s):", v_row)
        root.addWidget(rng)

        ms = QGroupBox("Map Settings")
        mf = QFormLayout(ms)
        mf.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.map_size = QSpinBox(); self.map_size.setRange(5, 5000); self.map_size.setValue(200)
        mf.addRow("Map resolution (px):", self.map_size)

        self.area_itr = QSpinBox(); self.area_itr.setRange(1, 100); self.area_itr.setValue(18)
        mf.addRow("Area iterations:", self.area_itr)

        root.addWidget(ms)

        root.addStretch()

        btn = QPushButton("Map Generation")
        btn.setObjectName("primary")
        btn.setFixedHeight(44)
        btn.clicked.connect(self._emit)
        root.addWidget(btn)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(inner)
        outer.addWidget(scroll)

# the setup page should exit wit a dict that allows the next section to make a propper areamap
    def _emit(self):
        self.proceed.emit(dict(
            y0=self.y0.value(),
            range=self.range.value(),
            t_min=self.t_min.value(), t_max=self.t_max.value(),
            v_min=self.v_min.value(), v_max=self.v_max.value(),
            size=self.map_size.value(),
            area_itr=self.area_itr.value()
        ))
# Second page map renderer_______________________________________________________________
class MapPage(QWidget):
    proceed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.area_map: AreaMap | None = None
        self._worker: MapWorker | None = None

        root = QHBoxLayout(self)

        rail = QWidget()
        rail.setFixedWidth(250)
        rv = QVBoxLayout(rail)

        rv.addWidget(head("Shot Fidelity Map"))
        rv.addWidget(divider())

        self.map_status = dim("No map loaded.")
        rv.addWidget(self.map_status)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        rv.addWidget(self.progress)

        rv.addWidget(divider())

        gen_btn = QPushButton("Generate Map")
        gen_btn.setObjectName("primary"); gen_btn.setFixedHeight(40)
        gen_btn.clicked.connect(self._generate)
        rv.addWidget(gen_btn)

        load_btn = QPushButton("Load Map (.npy)")
        load_btn.clicked.connect(self._load)
        rv.addWidget(load_btn)

        save_btn = QPushButton("Save Map (.npy)")
        save_btn.clicked.connect(self._save)
        rv.addWidget(save_btn)

        rv.addWidget(divider())

        fit_grp = QGroupBox("Best Fit Line")
        fit_lay = QVBoxLayout(fit_grp)
        co_row = QHBoxLayout()
        co_row.addWidget(QLabel("Angle cutoff (rad):"))
        self.cutoff = QDoubleSpinBox()
        self.cutoff.setRange(0, 3.14)
        self.cutoff.setValue(0.9)
        co_row.addWidget(self.cutoff)
        fit_lay.addLayout(co_row)
        line_btn = QPushButton("Find Best Fit Line")
        line_btn.clicked.connect(self._find_line)
        fit_lay.addWidget(line_btn)
        rv.addWidget(fit_grp)

        rv.addStretch()

        next_btn = QPushButton("Go to Table Editor")
        next_btn.setObjectName("primary")
        next_btn.clicked.connect(self.proceed.emit)
        rv.addWidget(next_btn)

        root.addWidget(rail)

        canvas_wrap = QWidget()
        cv = QVBoxLayout(canvas_wrap)

        self.canvas = MplCanvas()

        self.nav_toolbar = NavigationToolbar(self.canvas, self)

        cv.addWidget(self.canvas, 1)
        cv.addWidget(self.nav_toolbar)
        root.addWidget(canvas_wrap, 1)

    def set_area_map(self, am: AreaMap, cutoff: float = 0.9):
        self.area_map = am
        self.cutoff.setValue(cutoff)
        self.map_status.setText("Map configured. Generate or load a saved map.")

    def _generate(self):
        if self.area_map is None:
            QMessageBox.warning(self, "Setup First", "Complete the Setup page first.")
            return
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.map_status.setText("Generating map.")
        self._worker = MapWorker(self.area_map)
        self._worker.progress.connect(self.progress.setValue)
        self._worker.finished.connect(self._done)
        self._worker.start()

    def _done(self):
        self.progress.setVisible(False)
        self.map_status.setText("Map generated")
        self._render()

    def _render(self):
        if self.area_map is None:
            return
        ax = self.canvas.axes
        ax.cla()

        self.area_map.render_to_axes(ax)
        ax.set_title("Shot Fidelity Map", fontsize=11, pad=8)
        self.canvas.refresh_style()

    def _load(self):
        if self.area_map is None:
            QMessageBox.warning(self, "Setup First", "Complete the Setup page first.")
            return
        p, _ = QFileDialog.getOpenFileName(self, "Load Map", "", "NumPy (*.npy)")
        if p:
            self.area_map.load_map(p)
            self.map_status.setText(f"Loaded: {p.split('/')[-1]} ✓")
            self._render()

    def _save(self):
        if self.area_map is None or not self.area_map.map.any():
            QMessageBox.warning(self, "No Map", "Generate or load a map first.")
            return
        p, _ = QFileDialog.getSaveFileName(self, "Save Map", "map.npy", "NumPy (*.npy)")
        if p:
            self.area_map.save_map(p)

    def _find_line(self):
        if self.area_map is None or not self.area_map.map.any():
            QMessageBox.warning(self, "No Map", "Generate or load a map first.")
            return
        self.area_map.find_best_fit_line(t_cutoff=self.cutoff.value())
        self.map_status.setText("Best fit line found.")
        self._render()

# Third page table making/loading ________________________________________________________________-
class TablePage(QWidget):
    proceed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.traj_table: TrajectoryTable | None = None
        self._area_map: AreaMap | None = None

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        rail = QWidget()
        rail.setFixedWidth(270)

        rv = QVBoxLayout(rail)

        rv.addWidget(head("Trajectory Lookup Table"))
        rv.addWidget(divider())

        self.table_status = dim("No table loaded.")
        rv.addWidget(self.table_status)
        rv.addWidget(divider())

        from_map = QGroupBox("Create From Map")
        fm = QVBoxLayout(from_map)
        step_row = QHBoxLayout()
        step_row.addWidget(QLabel("Step size:"))
        self.step = QSpinBox(); self.step.setRange(1, 50); self.step.setValue(1)
        step_row.addWidget(self.step)
        fm.addLayout(step_row)
        from_map_btn = QPushButton("Create from Map")
        from_map_btn.setObjectName("primary")
        from_map_btn.clicked.connect(self._from_map)
        fm.addWidget(from_map_btn)
        rv.addWidget(from_map)

        rv.addWidget(divider())

        load_csv = QPushButton("Load CSV")
        load_csv.clicked.connect(self._load_csv)
        rv.addWidget(load_csv)

        save_btn = QPushButton("Save as CSV")
        save_btn.clicked.connect(self._save_csv)
        rv.addWidget(save_btn)

        java_btn = QPushButton("Export Java Array")
        java_btn.clicked.connect(self._export_java)
        rv.addWidget(java_btn)

        rv.addStretch()

        next_btn = QPushButton("Go to Calibration")
        next_btn.setObjectName("primary"); next_btn.setFixedHeight(40)
        next_btn.clicked.connect(self.proceed.emit)
        rv.addWidget(next_btn)

        root.addWidget(rail)

        tv = QWidget()
        tl = QVBoxLayout(tv)
        tl.setContentsMargins(24, 24, 24, 24)
        tl.setSpacing(10)

        self.row_lbl = dim("0 entries")
        tl.addWidget(self.row_lbl)

        self.table_view = QTableWidget(0, 3)
        self.table_view.setHorizontalHeaderLabels(["Distance  (m)", "Angle  (rad)", "Velocity  (m/s)"])
        self.table_view.setAlternatingRowColors(True)
        tl.addWidget(self.table_view, 1)
        root.addWidget(tv, 1)

    def set_area_map(self, am: AreaMap):
        self._area_map = am

    def _from_map(self):
        if self._area_map is None or self._area_map.T_line is None:
            QMessageBox.warning(self, "No Line",
                "Find the best fit line on the Map page first.")
            return
        try:
            self.traj_table = TrajectoryTable.from_areamap(
                self._area_map, stepsize=self.step.value())
            self._populate()
            self.table_status.setText(
                f"Created from map  ({len(self.traj_table.dists)} rows)")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _load_csv(self):
        p, _ = QFileDialog.getOpenFileName(self, "Load CSV", "", "CSV (*.csv)")
        if p:
            try:
                self.traj_table = TrajectoryTable.from_file(p)
                self._populate()
                self.table_status.setText(
                    f"Loaded  ({len(self.traj_table.dists)} rows)")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _populate(self):
        t = self.traj_table
        if t is None:
            return
        self.table_view.setRowCount(len(t.dists))
        for i, (d, th, v) in enumerate(zip(t.dists, t.thetas, t.vels)):
            self.table_view.setItem(i, 0, QTableWidgetItem(f"{d:.4f}"))
            self.table_view.setItem(i, 1, QTableWidgetItem(f"{th:.4f}"))
            self.table_view.setItem(i, 2, QTableWidgetItem(f"{v:.4f}"))
        self.row_lbl.setText(f"{len(t.dists)} entries")

    def _save_csv(self):
        if self.traj_table is None:
            QMessageBox.warning(self, "No Table", "Create or load a table first.")
            return
        p, _ = QFileDialog.getSaveFileName(self, "Save CSV", "table.csv", "CSV (*.csv)")
        if p:
            self.traj_table.save_table(p)

    def _export_java(self):
        if self.traj_table is None:
            QMessageBox.warning(self, "No Table", "Create or load a table first.")
            return
        p, _ = QFileDialog.getSaveFileName(self, "Export Java", "table.txt",
                                           "Java (*.txt);;All Files (*)")
        if p:
            self.traj_table.export_java_arr(p)
# Page 4 table calibration _______________________________________________________
class CalibratePage(QWidget):
    def __init__(self, get_table):
        super().__init__()
        self._get_table = get_table
        self._ref: TrajectoryTable | None = None

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        root = QVBoxLayout(inner)

        root.addWidget(head("Velocity Calibration"))
        root.addWidget(divider())

        ref_grp = QGroupBox("Refrence Table (manual csv)")
        ref_lay = QVBoxLayout(ref_grp)

        load_ref = QPushButton("Load Reference CSV")
        load_ref.clicked.connect(self._load_ref)
        ref_lay.addWidget(load_ref)


        self.ref_view = QTableWidget(0, 3)
        self.ref_view.setHorizontalHeaderLabels(["Distance  (m)", "Angle  (rad)", "Velocity  (m/s)"])
        ref_lay.addWidget(self.ref_view)
        root.addWidget(ref_grp)


        cal_btn = QPushButton("Run Calibration")
        cal_btn.setObjectName("primary"); cal_btn.setFixedHeight(40)
        cal_btn.clicked.connect(self._calibrate)
        root.addWidget(cal_btn)

        root.addStretch()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def _load_ref(self):
        p, _ = QFileDialog.getOpenFileName(self, "Load Reference CSV", "", "CSV (*.csv)")
        if p:
            try:
                self._ref = TrajectoryTable.from_file(p)
                self._fill_ref_view()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _fill_ref_view(self):
        t = self._ref
        self.ref_view.setRowCount(len(t.dists)) # type: ignore
        for i, (d, th, v) in enumerate(zip(t.dists, t.thetas, t.vels)): # type: ignore
            self.ref_view.setItem(i, 0, QTableWidgetItem(f"{d:.4f}"))
            self.ref_view.setItem(i, 1, QTableWidgetItem(f"{th:.4f}"))
            self.ref_view.setItem(i, 2, QTableWidgetItem(f"{v:.4f}"))

    def _calibrate(self):
        if self._ref is None:
            QMessageBox.warning(self, "No Reference", "Load a reference table first.")
            return
        traj = self._get_table()
        if traj is None:
            QMessageBox.warning(self, "No Working Table",
                "Load or create a table on the Table page first.")
            return
        try:
            traj.calibrate_vels(self._ref)
        except Exception as e:
            QMessageBox.critical(self, "Calibration Error", str(e))
# Main window class ____________________________________________________________________
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FRC Trajectory Tool")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)


        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sv = QVBoxLayout(sidebar)

        title = QWidget()
        ll = QVBoxLayout(title)
        
        name = QLabel("Trajectory Tool")
        ll.addWidget(name)
        sv.addWidget(title)
        sv.addWidget(divider())

        NAV_ITEMS = [
            ("1", "Setup"),
            ("2", "Map"),
            ("3", "Table"),
            ("4", "Calibrate"),
        ]

        self._nav_btns: list[QPushButton] = []
        for i, (num, name) in enumerate(NAV_ITEMS):
            btn = QPushButton()
            btn.setObjectName("nav")
            btn.setProperty("active", False)
            btn.setText(name)

            btn.clicked.connect(lambda _, idx=i: self._goto(idx))
            self._nav_btns.append(btn)
            sv.addWidget(btn)

        sv.addStretch()

        layout.addWidget(sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.setup_page = SetupPage()
        self.map_page   = MapPage()
        self.table_page = TablePage()
        self.cal_page   = CalibratePage(lambda: self.table_page.traj_table)

        for p in (self.setup_page, self.map_page, self.table_page, self.cal_page):
            self.stack.addWidget(p)

        self.setup_page.proceed.connect(self._on_setup)
        self.map_page.proceed.connect(lambda: self._goto(2))
        self.table_page.proceed.connect(lambda: self._goto(3))

        self._goto(0)


    def _on_setup(self, p: dict):
        am = AreaMap(
            y0=p["y0"],
            range=p["range"],
            size=p["size"],
            t_range=(p["t_min"], p["t_max"]),
            v_range=(p["v_min"], p["v_max"]),
            area_itr=p["area_itr"],
        )
        self.map_page.set_area_map(am)
        self.table_page.set_area_map(am)
        self._goto(1)

    def _goto(self, idx: int):
        self.stack.setCurrentIndex(idx)

if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORMTHEME"] = "gtk3"
app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()