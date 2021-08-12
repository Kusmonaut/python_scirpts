"""
Intranav GmbH © 2021
check tag positioning
"""

import sys
import numpy as np
import math

from PyQt5 import uic, QtGui
from PyQt5.Qt import Qt, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from numpy.core.function_base import linspace
from numpy.lib.ufunclike import isneginf


SPEED_OF_LIGHT = 299702547000

c_ = [1, 3]
x_ = [0, 5, -3.4]
y_ = [0, 3.9, -36.8]


towers = np.array([[-2166, 13137], [-4715.0, 10720.0], [-1773, 7694], [  754., 10178.]])
rec_times = np.array([0.0, 1.604954391609681e-09, -1.3815821375828818e-08, -1.2063200216516634e-08])

class Window(QMainWindow, QDialog):

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("live_analyticle_solver.ui", self)

        self.setWindowTitle("live Analyticle Solver")

        self._y = []
        self._x = linspace(-300, 300, 900)
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.y3 = 0
        self.y4 = 0


        # self.horizontalSlider_x_2.valueChanged.connect(self.analyticSolver)
        # self.horizontalSlider_y_2.valueChanged.connect(self.analyticSolver)
        # self.horizontalSlider_x_3.valueChanged.connect(self.analyticSolver)
        # self.horizontalSlider_y_3.valueChanged.connect(self.analyticSolver)
        # self.horizontalSlider_c_1.valueChanged.connect(self.analyticSolver)
        # self.horizontalSlider_c_2.valueChanged.connect(self.analyticSolver)

        self.horizontalSlider_x_2.valueChanged.connect(self.drawHyperbola)
        self.horizontalSlider_y_2.valueChanged.connect(self.drawHyperbola)
        self.horizontalSlider_x_3.valueChanged.connect(self.drawHyperbola)
        self.horizontalSlider_y_3.valueChanged.connect(self.drawHyperbola)
        self.horizontalSlider_c_1.valueChanged.connect(self.drawHyperbola)
        self.horizontalSlider_c_2.valueChanged.connect(self.drawHyperbola)

    def drawHyperbola(self):


        self._y = []
        x_[1] = self.horizontalSlider_x_2.value()
        y_[1] = self.horizontalSlider_y_2.value()
        x_[2] = self.horizontalSlider_x_3.value()
        y_[2] = self.horizontalSlider_y_3.value()
        c_[0] = self.horizontalSlider_c_1.value()
        c_[1] = self.horizontalSlider_c_2.value()

        for i in range(0, 2):
            y = []
            for x in self._x:
                y.append((c_[i]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i]**2 + 4*x**2 - 4*x*x_[i+1] + x_[i+1]**2 + y_[i+1]**2)) + c_[i]**2*y_[i+1] - x_[i+1]**2*y_[i+1] - y_[i+1]**3 + 2*x*x_[i+1]*y_[i+1])/(2*(c_[i]**2 - y_[i+1]**2)))
            self._y.append(y)

        self.drawCanvas()
        

    def analyticSolver(self):


        for i in range(0, 1):
            self.x1 = -(x_[i+1]**3*y_[i+2]**2 + x_[i+2]**3*y_[i+1]**2 - c_[i]**2*x_[i+2]**3 - c_[i+1]**2*x_[i+1]**3 - x_[i+1]*y_[i+1]*y_[i+2]**3 - x_[i+2]*y_[i+1]**3*y_[i+2] + c_[i]*y_[i+2]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i+1]**2 + x_[i+2]**2 + y_[i+2]**2)*(- c_[i]**2 + 2*c_[i]*c_[i+1] - c_[i+1]**2 + x_[i+1]**2 - 2*x_[i+1]*x_[i+2] + x_[i+2]**2 + y_[i+1]**2 - 2*y_[i+1]*y_[i+2] + y_[i+2]**2)) - c_[i+1]*y_[i+1]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i+1]**2 + x_[i+2]**2 + y_[i+2]**2)*(- c_[i]**2 + 2*c_[i]*c_[i+1] - c_[i+1]**2 + x_[i+1]**2 - 2*x_[i+1]*x_[i+2] + x_[i+2]**2 + y_[i+1]**2 - 2*y_[i+1]*y_[i+2] + y_[i+2]**2)) + c_[i]**2*c_[i+1]**2*x_[i+1] + c_[i]**2*c_[i+1]**2*x_[i+2] - c_[i]**2*x_[i+1]*y_[i+2]**2 - c_[i+1]**2*x_[i+1]*y_[i+1]**2 - c_[i]**2*x_[i+2]*y_[i+2]**2 - c_[i+1]**2*x_[i+2]*y_[i+1]**2 + x_[i+1]*y_[i+1]**2*y_[i+2]**2 + x_[i+2]*y_[i+1]**2*y_[i+2]**2 - c_[i]*c_[i+1]**3*x_[i+1] - c_[i]**3*c_[i+1]*x_[i+2] + c_[i]*c_[i+1]*x_[i+1]*x_[i+2]**2 + c_[i]*c_[i+1]*x_[i+1]**2*x_[i+2] + c_[i]*c_[i+1]*x_[i+1]*y_[i+2]**2 + c_[i]*c_[i+1]*x_[i+2]*y_[i+1]**2 + c_[i]**2*x_[i+2]*y_[i+1]*y_[i+2] + c_[i+1]**2*x_[i+1]*y_[i+1]*y_[i+2] - x_[i+1]*x_[i+2]**2*y_[i+1]*y_[i+2] - x_[i+1]**2*x_[i+2]*y_[i+1]*y_[i+2])/(2*(c_[i+1]**2*(x_[i+1]**2 + y_[i+1]**2) + x_[i+2]**2*(c_[i]**2 - y_[i+1]**2) + y_[i+2]**2*(c_[i]**2 - x_[i+1]**2) - 2*y_[i+1]*y_[i+2]*(c_[i]*c_[i+1] - x_[i+1]*x_[i+2]) - 2*c_[i]*c_[i+1]*x_[i+1]*x_[i+2]))
            self.x2 = -(x_[i+1]**3*y_[i+2]**2 + x_[i+2]**3*y_[i+1]**2 - c_[i]**2*x_[i+2]**3 - c_[i+1]**2*x_[i+1]**3 - x_[i+1]*y_[i+1]*y_[i+2]**3 - x_[i+2]*y_[i+1]**3*y_[i+2] - c_[i]*y_[i+2]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i+1]**2 + x_[i+2]**2 + y_[i+2]**2)*(- c_[i]**2 + 2*c_[i]*c_[i+1] - c_[i+1]**2 + x_[i+1]**2 - 2*x_[i+1]*x_[i+2] + x_[i+2]**2 + y_[i+1]**2 - 2*y_[i+1]*y_[i+2] + y_[i+2]**2)) + c_[i+1]*y_[i+1]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i+1]**2 + x_[i+2]**2 + y_[i+2]**2)*(- c_[i]**2 + 2*c_[i]*c_[i+1] - c_[i+1]**2 + x_[i+1]**2 - 2*x_[i+1]*x_[i+2] + x_[i+2]**2 + y_[i+1]**2 - 2*y_[i+1]*y_[i+2] + y_[i+2]**2)) + c_[i]**2*c_[i+1]**2*x_[i+1] + c_[i]**2*c_[i+1]**2*x_[i+2] - c_[i]**2*x_[i+1]*y_[i+2]**2 - c_[i+1]**2*x_[i+1]*y_[i+1]**2 - c_[i]**2*x_[i+2]*y_[i+2]**2 - c_[i+1]**2*x_[i+2]*y_[i+1]**2 + x_[i+1]*y_[i+1]**2*y_[i+2]**2 + x_[i+2]*y_[i+1]**2*y_[i+2]**2 - c_[i]*c_[i+1]**3*x_[i+1] - c_[i]**3*c_[i+1]*x_[i+2] + c_[i]*c_[i+1]*x_[i+1]*x_[i+2]**2 + c_[i]*c_[i+1]*x_[i+1]**2*x_[i+2] + c_[i]*c_[i+1]*x_[i+1]*y_[i+2]**2 + c_[i]*c_[i+1]*x_[i+2]*y_[i+1]**2 + c_[i]**2*x_[i+2]*y_[i+1]*y_[i+2] + c_[i+1]**2*x_[i+1]*y_[i+1]*y_[i+2] - x_[i+1]*x_[i+2]**2*y_[i+1]*y_[i+2] - x_[i+1]**2*x_[i+2]*y_[i+1]*y_[i+2])/(2*(c_[i+1]**2*(x_[i+1]**2 + y_[i+1]**2) + x_[i+2]**2*(c_[i]**2 - y_[i+1]**2) + y_[i+2]**2*(c_[i]**2 - x_[i+1]**2) - 2*y_[i+1]*y_[i+2]*(c_[i]*c_[i+1] - x_[i+1]*x_[i+2]) - 2*c_[i]*c_[i+1]*x_[i+1]*x_[i+2]))

            x = self.x2

            self.y1 =  (c_[i]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i]**2 + 4*x**2 - 4*x*x_[i+1] + x_[i+1]**2 + y_[i+1]**2)) + c_[i]**2*y_[i+1] - x_[i+1]**2*y_[i+1] - y_[i+1]**3 + 2*x*x_[i+1]*y_[i+1])/(2*(c_[i]**2 - y_[i+1]**2))
            self.y2 = -(c_[i]*np.sqrt((- c_[i]**2 + x_[i+1]**2 + y_[i+1]**2)*(- c_[i]**2 + 4*x**2 - 4*x*x_[i+1] + x_[i+1]**2 + y_[i+1]**2)) - c_[i]**2*y_[i+1] + x_[i+1]**2*y_[i+1] + y_[i+1]**3 - 2*x*x_[i+1]*y_[i+1])/(2*(c_[i]**2 - y_[i+1]**2))
            self.y3 =  (c_[i+1]*np.sqrt((- c_[i+1]**2 + x_[i+2]**2 + y_[i+2]**2)*(- c_[i+1]**2 + 4*x**2 - 4*x*x_[i+2] + x_[i+2]**2 + y_[i+2]**2)) + c_[i+1]**2*y_[i+2] - x_[i+2]**2*y_[i+2] - y_[i+2]**3 + 2*x*x_[i+2]*y_[i+2])/(2*(c_[i+1]**2 - y_[i+2]**2))
            self.y4 = -(c_[i+1]*np.sqrt((- c_[i+1]**2 + x_[i+2]**2 + y_[i+2]**2)*(- c_[i+1]**2 + 4*x**2 - 4*x*x_[i+2] + x_[i+2]**2 + y_[i+2]**2)) - c_[i+1]**2*y_[i+2] + x_[i+2]**2*y_[i+2] + y_[i+2]**3 - 2*x*x_[i+2]*y_[i+2])/(2*(c_[i+1]**2 - y_[i+2]**2))
 
        self.drawCanvas()

    def drawCanvas(self):

        self.MplWidget.canvas.axes.clear()

        _max_value = 0
        _min_value = 0

        # draw hyperbola
        for y in self._y:

            if _max_value < max(y) and not any(np.isnan(np.array(y))) and not any(np.isinf(np.array(y))):
                _max_value = max(y)

            if _min_value > min(y) and not any(np.isnan(np.array(y))) and not any(np.isinf(np.array(y))):
                _min_value = min(y)

            if not any(np.isnan(np.array(y))) and not any(np.isinf(np.array(y))):
                self.MplWidget.canvas.axes.plot(self._x, y)

        # draw interscetion points of hyperbola
        self.MplWidget.canvas.axes.scatter(self.x2, self.y1, marker='x', color='r')
        self.MplWidget.canvas.axes.scatter(self.x2, self.y2, marker='x', color='g')
        self.MplWidget.canvas.axes.scatter(self.x2, self.y3, marker='x', color='b')
        self.MplWidget.canvas.axes.scatter(self.x2, self.y4, marker='x', color='y')

        self.MplWidget.canvas.axes.set_xlim(min(self._x), max(self._x))
        self.MplWidget.canvas.axes.set_ylim(_min_value, _max_value)
        self.MplWidget.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()