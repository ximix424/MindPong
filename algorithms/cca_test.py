import sys
import threading, queue
import time
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import cursor_online_control
import BCIC_dataset_loader as bdl

# GLOBAL DATA
DATASTREAM = None
LABELSTREAM = list()
plot_data = list()
plot_label = list()
num_used_channels = 0
mutex = threading.Lock
q1 = queue.Queue(300)
'''
Sliding window size: 
    1 -> 200ms
    2 -> 400ms
    ...
    5 -> 1s
'''
SLIDING_WINDOW_SIZE_FACTOR = 5
VALID_VALUES_BORDER = 0.3


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))
        self.y = list()

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(width=2, color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        try:
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
            global q1
            self.y = self.y[1:]
            self.y.append(q1.get()) # Get and remove the first element of the queue
            self.data_line.setData(self.x, self.y)  # Update the data.
        except:
            time.sleep(0.05)




def loadBCICDataset(ch_weight):
    """
    - converts ch_weight into the corresponding channels and inserts C3 and C4 to the first two places in the list
    - provides the BCIC dataset for further processing
    :param ch_weight: weighted array to set channel selection
    :return: loaded_data: contains the samples of all channels for each trial
                Structure of 4-dim array from the data loader:
                        dim 0: subject
                        dim 1: trial
                        dim 3: EEG channel
                        dim 4: sample
             loaded_labels: contains the corresponding label for each trial
    """
    # Load BCIC dataset
    used_subjects = [4]
    validation_subjects = []
    n_class = 2
    used_ch_names = []
    # map ch_weight(channel selection) with channels names in BCI dataset to load to selected channels
    for i in range(len(bdl.CHANNELS)):
        if ch_weight[i] != 0:
            if bdl.CHANNELS[i] == 'C3':
                used_ch_names.insert(0, bdl.CHANNELS[i])
            elif bdl.CHANNELS[i] == 'C4':
                used_ch_names.insert(1, bdl.CHANNELS[i])
            else:
                used_ch_names.append(bdl.CHANNELS[i])
    global num_used_channels
    num_used_channels = len(used_ch_names)

    ds_tmin = -2
    ds_tmax = 5.5

    # print("  - ds_tmin, ds_tmax =", ds_tmin, ds_tmax)
    loaded_data, loaded_labels = dataset.load_subjects_data(used_subjects + validation_subjects, n_class, used_ch_names)
    return loaded_data, loaded_labels


def slice_array(array):
    """
    Slices a trial into sliding windows with a size of 200ms
    :param array: trial
    :return: small slices of data
    """
    # 100ms = 25 samples; 200ms = 50 samples; ... ; 1s -> 250samples
    slices = list()
    sliding_window_size = SLIDING_WINDOW_SIZE_FACTOR * 25
    for i in range(int(len(array) / sliding_window_size)):
        index = i * sliding_window_size
        slices.append(array[index:index + sliding_window_size])
    return slices


def calculate_sliding_windows(data, labels):
    """
    converts BCIC dta into beautiful equally sized  windows
    - window size is adjustable in global variable sliding_window_size_factor (in steps of 200ms)
    :param data: preloaded BCIC data
    :param labels: list of labels
    :return: None
    """
    global DATASTREAM
    DATASTREAM = [[] for _ in range(num_used_channels)]
    sliding_window_size = SLIDING_WINDOW_SIZE_FACTOR * 25
    for i in range(0, 144):
        # generate half sliding windows
        for j in range(num_used_channels):
            DATASTREAM[j] += slice_array(data[0][i][j][:])

        # scale LABELSTREAM to the same dimensions as DATASTREAM
        num_sliding_windows_label = (1875 / sliding_window_size)
        for a in range(int(num_sliding_windows_label * 0.4)):
            LABELSTREAM.append(None)
        for b in range(int(num_sliding_windows_label * 0.4)):
            LABELSTREAM.append(labels[0][i])
        for c in range(int(num_sliding_windows_label * 0.2)):
            LABELSTREAM.append(None)


def test_algorithm():
    """
    - create overlapping sliding windows
    - Calls the cursor control algorithm
    - calculate und plot accuracy
    :return: None
    """
    accuracy = 0
    global VALID_VALUES_BORDER
    valid_values_border = VALID_VALUES_BORDER
    num_valid_sliding_windows = 0
    num_sliding_windows = int(1875 / (25 * SLIDING_WINDOW_SIZE_FACTOR)) * 144 - 1
    for i in range(num_sliding_windows):
        samples = []
        # create an overlapping sliding window by combining two halves
        for j in range(num_used_channels):
            current_samples1 = DATASTREAM[:][j][i]
            current_samples2 = DATASTREAM[:][j][i + 1]
            sample = np.concatenate([current_samples1, current_samples2])
            samples.append(sample)

        # calls the one and only cursor control algorithm
        normalized_hcon = cursor_online_control.perform_algorithm(samples, SLIDING_WINDOW_SIZE_FACTOR)
        try:
            global q1
            q1.put(normalized_hcon)
        except:
            print('Fehler: kann nicht reingeldaden werden')
            
        # print(f'{i}: {normalized_hcon}')

        # converts the returned hcon to the corresponding label
        if normalized_hcon > valid_values_border:
            calculated_label = 0
        elif normalized_hcon < -valid_values_border:
            calculated_label = 1
        else:
            calculated_label = 0.5

        plot_data.append(calculated_label)

        # compare the calculated label with the predefined label, if same -> increase accuracy
        if LABELSTREAM[i] is not None:
            num_valid_sliding_windows += 1
            plot_label.append(LABELSTREAM[i])
            if calculated_label == LABELSTREAM[i]:
                accuracy += 1
        else:
            plot_label.append(0.5)

    # calculate und plot accuracy
    accuracy /= num_valid_sliding_windows
    print(f'Accuracy = {accuracy}')


# def doPlot():
#     # See: https://www.geeksforgeeks.org/matplotlib-animation-funcanimation-class-in-python/
#     fig, ax = plt.subplots(figsize=(8, 6))
#     ax = plt.axes(xlim=(0, 144), ylim=(-500, 500))
#     line, = ax.plot([], [], lw=2)
#     xdata, ydata = [], []
#
#     def funcAnimation(i):
#         global animation_func_var
#         animation_func_var += 1
#         try:
#             hcon = q.get_nowait()
#         except:
#             return
#         xdata.append(animation_func_var)
#         ydata.append(hcon)
#         line.set_data(xdata, ydata)
#         return line,
#
#     ani = FuncAnimation(fig, funcAnimation, frames=2, interval=40)
#     plt.show()

def start_algorithm():
    #                 Fz  FC3  FC1  FCz  FC2  FC4  C5  C3  C1  Cz  C2  C4  C6  CP3  CP1  CPz  CP2  CP4  P1  Pz  P2  POz
    ch_names_weight = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
    preloaded_data, preloaded_labels = loadBCICDataset(ch_names_weight)
    calculate_sliding_windows(preloaded_data, preloaded_labels)
    test_algorithm()


if __name__ == '__main__':
    # threading.Thread(target=start_algorithm).start()
    start_algorithm()

    # app = QtWidgets.QApplication(sys.argv)
    # w = MainWindow()
    # w.show()
    # sys.exit(app.exec_())
