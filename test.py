from neuxus.nodes import correct, io, filter, select, read

data_path = r'C:\Users\victor.ferat\Documents\Soraya\EEG-MRI\P05_eyes_open_mrion.vhdr'
weight_path = r'C:\Users\victor.ferat\Documents\GitHub\NeuXus\examples\mri-artifact-correction\weights-input-500.pkl'

# signal = io.RdaReceive(rdaport=51244)
# signal = io.LslReceive('name', 'MNE-LSL-Player', 'signal')
signal = read.Reader(data_path)

signal_ga = correct.GA(signal.output, marker_input_port=signal.marker_output, start_marker='Response/R128')  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')
signal_ds = filter.DownSample(signal_ga.output, int(5000 / 250))
signal_ds_ecg = select.ChannelSelector(signal_ds.output, 'name', ['ECG'])
signal_ds_ecg_fi = filter.ButterFilter(signal_ds_ecg.output,  0.5, 30)
signal_ds_fi = select.ChannelUpdater(signal_ds.output, signal_ds_ecg_fi.output)
signal_pa = correct.PA(signal_ds_fi.output, weight_path)


signal_lsl = io.LslSend(signal.output, 'raw', type='EEG')
signal_pa_lsl = io.LslSend(signal_pa.output, 'corrected', type='EEG')
