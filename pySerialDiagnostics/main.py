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

def plot_diagnostics(data_set, file_name):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(file_name)
    ax.grid(True)
    for diagnostics in data_set:
        test = (diagnostics['pp_index'] - int(diagnostics['fp_index'])) + 30
        delta = diagnostics['pp_index'] - int(diagnostics['fp_index'])
        # if diagnostics['fp_ampl1'] > 2500: # test > 35 and test < 45 and 
        diagnostics['cir_amplitude'][int(diagnostics['fp_index'])-30:]
        ax.plot(diagnostics['cir_amplitude'][int(diagnostics['fp_index'])-30:])
    pass
    plt.show()


def open_diagnostics(file_name):
    data = []
    with open(f'{file_name}.json', 'r') as f:
        data = f.read()
        new_data = data.replace('}{', '},{')
        json_data = json.loads(f'[{new_data}]')
    return json_data
    
#   for d in data:
    # draw_on_diag_canvas(line)

if __name__ == "__main__":
    file_name = 'node_v2_office_v2'
    data = open_diagnostics(file_name)
    plot_diagnostics(data, file_name)
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