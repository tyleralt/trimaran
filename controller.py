"""
Contains contains function for recieving the last 3 floats pushed by reciever.py
"""

import socket
import sys

# Constant declarations
NUM_RECEIVERS = 3
RECV_SIZE = 1024
STREAM_DELIMITER = ' '
ADDRESS = ['localhost', '130.91.49.80', '130.91.50.59']

# Global variables
port = [int(49736), int(55617), int(42856)]

def initializeInSocket(address, portNum):
    """ Connect to receiver, and output receiver socket"""
    inSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to target
    inSocket.connect((address, portNum))
    return inSocket

def getLastDistance(receiverSocket):
    """ Returns last distance output from receiver """
    def getLastFloat(stream):
    	""" Parses last float from stream."""
        floatToken = stream.split(STREAM_DELIMITER)[-2]
    	# Reverse floatToken, cast it to an float, and return it along with modified stream
    	return float(floatToken)

    # Refresh output stream and output last float in it
    stream = receiverSocket.recv(RECV_SIZE)
    if (stream == ''):
        return None
    else:
        return getLastFloat(stream)

# Initialize receiver sockets
inSockets = []
for i in range(NUM_RECEIVERS):
    inSocket = initializeInSocket(ADDRESS[i], port[i])
    inSockets.append(inSocket)

def getNextDistances():
    distances = []
	# Get last distances from each receiver
    for i in range(NUM_RECEIVERS):
        lastDistance = getLastDistance(inSockets[i])
        distances.append(lastDistance)
    return distances

