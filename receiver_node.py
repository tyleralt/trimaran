"""
this contains the functions for recieving chirps and the pushing them to the controller node
"""
import sensor.chirpSensor as chirpSensor
import sound.inputHandler
import time
import numpy as np
import pyaudio
import math
import receiver

print 'start'
# CHIRP_FILE = 'sound_files/npy/chirp_0.02s_len_48000Hz_freq_4_repeates.npy'
CHIRP_FILE = 'sound_files/npy/chirp_0.03s_len_96000Hz_freq_2_repeates_quadratic.npy'
chirp = np.load(CHIRP_FILE)

TIME_BETWEEN_CHIRP = 0.08
SAMPLE_RATE = 96000.0
SAMPLE_TYPE = pyaudio.paFloat32
NUMPY_TRANSLATION_TYPE = np.float32
CALLBACK = lambda a, b, c: None
NUMBER_CHANNELS = 2
NUMPY_CONVERTER = None
CHANNEL_INDEX = 0
CONVERTER = None #divides by this ammount so ints aren't huge

time.sleep(1.5)

input_handler = sound.inputHandler.InputHandler(SAMPLE_RATE, 10,
                                                SAMPLE_TYPE, NUMBER_CHANNELS, CHANNEL_INDEX,
                                                NUMPY_TRANSLATION_TYPE, NUMPY_CONVERTER, CONVERTER)

time.sleep(1.5)

start_time = input_handler.get_stream_time()

while input_handler.get_available_length(start_time) < 0.5 * SAMPLE_RATE:
    time.sleep(.1)

backgroup_sample = input_handler.get_audio_at_time(start_time, input_handler.get_available_length(start_time))
max_correlate = np.correlate(backgroup_sample, chirp, mode='valid').max()
minimum_correlation = max_correlate * 6.0

print 'the max correlation we found from the sample was {0} so we are setting the min to {1}'.format(max_correlate, minimum_correlation)

average_value = chirpSensor.get_chirp_time(chirp, TIME_BETWEEN_CHIRP, .0003, minimum_correlation, SAMPLE_RATE, input_handler)
print 'THIS IS THE TIME', average_value

import matplotlib.pyplot as plt

plt.ion()

ydata=np.zeros(300, dtype = np.float32)
ax1=plt.axes()

YLIM = 200

line, = plt.plot(ydata)
plt.ylim([0,YLIM])

HALF_WINDOW_WIDTH = .0032

window_chirp_sensor  = chirpSensor.CorrelationsArrayGet(SAMPLE_RATE, chirp, average_value + TIME_BETWEEN_CHIRP * 10, TIME_BETWEEN_CHIRP, HALF_WINDOW_WIDTH, input_handler)
import viterbi.helpers
import viterbi.viterbi
import viterbi.viterbi_transition_functions

chirp_arr = window_chirp_sensor.next()

NUMBER_GRAPH = 100
NUMBER_WINDOWS = 100
MAX_INDEX_CHANGE = 20
SPEED_OF_SOUND = 13503.9 #inch per sec
trans_function = viterbi.viterbi_transition_functions.linear_likelihood_index_state_change(MAX_INDEX_CHANGE)

points_per_window = chirp_arr.size // NUMBER_WINDOWS

#holds the probability of the most likely path ending on that node
most_likely_path_probs = np.repeat(1.0 / NUMBER_WINDOWS, NUMBER_WINDOWS)

path = [0.0] * NUMBER_GRAPH
index = 0

while (1):
    chirp_arr = window_chirp_sensor.next()
    chirp_arr += window_chirp_sensor.next()

    windowed_probs = viterbi.helpers.get_windowed_prob_arr(chirp_arr, NUMBER_WINDOWS)

    (origins, path_transition_probs) = viterbi.viterbi.apply_viterbi_transition(most_likely_path_probs.astype(np.float32), trans_function)
    most_likely_path_probs = path_transition_probs * windowed_probs

    most_likely_index = float(points_per_window * most_likely_path_probs.argmax())
    time_from_origin = (float(most_likely_index) / SAMPLE_RATE) - HALF_WINDOW_WIDTH

    most_likely_distance = time_from_origin * float(SPEED_OF_SOUND)

    receiver.pushDistance(most_likely_distance)
    print most_likely_distance

    if index < len(path):
        path[index] = most_likely_path_probs.argmax()
        index += 1
    else:
        path.append(most_likely_path_probs.argmax())
        path = path[1:]

    # plt.ylim([0,YLIM])
    # line.set_xdata(np.arange(NUMBER_GRAPH))
    # line.set_ydata(np.array(path))
    # plt.draw()
    # plt.pause(.01)
