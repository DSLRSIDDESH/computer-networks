import pyaudio
from time import sleep

pa = pyaudio.PyAudio()

def input_callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

def output_callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

input_stream = pa.open(rate=48000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=2048)
# input_stream.start_stream()

output_stream = pa.open(rate=48000, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=2048)
# output_stream.start_stream()

while True:
    data = input_stream.read(2048, exception_on_overflow=False)
    output_stream.write(data)