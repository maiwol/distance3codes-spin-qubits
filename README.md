# README

This repository contains the source code used to generate the data for the paper *Comparison of spin-qubit architectures for quantum error-correcting codes* by Mauricio Gutiérrez, Juan S. Rojas-Arias, David Obando, and Chien-Yuan Chang ([https://arxiv.org/abs/2506.17190](https://arxiv.org/abs/2506.17190)).  The full dataset is available in [this Zenodo repository](https://zenodo.org/records/15766971).

# Overview

The toolkit is based on python2 and uses a modified version of [CHP](https://www.scottaaronson.com/chp/) as its core simulator.  To generate the JSON files with the raw data, the two main scripts are:

`QEC_d3_surface17_MC_fast_qdot1.py`

`QEC_d3_surface17_MC_fast_qdot_prep1.py`

These scripts generate JSON files containing the results of the sampling. Since subset sampling is employed, a separate JSON file is generated for each subset.

The json files with the complete raw data are available in [this Zenodo repository](https://zenodo.org/records/15766971).


# Generating the JSON files with the raw data

To generate the JSON files with the raw data, run either 

`QEC_d3_surface17_MC_fast_qdot1.py` (for QEC) or 

`QEC_d3_surface17_MC_fast_qdot_prep1.py` (for state preparation).  

The scripts are written in Python2.  In bash, run the following command:

``` 
$python2 QEC_d3_surface17_MC_fast_qdot1.py n_proc QEC_code state
```

The inputs are:

`n_proc` number of processors to use (Monte Carlo sampling is embarrassingly parallel, so it's advisable to use all processors in your computer)

`QEC_code` either "surface17" or "BS17"

`state` the logical state (either "X" or "Z")

The script builds the corresponding quantum circuit and samples the error configuration space.  The information regarding which error subsets to sample and how many samples to get from each subset is found in a file of the form `subset_dictx.json`, which is called by the python scripts.  Only the error subsets with a high probability of occurrence are sampled.  For each sampled error subset, a JSON file is generated and saved in the corresponding folder.  This JSON file contains the logical error rate for that given subset.  We include all the generated JSON files in the associated [Zenodo repository](https://zenodo.org/records/15766971).  

# Curating the raw data

To extract the data from each error subset JSON file, run the following command:

```
$python2 summary_pfail_surface17.py QEC_code state process_kind error_model
```

The inputs are:

`QEC_code` either "surface17" or "BS17"

`state` the logical state (either "X" or "Z")

`process_kind` either "QEC" or "prep" (for logical state preparation)

`error_model` either "qdot0" or "qdot1" ("qdot1" is the more detailed error model used in the paper)

This generates a file named `summary_lookupdecoder.json` which includes the logical error rate for each sampled error subset.

# Generating the dat files for plotting

To generate the dat file for each figure in the paper, run the following command:

```
$python2 script_FigX.py QEC_code state process_kind pmST_constant plot_int_t ramp_t
```

The first 3 inputs are the same as before.  The other inputs are:

`pmST_constant` whether the readout error rate of the ST qubit will be constant or not (`0` not constant; `1` constant)

`plot_int_t` whether we want to plot as the X axis the integration time or the total readout time (`0` total readout time; `1` integration time)

`ramp_t` the ramping time of the ST qubit readout in microseconds (for the paper, we set it to 0.4)

# Generating the plots

Run the notebook `Plots_qdots.ipynb`.  Be mindful of the folder paths to import the dat files.




