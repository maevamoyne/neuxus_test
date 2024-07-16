import numpy as np
from neuxus.node import Node
from collections import deque
import pandas as pd

from neuxus.chunks import Port

import numpy as np
import mne
from scipy import signal



def delay_data(data, time_delay, sfreq):
    sample_shift = int(np.ceil(time_delay * sfreq))
    sample_shifts = np.arange(-sample_shift, sample_shift+1, 1)

    delayed_signals = []
    for shift in sample_shifts:
        delayed_signal = np.roll(data, shift, axis=1)
        if shift > 0:
            delayed_signal[:, :shift] = data[:, :shift]  # Zero out the initial part to avoid wrap-around
        elif shift < 0:
            delayed_signal[:, shift:] = data[:, shift:]  # Zero out the end part to avoid wrap-around
        delayed_signals.append(delayed_signal)

    delay_signals = np.concatenate(delayed_signals, axis=0)
    return delay_signals


def _correct_data(eeg_data, cwl_data, window_size, overlap):
    hanning_window = np.hanning(window_size)
    
    n_channels, n_times = eeg_data.shape
    eeg_corrected = np.zeros_like(eeg_data)
    weight_sum = np.zeros_like(eeg_data)
    step = int(window_size * (1 - overlap))
    starts = np.arange(0, n_times, step)

    for ch in range(n_channels):
        for start in starts:
            end = min(start + window_size, n_times)
            actual_window_size = end - start
            
            eeg_segment = eeg_data[ch, start:end] #* hanning_window[:actual_window_size]
            cwl_segment = cwl_data[:, start:end] #* hanning_window[:actual_window_size]

            # Regression
            coeffs = np.linalg.lstsq(cwl_segment.T, eeg_segment.T, )[0]
            correction = np.dot(coeffs.T, cwl_segment)
            corrected_segment = eeg_segment - correction

            # Apply Hanning window to the corrected segment
            corrected_segment *= hanning_window[:actual_window_size]

            eeg_corrected[ch, start:end] += corrected_segment
            weight_sum[ch, start:end] += hanning_window[:actual_window_size]
            
    # Normalize the corrected signal by the weight sum
    weight_sum[weight_sum == 0] = 1 # Avoid division by zero
    eeg_corrected /= weight_sum
    return eeg_corrected


def cwl_correction_raw(raw, eeg_picks, cwl_picks, time_delay=21e-3, window_duration=4, overlap=0.5):
    # Get data
    sfreq = raw.info['sfreq']
    eeg_data = raw.get_data(picks=eeg_picks)
    cwl_data = raw.get_data(picks=cwl_picks)
    # Create delayed versions of the CWL data
    cwl_data = delay_data(cwl_data, time_delay, sfreq)
    # compute Hanning window
    window_size = int(np.ceil((window_duration * sfreq)))
    eeg_corrected = _correct_data(eeg_data, cwl_data, window_size, overlap)
    # Create new MNE Raw object
    data = raw.get_data()
    data[eeg_picks] = eeg_corrected
    raw_corrected = mne.io.RawArray(data, raw.info)
    return raw_corrected


class CWL(Node):
    def __init__(self, input_port, time_delay, window_duration, overlap=0.5):
        Node.__init__(self, input_port)
        self.channels = self.input.channels
        self.sfreq = self.input.sampling_frequency

        # CWL parameters
        self.time_delay = time_delay
        self.window_duration = window_duration
        self.overlap = overlap
        # Find picks
        self.cwl_picks = [i for i, ch in enumerate(self.channels) if 'CWL' in ch]
        self.eeg_picks = [i for i, ch in enumerate(self.channels) if 'CWL' not in ch]

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
            if self.buffer.shape[1] < self.sfreq * self.window_duration:
                # If the buffer is not full, no correction
                self.output.set_from_df(input_chunk)
                continue
            elif self.buffer.shape[1] > self.sfreq * self.window_duration:
                # If the buffer is too full, keep only the last window_duration
                self.buffer = self.buffer[:, -int(self.sfreq * self.window_duration):]
                self.timestamps = self.timestamps[-int(self.sfreq * self.window_duration):]

            raw = mne.io.RawArray(self.buffer * 1e-6, self.info)
            raw_corrected = cwl_correction_raw(raw, self.eeg_picks, self.cwl_picks, time_delay=self.time_delay, window_duration=self.window_duration, overlap=self.overlap)
            output_chunk = raw_corrected.to_data_frame()
            output_chunk = output_chunk.drop('time', axis=1)
            self.output.set(output_chunk.values[-len(input_chunk):, :], self.timestamps[-len(input_chunk):])