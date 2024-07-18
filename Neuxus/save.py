import numpy as np
from neuxus.node import Node
from collections import deque
import pandas as pd

from neuxus.chunks import Port

import numpy as np
import mne

class Save(Node):
    def __init__(self, input_port, marker_input_port=None, filename='test-raw.fif'):
        Node.__init__(self, input_port)
        self.channels = self.input.channels
        self.sfreq = self.input.sampling_frequency
        self.marker_input = marker_input_port
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
        self.marker_values = []
        self.marker_timestmaps = []

    def update(self):
        for input_chunk in self.input:
            input_chunk_values = input_chunk.values
            self.buffer = np.hstack((self.buffer, input_chunk_values.T))
            self.timestamps = np.hstack((self.timestamps, input_chunk.index.values))
        if self.marker_input is not None:
            for marker in self.marker_input:
                marker_values = marker.select_dtypes(include=['object']).values
                marker_timestamps = marker.index.values
                for timestamp, value in zip(marker_timestamps, marker_values):
                    self.marker_timestmaps.append(timestamp)
                    self.marker_values.append(value)
        print(self.marker_timestmaps, self.marker_values)
                

    def terminate(self):
        raw = mne.io.RawArray(self.buffer * 1e-6, self.info)
        
        annotations = raw.annotations
        for timestamp, value in zip(self.marker_timestmaps, self.marker_values):
           timestamp = timestamp - self.timestamps[0]
           annotations += mne.Annotations(onset=timestamp, duration=0, description=value)
        raw.set_annotations(annotations)

        raw.save(self.filename)
        return super().terminate()