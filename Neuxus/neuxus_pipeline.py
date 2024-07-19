import os
os.environ['NUMEXPR_MAX_THREADS'] = '18'

from neuxus.nodes import correct, io, filter, read
from cwl_node import CWL
from save import Save

# Read from LSL
signal = io.LslReceive('name', 'BrainAmpSeries-Dev_1', 'signal')

# GA
signal_ga = correct.GA(signal.output, start_marker='Response/R128', tr=0.8)  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')
#signal_save_ga = Save(signal_ga.output, marker_input_port=signal_ga.marker_output, filename='P05_eyes_closed_mrion-GA-raw.fif')

# Down-sample
signal_ds = filter.DownSample(signal_ga.output, 20)

# CWL
#signal_pa_cwl = CWL(signal_pa.output, time_delay=21e-3, window_duration=4, overlap=0.5)
signal_cwl = CWL(signal_ds.output, time_delay=21e-3, window_duration=4, overlap=0.5)

# Send to LSL
signal_lsl = io.LslSend(signal_cwl.output, 'BrainAmpSeries-Dev_1', type='EEG')
