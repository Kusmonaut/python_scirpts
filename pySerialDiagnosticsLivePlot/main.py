"""
Intranav GmbH © 2021
check tag positioning
"""

import json

import sys

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.Qt import Qt, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from numpy.core.function_base import linspace
from numpy.lib.ufunclike import isneginf

from decode import *
import serial
import matplotlib.pyplot as plt

NUMBER_OF_MEASURMENTS = 100

DIAG = {}

class YourThreadName(QThread):

    my_signal = pyqtSignal(dict)

    def __init__(self):
        super(YourThreadName, self).__init__()
        QThread.__init__(self)
        self.ser = serial.Serial(port="COM4", baudrate=115200)
    def __del__(self):
        self.wait()

    def run(self):
        while True:
            if (self.ser.readable()):
                buffer = self.ser.read_all()

                if buffer:
                    print(buffer)
                    DIAG = decode_diagnostics(buffer, 21312, 23123)
                    self.my_signal.emit(DIAG)


class Window(QMainWindow, QDialog):

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("liveplot.ui", self)
        self.myThread = YourThreadName()
        self.myThread.start()
        # self.myThread.run()
        if self.myThread.isRunning():
            self.myThread.my_signal.connect(self.test)
        pass
    
    def test(self, bla):
        self.plot_diagnostics(bla, 'test')

    def plot_diagnostics(self, diagnostics, file_name):
        # fig = plt.figure()
        # ax = fig.add_subplot(1, 1, 1)
        # ax.grid(True)
        bad_signal = 0
        good_signal = 0

        report = create_quality_report(diagnostics, 'test')

        if report['prNlos'] < 1:
            good_signal += 1
        else:
            bad_signal += 1

        # if diagnostics['fp_ampl1'] < 3000: # test > 35 and test < 45 and 
        diagnostics['cir_amplitude'][int(diagnostics['fp_index'])-30:]
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(diagnostics['cir_amplitude'][int(diagnostics['fp_index'])-30:])
        self.MplWidget.canvas.draw()
        
        # ax.set_title(f'{file_name}, bad_signal = {bad_signal}, good_signal = {good_signal}')
        # plt.show()

def draw_on_diag_canvas(node_diags):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(node_diags['cir_amplitude'])
    ax.axvline(x = int(node_diags['fp_index']), linestyle='-.')
    ax.axhline(y = int(node_diags['noise_threshold']), linestyle='-.')
    ax.scatter(y = node_diags['fp_ampl3'], x = int(diag['fp_index']) + 1, marker='x')
    ax.scatter(y = node_diags['fp_ampl2'], x = int(diag['fp_index']) + 2, marker='x')
    ax.scatter(y = node_diags['fp_ampl1'], x = int(diag['fp_index']) + 3, marker='x')
    ax.yaxis.label.set_text('Channel Impulse Response Amplitude')
    ax.xaxis.label.set_text('Sample Index')
    ax.grid(True)
    ax.legend()
    plt.show()

def open_diagnostics(file_name):
    data = []
    with open(f'{file_name}.json', 'r') as f:
        data = f.read()
        new_data = data.replace('}{', '},{')
        json_data = json.loads(f'[{new_data}]')
    return json_data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
