"""
This contains the function for sending floats over the LAN
"""
import socket
import sys
import random
import time

# Constant declarations
ADDRESS = ''
STREAM_DELIMITER = ' '
SLEEP_TIME = .08

# Global variables
port = random.randint(40000, 60000)
outSocket = None

def initializeOutSocket(portNum):
	""" Create new socket, listen for and accept a connection, 
		and then output controller socket"""
	outSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	outSocket.bind((ADDRESS, portNum))
	# Listen for controller and accept connection
	print '[*] Listening on port %d' % portNum
	outSocket.listen(1)
	return outSocket.accept()[0]

def pushDistance(distance):
	outSocket.send(str(distance) + STREAM_DELIMITER)

# Initialize socket for outputting data stream
outSocket = initializeOutSocket(port)

# Generate random numbers and output them to socket
#only run if it is the main 
if __name__ == '__main__':
    while True:
        newRand = random.random()
    	pushDistance(newRand)
    	time.sleep(SLEEP_TIME)
