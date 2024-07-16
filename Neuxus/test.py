import os
os.environ['NUMEXPR_MAX_THREADS'] = '12'

from neuxus.nodes import correct, io, filter, read
from cwl_node import CWL



data_path = r'C:\Users\victor.ferat\Documents\Soraya\EEG-MRI\P05_eyes_open_mrion.vhdr'

# signal = io.RdaReceive(rdaport=51244)
# signal = io.LslReceive('name', 'MNE-LSL-Player', 'signal')
signal = read.Reader(data_path)

signal_ga = correct.GA(signal.output, marker_input_port=signal.marker_output, start_marker='Response/R128', tr=0.8)  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')

signal_ds = filter.DownSample(signal_ga.output, 20)

signal_cwl = CWL(signal_ds.output, time_delay=21e-3, window_duration=4, overlap=0.5)

signal_lsl = io.LslSend(signal_ga.output, 'raw', type='EEG')

signal_pa_lsl = io.LslSend(signal_cwl.output, 'cwl', type='EEG')

