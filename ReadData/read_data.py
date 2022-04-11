import time

import numpy as np
from numpy_ringbuffer import RingBuffer
import serial
import serial.tools.list_ports
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from SaveTrial import trial_handler

# time which is needed for one sample in s, T = 1/f = 1/125 = 0.008
time_for_one_sample = 1 / BoardShim.get_sampling_rate(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)

sliding_window_duration = 0.2  # size of sliding window in s
# size of sliding window in amount of samples, *8ms for time
sliding_window_samples = int(sliding_window_duration / time_for_one_sample)

offset_duration = 0.1  # size of offset in s between two consecutive sliding windows
offset_samples = int(offset_duration / time_for_one_sample)  # size of offset in amount of samples, *8ms for time

number_channels = len(BoardShim.get_eeg_channels(
    brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD))

allow_window_creation = True
first_window = True
first_data = True
stream_available = False  # indicates if stream is available
board: BoardShim
window_buffer = [RingBuffer(capacity=sliding_window_samples, dtype=float) for _ in range(number_channels)]


def init():
    """
    --- starting point ---
    Initializing steps:
    (1) initialize the board
    (2) search for the serial port
    (3) starts the data acquisition
    """
    params = BrainFlowInputParams()
    params.serial_port = search_port()

    if params.serial_port is not None:
        BoardShim.enable_dev_board_logger()
        global board, stream_available
        board = BoardShim(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD, params)
        board.prepare_session()
        board.start_stream()
        stream_available = True
        handle_samples()
    else:
        print('Port not found')


def search_port():
    """
    Search for the name of the used usb port
    :return: name of the used serial port
    :rtype: str
    """
    print('Search...')
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports:
        if port.vid == 1027 and port.pid == 24597:
            port_name = port.device
            print('found port: ', port_name)
            return port_name
    return None


def handle_samples():
    """
    Reads EEG data from port, sends it to trial_handler and writes into in the window_buffer
    """
    global first_window, window_buffer, allow_window_creation, first_data
    count_samples = 0
    while stream_available:
        data = board.get_board_data(1)[board.get_eeg_channels(
            brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)]  # get all data and remove it from internal buffer
        if len(data[0]) > 0:
            if first_data:
                trial_handler.send_raw_data(data, start=time.time())
                first_data = False
            else:
                trial_handler.send_raw_data(data)
            if allow_window_creation:
                for i in range(len(data)):
                    window_buffer[i].extend(data[i])
                count_samples += 1
                if first_window and count_samples == sliding_window_samples:
                    first_window = False
                    send_window()
                    count_samples = 0
                elif not first_window and count_samples == offset_samples:
                    send_window()
                    count_samples = 0


def send_window():
    """
    Create sliding window and send it to the algorithm
    """
    global window_buffer, number_channels
    window = np.zeros((number_channels, sliding_window_samples), dtype=float)
    for i in range(len(window)):
        window[i] = np.array(window_buffer[i])
    # ToDo: push window to algorithm


def stop_stream():
    """
    Stops the data stream and the releases session
    """
    global stream_available
    stream_available = False
    # time.sleep(0.3) , needed for multithreading
    board.stop_stream()
    board.release_session()


init()
