import os
from neuxus.nodes import correct, io, filter, read
from cwl_node import CWL
from save import Save




#SubList=['01','02','03','04','05','06','07','08','09','10','11','12']

#rootDir = 'C:/Vision/eeg/raw/GA_CWL'

#for sub in SubList: 
    #file_path = os.path.join(rootDir, f"P{sub:02}_eyes_closed-ref-postICA-raw.fif")
#data_path = r'C:\Vision\eeg\raw\GA_CWL\P02_eyes_closed_mrion.vhdr'

# Read from file
data_path = r'C:\Vision\eeg\raw\GA_CWL\P02_eyes_closed_mrion.vhdr'

basename = os.path.splitext(os.path.basename(data_path))[0]

ga_save_path = fr"C:\Users\moyne\Documents\GitHub\neuxus_test\Post_corrections\Neuxus\GA\Neuxus_GA_{basename}_raw.fif"
pa_save_path = fr"C:\Users\moyne\Documents\GitHub\neuxus_test\Post_corrections\Neuxus\GA_PA\Neuxus_GA_PA_{basename}_raw.fif"
cwl_save_path = fr"C:\Users\moyne\Documents\GitHub\neuxus_test\Post_corrections\Neuxus\GA_CWL\Neuxus_GA_CWL_{basename}_raw.fif"
signal = read.Reader(data_path)

# GA
signal_ga = correct.GA(signal.output, start_marker='Response/R128', tr=0.8)  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')

# Down-sample
signal_ds = filter.DownSample(signal_ga.output, 20) #check if needed

# PA
weight_path = r'C:\Users\moyne\Documents\GitHub\LaSEEB-NeuXus\data\PA correction LSTM models\weights-input-500.pkl'
signal_pa = correct.PA(signal_ds.output, weights_path=weight_path)

# CWL
signal_cwl = CWL(signal_ds.output, time_delay=21e-3, window_duration=4, overlap=0.5)

#print (signal_ds.output) #check if the output variable was generated
 
# Save to file
signal_save = Save(signal_ds.output, filename=ga_save_path, overwrite=True)
signal_save_pa = Save(signal_pa.output, marker_input_port=signal_pa.marker_output, filename=pa_save_path, overwrite=True)
signal_save_cwl = Save(signal_cwl.output, filename=cwl_save_path, overwrite=True)

#'Neuxus_GA_CWL_P{subject:02}_{condition}_mrion.fif')
#'Neuxus_GA_CWL_P2_eyes_closed_mrion.fif'
# rootDir = '/Users/moyne/Documents/GitHub/neuxus_test/Post_corrections/Neuxus/GA_CWL'
# file_path_GA_CWL_Neuxus = os.path.join(rootDir, f"Neuxus_GA_CWL_P{subject:02}_{condition}_mrion.fif")