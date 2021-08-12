"""
Intranav GmbH © 2021
check tag positioning
"""

import numpy as np
import time as tm

from multilaterate import get_loci
import matplotlib.pyplot as plt


SPEED_OF_LIGHT = 299702547000


towers = np.array([[-2166, 13137], [-4715.0, 10720.0], [-1773, 7694], [  754., 10178.]])
rec_times = np.array([0.0, 1.604954391609681e-09, -1.3815821375828818e-08, -1.2063200216516634e-08])
delta_d = 1
max_d = 10000

def create_intersection():
    loci = []

    first_tower = int(np.where(rec_times == 0)[0])
    for j in [x for x in range(towers.shape[0]) if x!= first_tower]:
        locus = calc_intersection(tower_1=(towers[first_tower][0],
                                   towers[first_tower][1]),
                          tower_2=(towers[j][0], towers[j][1]),
                          time=rec_times[j])
        loci.append(locus)
    
    return loci

def calc_intersection(tower_1, tower_2, time):
    x1 = tower_1[0]
    y1 = tower_1[1]
    x2 = tower_2[0]
    y2 = tower_2[1]
    dx = x2-x1
    dx_tower = tower_2[0] - (dx/2)
    dy = y2-y1
    dy_tower = tower_2[1] - (dy/2)
    d = np.sqrt( dx*dx + dy*dy )
    theta = np.arctan(dx/dy)
    a = (time*SPEED_OF_LIGHT)/2
    c = d/2
    b = np.sqrt( (c*c) - (a*a) )
    x = [] 
    y = []
    y2 = []
    for i in range(-int(1000/2), int(1000/2)):
        x_ = i
        # y_= 2.99506465007412e-70 * (3.3713603331508473e72 + 5.721833082973572e68 * i - 1. * np.sqrt(4.843840912886152e145 + 2.232761787078023e141 * i + 1.5503647967492694e139 * i**2))
        # y_= 5.990129300148239e-72 * (1.7557201774966324e75 + 2.8609165414867856e70 * i - 1. * np.sqrt(1.4269679250986366e149 + 5.813832598327787e145 * i + 3.875911991873174e142 * i**2))
        # y_= 1.6367026679239476e-85 * (6.318560931176262e88 + 1.0470600638890798e84 * i - 1. * np.sqrt(2.1578020890372452e176 - 1.0574405500048376e173 * i + 5.1916657086235014e169 * i**2))
        # y_= 1.6367026679239476e-85 * (6.532876393630171e88 + 1.0470600638890798e84 * i - 1. * np.sqrt(4.912063822500576e176 + 2.614930781965888e173 * i + 5.1916657086235014e169 * i**2))
        # y_= 6.7568940332110595e-87 * (1.5853162666869645e90 + 2.5362629510255417e85 * i - 1. * np.sqrt(3.194507066649804e179 + 1.653686462333309e176 * i + 3.0461556098607913e172 * i**2))
        # y_= 7.598211008675736e-87 * (1.4046646519855365e90 + 2.2554335462480855e85 * i - 1. * np.sqrt(2.0506456094572878e179 + 1.118899744444298e176 * i + 2.4089267868792567e172 * i**2))
        # y_= 1.672337003923654e-86 * (8.013647651878973e89 + 1.0247491958995794e85 * i - 1. * np.sqrt(4.2331211963354126e178 + 2.3097358829015902e175 * i + 4.972773770815189e171 * i**2))
        # y_= 1.672337003923654e-86 * (6.538583048846833e89 + 1.0247491958995794e85 * i - 1. * np.sqrt(3.842193583722586e178 + 2.1347791495721054e175 * i + 4.972773770815189e171 * i**2))
        # y_= 1.4689713786044185e-80 * (5.666344204903617e83 - 1.3629415693054348e80 * i - 1. * np.sqrt(9.55801152285081e167 - 2.3058820198884533e164 * i + 1.3695700510937922e160 * i**2))
        # y_= (0.5 * (-np.sqrt(-2.8889220905463392e23 * np.cos(2 * theta) + 4.14717968196e15 * i**2 + 9.94078969765812e19 * i * np.sin(theta) + 2.9325784557352085e23) - np.cos(theta) * (1.50013298e8 * i * np.sin(theta) + 4.3806673125e11)))/(1.8275625e7 * np.cos(theta)**2 - 5.6731024e7 * np.sin(theta)**2)
        # y_1 = (-2 * a**2 * i * np.sin(theta) * np.cos(theta) - np.sqrt(2) * np.sqrt(a**4 * b**2 * np.cos(2 * theta) + a**4 * (-b**2) + a**2 * b**4 * np.cos(2 * theta) + a**2 * b**4 + 2 * a**2 * b**2 * i**2) - 2 * b**2 * i * np.sin(theta) * np.cos(theta))/(2 * (b**2 * np.cos(theta)**2 - a**2 * np.sin(theta)**2))
        # y_2 = 3.5113092059313026e-71 * (-5.722963393452829e70 * i - 1. * np.sqrt(-2.5953833468330722e147 + 2.4159188624828912e141 * i**2))
        # y_ = np.sign(time) * (np.sqrt((1+ ((float(i)*float(i))/(b*b)) ) * (a*a)))
        # theta = -0.13738
        # y_1_neg = (-(np.sqrt(2) * np.sqrt(a**2 * (-np.cos(2 * theta)) - a**2 - b**2 * np.cos(2 * theta) + b**2 + i**2 * np.cos(4 * theta) + i**2))/(a * b) - (2 * i * np.sin(theta) * np.cos(theta))/a**2 + (2 * i * np.sin(theta) * np.cos(theta))/b**2)/(2 * ((np.cos(theta)**2)/b**2 - (np.sin(theta)**2)/a**2))
        # y_1_pos = ((np.sqrt(2) * np.sqrt(a**2 * (-np.cos(2 * theta)) - a**2 - b**2 * np.cos(2 * theta) + b**2 + i**2 * np.cos(4 * theta) + i**2))/(a * b) - (2 * i * np.sin(theta) * np.cos(theta))/a**2 + (2 * i * np.sin(theta) * np.cos(theta))/b**2)/(2 * ((np.cos(theta)**2)/b**2 - (np.sin(theta)**2)/a**2))
        # y_1_pos = ( (np.sqrt(2) * np.sqrt(a**2 * np.cos(2 * theta) + a**2 + b**2 * np.cos(2 * theta) - b**2 + i**2 * np.cos(4 * theta) + i**2))/(a * b) - (2 * i * np.sin(theta) * np.cos(theta))/a**2 + (2 * i * np.sin(theta) * np.cos(theta))/b**2)/(2 * ((np.cos(theta)**2)/b**2 - (np.sin(theta)**2)/a**2))
        # y_1_neg = (-(np.sqrt(2) * np.sqrt(a**2 * np.cos(2 * theta) + a**2 + b**2 * np.cos(2 * theta) - b**2 + i**2 * np.cos(4 * theta) + i**2))/(a * b) - (2 * i * np.sin(theta) * np.cos(theta))/a**2 + (2 * i * np.sin(theta) * np.cos(theta))/b**2)/(2 * ((np.cos(theta)**2)/b**2 - (np.sin(theta)**2)/a**2))
        # y_1_pos = (-2 * a**2 * i * np.tan(theta) - np.sqrt(2) * np.sqrt(-a**2 * b**2 * (1/np.cos(theta)**2) + a**2 * b**2 * np.cos(2 * theta) * (1/np.cos(theta)**2) + a**2 * b**2 * (1/np.cos(theta)**2) + a**2 * b**2 * np.cos(2 * theta) * (1/np.cos(theta)**2) + 2 * a**2 * b**2 * i**2 * (1/np.cos(theta)**2)) - 2 * b**2 * i * np.tan(theta))/(2 * (b**2 - a**2 * np.tan(theta)**2))
        y_1_pos = (-np.sqrt(((i * np.sin(theta) * np.cos(theta))/a**2 + (i * np.sin(theta) * np.cos(theta))/b**2)**2 - 4 * ((np.cos(theta)**2)/a**2 - (np.sin(theta)**2)/b**2) * ((i**2 * np.sin(theta)**2)/a**2 - (i**2 * np.cos(theta)**2)/b**2 - 1)) - (i * np.sin(theta) * np.cos(theta))/a**2 - (i * np.sin(theta) * np.cos(theta))/b**2)/(2 * ((np.cos(theta)**2)/a**2 - (np.sin(theta)**2)/b**2))
        y_1_neg = ( np.sqrt(((i * np.sin(theta) * np.cos(theta))/a**2 + (i * np.sin(theta) * np.cos(theta))/b**2)**2 - 4 * ((np.cos(theta)**2)/a**2 - (np.sin(theta)**2)/b**2) * ((i**2 * np.sin(theta)**2)/a**2 - (i**2 * np.cos(theta)**2)/b**2 - 1)) - (i * np.sin(theta) * np.cos(theta))/a**2 - (i * np.sin(theta) * np.cos(theta))/b**2)/(2 * ((np.cos(theta)**2)/a**2 - (np.sin(theta)**2)/b**2))

        x.append( x_ )
        y.append( (y_1_pos, y_1_neg) )
        
    return (x, y)

def create_graph():

    loci = []

    first_tower = int(np.where(rec_times == 0)[0])
    for j in [x for x in range(towers.shape[0]) if x!= first_tower]:
        locus = calc_hyperbole(tower_1=(towers[first_tower][0],
                                   towers[first_tower][1]),
                          tower_2=(towers[j][0], towers[j][1]),
                          time=rec_times[j])
        loci.append(locus)
    
    return loci

def calc_hyperbole(tower_1, tower_2, time):
    x1 = tower_1[0]
    y1 = tower_1[1]
    x2 = tower_2[0]
    y2 = tower_2[1]
    dx = x2-x1
    dy = y2-y1
    d = np.sqrt( dx*dx + dy*dy )
    theta = np.arctan(dx/dy)

    a = (time*SPEED_OF_LIGHT)/2
    c = d/2
    b = np.sqrt( (c*c) - (a*a) )

    y = []
    x = []

    start = tm.time()
    for i in range(-max_d, max_d):
        x_ = i
        y_ = np.sign(time) * (np.sqrt((1+ ((float(i)*float(i))/(b*b)) ) * (a*a)))
        
        x.append( tower_2[0]-(dx/2) + (x_ * np.cos(-theta) - y_ * np.sin(-theta)) )
        y.append( tower_2[1]-(dy/2) + (x_ * np.sin(-theta) + y_ * np.cos(-theta)) )
    end = tm.time()
    runtime = end - start
    return (x, y)

def test ():
    x_1 = 0.3
    y_1 = -1
    x_2 = -2.4
    y_2 = -2
    c_1 = -0.3


    a = x_1
    b = y_1
    c = x_2
    d = y_2
    e = c_1
    x_ = []
    y_ = []
    l = (a*d - a*b + b*c - c*d)
    m = (a**3 - a**2*c + a*b**2- a*c**2- a*d**2 - e**2*a- b**2*c + c**3 + c*d**2 - c*e**2)
    n = (-a**2 + 2*a*c - c**2 + e**2)
    o = (a*b - a*d - b*c + c*d)

    g = (4*a**2*b - 4*a**2*d + 4*b**3 - 4*b**2*d - 4*b*c**2 - 4*b*d**2 - 4*b*e**2 + 4*c**2*d + 4*d**3 - 4*d*e**2)
    h = 4*(-4*b**2 + 8*b*d - 4*d**2 + 4*e**2)
    i = (-a**4 - 2*a**2*b**2 + 2*a**2*c**2 + 2*a**2*d**2 + 2*a**2*e**2 - b**4 + 2*b**2*c**2 + 2*b**2*d**2 + 2*b**2*e**2 - c**4 - 2*c**2*d**2 + 2*c**2*e**2 - d**4 + 2*d**2*e**2 - e**4)
    j = (-4*b**3 + 4*b**2*d + 4*b*c**2 + 4*b*d**2 + 4*b*e**2 - 4*c**2*d - 4*d**3 + 4*d*e**2)
    k = (2* (-4*b**2 + 8*b*d - 4*d**2 + 4*e**2))
    f = (-4*a**2*b + 4*a**2*d)

    for x in range(-300, 300):
        y_.append((f - np.sqrt((8*x*l+g)**2 - h*(4*x*m + 4*x**2*n + i)) + 8*x*o + j)/k)
        y_.append((-4 * a**2 * b + 4 * a**2 * d - np.sqrt((4 * a**2 * b - 4 * a**2 * d - 8 * a * b * x + 8 * a * d * x + 4 * b**3 - 4 * b**2 * d - 4 * b * c**2 + 8 * b * c * x - 4 * b * d**2 - 4 * b * e**2 + 4 * c**2 * d - 8 * c * d * x + 4 * d**3 - 4 * d * e**2)**2 - 4 * (-4 * b**2 + 8 * b * d - 4 * d**2 + 4 * e**2) * (-a**4 + 4 * a**3 * x - 2 * a**2 * b**2 + 2 * a**2 * c**2 - 4 * a**2 * c * x + 2 * a**2 * d**2 + 2 * a**2 * e**2 - 4 * a**2 * x**2 + 4 * a * b**2 * x - 4 * a * c**2 * x + 8 * a * c * x**2 - 4 * a * d**2 * x - 4 * a * e**2 * x - b**4 + 2 * b**2 * c**2 - 4 * b**2 * c * x + 2 * b**2 * d**2 + 2 * b**2 * e**2 - c**4 + 4 * c**3 * x - 2 * c**2 * d**2 + 2 * c**2 * e**2 - 4 * c**2 * x**2 + 4 * c * d**2 * x - 4 * c * e**2 * x - d**4 + 2 * d**2 * e**2 - e**4 + 4 * e**2 * x**2)) + 8 * a * b * x - 8 * a * d * x - 4 * b**3 + 4 * b**2 * d + 4 * b * c**2 - 8 * b * c * x + 4 * b * d**2 + 4 * b * e**2 - 4 * c**2 * d + 8 * c * d * x - 4 * d**3 + 4 * d * e**2)/(2 * (-4 * b**2 + 8 * b * d - 4 * d**2 + 4 * e**2)))
        # y_.append((-4 * a**2 * b + 4 * a**2 * d - np.sqrt((4 * a**2 * b - 4 * a**2 * d - 8 * a * b * x + 8 * a * d * x + 4 * b**3 - 4 * b**2 * d - 4 * b * c**2 + 8 * b * c * x - 4 * b * d**2 - 4 * b * e**2 + 4 * c**2 * d - 8 * c * d * x + 4 * d**3 - 4 * d * e**2)**2 - 4 * (-4 * b**2 + 8 * b * d - 4 * d**2 + 4 * e**2) * (-a**4 + 4 * a**3 * x - 2 * a**2 * b**2 + 2 * a**2 * c**2 - 4 * a**2 * c * x + 2 * a**2 * d**2 + 2 * a**2 * e**2 - 4 * a**2 * x**2 + 4 * a * b**2 * x - 4 * a * c**2 * x + 8 * a * c * x**2 - 4 * a * d**2 * x - 4 * a * e**2 * x - b**4 + 2 * b**2 * c**2 - 4 * b**2 * c * x + 2 * b**2 * d**2 + 2 * b**2 * e**2 - c**4 + 4 * c**3 * x - 2 * c**2 * d**2 + 2 * c**2 * e**2 - 4 * c**2 * x**2 + 4 * c * d**2 * x - 4 * c * e**2 * x - d**4 + 2 * d**2 * e**2 - e**4 + 4 * e**2 * x**2)) + 8 * a * b * x - 8 * a * d * x - 4 * b**3 + 4 * b**2 * d + 4 * b * c**2 - 8 * b * c * x + 4 * b * d**2 + 4 * b * e**2 - 4 * c**2 * d + 8 * c * d * x - 4 * d**3 + 4 * d * e**2)/(2 * (-4 * b**2 + 8 * b * d - 4 * d**2 + 4 * e**2)))
        x_.append(x)
    
    plt.plot(x_, y_)
    plt.grid()
    plt.show()
    pass

def test2():
    x_1 = -3
    y_1 = -0.8
    x_2 = 66.6
    y_2 = 100
    x_3 = 100
    y_3 = -100
    c_1 = 120
    c_2 = 138

    f_1 = (x_2 - x_1 - y_1)
    g_1 = (x_1**2 - x_2**2 + c_1**2)
    
    f_2 = (x_3 - x_1 - y_1)
    g_2 = (x_1**2 - x_3**2 + c_2**2)

    e_1 = c_1
    e_2 = c_2
    a = x_1
    b = y_1
    c_1 = x_2
    d_1 = y_2
    c_2 = x_3
    d_2 = y_3
    

    x__1 = (-np.sqrt((-8 * a * e_1**2 + 16 * a * e_2 * e_1 - 8 * a * e_2**2 - 8 * b * e_1**2 + 16 * b * e_2 * e_1 - 8 * b * e_2**2 - 4 * f_1 * g_1 + 4 * f_2 * g_1 + 4 * f_1 * g_2 - 4 * f_2 * g_2)**2 - 4 * (8 * e_1**2 - 16 * e_2 * e_1 + 8 * e_2**2 - 4 * f_1**2 - 4 * f_2**2 + 8 * f_1 * f_2) * (4 * a**2 * e_1**2 + 4 * a**2 * e_2**2 - 8 * a**2 * e_1 * e_2 + 4 * b**2 * e_1**2 + 4 * b**2 * e_2**2 - 8 * b**2 * e_1 * e_2 - g_1**2 - g_2**2 + 2 * g_1 * g_2)) + 8 * a * e_1**2 - 16 * a * e_2 * e_1 + 8 * a * e_2**2 + 8 * b * e_1**2 - 16 * b * e_2 * e_1 + 8 * b * e_2**2 + 4 * f_1 * g_1 - 4 * f_2 * g_1 - 4 * f_1 * g_2 + 4 * f_2 * g_2)/(2 * (8 * e_1**2 - 16 * e_2 * e_1 + 8 * e_2**2 - 4 * f_1**2 - 4 * f_2**2 + 8 * f_1 * f_2))
    x__2 = (+np.sqrt((-8 * a * e_1**2 + 16 * a * e_2 * e_1 - 8 * a * e_2**2 - 8 * b * e_1**2 + 16 * b * e_2 * e_1 - 8 * b * e_2**2 - 4 * f_1 * g_1 + 4 * f_2 * g_1 + 4 * f_1 * g_2 - 4 * f_2 * g_2)**2 - 4 * (8 * e_1**2 - 16 * e_2 * e_1 + 8 * e_2**2 - 4 * f_1**2 - 4 * f_2**2 + 8 * f_1 * f_2) * (4 * a**2 * e_1**2 + 4 * a**2 * e_2**2 - 8 * a**2 * e_1 * e_2 + 4 * b**2 * e_1**2 + 4 * b**2 * e_2**2 - 8 * b**2 * e_1 * e_2 - g_1**2 - g_2**2 + 2 * g_1 * g_2)) + 8 * a * e_1**2 - 16 * a * e_2 * e_1 + 8 * a * e_2**2 + 8 * b * e_1**2 - 16 * b * e_2 * e_1 + 8 * b * e_2**2 + 4 * f_1 * g_1 - 4 * f_2 * g_1 - 4 * f_1 * g_2 + 4 * f_2 * g_2)/(2 * (8 * e_1**2 - 16 * e_2 * e_1 + 8 * e_2**2 - 4 * f_1**2 - 4 * f_2**2 + 8 * f_1 * f_2))
    pass
    t = 123

def test3_paper_example():

    x_1 = -40
    y_1 = 40
    x_2 = -40
    y_2 = -40
    x_3 = 40
    y_3 = -40
    x_4 = 40
    y_4 = 41
    c_1 = 1.24929
    c_2 = -12.6078190689049
    c_3 = -13.411355865854

    Mx = []
    My = []

    Nx = []
    Ny = []
    delta = []

    a = []
    b = []
    c = []
    
    x1 = []
    x2 = []
    y1 = []
    y2 = []

    K1 = []
    K2 = []

    A = c_1**2 - x_2**2 - y_2**2
    B = 2*c_1
    C = c_2**2 - x_3**2 - y_3**2
    D = 2*c_2
    E = c_3**2 - x_4**2 - y_4**2
    F = 2*c_3

    delta.append( 4*(x_2*y_3 - y_2*x_3)             )
    delta.append( 4*(x_3*y_4 - y_3*x_4)             )
    delta.append( 4*(x_4*y_2 - y_4*x_2)             )

    Mx.append( (4/delta[0]) * (c_2*y_2 - c_1*y_3)   )
    My.append( (4/delta[0]) * (c_1*x_3 - c_2*x_2)   )
    Nx.append( (2/delta[0]) * (C*y_2 - A*y_3)       )
    Ny.append( (2/delta[0]) * (A*x_3 - C*x_2)       )

    Mx.append( (4/delta[1]) * (c_3*y_3 - c_2*y_4)   )
    My.append( (4/delta[1]) * (c_2*x_4 - c_3*x_3)   )
    Nx.append( (2/delta[1]) * (E*y_3 - C*y_4)       )
    Ny.append( (2/delta[1]) * (C*x_4 - E*x_3)       )

    Mx.append( (4/delta[2]) * (c_1*y_4 - c_3*y_2)   )
    My.append( (4/delta[2]) * (c_3*x_2 - c_1*x_4)   )
    Nx.append( (2/delta[2]) * (A*y_4 - E*y_2)       )
    Ny.append( (2/delta[2]) * (E*x_2 - A*x_4)       )
    
    for i in range(0,3):
        a.append(Mx[i]**2 + My[i]**2 - 1)
        b.append(2*(Mx[i]*Nx[i] + My[i]*Ny[i]))
        c.append(Nx[i]**2 + Ny[i]**2)

        K1.append(((-b[i] + np.sqrt(b[i]**2 - 4*a[i]*c[i]))/2*a[i]))
        K2.append(((-b[i] - np.sqrt(b[i]**2 - 4*a[i]*c[i]))/2*a[i]))

        x1.append(((Mx[i] * K1[i]) + Nx[i]) + x_1)
        x2.append(((Mx[i] * K2[i]) + Nx[i]) + x_1)

        y1.append(My[i] * K1[i] + Ny[i] + y_1)
        y2.append(My[i] * K2[i] + Ny[i] + y_1)
    

    pass

    
def test4():
    x_1 = -40
    y_1 = 40
    x_2 = -40
    y_2 = -40
    x_3 = 44
    y_3 = -40
    x_4 = 40
    y_4 = 41
    c_1 = 1.2492912151
    c_2 = -10.147866133
    c_3 = -13.411354564969

    M = np.array(   [   [(x_3 - x_2), (y_3 - y_2), (c_2 - c_1)],
                        [(x_4 - x_2), (y_4 - y_2), (c_3 - c_1)],
                        [(x_3 - x_4), (y_3 - y_4), (c_2 - c_3)]])

    v = np.array(   [   ((x_3**2 - x_2**2 + y_3**2 - y_2**2 + c_1**2 - c_2**2)/2),
                        ((x_4**2 - x_2**2 + y_4**2 - y_2**2 + c_1**2 - c_3**2)/2),
                        ((x_3**2 - x_4**2 + y_3**2 - y_4**2 + c_3**2 - c_2**2)/2)])

    b = np.linalg.solve(M , v)
    pass

def test5():


    start = tm.time()
    # ein schnittpunkt
    # x_2+ y_2+ x_3+ y_3+ c_1+ c_2+ --> for x3 = y1 or y3
    # x_2+ y_2+ x_3+ y_3+ c_1+ c_2- --> for x3 = y1 or y3
    # x_2+ y_2+ x_3+ y_3+ c_1- c_2+ --> for x4 = y1 or y3, ? for x3 = y1 or y3
    # x_2+ y_2+ x_3+ y_3+ c_1- c_2- --> for x3 = y1 or y3
    # x_2+ y_2+ x_3+ y_3- c_1+ c_2+ --> for x3 = y1 or y4
    # x_2+ y_2+ x_3+ y_3- c_1+ c_2- --> for x3 = y1 or y4
    # x_2+ y_2+ x_3+ y_3- c_1- c_2+ --> for x3 = y1 or y4
    # x_2+ y_2+ x_3+ y_3- c_1- c_2- --> for x3 = y1 or y4
    # x_2+ y_2+ x_3- y_3+ c_1+ c_2+ --> for x4 = y1 or y3
    # x_2+ y_2+ x_3- y_3+ c_1+ c_2- --> for x4 = y1 or y3
    # x_2+ y_2+ x_3- y_3+ c_1- c_2+ --> for x4 = y1 or y3
    # x_2+ y_2+ x_3- y_3+ c_1- c_2- --> for x4 = y1 or y3
    # x_2+ y_2+ x_3- y_3- c_1+ c_2+ --> for x3 = y1 or y4
    # x_2+ y_2+ x_3- y_3- c_1+ c_2- --> for x3 = y1 or y4
    # x_2+ y_2+ x_3- y_3- c_1- c_2+ --> for x3 = y1 or y4
    # x_2+ y_2+ x_3- y_3- c_1- c_2- --> for x3 = y1 or y4
    # x_2+ y_2- x_3+ y_3+ c_1+ c_2+ --> for x4 = y2 or y3
    # x_2+ y_2- x_3+ y_3+ c_1+ c_2- --> for x4 = y2 or y3
    # x_2+ y_2- x_3+ y_3+ c_1- c_2+ --> for x4 = y2 or y3
    # x_2+ y_2- x_3+ y_3+ c_1- c_2- --> for x4 = y2 or y3
    # x_2+ y_2- x_3+ y_3- c_1+ c_2+ --> for x4 = y2 or y4
    # x_2+ y_2- x_3+ y_3- c_1+ c_2- --> for x4 = y2 or y4
    # x_2+ y_2- x_3+ y_3- c_1- c_2+ --> for x4 = y2 or y4
    # x_2+ y_2- x_3+ y_3- c_1- c_2- --> for x4 = y2 or y4
    # x_2+ y_2- x_3- y_3+ c_1+ c_2+ --> for x3 = y2 or y3
    # x_2+ y_2- x_3- y_3+ c_1+ c_2- --> for x3 = y2 or y3
    # x_2+ y_2- x_3- y_3+ c_1- c_2+ --> for x3 = y2 or y3
    # x_2+ y_2- x_3- y_3+ c_1- c_2- --> for x3 = y2 or y3
    # x_2+ y_2- x_3- y_3- c_1+ c_2+ --> for x3 = y2 or y4
    # x_2+ y_2- x_3- y_3- c_1+ c_2- --> for x3 = y3 or y4
    # x_2+ y_2- x_3- y_3- c_1- c_2+ --> for x3 = y2 or y4
    # x_2+ y_2- x_3- y_3- c_1- c_2- --> for x3 = y2 or y4
    
    # x_2- y_2+ x_3+ y_3+ c_1+ c_2+ --> for x3 = y1 or y3
    # x_2- y_2+ x_3+ y_3+ c_1+ c_2- --> for x

    # zwei schnittpunkte
    # x_2+ y_2+ x_3+ y_3+ c_1+ c_2+ --> 
    # x_2+ y_2+ x_3+ y_3+ c_1+ c_2- --> 
    # x_2+ y_2+ x_3+ y_3+ c_1- c_2+ --> for x3 = y1 or y3, for x4 = y1 or y3
    # x_2+ y_2+ x_3+ y_3+ c_1- c_2- --> 
    # x_2+ y_2+ x_3+ y_3- c_1+ c_2+ --> for x3 = y1 or y4, for x4 = y1 or y4
    # x_2+ y_2+ x_3+ y_3- c_1+ c_2- --> 
    # x_2+ y_2+ x_3+ y_3- c_1- c_2+ --> 
    # x_2+ y_2+ x_3+ y_3- c_1- c_2- --> 
    # x_2+ y_2+ x_3- y_3+ c_1+ c_2+ --> 
    # x_2+ y_2+ x_3- y_3+ c_1+ c_2- --> 
    # x_2+ y_2+ x_3- y_3+ c_1- c_2+ --> 
    # x_2+ y_2+ x_3- y_3+ c_1- c_2- --> 
    # x_2+ y_2+ x_3- y_3- c_1+ c_2+ --> for x3 = y1 or y4, for x4 = y1 or y4
    #
    #
    # x_2+ y_2- x_3- y_3+ c_1+ c_2+ --> for x3 = y2 or y3, for x4 = y2 or y3
    # x_2+ y_2- x_3- y_3+ c_1- c_2+ --> for x3 = y2 or y3, for x4 = y2 or y3
    # x_2+ y_2- x_3- y_3- c_1+ c_2+ --> for x3 = y2 or y4, for x4 = y2 or y4

    x_2 = 5
    y_2 = 3.9
    x_3 = -3.4
    y_3 = -36.8
    c_1 = 1
    c_2 = 3

    x1 = -(x_2**3*y_3**2 + x_3**3*y_2**2 - c_1**2*x_3**3 - c_2**2*x_2**3 - x_2*y_2*y_3**3 - x_3*y_2**3*y_3 + c_1*y_3*np.sqrt((- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(- c_1**2 + 2*c_1*c_2 - c_2**2 + x_2**2 - 2*x_2*x_3 + x_3**2 + y_2**2 - 2*y_2*y_3 + y_3**2)) - c_2*y_2*np.sqrt((- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(- c_1**2 + 2*c_1*c_2 - c_2**2 + x_2**2 - 2*x_2*x_3 + x_3**2 + y_2**2 - 2*y_2*y_3 + y_3**2)) + c_1**2*c_2**2*x_2 + c_1**2*c_2**2*x_3 - c_1**2*x_2*y_3**2 - c_2**2*x_2*y_2**2 - c_1**2*x_3*y_3**2 - c_2**2*x_3*y_2**2 + x_2*y_2**2*y_3**2 + x_3*y_2**2*y_3**2 - c_1*c_2**3*x_2 - c_1**3*c_2*x_3 + c_1*c_2*x_2*x_3**2 + c_1*c_2*x_2**2*x_3 + c_1*c_2*x_2*y_3**2 + c_1*c_2*x_3*y_2**2 + c_1**2*x_3*y_2*y_3 + c_2**2*x_2*y_2*y_3 - x_2*x_3**2*y_2*y_3 - x_2**2*x_3*y_2*y_3)/(2*(c_2**2*(x_2**2 + y_2**2) + x_3**2*(c_1**2 - y_2**2) + y_3**2*(c_1**2 - x_2**2) - 2*y_2*y_3*(c_1*c_2 - x_2*x_3) - 2*c_1*c_2*x_2*x_3))
    x2 = -(x_2**3*y_3**2 + x_3**3*y_2**2 - c_1**2*x_3**3 - c_2**2*x_2**3 - x_2*y_2*y_3**3 - x_3*y_2**3*y_3 - c_1*y_3*np.sqrt((- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(- c_1**2 + 2*c_1*c_2 - c_2**2 + x_2**2 - 2*x_2*x_3 + x_3**2 + y_2**2 - 2*y_2*y_3 + y_3**2)) + c_2*y_2*np.sqrt((- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(- c_1**2 + 2*c_1*c_2 - c_2**2 + x_2**2 - 2*x_2*x_3 + x_3**2 + y_2**2 - 2*y_2*y_3 + y_3**2)) + c_1**2*c_2**2*x_2 + c_1**2*c_2**2*x_3 - c_1**2*x_2*y_3**2 - c_2**2*x_2*y_2**2 - c_1**2*x_3*y_3**2 - c_2**2*x_3*y_2**2 + x_2*y_2**2*y_3**2 + x_3*y_2**2*y_3**2 - c_1*c_2**3*x_2 - c_1**3*c_2*x_3 + c_1*c_2*x_2*x_3**2 + c_1*c_2*x_2**2*x_3 + c_1*c_2*x_2*y_3**2 + c_1*c_2*x_3*y_2**2 + c_1**2*x_3*y_2*y_3 + c_2**2*x_2*y_2*y_3 - x_2*x_3**2*y_2*y_3 - x_2**2*x_3*y_2*y_3)/(2*(c_2**2*(x_2**2 + y_2**2) + x_3**2*(c_1**2 - y_2**2) + y_3**2*(c_1**2 - x_2**2) - 2*y_2*y_3*(c_1*c_2 - x_2*x_3) - 2*c_1*c_2*x_2*x_3))
    # x3 =  (c_1**2*x_3**3 - x_3**3*y_2**2 - x_2**3*y_3**2 + c_2**2*x_2**3 + x_2*y_2*y_3**3 + x_3*y_2**3*y_3 - c_1**2*c_2**2*x_2 - c_1**2*c_2**2*x_3 + c_1**2*x_2*y_3**2 + c_2**2*x_2*y_2**2 + c_1**2*x_3*y_3**2 + c_2**2*x_3*y_2**2 - x_2*y_2**2*y_3**2 - x_3*y_2**2*y_3**2 + c_1*y_3*np.sqrt(-(- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(c_1**2 + 2*c_1*c_2 + c_2**2 - x_2**2 + 2*x_2*x_3 - x_3**2 - y_2**2 + 2*y_2*y_3 - y_3**2)) + c_2*y_2*np.sqrt(-(- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(c_1**2 + 2*c_1*c_2 + c_2**2 - x_2**2 + 2*x_2*x_3 - x_3**2 - y_2**2 + 2*y_2*y_3 - y_3**2)) - c_1*c_2**3*x_2 - c_1**3*c_2*x_3 + c_1*c_2*x_2*x_3**2 + c_1*c_2*x_2**2*x_3 + c_1*c_2*x_2*y_3**2 + c_1*c_2*x_3*y_2**2 - c_1**2*x_3*y_2*y_3 - c_2**2*x_2*y_2*y_3 + x_2*x_3**2*y_2*y_3 + x_2**2*x_3*y_2*y_3)/(2*(c_2**2*(x_2**2 + y_2**2) + x_3**2*(c_1**2 - y_2**2) + y_3**2*(c_1**2 - x_2**2) + 2*y_2*y_3*(c_1*c_2 + x_2*x_3) + 2*c_1*c_2*x_2*x_3))
    # x4 =  (c_1**2*x_3**3 - x_3**3*y_2**2 - x_2**3*y_3**2 + c_2**2*x_2**3 + x_2*y_2*y_3**3 + x_3*y_2**3*y_3 - c_1**2*c_2**2*x_2 - c_1**2*c_2**2*x_3 + c_1**2*x_2*y_3**2 + c_2**2*x_2*y_2**2 + c_1**2*x_3*y_3**2 + c_2**2*x_3*y_2**2 - x_2*y_2**2*y_3**2 - x_3*y_2**2*y_3**2 - c_1*y_3*np.sqrt(-(- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(c_1**2 + 2*c_1*c_2 + c_2**2 - x_2**2 + 2*x_2*x_3 - x_3**2 - y_2**2 + 2*y_2*y_3 - y_3**2)) - c_2*y_2*np.sqrt(-(- c_1**2 + x_2**2 + y_2**2)*(- c_2**2 + x_3**2 + y_3**2)*(c_1**2 + 2*c_1*c_2 + c_2**2 - x_2**2 + 2*x_2*x_3 - x_3**2 - y_2**2 + 2*y_2*y_3 - y_3**2)) - c_1*c_2**3*x_2 - c_1**3*c_2*x_3 + c_1*c_2*x_2*x_3**2 + c_1*c_2*x_2**2*x_3 + c_1*c_2*x_2*y_3**2 + c_1*c_2*x_3*y_2**2 - c_1**2*x_3*y_2*y_3 - c_2**2*x_2*y_2*y_3 + x_2*x_3**2*y_2*y_3 + x_2**2*x_3*y_2*y_3)/(2*(c_2**2*(x_2**2 + y_2**2) + x_3**2*(c_1**2 - y_2**2) + y_3**2*(c_1**2 - x_2**2) + 2*y_2*y_3*(c_1*c_2 + x_2*x_3) + 2*c_1*c_2*x_2*x_3))
    
    x = x1

    y1 =  (c_1*np.sqrt((- c_1**2 + x_2**2 + y_2**2)*(- c_1**2 + 4*x**2 - 4*x*x_2 + x_2**2 + y_2**2)) + c_1**2*y_2 - x_2**2*y_2 - y_2**3 + 2*x*x_2*y_2)/(2*(c_1**2 - y_2**2))
    y2 = -(c_1*np.sqrt((- c_1**2 + x_2**2 + y_2**2)*(- c_1**2 + 4*x**2 - 4*x*x_2 + x_2**2 + y_2**2)) - c_1**2*y_2 + x_2**2*y_2 + y_2**3 - 2*x*x_2*y_2)/(2*(c_1**2 - y_2**2))
    y3 =  (c_2*np.sqrt((- c_2**2 + x_3**2 + y_3**2)*(- c_2**2 + 4*x**2 - 4*x*x_3 + x_3**2 + y_3**2)) + c_2**2*y_3 - x_3**2*y_3 - y_3**3 + 2*x*x_3*y_3)/(2*(c_2**2 - y_3**2))
    y4 = -(c_2*np.sqrt((- c_2**2 + x_3**2 + y_3**2)*(- c_2**2 + 4*x**2 - 4*x*x_3 + x_3**2 + y_3**2)) - c_2**2*y_3 + x_3**2*y_3 + y_3**3 - 2*x*x_3*y_3)/(2*(c_2**2 - y_3**2))
 
    end = tm.time()
    zeit = end - start
    pass 
    t = 13

if __name__ == "__main__":

    # test()

    # test2()

    # test3_paper_example()

    # test4()

    test5()

    loci1 = create_graph()
    intersect = create_intersection()
    # create loci for the positioning nodes to the reference node    
    loci2 = get_loci(rec_times, towers, SPEED_OF_LIGHT, delta_d, max_d)

    for i in range(3):
        # plt.plot(intersect[i][0], intersect[i][1])
        # plt.plot(intersect[i][0], intersect[i][2])
        plt.plot(loci2[i][0], loci2[i][1])

    plt.grid()

    plt.show()