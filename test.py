from neuxus.nodes import correct, io, filter, select


weight_path = r'C:\Users\moyne\Documents\GitHub\LaSEEB-NeuXus\examples\mri-artifact-correction\weights-input-500.pkl'

# signal = io.RdaReceive(rdaport=51244)
signal = io.LslReceive('name', 'MNE-LSL-Player', 'signal')
signal_ga = correct.GA(signal.output)  # 'Response/R128' is the marker of the start of every MRI volume (in case the data is read from a Brain Vision file; in case it's streamed by Brain Vision Recorder, it is 'R128')
signal_ds = filter.DownSample(signal_ga.output, int(5000 / 250))
signal_ds_ecg = select.ChannelSelector(signal_ds.output, 'name', ['ECG'])
signal_ds_ecg_fi = filter.ButterFilter(signal_ds_ecg.output,  0.5, 30)
signal_ds_fi = select.ChannelUpdater(signal_ds.output, signal_ds_ecg_fi.output)
signal_pa = correct.PA(signal_ds_fi.output, weight_path)


signal_pa_lsl = io.LslSend(signal_pa.output, 'signal_pa', type='EEG')
