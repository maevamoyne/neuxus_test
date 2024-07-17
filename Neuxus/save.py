import numpy as np
from neuxus.node import Node
from collections import deque
import pandas as pd

from neuxus.chunks import Port

import numpy as np
import mne

class Save(Node):
    def __init__(self, input_port, filename='test-raw.fif'):
        Node.__init__(self, input_port)
        self.channels = self.input.channels
        self.sfreq = self.input.sampling_frequency
        # Inputs
        self.filename = filename
        # Create MNE info object
        self.info = mne.create_info(self.channels, self.sfreq, ch_types=['eeg'] * len(self.channels))
        # Create buffer
        self.buffer = np.empty((len(self.channels), 0))
        self.timestamps = np.empty(0)

        # Set output parameters
        self.output.set_parameters(
            data_type=self.input.data_type,
            channels=self.input.channels,
            sampling_frequency=self.sfreq,
            meta=self.input.meta,
            epoching_frequency=self.input.epoching_frequency
        )

    def update(self):
        for input_chunk in self.input:
            input_chunk_values = input_chunk.values
            self.buffer = np.hstack((self.buffer, input_chunk_values.T))
            self.timestamps = np.hstack((self.timestamps, input_chunk.index.values))

    def terminate(self):
        raw = mne.io.RawArray(self.buffer * 1e-6, self.info)
        raw.save(self.filename)
        return super().terminate()