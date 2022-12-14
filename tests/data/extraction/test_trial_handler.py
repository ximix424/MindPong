import datetime
import time
import unittest

import numpy as np
from numpy import dtype

from scripts.data.extraction import trial_handler
from scripts.mvc.models import MetaData


class MyTestCase(unittest.TestCase):

    def setUp(self):
        trial_handler.raw_data = [[] for _ in range(16)]
        trial_handler.event_pos = []
        trial_handler.event_duration = []
        trial_handler.event_type = []

    def test_send_raw_data(self):
        data1 = [[1] for _ in range(16)]
        data2 = [[2] for _ in range(16)]
        data3 = [[3] for _ in range(16)]
        data4 = [[4] for _ in range(16)]
        trial_handler.send_raw_data(data1, start=time.time())
        trial_handler.send_raw_data(data2)
        trial_handler.send_raw_data(data3)
        trial_handler.send_raw_data(data4)
        expected_array = [[] for _ in range(16)]
        for i in range(len(expected_array)):
            expected_array[i] = [1, 2, 3, 4]
        self.assertEqual(expected_array, trial_handler.raw_data)

    def test_mark_trial(self):
        data1 = [[1] for _ in range(16)]
        start = time.time()
        trial_handler.send_raw_data(data1, start=start)
        trial_handler.mark_trial(start + 0.008, start + (0.008 * 5), trial_handler.Labels.LEFT)
        self.assertEqual(1, trial_handler.event_pos[0])
        self.assertEqual(4, trial_handler.event_duration[0])
        self.assertEqual(trial_handler.Labels.LEFT, trial_handler.event_type[0])
        self.assertEqual(1, trial_handler.count_event_types)
        self.assertEqual(1, trial_handler.count_trials)
        data2 = [[2] for _ in range(16)]
        start = time.time()
        trial_handler.send_raw_data(data2)
        trial_handler.mark_trial(start, start + (0.008 * 5), trial_handler.Labels.LEFT)
        self.assertEqual(2, trial_handler.count_trials)
        self.assertEqual(1, trial_handler.count_event_types)

    def test_save_session(self):
        data1 = [[1.0] for _ in range(16)]
        data2 = [[2.0] for _ in range(16)]
        data3 = [[3.0] for _ in range(16)]
        data4 = [[4.0] for _ in range(16)]
        start = time.time()
        trial_handler.send_raw_data(data1, start=start)
        trial_handler.send_raw_data(data2)
        trial_handler.send_raw_data(data3)
        trial_handler.send_raw_data(data4)
        trial_handler.mark_trial(start + 0.008, start + (0.008 * 5), trial_handler.Labels.LEFT)
        expected_array = [[] for _ in range(16)]
        for i in range(len(expected_array)):
            expected_array[i] = [1.0, 2.0, 3.0, 4.0]
        expected_array = np.array(expected_array)

        timestamp = datetime.datetime.now().time()
        ses = MetaData(sid=1, sex='f', age=27, amount_events=2, comment='hallo', amount_trials=7,
                       time=timestamp)
        meta = [('id', 1), ('sex', 'f'), ('age', 27), ('date', datetime.date.today()), ('time', timestamp),
                ('sampling_rate', 125), ('channels', MetaData.bci_channels),
                ('recording_type', 'game'), ('headset', 'BCI'), ('amount_trials', 7), ('different_events', 2),
                ('comment', 'hallo')]
        metadata = ses.turn_into_np_array()
        expected_metadata = np.array(meta, dtype=dtype)
        expected_pos = np.array([1])
        expected_duration = np.array([4])
        expected_type = np.array([trial_handler.Labels.LEFT])
        trial_handler.save_session(metadata, 'test_trial_handler.npz')
        test = np.load('../../../scripts/data/session/test_trial_handler.npz', allow_pickle=True)
        self.assertEqual(test['meta'].tolist(), expected_metadata.tolist())
        self.assertEqual(test['raw_data'].tolist(), expected_array.tolist())
        self.assertEqual(test['event_pos'].tolist(), expected_pos.tolist())
        self.assertEqual(test['event_type'].tolist(), expected_type.tolist())
        self.assertEqual(test['event_duration'].tolist(), expected_duration.tolist())


if __name__ == '__main__':
    unittest.main()
