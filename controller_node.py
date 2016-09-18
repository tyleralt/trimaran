"""
This is the file to run on the central plotter node
Collects the 3 distances and then plots the place in 3d
Fill in the coordinates for POS1 thru POS3 as the 3 recieved nodes
and START pos as the phones starting point
"""

import numpy as np
import numpy.linalg
import controller
import math
import cmath
import time 
import pygame, sys


def calculatePosition(P1, P2, P3, DistA, DistB, DistC):
    """Return the euclidian coordinates of the point the is trilateralized from these points with these distances
    ENUSURES A POSITIVE Z POS FOR TIEBREAKER
    Ps must be of the form numpy arrays with 3 dimentions [x,y,z]
    :P1: first point 
    :P2: second point 
    :P3: third point 
    :DistA: distance from P1
    :DistB: idstance from P2
    :DistC: distanfce rom P3
    a modifide version of something online http://ebanshi.cc/questions/131614/trilateration-using-3-latitude-and-longitude-points-and-3-distances

    """
    #SEE wikipedia for why trilateralization : https://en.wikipedia.org/wiki/Trilateration
    ex = (P2 - P1)/(numpy.linalg.norm(P2 - P1))
    i = np.dot(ex, P3 - P1)
    ey = (P3 - P1 - i * ex)/(numpy.linalg.norm(P3 - P1 - i * ex))
    ez = numpy.cross(ex,ey)
    d = numpy.linalg.norm(P2 - P1)
    j = np.dot(ey, P3 - P1)
    
    x = (pow(DistA,2) - pow(DistB,2) + pow(d,2))/(2 * d)
    y = ((pow(DistA,2) - pow(DistC,2) + pow(i,2) + pow(j,2))/(2 * j)) - ((i/j)*x)

    z = cmath.sqrt(pow(DistA,2) - pow(x,2) - pow(y,2))

    if z.imag != 0.0:
        return [None, None, None]
    else:
        return np.real(P1 + x*ex + y*ey + z*ez)

POS1 = np.array([3.0, 67.0, 31.0])
POS2 = np.array([0.0, 71.0, 0.0])
POS3 = np.array([55.0, 65.0, 31.0])
START_POS = np.array([30.0, 30.0, 30.0])

start_dist1 = math.sqrt(sum( np.square(POS1 - START_POS) ))
start_dist2 = math.sqrt(sum( np.square(POS2 - START_POS) ))
start_dist3 = math.sqrt(sum( np.square(POS3 - START_POS) ))

#wait until we can get all values
while (1):
    [first, second, third] = controller.getNextDistances()
    if first != None and second != None and third != None:
        break
    time.sleep(.08)

print 'WE JUST GOT SOME VALUES FOR EACH'

LOWER_BOUND = 0.0
UPER_BOUND = 5.0 * 12
z = [LOWER_BOUND, UPER_BOUND]
x = [LOWER_BOUND, UPER_BOUND]
y = [LOWER_BOUND, UPER_BOUND]

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(x, y, z)
fig.show()

start_time = time.time()

while (1):
    [new_first, new_second, new_third] = controller.getNextDistances()
    if new_first:
        first = new_first
    if new_second:
        second = new_second
    if new_third:
        third = new_third
    dist1 = first + start_dist1
    dist2 = second + start_dist2
    dist3 = third + start_dist2

    print 'these are the distances', dist1, dist2, dist3

    [xpos, ypos, zpos] = calculatePosition(POS1, POS2, POS3, dist1, dist2, dist3)


    if xpos != None:
        x.append( xpos)
        y.append( ypos)
        z.append( zpos)

    if time.time() - start_time > 25.0:
        break

    sc._offsets3d = (x, y, z)
    plt.pause(0.005)
    plt.draw()

plt.pause(120.0)
