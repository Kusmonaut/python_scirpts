"""
Intranav GmbH © 2021
check tag positioning
"""

import json
import logging
import os
import sys
import numpy as np
from time import time
import csv

from serial.serialutil import to_bytes

from decode import *
import serial
import matplotlib.pyplot as plt


def draw_on_diag_canvas(node_diags):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(node_diags['cir_amplitude'])
    ax.axvline(x = node_diags['pp_index'] - int(node_diags['fp_index']) + 10, linestyle='-.')
    ax.axhline(y = node_diags['noise_threshold'], linestyle='-.')
    ax.scatter(y = node_diags['fp_ampl3'], x = 11, marker='x')
    ax.scatter(y = node_diags['fp_ampl2'], x = 12, marker='x')
    ax.scatter(y = node_diags['fp_ampl1'], x = 13, marker='x')
    ax.yaxis.label.set_text('Channel Impulse Response Amplitude')
    ax.xaxis.label.set_text('Sample Index')
    ax.grid(True)
    ax.legend()
    plt.show()

if __name__ == "__main__":
    ser = serial.Serial(port="COM4", baudrate=115200)
    # f = open("measured_data.bin", "w+b")
    counter = 0
    while(counter < 200):
        if (ser.readable()):
            buffer = ser.read_all()

            if buffer:
                with open("measured_data.bin", "ab") as f:
                    f.write(buffer)
                    f.close()
            # if buffer:
            #     print(buffer)
            # diag = decode_diagnostics(buffer, 21312, 23123)

            # if diag:
            #     f.write(buffer)
            #     # draw_on_diag_canvas(diag)
            #     counter += 1

    print(counter)