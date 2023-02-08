#tag = 'new_vbf_16_2'
tag = 'new_vbf_16'

runnerFile = 'default'

outputFile    = "mkShapes__{}.root".format(tag)
outputFolder  = "rootFiles"
batchFolder   = 'condor'
configsFolder = 'configs'

plotPath      = "/eos/user/g/gpizzati/www/rdf/2016_new_prefit"


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

structureFile = 'structure.py'

# nuisances file for mkDatacards and for mkShape
nuisancesFile = 'nuisances.py'

# luminosity to normalize to (in 1/fb)
#lumi = 35.9
lumi = 36.33
minRatio = 0.5
maxRatio = 1.5

mountEOS=True

imports = ['os', 'glob', ('collections', 'OrderedDict'), 'ROOT']
filesToExec = [samplesFile, aliasesFile, variablesFile, cutsFile,  plotFile, nuisancesFile]
varsToKeep = ['outputFolder', 'batchFolder', 'configsFolder', 'outputFile', 'runnerFile', 'tag', 'samples', 'aliases', 'variables', ('cuts', {'cuts': 'cuts', 'preselections': 'preselections'} ), ('plot', {'plot' : 'plot', 'groupPlot': 'groupPlot'}), 'nuisances', 'lumi', 'mountEOS']
batchVars = varsToKeep[varsToKeep.index('samples'):]

