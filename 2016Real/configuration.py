#tag = 'new_vbf_16_2'
tag = 'new_vbf_16_4'

outputFile   = f"mkShapes__{tag}.root"
outputFolder = f"rootFiles"

plotPath = "/eos/user/g/gpizzati/www/rdf/2016_full/"


# file with TTree aliases
aliasesFile = 'aliases.py'

# file with list of variables
variablesFile = 'variables.py'

# file with list of cuts
cutsFile = 'cuts.py' 

# file with list of samples
samplesFile = 'samples.py' 

# file with list of samples
plotFile = 'plot.py' 

# nuisances file for mkDatacards and for mkShape
nuisancesFile = 'nuisances.py'

# luminosity to normalize to (in 1/fb)
#lumi = 35.9
lumi = 36.33
minRatio = 0.5
maxRatio = 1.5

batchFolder = f'condor'
