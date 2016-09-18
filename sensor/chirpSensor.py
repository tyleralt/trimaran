import sound.inputHandler
import time
import math
import numpy as np
import pyaudio
import time
#TODO : add in the ability to make higher and lower the volume so loud sudden noises don't set off the chirp sensor

#this is a class for handling the sensing and timing multiple incoming chirps
#mostly used for outputting the time between chirp senses

class ChirpSensor:
    def __init__(self, sample_rate, chirp_arr, input_handler):
        self.input_handler = input_handler
        self.sample_rate = float(sample_rate)
        self.chirp_arr = chirp_arr

    def get_stream_time(self):
        return self.input_handler.get_stream_time()

def get_correlation_at_time(chirp, start_time, length, input_handler):
    """wait for the length to become available and then return the correaltion_array

    :chirp: TODO
    :start_time: TODO
    :length: TODO
    :input_handler: TODO
    :returns: TODO

    """
    available_length = input_handler.get_available_length(start_time)

    while( available_length <=  length + chirp.size):
        time.sleep(.001)
        available_length = input_handler.get_available_length(start_time)
        continue

    test_sample = input_handler.get_audio_at_time(start_time, length + chirp.size)
    return np.correlate(test_sample, chirp, mode='valid')

def get_first_chirp(chirp, time_between_chirps, correlation_min, sample_rate, input_handler):
    """Wait for and return the time_of_first_chirp

    :chirp: TODO
    :time_between_chirps: TODO
    :correlation_min: should be large enough that no background correlation gets mixed up with it
    :sample_rate: TODO
    :input_handler: TODO
    :returns: TODO

    """

    next_check_starting_time = input_handler.get_stream_time()
    garunteed_chirp_cover_len = chirp.size * 2 + time_between_chirps * sample_rate

    while(1):
        correlation = get_correlation_at_time(chirp, next_check_starting_time, garunteed_chirp_cover_len, input_handler)
        correlation_max = correlation.max()

        next_check_starting_time += (garunteed_chirp_cover_len - chirp.size) / sample_rate

        if correlation_max > correlation_min:
            correlation = get_correlation_at_time(chirp, next_check_starting_time, garunteed_chirp_cover_len, input_handler)
            correlation_max = correlation.max()
            correlation_max_point = correlation.argmax()
            if correlation_max > correlation_min:
                return next_check_starting_time + float(correlation_max_point) / sample_rate
            else:
                next_check_starting_time += (garunteed_chirp_cover_len - chirp.size)/ sample_rate
                continue

def get_chirp_time(chirp, time_between_chirps, max_change_between_chirps, correlation_min, sample_rate, input_handler):
    """wait for and then return when a chirp arrived (only needs to be generaly when it arrived)

    :chirp: Array containing the chirp
    :time_between_chirps: The time expected between chirps
    :amx_change_between_chrips: the maximum change in seconds between each ariving chirp
    :input_handler: the input handler device
    :sample_rate: the frequency at which the sound sample
    :correlation_min: the min correlation with the chirp to be considered a chirp
    :returns: the time the chirp started

    """
    NUMBER_GETS_IN_A_ROW = 7
    while(1):
        first_get_time = get_first_chirp(chirp, time_between_chirps, correlation_min, sample_rate, input_handler)

        gotten_times = [first_get_time]
        next_check_starting_time = first_get_time + time_between_chirps - max_change_between_chirps
        for i in range(1, NUMBER_GETS_IN_A_ROW):
            start_time = first_get_time + time_between_chirps * i - max_change_between_chirps
            correlation = get_correlation_at_time(chirp,  start_time,
                                              chirp.size + sample_rate * max_change_between_chirps * 2, input_handler)
            if correlation.max() > correlation_min:
                time_recieved = correlation.argmax() / sample_rate + start_time
                gotten_times.append(time_recieved)
            else:
                break

        #means all 5 values were above min and we have a good sample
        if len(gotten_times) == NUMBER_GETS_IN_A_ROW:
            break

    sum_of_extrapolated_times = 0.0
    for index, value in enumerate(gotten_times):
        sum_of_extrapolated_times += value - (time_between_chirps * index)

    return sum_of_extrapolated_times / len(gotten_times)

# a class for getting multiple values all over the peak from the sensor
class CorrelationsArrayGet (ChirpSensor):
    def __init__(self, sample_rate, chirp_arr, start_time, time_between_chirps, half_window_width, input_handler):
        ChirpSensor.__init__(self,sample_rate, chirp_arr, input_handler)
        self.start_time = start_time
        self.time_between_chirps = time_between_chirps
        self.half_window_width = half_window_width

        self.next_search_window = start_time

    def __iter__(self):
        return self

    def next(self):
        while(1):
            if self.has_next_output_available():
                return self.get_next_output_time()
            else :
                continue

    def has_next_output_available(self):
        return self.input_handler.get_available_length(self.next_search_window - self.half_window_width) >= (2 * self.half_window_width * self.sample_rate) + self.chirp_arr.size

    #only call if has_next_output_available was true
    def get_next_output_time(self):
        test_window = self.input_handler.get_audio_at_time(self.next_search_window - self.half_window_width, int(self.sample_rate * 2 * self.half_window_width + self.chirp_arr.size))
        self.next_search_window += self.time_between_chirps
        correlation = np.correlate(test_window, self.chirp_arr, mode='valid')
        correlation_window = correlation
        return correlation_window
