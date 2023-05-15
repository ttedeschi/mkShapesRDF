tag = "new_vbf_16"

runnerFile = "default"

outputFile = "mkShapes__{}.root".format(tag)
outputFolder = "rootFiles"
batchFolder = "condor"
configsFolder = "configs"

# luminosity to normalize to (in 1/fb)
lumi = 36.33


# file with TTree aliases
aliasesFile = "aliases.py"

# file with list of variables
variablesFile = "variables.py"

# file with list of cuts
cutsFile = "cuts.py"

# file with list of samples
samplesFile = "samples.py"

# file with list of samples
plotFile = "plot.py"

structureFile = "structure.py"

# nuisances file for mkDatacards and for mkShape
nuisancesFile = "nuisances.py"

minRatio = 0.5
maxRatio = 1.5
#plotPath = "/eos/user/g/gpizzati/www/rdf/2016/"
plotPath = "plots"

# this lines are executed right before the runner on the condor node
mountEOS = [
#     "export KRB5CCNAME=/home/gpizzati/krb5\n",
]

imports = ["os", "glob", ("collections", "OrderedDict"), "ROOT"]
filesToExec = [
    samplesFile,
    aliasesFile,
    variablesFile,
    cutsFile,
    plotFile,
    nuisancesFile,
    structureFile,
]

varsToKeep = [
    "batchVars",
    "outputFolder",
    "batchFolder",
    "configsFolder",
    "outputFile",
    "runnerFile",
    "tag",
    "samples",
    "aliases",
    "variables",
    ("cuts", {"cuts": "cuts", "preselections": "preselections"}),
    ("plot", {"plot": "plot", "groupPlot": "groupPlot", "legend": "legend"}),
    "nuisances",
    "structure",
    "lumi",
    "mountEOS",
]

batchVars = varsToKeep[varsToKeep.index("samples") :]

varsToKeep += ['minRatio', 'maxRatio', 'plotPath']
