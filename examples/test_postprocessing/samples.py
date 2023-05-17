import os, glob
mcProduction = 'Summer20UL18_106x_nAODv9_Full2018v9'
dataReco = 'Run2018_UL2018_nAODv9_Full2018v9'
mcSteps = 'MCFull2018v9'
dataSteps = 'DATAl1loose2018v9'

##############################################
###### Tree base directory for the site ######
##############################################
treeBaseDir = '/eos/user/g/gpizzati/mkShapesRDF_nanoAOD/'
limitFiles = -1

def makeMCDirectory(var=''):
        return os.path.join(treeBaseDir, mcProduction, mcSteps.format(var=''))

mcDirectory = makeMCDirectory()
dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)

samples = {}

from mkShapesRDF.shapeAnalysis.libs.SearchFiles import SearchFiles
s = SearchFiles()

useXROOTD = False
redirector = 'root://eoscms.cern.ch/'

def nanoGetSampleFiles(path, name):
    _files = s.searchFiles(path,  f"/{name}__part*.root", useXROOTD, redirector=redirector)
    if limitFiles != -1 and len(_files) > limitFiles:
        return [(name, _files[:limitFiles])]
    else:
        return  [(name, _files)]

def CombineBaseW(samples, proc, samplelist):
    _filtFiles = list(filter(lambda k: k[0] in samplelist, samples[proc]['name']))
    _files = list(map(lambda k: k[1], _filtFiles))
    _l = list(map(lambda k: len(k), _files))
    leastFiles = _files[_l.index(min(_l))]
    dfSmall = ROOT.RDataFrame("Runs", leastFiles)
    s = dfSmall.Sum('genEventSumw').GetValue()
    f = ROOT.TFile(leastFiles[0])
    t = f.Get("Events")
    t.GetEntry(1)
    xs = t.baseW * s

    __files = []
    for f in _files:
        __files += f
    df = ROOT.RDataFrame("Runs", __files)
    s = df.Sum('genEventSumw').GetValue()
    newbaseW = str(xs / s)
    weight = newbaseW + '/baseW'

    for iSample in samplelist:
        addSampleWeight(samples, proc, iSample, weight) 

def addSampleWeight(samples, sampleName, sampleNameType, weight):
    obj = list(filter(lambda k: k[0] == sampleNameType, samples[sampleName]['name']))[0]
    samples[sampleName]['name'] = list(filter(lambda k: k[0] != sampleNameType, samples[sampleName]['name']))
    if len(obj) > 2:
        samples[sampleName]['name'].append((obj[0], obj[1], obj[2] + '*(' + weight + ')'))
    else:
        samples[sampleName]['name'].append((obj[0], obj[1], '(' + weight + ')' ))


################################################
############ DATA DECLARATION ##################
################################################

DataRun = [
    ['A','Run2018A-UL2018-v1'],
    ['B','Run2018B-UL2018-v1'],
    ['C','Run2018C-UL2018-v1'],
    ['D','Run2018D-UL2018-v1'],
]

DataSets = ['MuonEG','SingleMuon','EGamma','DoubleMuon']

DataTrig = {
    'MuonEG'         : 'Trigger_ElMu' ,
    'DoubleMuon'     : '!Trigger_ElMu && Trigger_dblMu' ,
    'SingleMuon'     : '!Trigger_ElMu && !Trigger_dblMu && Trigger_sngMu' ,
    'EGamma'         : '!Trigger_ElMu && !Trigger_dblMu && !Trigger_sngMu && (Trigger_sngEl || Trigger_dblEl)' ,
}

#########################################
############ MC COMMON ##################
#########################################

# SFweight does not include btag weights
mcCommonWeight = 'baseW'

###########################################
#############  BACKGROUNDS  ###############
###########################################

###### DY #######

files = nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-50') 

samples['dyll'] = {
    'name': files,
    'weight': mcCommonWeight,
    'FilesPerJob': 2,
}



###########################################
################## DATA ###################
###########################################

files = nanoGetSampleFiles(dataDirectory, 'DoubleMuon_Run2018A-UL2018-v1')
samples['DATA'] = {
  'name': files,
  'weight': '1.0',
  'isData': ['all'],
  'FilesPerJob': 50
}

# for _, sd in DataRun:
#   for pd in DataSets:
#     datatag = pd + '_' + sd

#     if (   ('DoubleMuon' in pd and 'Run2018B' in sd)
#         or ('DoubleMuon' in pd and 'Run2018D' in sd)
#         or ('SingleMuon' in pd and 'Run2018A' in sd)
#         or ('SingleMuon' in pd and 'Run2018B' in sd)
#         or ('SingleMuon' in pd and 'Run2018C' in sd)):
#         print("sd      = {}".format(sd))
#         print("pd      = {}".format(pd))
#         print("Old datatag = {}".format(datatag))
#         datatag = datatag.replace('v1','v2')
#         print("New datatag = {}".format(datatag))

#     files = nanoGetSampleFiles(dataDirectory, datatag)

#     samples['DATA']['name'].extend(files)
#     addSampleWeight(samples, 'DATA', datatag, DataTrig[pd])
#     #samples['DATA']['weights'].extend([DataTrig[pd]] * len(files))

