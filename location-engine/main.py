
import json
import logging
import os
import sys

import numpy as np

from multilateration import MultiLateration

MILIMETER = int(os.getenv('MILIMETER',  1))
TDOA_REPORTS = os.getenv('TDOA_REPORTS', 'results/1615540960/asset_135_floor_2.json')

def get_tag_reports():

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

    return tags

def main(tag_reports):

    # 01aa2145caf2061c, 01aa2145caf20eae, 01aa2145ca144239, 01aa2145ccb1ce99
    node_coords = np.mat([[ 7.994, -0.382], [ 4.857, -2.483], [11.694, -2.262]])
    tdoa = np.array([[ 0.00000000e+00,  1.19224420e-08, -1.27852378e-08]])

    # node_coords = np.mat([[6.059, 11.724], [8.332, 8.582], [-0.049, 0.296], [-2.559, 2.986]])
    # tdoa = np.array([[0, -2.3792523506926955e-09, -1.882530931140991e-08, -1.9270704143536932e-08]])
    cleSolver3D = False

    tag_reports

    multilaterator = MultiLateration()
    multilaterator.setNodes(node_coords, cleSolver3D)
    result = multilaterator.multilaterate(tdoa, cleSolver3D)
    return result

if __name__ == "__main__":

    try:
        f = open(TDOA_REPORTS)
        data = json.load(f)
    except OSError as exc:
        logging.warning(f"Failed to open file: {exc}")
        sys.exit(1)

    tag_reports = get_tag_reports()

    main(tag_reports)

    pass