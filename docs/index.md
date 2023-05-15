# Welcome to mkShapesRDF

## Installation 

Git clone the project and work with the `v0.0.1` 

```bash

git clone https://github.com/giorgiopizz/mkShapesRDF.git
git checkout v0.0.1

```

Lxplus is currently the suggested machine to work with.
In general one should need `cvmfs` with `sft.cern.ch` and `cms.cern.ch`.
### Automatic installation

mkShapesRDF has its own install script: `install.sh`: it first sources the correct python environment (it should contain a recent python3 and ROOT bindings) and then proceeds with the creation of a virtual environment `myenv` where all the needed packages and the framework scripts will be installed.

You're free to change the environment with conda/mamba insted of a LCG release inside `install.sh`.

When you're ready just run:
```bash
./install.sh
```
It will create a `start.sh` script that should be run everytime to activate the environment.


### Manual installation

In order to install the package it's first necessary to source the right LCG release:
```bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/setup.sh
```
now the right python version (3.9) and it's bindings with ROOT are setup.
It's highly reccomended to create a virtual environment for the installation:
```bash
python -m venv --system-site-packages myenv
```
and of course activate it:
```bash
source myenv/bin/activate
```

Now you can proceed to the simple installation:
```bash
pip install -e .
```

Now to work with `mkShapes.processor` one should also install correctionlib and compile it:
```bash
python -m pip install --no-binary=correctionlib correctionlib
```

From now on, when you will login again on lxplus you will just have to run the setup command:
```bash
. ./start.sh
```

## Configure the configuration folder (e.g. `examples/2016Real`):
Documentation on the configuration folder structure at [this page](config.md)
<!-- - configuration.py 

- aliases.py
- configuration.py
- cuts.py
- nuisances.py
- plot.py
- samples.py
- variables.py -->

## Compile the configuration folder:
Inside a configuration folder one can compile it into `.json` and `.pkl`.
The compiled version are used across all the operating modes of mkShapesRDF
``` bash
mkShapesRDF -c 1
```


## Run the analysis:
``` bash
mkShapesRDF -o 0 -f . -b 1
```
`-o` indicates the operationMode:
- 0 run analysis
- 1 check batch output and errs
- 2 merge root files
- 3 plot them

For the provided example (2016Real) it's estimated an execution time of ~ 10 mins running on lxbatch (condor on lxplus) @ CERN when disabling nuisances.


It's highly recommended to limit input ROOT files at the first run to check for errors. The following command will only take 1 event for each sample type:
``` bash
mkShapesRDF -o 0 -f . -l 1
```

## Check for errors
After all the jobs finished (or most of them did) you can run `mkShapesRDF -o 1 -f .` to know which jobs failed and why.

One can resubmit failed jobs with `mkShapesRDF -o 1 -f . -r 1`.

While if one wants to resubmit jobs that are still running, the option `-r 2` should be used.

## Merge files
If all the jobs succeeded run the merger with the option: 
```bash
mkShapesRDF -o 2 -f .
```

## Plots
Plot with 
```bash
mkShapesRDF -o 3 -f .
```
which will create the plots to the specified paths provided in `configuration.py` 
