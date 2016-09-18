import numpy as np
import math
import sys
import scipy.signal as signal
import wave
import scipy.io.wavfile as wave

FREQ = 96000
SECONDS_OF_SOUND = 120
SECONDS_BETWEEN_CHIRPS = 0.08
SINGLE_CHIRP_LENGTH = 0.03

START_FREQ = 18000.0
END_FREQ = 20000.0

time_arr_chirp = np.arange(0.0, SINGLE_CHIRP_LENGTH , 1.0/FREQ)
chirp_signal_1 = signal.chirp(time_arr_chirp, START_FREQ, SINGLE_CHIRP_LENGTH, END_FREQ)
chirp_signal_2 = (np.copy(chirp_signal_1))[::-1] * -1

chirp_signal_3 = signal.chirp(time_arr_chirp, START_FREQ, SINGLE_CHIRP_LENGTH, END_FREQ, method='quadratic')
chirp_signal_4 = (np.copy(chirp_signal_3))[::-1]

print chirp_signal_2[0:50]
print chirp_signal_1[-1]

multi_chirp_signal = np.concatenate((chirp_signal_3, chirp_signal_2))

base_sound = np.cos(np.arange(0.0, SECONDS_OF_SOUND, 1.0/FREQ) * np.pi * END_FREQ * 2)


for i in range(0, base_sound.size):
    starting_index = int(i * SECONDS_BETWEEN_CHIRPS * FREQ)
    if starting_index < base_sound.size:
        base_sound[starting_index:starting_index + multi_chirp_signal.size] = multi_chirp_signal[0: base_sound.size - starting_index]
    else:
        break

two_channels = np.array([base_sound,base_sound]).transpose()

base_file_name ='chirp_{0}s_len_{1}Hz_freq_{2}_repeates_quadratic'.format(SINGLE_CHIRP_LENGTH, FREQ, 2)

np.save('npy/' + base_file_name + '.npy', multi_chirp_signal)
wave.write('wav/' + base_file_name + '_{0}s_between_chirps_{1}_chirps_quadratic'.format(SECONDS_BETWEEN_CHIRPS, 2) + '.wav', FREQ, two_channels)

#with wave.open(, 'wb') as wave_file:
    #BLOCK_SIZE = 512
    #number_of_blocks = math.ceil(float(base_sound) / float(BLOCK_SIZE)) * BLOCK_SIZE
    #wave_file.setparams((2, BLOCK_SIZE,FREQ, number_of_blocks, None, 'no compresion'))
    #for i in range(0, number_of_blocks, BLOCK_SIZE):
        #wave_file.write(
    ##while two_channels
