# Simple RDF version of Latinos mkShapes

1. Run the setup command:
```
. ./setup.sh
```

2. Configure the configuration folder (e.g. plots16) with the main files:
- aliases.py
- configuration.py
- cuts.py
- plot.py
- samples.py
- variables.py

3. Run the analysis:
```
python mkShapesRDF.py -a 1 -f plots16
```
For the provided example (plots16) it's estimated an execution time of ~ 45 mins running with the 10 cores of lxplus @ CERN.


It's highly recommended to limit input ROOT files at the first run to check for errors. The following command will only take 1 file for each sample type:
```
python mkShapesRDF.py -a 1 -f plots16 -l 1
```

4. After the output ROOT file was created run the plots:
```
python mkShapesRDF.py -p 1 -f plots16
```
which will create the plots to the specified paths provided in `configuration.py` 

