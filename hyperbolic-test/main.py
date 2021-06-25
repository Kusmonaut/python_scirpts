
from matplotlib import pyplot as plt
import numpy as np
import math
from scipy.spatial import distance

b = 40
a = 22.9


# How many towers. All towers recieve the transmission.
num_towers = 4

# Metre length of a square containing the transmitting
# device, centred around (x, y) = (0, 0). Device will be randomly placed
# in this area.
tx_square_side = 50

# Metre length of a square containing the towers,
# centred around (x, y) = (0, 0). towers will be randomly placed
# in this area.
rx_square_side = 25

# Speed of transmission propogation. Generally equal to speed of 
# light for radio signals.
v = 299792458

# Time at which transmission is performed. Really just useful to
# make sure the code is using relative times rather than depending on one
# of the receive times being zero.
t_0 = 2.5

# Metre increments to radii of circles when generating locus of
# circle intersection.
delta_d = int(1)

# Max distance a transmission will be from the tower that first
# received the transmission. This puts an upper bound on the radii of the
# circle, thus limiting the size of the locus to be near the towers.
max_d = int(100)

# Standard deviation of noise added to the
# receive times at the towers. Mean is zero.
rec_time_noise_stdd = 1e-6

# Whether to plot circles that would be
# used if performing trilateration. These are circles that are centred
# on the towers and touch the transmitter site.
plot_trilateration_circles = False

# Whether to plot a straight line
# between every pair of towers. This is useful for visualising the
# hyperbolic loci focal points.
plot_lines_between_towers = False

def get_locus(tower_1, tower_2, time_1, time_2, v, delta_d, max_d):
    ''' Return a locus in x, y given two towers and their recieve times.

    Given two towers at locations tower_1 and tower_2, a message transmitted
    at some arbitrary time at location (x_t, y_t), and the times at which
    the towers received the transmission, the set of possible
    locations of the transmission is defined by the locus of the intersection
    of two circles with one circle around each tower and the difference in
    radius of the circles defined by the difference in receive tiemes
    of the transmission and the propogation speed of the transmission.

    Args:
        tower_1 (tuple): (x, y) of one tower.
        tower_2 (tuple): (x, y) of other tower.
        time_1 (float): Transmission recieve time at tower_1.
        time_2 (float): Transmission recieve time at tower_2.
        v (int): Speed of transmission propogation.
        delta_d (int): Metre increments to radii of circles when generating
            locus of circle intersection.
        max_d (int): Max distance a transmission will be from the tower that
            first received the transmission. This puts an upper bound on the
            radii of the circle, thus limiting the size of the locus to be
            near the towers.

    Returns
        list of form [x, y], with:
                x: list of x values of locus.
                y: list of y values of locus.
    '''
    # two lines, x0/y0 and x1/y1 corresponding to the two intersections of the
    # circles. These will be concateneated at the end to form a single line.
    x0 = []
    x1 = []
    y0 = []
    y1 = []

    # The radii have constant difference of t_delta_d. "time delta difference"
    t_delta_d = abs(time_1 - time_2) * v

    # Determine which tower received the transmission first.
    if(time_1 < time_2):
        circle1 = (tower_1[0], tower_1[1], 0)
        circle2 = (tower_2[0], tower_2[1], t_delta_d)
    else:
        circle1 = (tower_2[0], tower_2[1], 0)
        circle2 = (tower_1[0], tower_1[1], t_delta_d)

    # Iterate over all potential radii.
    for _ in range(int(max_d)//int(delta_d)):
        intersect = circle_intersection(circle1, circle2)
        if(intersect is not None):
            x0.append(intersect[0][0])
            x1.append(intersect[1][0])
            y0.append(intersect[0][1])
            y1.append(intersect[1][1])

        circle1 = (circle1[0], circle1[1], circle1[2]+delta_d)
        circle2 = (circle2[0], circle2[1], circle2[2]+delta_d)

    # Reverse so the concatenated locus is continous. Could reverse only
    # x1/y1 instead if you wanted.
    x0 = list(reversed(x0))
    y0 = list(reversed(y0))

    # Concatenate
    x = x0 + x1
    y = y0 + y1

    return [x, y]

def get_loci(rec_times, towers, v, delta_d, max_d):
    ''' Return a set of loci on which a transmission may have occurred.

    Args:
        rec_times (np.array 1D): The times at which the towers recieved
            the transmission, in seconds. Element i corresponds to tower i.
        towers (np.array 2D): Locations of towers. Tower i is located at
            (x, y) = (towers[i][0], towers[i][1])
        v (int): Speed of transmission propogation.
        delta_d (int): Metre increments to radii of circles when generating
            locus of circle intersection.
        max_d (int): Max distance a transmission will be from the tower that
            first received the transmission. This puts an upper bound on the
            radii of the circle, thus limiting the size of the locus to be
            near the towers.

    Returns
        list of tuples, where each tuple contains a list of x and a list of
            y elements.
        '''

    if(rec_times.shape[0] == 0):
        return [] # return no loci
    
    loci = []

    # Tower that receives the transmission first.
    first_tower = int(np.argmin(rec_times))
    # Iterate over all other towers.
    for j in [x for x in range(towers.shape[0]) if x!= first_tower]:
        # print('tower', str(first_tower), 'to', str(j))
        locus = get_locus(tower_1=(towers[first_tower][0],
                                   towers[first_tower][1]),
                          tower_2=(towers[j][0], towers[j][1]),
                          time_1=rec_times[first_tower],
                          time_2=rec_times[j],
                          v=v, delta_d=delta_d, max_d=max_d)
        # Sometimes empty locus is produced depending on geometry of the
        # situation. Discard these.
        if(len(locus[0]) > 0):
            loci.append(locus)
    return loci

def circle_intersection(circle1, circle2):
    ''' Calculate intersection points of two circles.
    from https://gist.github.com/xaedes/974535e71009fa8f090e

    Args:
        circle1: tuple(x,y,radius)
        circle2: tuple(x,y,radius)

    Returns
        tuple of intersection points (which are (x,y) tuple)

    >>> circle_intersection((-0.5, 0, 1), (0.5, 0, 1))
    ((0.0, -0.8660254037844386), (0.0, 0.8660254037844386))
    >>> circle_intersection((-1, 0, 1), (1, 0, 1))
    ((0.0, 0.0), (0.0, 0.0))

    '''
    x1,y1,r1 = circle1
    x2,y2,r2 = circle2
    # http://stackoverflow.com/a/3349134/798588
    # d is euclidean distance between circle centres
    dx,dy = x2-x1,y2-y1
    d = math.sqrt(dx*dx+dy*dy)
    if d > r1+r2:
        # print('No solutions, the circles are separate.')
        return None # No solutions, the circles are separate.
    elif d < abs(r1-r2):
        # No solutions because one circle is contained within the other
        # print('No solutions because one circle is contained within the other')
        return None
    elif d == 0 and r1 == r2:
        # Circles are coincident - infinite number of solutions.
        # print('Circles are coincident - infinite number of solutions.')
        return None

    a = (r1*r1-r2*r2+d*d)/(2*d)
    h = math.sqrt(r1*r1-a*a)
    xm = x1 + a*dx/d
    ym = y1 + a*dy/d
    xs1 = xm + h*dy/d
    xs2 = xm - h*dy/d
    ys1 = ym - h*dx/d
    ys2 = ym + h*dx/d

    return ((xs1,ys1),(xs2,ys2))


def main():
    # Generate towers with x and y coordinates.
    # for tower i: x, y = towers[i][0], towers[i][1]
    
    towers = np.array(([0, 0.35], [8.3, 8.6], [6, 11], [-2.5, 3]))
    # towers = (np.random.rand(num_towers, 2)-0.5) * rx_square_side
    print('towers:\n', towers)

    # location of transmitting device with tx[0] being x and tx[1] being y.
    tx = np.array([-0.2958069119321293, 3.673564858162514])
    prime_node = np.array([6.059, 11.724])

    test = prime_node - tx

    tust = distance.euclidean(tx, prime_node)

    rec_times = [
    tust/v + 2.5156618121968677e-08,
    tust/v + 3.3564191426194157e-09,
    tust/v + 2.7847082861853778e-08,
    tust/v + 0.0]
    # tx = (np.random.rand(2)-0.5) * tx_square_side
    print('tx:', tx)

    # Distances from each tower to the transmitting device,
    # simply triangle hypotenuse.
    # distances[i] is distance from tower i to transmitter.
    distances = np.array([ ( (x[0]-tx[0])**2 + (x[1]-tx[1])**2 )**0.5
                        for x in towers])
    print('distances:', distances)

    # Time at which each tower receives the transmission.
    rec_times = distances/v
    # Add noise to receive times
    # rec_times += np.random.normal(loc=0, scale=rec_time_noise_stdd,
    #                             size=num_towers)
    print('rec_times:', rec_times)

    # Get the loci.
    loci = get_loci(rec_times, towers, v, delta_d, max_d)

    fig, ax = plt.subplots(figsize=(5,5))
    max_width = max(tx_square_side, rx_square_side)/2
    ax.set_ylim((max_width*-1, max_width))
    ax.set_xlim((max_width*-1, max_width))
    for i in range(towers.shape[0]):
        x = towers[i][0]
        y = towers[i][1]
        ax.scatter(x, y)
        ax.annotate('Tower '+str(i), (x, y))
    ax.scatter(tx[0], tx[1])
    ax.annotate('Tx', (tx[0], tx[1]))

    # Iterate over every unique combination of towers and plot nifty stuff.
    for i in range(num_towers):
        if(plot_trilateration_circles):
            # Circle from tower i to tx site
            circle1 = (towers[i][0], towers[i][1], distances[i])
            circle = plt.Circle((circle1[0], circle1[1]),
                                radius=circle1[2], fill=False)
            ax.add_artist(circle)
        for j in range(i+1, num_towers):
            if(plot_lines_between_towers):
                # Line between towers
                ax.plot((towers[i][0], towers[j][0]),
                        (towers[i][1], towers[j][1]))

    for locus in loci:
        ax.plot(locus[0], locus[1])
    plt.show()


if __name__ == "__main__":
    main()
    # x = np.arange(-30.0, 30.0, 0.1)
    # y1 = b * np.sqrt((np.square(x)/ np.square(a))-1)
    # y2 = - (b * np.sqrt((np.square(x)/ np.square(a))-1))
    # # y = np.sin(2 * np.pi * x)

    # fig, ax = plt.subplots()
    
    # ax.plot(x, y1)
    # ax.plot(x, y2)

    # plt.show()