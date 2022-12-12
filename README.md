# Simple Parallel RDF version of Latinos mkShapes

1. Run the setup command:
```
. ./setup.sh
```

2. Configure the configuration folder (e.g. plotsP) with the main files:
- aliases.py
- configuration.py
- cuts.py
- plot.py
- samples.py
- variables.py

3. Run the analysis:
```
python mkShapesRDFParallel.py -o 0 -f plotsP -b 1
```
`-o` indicates the operationMode:
- 0 run analysis on condor
- 1 merge root files
- 2 plot them

For the provided example (plotsP) it's estimated an execution time of ~ 10 mins running on lxbatch (condor on lxplus) @ CERN.


It's highly recommended to limit input ROOT files at the first run to check for errors. The following command will only take 1 file for each sample type:
```
python mkShapesRDFParallel.py -o 0 -f plotsP -l 1
```

4. After all the jobs finished (or most of them did) you can run `mkShapesRDFParallel.py -o 1 -f plotsP` to know which jobs failed and why

5. If all the jobs succeeded run the merger with the option: 
```
python mkShapesRDFParallel.py -o 2 -f plotsP
```

6. Plot with 
```
python mkShapesRDFParallel.py -o 3 -f plotsP
```
which will create the plots to the specified paths provided in `configuration.py` 

