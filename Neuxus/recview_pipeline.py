import os
os.environ['NUMEXPR_MAX_THREADS'] = '18'

from neuxus.nodes import correct, io, filter, read
from cwl_node import CWL
from save import Save

# Read from Recview
signal = io.LslReceive('name', 'RDA2LSL', 'signal')

# CWL
signal_cwl = CWL(signal.output, time_delay=21e-3, window_duration=4, overlap=0.5)

# Save
#signal_save_ga = Save(signal_ga.output, filename='P05_eyes_closed_mrion-GA-raw.fif')
#signal_save_ga_pa = Save(signal_pa.output, marker_input_port=signal_pa.marker_output, filename='P05_eyes_closed_mrion-GA-PA-raw.fif')
#signal_save_ga_cwl = Save(signal_cwl.output, filename='P05_eyes_closed_mrion-GA-CWL-raw.fif')
#signal_save_ga_pa_cwl = Save(signal_pa_cwl.output, filename='P05_eyes_closed_mrion-GA-PA-CWL-raw.fif')

# Send to LSL
signal_lsl = io.LslSend(signal_cwl.output, 'BrainAmpSeries-Dev_1', type='EEG')
#signal_pa_lsl = io.LslSend(signal_cwl.output, 'cwl', type='EEG')
