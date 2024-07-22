# neuxus_test

## EEG PC

### Installation

### Create new conda env
```bash
conda create -n mne-lsl python=3.12
```
#### Install dependencies
```bash
conda activate mne-lsl
pip install RDA/requirements.txt
```

### Usage

1. Start Recorder

2. Start Recview
    - Filter Tree
        MRI filter + RDA server
    - Connect Recorder
3. Start RDA_lsl.py (RDA/RDA_lsl.py)
```bash
conda activate mne-lsl
python RDA_lsl.py
```

## Experiment PC

### Installation

```bash
conda create -n LaSEEB-neuxus python=3.7
```

Clone: https://github.com/LaSEEB/NeuXus

Dans le dossier LaSEEB/NeuXus:
```bash
conda activate LaSEEB-neuxus
pip install -e .
```

### Usage

```bash
conda activate LaSEEB-neuxus
neuxus recview_pipeline.py
```

## MNE-LSL

### installer mne-lsl
```bash
conda create -n mne-lsl python=3.10
conda activate mne-lsl
pip install mne-lsl pyqt5
```

### use
```bash
conda activate mne-lsl
mne_lsl_stream_viewer
```

```bash
conda activate mne-lsl
mne_lsl_player  path/to/my/file.vhdr
```

