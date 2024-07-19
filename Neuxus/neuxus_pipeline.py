import os
os.environ['NUMEXPR_MAX_THREADS'] = '18'

from neuxus.nodes import correct, io, filter, read
from cwl_node import CWL
from save import Save

# Read from LSL
#signal = io.RdaReceive(rdaport=51244)
signal = io.LslReceive('name', 'MNE-LSL-Player', 'signal')

# Read from file
# data_path = r'C:\Users\victor.ferat\Documents\Soraya\EEG-MRI\P05_eyes_closed_mrion.vhdr'
# signal = read.Reader(data_path)

# GA
signal_ga = correct.GA(signal.output, marker_input_port=signal.marker_output, start_marker='Response/R128', tr=0.8)  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')
signal_save_ga = Save(signal_ga.output, marker_input_port=signal_ga.marker_output, filename='P05_eyes_closed_mrion-GA-raw.fif')

# Down-sample
signal_ds = filter.DownSample(signal_ga.output, 20)

# PA
signal_pa = correct.PA(signal_ds.output, weights_path=r"c:\Users\victor.ferat\Documents\GitHub\NeuXus\data\PA correction LSTM models\weights-input-500.pkl")

# CWL
#signal_pa_cwl = CWL(signal_pa.output, time_delay=21e-3, window_duration=4, overlap=0.5)
signal_cwl = CWL(signal_ds.output, time_delay=21e-3, window_duration=4, overlap=0.5)

# Save
#signal_save_ga = Save(signal_ga.output, filename='P05_eyes_closed_mrion-GA-raw.fif')
#signal_save_ga_pa = Save(signal_pa.output, marker_input_port=signal_pa.marker_output, filename='P05_eyes_closed_mrion-GA-PA-raw.fif')
#signal_save_ga_cwl = Save(signal_cwl.output, filename='P05_eyes_closed_mrion-GA-CWL-raw.fif')
#signal_save_ga_pa_cwl = Save(signal_pa_cwl.output, filename='P05_eyes_closed_mrion-GA-PA-CWL-raw.fif')

# Send to LSL
signal_lsl = io.LslSend(signal_cwl.output, 'BrainAmpSeries-Dev_1', type='EEG')
#signal_pa_lsl = io.LslSend(signal_cwl.output, 'cwl', type='EEG')
