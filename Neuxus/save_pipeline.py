from neuxus.nodes import correct, io, filter, read
from cwl_node import CWL
from save import Save


# Read from file
data_path = r'C:\Users\victor.ferat\Documents\Soraya\EEG-MRI\P05_eyes_closed_mrion.vhdr'
signal = read.Reader(data_path)

# GA
signal_ga = correct.GA(signal.output, start_marker='Response/R128', tr=0.8)  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')

# Down-sample
signal_ds = filter.DownSample(signal_ga.output, 20)

# CWL
signal_cwl = CWL(signal_ds.output, time_delay=21e-3, window_duration=4, overlap=0.5)

# Save to file
signal_save = Save(signal_cwl.output, filename='P05_eyes_closed_mrion-GACWL-raw.fif')
