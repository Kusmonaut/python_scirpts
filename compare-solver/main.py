"""
Intranav GmbH © 2021
check tag positioning
"""

import json
import logging
import os
import time
import sys
import numpy as np
import csv

from shapely import geometry
from scipy.spatial import distance
from scipy.optimize import least_squares
from PyQt5 import uic, QtGui
from PyQt5.Qt import Qt, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from requests import RequestException, Session

from config import *
from multilaterate import get_loci
from multilateration import *
from intranav.constants.devices import (
    NODE_UID_PROP_ID,
    NODE_X_PROP_ID,
    NODE_Y_PROP_ID,
    NODE_Z_PROP_ID,
    NODE_TYPE_PROP_ID,
    NODE_FLOOR_PROP_ID
)

TAG_REPORT = 0
SCATTER_NODES = {}
X_AXE = []
Y_AXE = []

class Window(QMainWindow, QDialog):

    def __init__(self, tags, floors):
        super(Window, self).__init__()
        uic.loadUi("compare-solver.ui", self)

        self._active_tag = 0
        self.all_p_i = 0
        self.all_t_i = 0
        self.p_c = 0
        self.t_c = 0
        self.x_init = None
        self.tdoa_offset = 0

        self.setWindowTitle("Node Tag Analyse")
        
        # add tag names in combobox
        for tag in tags:
            self.comboBox.addItem(tag)

        # add floors in combobox
        for floor in floors:
            self.floorBox.addItem(str(floor))

        # select a tag for update_scatter_dots
        self.load_tag()

        # draw the nodes and tags into matplotlib
        self.update_scatter_dots()

        # connect all signals 
        self.horizontalSlider.valueChanged.connect(self.update_scatter_dots)
        self.floorBox.currentIndexChanged.connect(self.update_scatter_dots)
        self.comboBox.currentIndexChanged.connect(self.load_tag)
        self.checkBox.toggled.connect(self.update_scatter_dots)
        self.tdoaOffsetSlider.valueChanged.connect(self.update_tdoaOfRefNode)

    def update_tdoaOfRefNode(self):
        max_value = self.tdoaOffsetSlider.maximum()
        total_difference = 20
        value = self.tdoaOffsetSlider.value()
        self.tdoa_offset = (((value - max_value/2) * (total_difference/max_value)) / SPEED_OF_LIGHT) * 1000
        
        self.tdoaOffsetLcd.display(self.tdoa_offset)

        self.update_hyperbola()

    def update_locationCalc(self):

        tdoaMeasurement = []
        tdoaMeasurement_corrected = []
        nodeCoordinates = []
        nodeCoordinates_corrected = []

        for receive_time in SCATTER_NODES['referenceNode']['tdoa'] + SCATTER_NODES['positioningNodes']['tdoa']:
            tdoaMeasurement.append(receive_time)

        for receive_time in SCATTER_NODES['referenceNode']['tdoa'] + SCATTER_NODES['positioningNodes_corrected']['tdoa']:
            tdoaMeasurement_corrected.append(receive_time)
            
        for x, y in zip(SCATTER_NODES['referenceNode']['pos']['x'] + SCATTER_NODES['positioningNodes']['pos']['x'], SCATTER_NODES['referenceNode']['pos']['y'] + SCATTER_NODES['positioningNodes']['pos']['y']):
            nodeCoordinates.append([x/1000, y/1000])

        for x, y in zip(SCATTER_NODES['referenceNode']['pos']['x'] + SCATTER_NODES['positioningNodes_corrected']['pos']['x'], SCATTER_NODES['referenceNode']['pos']['y'] + SCATTER_NODES['positioningNodes_corrected']['pos']['y']):
            nodeCoordinates_corrected.append([x/1000, y/1000])

        cleSolver3D = False
        multilaterator = MultiLateration()

        if len(tdoaMeasurement_corrected) >= 3:
            node_coords_corected = np.mat(nodeCoordinates_corrected)
            
            tdoa_corrected = np.array([tdoaMeasurement_corrected])
            
            res_corrected = self.calc_pos(nodeCoordinates_corrected, tdoaMeasurement_corrected)
            
            SCATTER_NODES['calc_tag_corrected']['pos']['x'] = res_corrected[0]
            SCATTER_NODES['calc_tag_corrected']['pos']['y'] = res_corrected[1]

            multilaterator.setNodes(node_coords_corected, cleSolver3D)
            result_corrected = multilaterator.multilaterate(tdoa_corrected, cleSolver3D) * 1000

            # worng result will be returned as a array of size 1
            if np.size(result_corrected) == 1:
                SCATTER_NODES['real_tag_corrected']['pos']['x'] = []
                SCATTER_NODES['real_tag_corrected']['pos']['y'] = []
            else:
                SCATTER_NODES['real_tag_corrected']['pos']['x'] = [result_corrected[0,0]]
                SCATTER_NODES['real_tag_corrected']['pos']['y'] = [result_corrected[0,1]]

        # only if the list of tdoa measurements ist biger equale 3 than calc new position
        if len(tdoaMeasurement) >= 3:
            node_coords = np.mat(nodeCoordinates)

            tdoa = np.array([tdoaMeasurement])

            res = self.calc_pos(nodeCoordinates, tdoaMeasurement)

            SCATTER_NODES['calc_tag']['pos']['x'] = res[0]
            SCATTER_NODES['calc_tag']['pos']['y'] = res[1]


            multilaterator.setNodes(node_coords, cleSolver3D)
            result = multilaterator.multilaterate(tdoa, cleSolver3D) * 1000
            

            # worng result will be returned as a array of size 1
            if np.size(result) == 1:
                SCATTER_NODES['real_tag']['pos']['x'] = []
                SCATTER_NODES['real_tag']['pos']['y'] = []
            else:
                SCATTER_NODES['real_tag']['pos']['x'] = [result[0,0]]
                SCATTER_NODES['real_tag']['pos']['y'] = [result[0,1]]
    
        self.update_canvas()

    def calc_pos(self, nodeCoordinates, tdoaMeasurement):

        node_coords = np.array(nodeCoordinates)
        tdoa = np.array(tdoaMeasurement)

        self.p_c = np.expand_dims(node_coords[0], axis=0)
        self.t_c = tdoa[0]

        # Remove the c tower to allow for vectorization.
        self.all_p_i = np.delete(node_coords, 0, axis=0)
        self.all_t_i = np.delete(tdoa, 0, axis=0)

        # Initial guess.
        if self.x_init is None:
            self.x_init = [0, 0]

        # Find a value of x such that eval_solution is minimized.
        # Remember the receive times have error added to them: rec_time_noise_stdd.
        res = least_squares(self.eval_solution, self.x_init).x*1000
        
        self.x_init = [res[0]/1000, res[1]/1000]

        return res

    def eval_solution(self, x):
        """ x is 2 element array of x, y of the transmitter"""
        return (
            np.linalg.norm(x - self.p_c, axis=1)
            - np.linalg.norm(x - self.all_p_i, axis=1) 
            + (SPEED_OF_LIGHT/1000)*(self.all_t_i - self.t_c) 
        )
    

    def load_tag(self):
        uid = self.comboBox.currentText()
        self._active_tag = tags[uid]
        # set the limit of the horizontalSlider after change of tag
        self.horizontalSlider.setMaximum(len(self._active_tag)-1)

        self.horizontalSlider.setValue(0)

    def update_canvas(self):

        # clear the old plot
        self.UnfilteredPlot.canvas.axes.clear()
        self.FilteredPlot.canvas.axes.clear()

        self.UnfilteredPlot.canvas.axes.set_title('Unfilterd TDOA Signal')
        self.FilteredPlot.canvas.axes.set_title('Filterd TDOA Signal')

        
        # activate minor and major grid for unfilterd and filtered plot
        self.UnfilteredPlot.canvas.axes.grid(True, which='minor', alpha=0.2)
        self.UnfilteredPlot.canvas.axes.grid(True, which='major', alpha=0.5)
        self.FilteredPlot.canvas.axes.grid(True, which='minor', alpha=0.2)
        self.FilteredPlot.canvas.axes.grid(True, which='major', alpha=0.5)

        if MANUAL:
            # set limits for x achse and y achse
            self.UnfilteredPlot.canvas.axes.set_xlim(X_MIN, X_MAX)
            self.UnfilteredPlot.canvas.axes.set_ylim(Y_MAX, Y_MIN)
            self.FilteredPlot.canvas.axes.set_xlim(X_MIN, X_MAX)
            self.FilteredPlot.canvas.axes.set_ylim(Y_MAX, Y_MIN)

            # set ticks of the minor grid 
            self.UnfilteredPlot.canvas.axes.set_xticks(np.arange(X_MIN, X_MAX, 1000), minor=True)
            self.UnfilteredPlot.canvas.axes.set_yticks(np.arange(Y_MAX, Y_MIN, 1000), minor=True)
            self.FilteredPlot.canvas.axes.set_xticks(np.arange(X_MIN, X_MAX, 1000), minor=True)
            self.FilteredPlot.canvas.axes.set_yticks(np.arange(Y_MAX, Y_MIN, 1000), minor=True)
        else:
            # set limits for x achse and y achse
            self.UnfilteredPlot.canvas.axes.set_xlim(min(X_AXE)-500, max(X_AXE)+500)
            self.UnfilteredPlot.canvas.axes.set_ylim(min(Y_AXE)-500, max(Y_AXE)+500)
            self.FilteredPlot.canvas.axes.set_xlim(min(X_AXE)-500, max(X_AXE)+500)
            self.FilteredPlot.canvas.axes.set_ylim(min(Y_AXE)-500, max(Y_AXE)+500)

            # set ticks of the minor grid 
            self.UnfilteredPlot.canvas.axes.set_xticks(np.arange(min(X_AXE)-500, max(X_AXE)+500, 1000), minor=True)
            self.UnfilteredPlot.canvas.axes.set_yticks(np.arange(min(Y_AXE)-500, max(Y_AXE)+500, 1000), minor=True)
            self.FilteredPlot.canvas.axes.set_xticks(np.arange(min(X_AXE)-500, max(X_AXE)+500, 1000), minor=True)
            self.FilteredPlot.canvas.axes.set_yticks(np.arange(min(Y_AXE)-500, max(Y_AXE)+500, 1000), minor=True)

        s = 100

        # plot the least squere solution
        self.UnfilteredPlot.canvas.axes.scatter(SCATTER_NODES['calc_tag']['pos']['x'], SCATTER_NODES['calc_tag']['pos']['y'], color = 'b', marker = 'v', zorder=10, s=s, label='least squares')
        self.FilteredPlot.canvas.axes.scatter(SCATTER_NODES['calc_tag_corrected']['pos']['x'], SCATTER_NODES['calc_tag_corrected']['pos']['y'], color = 'b', marker = 'v', zorder=10, s=s, label='least squares')

        # plot scatter nodes
        for nodes in SCATTER_NODES:
            if nodes == "tag":
                self.UnfilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = SCATTER_NODES[nodes]['colorCode'][:], marker = 'X', zorder=10, s=s, lw=0, label='tdao debug')
                self.FilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = SCATTER_NODES[nodes]['colorCode'][:], marker = 'X', zorder=10, s=s, lw=0, label='tdao debug')
            if nodes == "real_tag":
                self.UnfilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = 'r', marker = '+', zorder=10, s=s, label='LE algo')
            if nodes == "real_tag_corrected":
                self.FilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = 'r', marker = '+', zorder=10, s=s, label='LE algo')
            if nodes == "referenceNode":
                self.UnfilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = SCATTER_NODES[nodes]['colorCode'][:], marker = 's', s=s, lw=0)
                self.FilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = SCATTER_NODES[nodes]['colorCode'][:], marker = 's', s=s, lw=0)
            if nodes == "nonePositioningNodes" or nodes == "positioningNodes":
                self.UnfilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = SCATTER_NODES[nodes]['colorCode'][:], s=s, lw=0)
                self.FilteredPlot.canvas.axes.scatter(SCATTER_NODES[nodes]['pos']['x'][:], SCATTER_NODES[nodes]['pos']['y'][:], color = SCATTER_NODES[nodes]['colorCode'][:], s=s, lw=0)

        # plot the graphs with the corresponding color code
        for i in range(len(SCATTER_NODES['positioningNodes']['uid'])):
            self.UnfilteredPlot.canvas.axes.plot(SCATTER_NODES['positioningNodes']['loci']['pos']['x'][i],
                SCATTER_NODES['positioningNodes']['loci']['pos']['y'][i],
                color=SCATTER_NODES['positioningNodes']['colorCode'][i])
         
        for i in range(len(SCATTER_NODES['positioningNodes_corrected']['uid'])):   
            self.FilteredPlot.canvas.axes.plot(SCATTER_NODES['positioningNodes_corrected']['loci']['pos']['x'][i],
                SCATTER_NODES['positioningNodes_corrected']['loci']['pos']['y'][i],
                color=SCATTER_NODES['positioningNodes_corrected']['colorCode'][i])

        # plot legend
        self.UnfilteredPlot.canvas.axes.legend()
        self.FilteredPlot.canvas.axes.legend()

        #write the name of the nodes
        if self.checkBox.checkState():
            try:
                for label, x, y in zip(SCATTER_NODES['positioningNodes']['name'][:], SCATTER_NODES['positioningNodes']['pos']['x'][:], SCATTER_NODES['positioningNodes']['pos']['y'][:]):
                    self.UnfilteredPlot.canvas.axes.annotate(
                        label,
                        xy=(x, y), xytext=(-10, 10),
                        textcoords='offset points', ha='right', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

                self.UnfilteredPlot.canvas.axes.annotate(
                    SCATTER_NODES['referenceNode']['name'][0],
                    xy=(SCATTER_NODES['referenceNode']['pos']['x'][0], SCATTER_NODES['referenceNode']['pos']['y'][0]), xytext=(-10, 10),
                    textcoords='offset points', ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
            except:
                pass

        self.UnfilteredPlot.canvas.draw()
        self.FilteredPlot.canvas.draw()

    def filter_or_correcting_positioningNodes():
        pass
        # SCATTER_NODES['positioningNodes']['loci_corrected']['pos']['x'] = []
        # SCATTER_NODES['positioningNodes']['loci_corrected']['pos']['y'] = []
        # SCATTER_NODES['positioningNodes']['tdoa_corrected'] = []
        # SCATTER_NODES['positioningNodes']['filtered_pos']['x'] = []
        # SCATTER_NODES['positioningNodes']['filtered_pos']['y'] = []

    def update_hyperbola(self):
        global SCATTER_NODES

        nodeWithTdoaOffset = []
        nodeWithTdoaOffset_corrected = []

        # SCATTER_NODES['positioningNodes']['loci']['pos']['x'] = []
        # SCATTER_NODES['positioningNodes']['loci']['pos']['y'] = []

        try:
            # add an tdoa offset for the receiver node
            for i, _ in enumerate(SCATTER_NODES['positioningNodes']['tdoa']):
                nodeWithTdoaOffset.append(SCATTER_NODES['positioningNodes']['tdoa'][i] + self.tdoa_offset)
            
            for i, _ in enumerate(SCATTER_NODES['positioningNodes_corrected']['tdoa']):
                nodeWithTdoaOffset_corrected.append(SCATTER_NODES['positioningNodes_corrected']['tdoa'][i] + self.tdoa_offset)

            #create copy of receive_time and node position as numpy array to create hyperbula function and also append primary node to this copy
            receive_time = np.array(SCATTER_NODES['referenceNode']['tdoa'] + (nodeWithTdoaOffset))
            receive_time_correction = np.array(SCATTER_NODES['referenceNode']['tdoa'] + (nodeWithTdoaOffset_corrected))

            # create towers for loci
            tower_positions = np.transpose(np.array([(SCATTER_NODES['referenceNode']['pos']['x'] + SCATTER_NODES['positioningNodes']['pos']['x']),
                (SCATTER_NODES['referenceNode']['pos']['y'] + SCATTER_NODES['positioningNodes']['pos']['y'])]))
            tower_positions_corrected = np.transpose(np.array([(SCATTER_NODES['referenceNode']['pos']['x'] + SCATTER_NODES['positioningNodes_corrected']['pos']['x']),
                (SCATTER_NODES['referenceNode']['pos']['y'] + SCATTER_NODES['positioningNodes_corrected']['pos']['y'])]))

            # create loci for the positioning nodes to the reference node    
            loci = get_loci(receive_time, tower_positions, SPEED_OF_LIGHT, DELTA_D, MAX_D)
            loci_corrected = get_loci(receive_time_correction, tower_positions_corrected, SPEED_OF_LIGHT, DELTA_D, MAX_D)

            # append hyperbula graph to the scatter Nodes
            for locus in loci:
                SCATTER_NODES['positioningNodes']['loci']['pos']['x'].append(locus[0][:])
                SCATTER_NODES['positioningNodes']['loci']['pos']['y'].append(locus[1][:])
                
            for locus in loci_corrected:
                SCATTER_NODES['positioningNodes_corrected']['loci']['pos']['x'].append(locus[0][:])
                SCATTER_NODES['positioningNodes_corrected']['loci']['pos']['y'].append(locus[1][:])
        except:
            pass
    
    def update_scatter_dots(self):
        global TAG_REPORT, SCATTER_NODES, X_AXE, Y_AXE
        SCATTER_NODES = {'tag': {'colorCode':['blue'],
                                'pos': {'x': [], 'y': [] },
                                'scatterType' : ['o']  },

                        'real_tag': {'colorCode':['r'],
                                'pos': {'x': [], 'y': [] },
                                'scatterType' : ['s']  },

                        'real_tag_corrected': {'colorCode':['r'],
                                'pos': {'x': [], 'y': [] },
                                'scatterType' : ['s']  },

                        'calc_tag': {'colorCode':['r'],
                                'pos': {'x': [], 'y': [] },
                                'scatterType' : ['s']  },

                        'calc_tag_corrected': {'colorCode':['r'],
                                'pos': {'x': [], 'y': [] },
                                'scatterType' : ['s']  },

                        'nonePositioningNodes': {'colorCode':[],
                                                'pos': {'x': [], 'y': [] },
                                                'scatterType' : [] },

                        'positioningNodes_corrected': {'colorCode': [],
                                            'pos': {'x': [],'y': [] },
                                            'scatterType' : [],
                                            'uid': [],
                                            'name': [],
                                            'tdoa': [],
                                            'loci': {'pos': {'x': [], 'y': [] } }, },

                        'positioningNodes': {'colorCode': [],
                                            'pos': {'x': [],'y': [] },
                                            'scatterType' : [],
                                            'uid': [],
                                            'name': [],
                                            'tdoa': [],
                                            'loci': {'pos': {'x': [], 'y': [] } },
                                            'loci_corrected': {'pos': {'x': [], 'y': [] } }, }, 

                        'referenceNode': {'colorCode':['red'],
                                        'pos': {'x': [], 'y': [] },
                                        'scatterType' : [],
                                        'uid': [],
                                        'name': [],
                                        'tdoa': [] } }

        # get index of slider
        index = self.horizontalSlider.value()
        # fetch overflow inf slider value
        if index > len(self._active_tag):
            self.horizontalSlider.setValue(0)
            TAG_REPORT = self._active_tag[0]
        else:
            TAG_REPORT = self._active_tag[index]

        # create dot for tag
        SCATTER_NODES['tag']['pos']['x'].append(float(TAG_REPORT['pos']['x']))
        SCATTER_NODES['tag']['pos']['y'].append(float(TAG_REPORT['pos']['y']))

        # decode time from timestamp
        ts = time.gmtime(float(TAG_REPORT['time'])/1000)
        timestamp = time.strftime("%H:%M:%S %d-%m-%Y", ts)
        self.labelTime.setText(timestamp)

        X_AXE = []
        Y_AXE = []

        # create dots for nodes
        for node in floors[int(self.floorBox.currentText())]:

            X_AXE.append(node['x'])
            Y_AXE.append(node['y'])

            # fetch all tags with none tdoadbug reports
            try:
                # itterate trough the tdoadebug list
                for tdoa_node in TAG_REPORT['tdoadebug']:
                    if tdoa_node['uid'] == node['uid']:
                        if tdoa_node['tdoa'] == 0:
                            # save name and position of primory node   
                            SCATTER_NODES['referenceNode']['name'].append(node['name'])
                            SCATTER_NODES['referenceNode']['uid'].append(node['uid'])
                            SCATTER_NODES['referenceNode']['tdoa'].append(tdoa_node['tdoa'])
                            SCATTER_NODES['referenceNode']['pos']['x'].append(float(node['x']))
                            SCATTER_NODES['referenceNode']['pos']['y'].append(float(node['y']))
                            SCATTER_NODES['referenceNode']['scatterType'].append(node['nodeType'])

                        else:
                            # save names and positions of positioning node
                            SCATTER_NODES['positioningNodes']['name'].append(node['name'])
                            SCATTER_NODES['positioningNodes']['uid'].append(node['uid'])
                            SCATTER_NODES['positioningNodes']['tdoa'].append(tdoa_node['tdoa'])
                            SCATTER_NODES['positioningNodes']['pos']['x'].append(float(node['x']))
                            SCATTER_NODES['positioningNodes']['pos']['y'].append(float(node['y']))
                            SCATTER_NODES['positioningNodes']['colorCode'].append(COLOR_PALET[len(SCATTER_NODES['positioningNodes']['colorCode'])])
                            SCATTER_NODES['positioningNodes']['scatterType'].append(node['nodeType'])

                            if [tdoa['uid'] == '01aa2145caf20e92' and tdoa['tdoa'] == 0 for tdoa in TAG_REPORT['tdoadebug']]:
                                if tdoa_node['uid'] == '01aa2145caf203b4' and tdoa_node['tdoa'] > 1e-8:
                                    if not FILTER_TDOA:
                                        SCATTER_NODES['positioningNodes_corrected']['name'].append(node['name'])
                                        SCATTER_NODES['positioningNodes_corrected']['uid'].append(node['uid'])
                                        SCATTER_NODES['positioningNodes_corrected']['tdoa'].append(tdoa_node['tdoa'] - 5e-9)
                                        SCATTER_NODES['positioningNodes_corrected']['pos']['x'].append(float(node['x']))
                                        SCATTER_NODES['positioningNodes_corrected']['pos']['y'].append(float(node['y']))
                                        SCATTER_NODES['positioningNodes_corrected']['colorCode'].append(COLOR_PALET[len(SCATTER_NODES['positioningNodes']['colorCode'])-1])
                                        SCATTER_NODES['positioningNodes_corrected']['scatterType'].append(node['nodeType'])
                                else:
                                    SCATTER_NODES['positioningNodes_corrected']['name'].append(node['name'])
                                    SCATTER_NODES['positioningNodes_corrected']['uid'].append(node['uid'])
                                    SCATTER_NODES['positioningNodes_corrected']['tdoa'].append(tdoa_node['tdoa'])
                                    SCATTER_NODES['positioningNodes_corrected']['pos']['x'].append(float(node['x']))
                                    SCATTER_NODES['positioningNodes_corrected']['pos']['y'].append(float(node['y']))
                                    SCATTER_NODES['positioningNodes_corrected']['colorCode'].append(COLOR_PALET[len(SCATTER_NODES['positioningNodes']['colorCode'])-1])
                                    SCATTER_NODES['positioningNodes_corrected']['scatterType'].append(node['nodeType'])
                            else:
                                SCATTER_NODES['positioningNodes_corrected']['name'].append(node['name'])
                                SCATTER_NODES['positioningNodes_corrected']['uid'].append(node['uid'])
                                SCATTER_NODES['positioningNodes_corrected']['tdoa'].append(tdoa_node['tdoa'])
                                SCATTER_NODES['positioningNodes_corrected']['pos']['x'].append(float(node['x']))
                                SCATTER_NODES['positioningNodes_corrected']['pos']['y'].append(float(node['y']))
                                SCATTER_NODES['positioningNodes_corrected']['colorCode'].append(COLOR_PALET[len(SCATTER_NODES['positioningNodes']['colorCode'])-1])
                                SCATTER_NODES['positioningNodes_corrected']['scatterType'].append(node['nodeType'])
                    else:
                        #save the positions of all none positioning nodes
                        SCATTER_NODES['nonePositioningNodes']['pos']['x'].append(float(node['x']))
                        SCATTER_NODES['nonePositioningNodes']['pos']['y'].append(float(node['y']))
                        SCATTER_NODES['nonePositioningNodes']['colorCode'].append('green')
                        SCATTER_NODES['nonePositioningNodes']['scatterType'].append(node['nodeType'])

            except:
                # if tdoadebug doese not exist save all nodes to nonepositioning nodes
                SCATTER_NODES['nonePositioningNodes']['pos']['x'].append(float(node['x']))
                SCATTER_NODES['nonePositioningNodes']['pos']['y'].append(float(node['y']))
                SCATTER_NODES['nonePositioningNodes']['colorCode'].append('green')
                SCATTER_NODES['nonePositioningNodes']['scatterType'].append(node['nodeType'])

        for item in TAG_REPORT['tdoadebug']:
            if 'raw_position' in item:
                if MILIMETER:
                    SCATTER_NODES['real_tag']['pos']['x'].append(item['raw_position']['x']*1000)
                    SCATTER_NODES['real_tag']['pos']['y'].append(item['raw_position']['y']*1000)
                else:
                    SCATTER_NODES['real_tag']['pos']['x'].append(item['raw_position']['x'])
                    SCATTER_NODES['real_tag']['pos']['y'].append(item['raw_position']['y'])

        # self.filter_or_correcting_positioningNodes()
        self.update_hyperbola()
        self.update_locationCalc()
        self.update_canvas()
        pass

def main(data):

    tags = {}

    for entrence in data:
        # if entrence['id'] is not None:
        #     uid = entrence['id']
        #     uid = entrence.pop('id')
        if entrence['asset']['assetId'] is not None:
            uid = entrence['asset']['assetId']
        else:
            # if asset/ assetId doesnt exist save tag with uid
            uid = entrence.pop('id')

        # change the units from meter to millimeter
        if MILIMETER:
            entrence['pos']['x'] = int(entrence['pos']['x']*1000)
            entrence['pos']['y'] = int(entrence['pos']['y']*1000)
            try:
                for node in entrence['tdoadebug']:
                    node['x'] = int(node['x']*1000)
                    node['y'] = int(node['y']*1000)
                    node['z'] = int(node['z']*1000)
            except:
                pass

        if uid not in tags:
            tags[uid] = [entrence]
        else:
            tags[uid].append(entrence)

    for uid in tags:

        tags[uid] = sorted(tags[uid], key=lambda k: k['time'])

    return tags

class apiInterface:
    def __init__(self):

        self._floorlist = []
        self._apibase = API_BASE
        self._apitoken = API_TOKEN

        # to filter only the devicese that are currenctly used for twr
        self._node_filter_list = set(NODE_FILTER)
        pass

    def get_nodes(self):

        floors = {}
        s = Session()

        s.headers.update({"Authorization": "Api-Key {}".format(self._apitoken)})

        try:
            nodes_request = s.get(f"{self._apibase}/devices?type=node", timeout=HTTP_TIMEOUT)
        except RequestException as exc:
            logging.warning(f"Failed to get current Nodes: {exc}")
            sys.exit(1)

        if not nodes_request.ok:
            logging.warning(f"Failed to query API for Nodes: { nodes_request.reason }")
            sys.exit(1)

        if not nodes_request.json():
            logging.warning(f"No Nodes found")
            return {}

        for node in nodes_request.json():
            n = self.parse_props(node.get("properties", []))
            if n is not None:
                if "uid" in n and n["uid"] not in self._node_filter_list:
                    n["name"] = node["name"]
                    n["id"] = node["id"]
                    if MILIMETER:
                        n['x'] = int(n['x'])
                        n['y'] = int(n['y'])
                        n['z'] = int(n['z'])
                    else:
                        n['x'] = float(n['x'])/1000
                        n['y'] = float(n['y'])/1000
                        n['z'] = float(n['z'])/1000

                    floor = int(n.pop("floor"))
                    if floor not in floors:
                        floors[floor] = [n]
                    else:
                        floors[floor].append(n)
        
        self._floorlist = floors

        return floors

    def parse_props(self, props):

        n = {}

        for prop in props:
            if (
                prop["propId"]
                in [
                    NODE_UID_PROP_ID,
                    NODE_X_PROP_ID,
                    NODE_Y_PROP_ID,
                    NODE_Z_PROP_ID,
                    NODE_FLOOR_PROP_ID,
                    NODE_TYPE_PROP_ID
                ]
            ):
                if prop['name'] == 'floor' and prop['value'] is None:
                    return
                # if pos x and y are not existing just return
                elif (prop['name'] == 'x' or prop['name'] == 'y' or prop['name'] == 'z') and prop['value'] is None:
                    return
                else: 
                    n[prop["name"]] = prop["value"]

        return n

def nodes_from_list(name):

    f = open(name, 'r', newline='')
    reader = csv.reader(f, delimiter =',', dialect='excel')

    floors = {}

    # just a place holder for the second floor
    floor = 2

    for row in reader:
        if MILIMETER:
            if floor not in floors:
                floors[floor] = [{'uid' : row[0], 'name': row[1], 'x': float(row[2]), 'y': float(row[3]), 'z': float(row[4])}]
            else:
                floors[floor].append({'uid' : row[0], 'name': row[1], 'x': float(row[2]), 'y': float(row[3]), 'z': float(row[4])})
        else:
            if floor not in floors:
                floors[floor] = [{'uid' : row[0], 'name': row[1], 'x': float(row[2])/1000, 'y': float(row[3])/1000, 'z': float(row[4])/1000}]
            else:
                floors[floor].append({'uid' : row[0], 'name': row[1], 'x': float(row[2])/1000, 'y': float(row[3])/1000, 'z': float(row[4])/1000})


    return floors

if __name__ == "__main__":

    api = apiInterface()

    if API_ONLINE:
        floors = api.get_nodes()
    else:
        floors = nodes_from_list(name = NODE_FROM_LIST)

    try:
        f = open(TDOA_REPORTS)
        data = json.load(f)
    except OSError as exc:
        logging.warning(f"Failed to open file: {exc}")
        sys.exit(1)
    
    tags = main(data)

    app = QApplication(sys.argv)
    window = Window(tags, floors)
    window.show()
    app.exec_()
