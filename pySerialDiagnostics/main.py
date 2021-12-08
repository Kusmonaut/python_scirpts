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

def plot_diagnostics(data_set):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(True)
    for diagnostics in data_set: 
        ax.plot(diagnostics['cir_amplitude'])
    pass
    plt.show()


def open_diagnostics():
    data = []
    with open('data.json', 'r') as f:
        data = f.read()
        new_data = data.replace('}{', '},{')
        json_data = json.loads(f'[{new_data}]')
    return json_data
    
#   for d in data:
    # draw_on_diag_canvas(line)

if __name__ == "__main__":
    data = open_diagnostics()
    plot_diagnostics(data)
    ser = serial.Serial(port="COM4", baudrate=115200)
    counter = 0
    while(counter < 200):
        if (ser.readable()):
            buffer = ser.read_all()

            if buffer:
                print(buffer)
                diag = decode_diagnostics(buffer, 21312, 23123)
                with open('data.json', 'a') as f:
                    json.dump(diag, f) #, f, indent=2, indent=4
                # if diag:
                #     draw_on_diag_canvas(diag)