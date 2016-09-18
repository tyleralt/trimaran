import threading
import math
import thread
import time
import numpy as np
import pyaudio

FRAMES_PER_BUFFER = 1024 / 2
#this is a class used to recieve incoming audio from the mic based on the time you want to analyze it
class InputHandler:

    #sample_type should be a pyaudio type pyadio.paFloat32
    #numpy_translation_type np.float32 should be should be a np type for the from string method and correlate with the sample_type
    #in_data is a numpy array and read_time and frame_count is relative to the stream
    def __init__(self, sample_rate, secs_in_buffer = 10, 
                 sample_type = pyaudio.paFloat32, number_channels = 2, input_device_index = None, 
                 numpy_translation_type = np.float32, numpy_converter = np.float32, sample_divisor = None, callback = None):
        """
        sample_rate- number of samples to take a second given to the pyadio stream
        secs_in_buffer- number of seconds to save
        sample_type- the type to get from the input device as the pyadio
        number_channels- number input channels
        input_device_index = if not base device this is the index
        numpy_translation_type- the analogous type of the sample_type used because the sample type comes in as a string
        numpy_converter-translates all arrays to this when reading in so can know what to expect back
        """

        self.lock = threading.Lock()
        self.lock.acquire()

        self.sample_rate = float(sample_rate)
        self.secs_in_buffer = secs_in_buffer
        self.sample_type = sample_type
        self.number_channels = number_channels
        self.numpy_converter = numpy_converter
        self.np_translation_type = numpy_translation_type
        self.sample_divisor = sample_divisor
        self.callback = callback

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = sample_type,
                input_device_index = input_device_index,
                channels = self.number_channels,
                rate = int(sample_rate),
                input=True,
                frames_per_buffer = FRAMES_PER_BUFFER,
                stream_callback = self.handle_audio)

        self.last_read_in_time = None
        self.stream.start_stream()
        self.audio_buffer = np.array([], dtype=np.float32)

        self.lock.release()
        self.should_clean_audio_buffer = True
        self.last_time = 10.0
        self.start_time = None
        thread.start_new_thread(self.clean_up_audio_buffer, ())

    def __enter__(self):
        return self

    def __exit__(self, exception_type, execption_val, trace):
        self.stop_and_cleanup()

    def clean_up_audio_buffer(self):
        while (self.should_clean_audio_buffer):
            self.lock.acquire()
            length_wanted = int(self.sample_rate * self.secs_in_buffer)
            if self.audio_buffer.size >= length_wanted:
                self.audio_buffer = self.audio_buffer[self.audio_buffer.size - length_wanted: self.audio_buffer.size]
            self.lock.release()
            time.sleep(self.secs_in_buffer * .5)

    def handle_audio(self, in_data, frame_count, time_info, status):
        input_time = time_info['input_buffer_adc_time']
        one_channel_data = np.fromstring(in_data, dtype=self.np_translation_type)[::self.number_channels]

        if self.sample_divisor:
            one_channel_data = one_channel_data / self.sample_divisor

        if (self.callback):
            self.callback(input_time)

        self.lock.acquire()
        self.audio_buffer = np.concatenate((self.audio_buffer, one_channel_data), axis=0)
        self.last_read_in_time = input_time + (float(FRAMES_PER_BUFFER) / (self.sample_rate))
        self.lock.release()
        return (in_data, pyaudio.paContinue)

    def get_available_length(self, sample_start_time):
        if self.last_read_in_time == None:
            return 0
        self.lock.acquire()
        available_time = int(math.floor((self.last_read_in_time - sample_start_time) * (self.sample_rate)))
        self.lock.release()
        return available_time

    def get_audio_at_time(self, sample_start_time, length):
        self.lock.acquire()
        indecies_from_end = int((self.last_read_in_time - sample_start_time) * (self.sample_rate))
        start_index = self.audio_buffer.size - indecies_from_end
        needed_sample = np.copy(self.audio_buffer[start_index: start_index + int(length)])
        self.lock.release()
        return needed_sample.astype(self.numpy_converter)

    def get_stream(self):
        return self.stream

    def get_stream_time(self):
        return self.stream.get_time()

    def stop_and_cleanup(self):
        self.should_clean_audio_buffer = False
        self.lock.acquire()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.lock.release()
