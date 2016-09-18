import numpy as np
import math
import sys
import scipy.signal as signal
import wave
import scipy.io.wavfile as wave

FREQ = 48000
SECONDS_OF_SOUND = 120
SECONDS_BETWEEN_CHIRPS = 0.03
#every 3 thousands is about one meter so seperate by .003 times number of meters
CHIRP_LENGTH = 0.02
START_FREQ = 1800.0
END_FREQ = 20000.0
time_arr_chirp = np.arange(0.0, CHIRP_LENGTH , 1.0/FREQ)
chirp_signal = signal.chirp(time_arr_chirp, START_FREQ, CHIRP_LENGTH, END_FREQ)

base_sound = np.zeros(FREQ * SECONDS_OF_SOUND, dtype=np.float32)

for i in range(0, base_sound.size):
    starting_index = int(i * SECONDS_BETWEEN_CHIRPS * FREQ)
    if starting_index < base_sound.size:
        base_sound[starting_index:starting_index + chirp_signal.size] = chirp_signal[0: base_sound.size - starting_index]
    else:
        break

two_channels = np.array([base_sound,base_sound]).transpose()

base_file_name ='chirp_{0}s_len_{1}Hz_freq'.format(CHIRP_LENGTH, FREQ)

np.save('npy/' + base_file_name + '.npy', chirp_signal)
wave.write('wav/' + base_file_name + '_{0}s_between_chirps'.format(SECONDS_BETWEEN_CHIRPS) + '.wav', FREQ, two_channels)

#with wave.open(, 'wb') as wave_file:
    #BLOCK_SIZE = 512
    #number_of_blocks = math.ceil(float(base_sound) / float(BLOCK_SIZE)) * BLOCK_SIZE
    #wave_file.setparams((2, BLOCK_SIZE,FREQ, number_of_blocks, None, 'no compresion'))
    #for i in range(0, number_of_blocks, BLOCK_SIZE):
        #wave_file.write(
    ##while two_channels
