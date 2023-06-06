# flake8: noqa E266
from mkShapesRDF.lib.search_files import SearchFiles

searchFiles = SearchFiles()
# redirector = "root://eoscms.cern.ch/"
redirector = ""


mcProduction = "Summer16_102X_nAODv7_Full2016v7"
dataReco = "Run2016_102X_nAODv7_Full2016v7"
mcSteps = "MCl1loose2016v7__MCCorr2016v7__l2loose__l2tightOR2016v7"
fakeSteps = "DATAl1loose2016v7__l2loose__fakeW"
dataSteps = "DATAl1loose2016v7__l2loose__l2tightOR2016v7"

##############################################
###### Tree base directory for the site ######
##############################################
treeBaseDir = "/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano"
limitFiles = -1


def makeMCDirectory(var=""):
    _treeBaseDir = treeBaseDir + ""
    if redirector != "":
        _treeBaseDir = redirector + treeBaseDir
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])


mcDirectory = makeMCDirectory()
fakeDirectory = os.path.join(treeBaseDir, dataReco, fakeSteps)
dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)

samples = {}


def nanoGetSampleFiles(path, name):
    _files = searchFiles.searchFiles(path, name, redirector=redirector)
    if limitFiles != -1 and len(_files) > limitFiles:
        return [(name, _files[:limitFiles])]
    else:
        return [(name, _files)]


def CombineBaseW(samples, proc, samplelist):
    _filtFiles = list(filter(lambda k: k[0] in samplelist, samples[proc]["name"]))
    _files = list(map(lambda k: k[1], _filtFiles))
    _l = list(map(lambda k: len(k), _files))
    leastFiles = _files[_l.index(min(_l))]
    dfSmall = ROOT.RDataFrame("Runs", leastFiles)
    s = dfSmall.Sum("genEventSumw").GetValue()
    f = ROOT.TFile(leastFiles[0])
    t = f.Get("Events")
    t.GetEntry(1)
    xs = t.baseW * s

    __files = []
    for f in _files:
        __files += f
    df = ROOT.RDataFrame("Runs", __files)
    s = df.Sum("genEventSumw").GetValue()
    newbaseW = str(xs / s)
    weight = newbaseW + "/baseW"

    for iSample in samplelist:
        addSampleWeight(samples, proc, iSample, weight)


def addSampleWeight(samples, sampleName, sampleNameType, weight):
    obj = list(filter(lambda k: k[0] == sampleNameType, samples[sampleName]["name"]))[0]
    samples[sampleName]["name"] = list(
        filter(lambda k: k[0] != sampleNameType, samples[sampleName]["name"])
    )
    if len(obj) > 2:
        samples[sampleName]["name"].append(
            (obj[0], obj[1], obj[2] + "*(" + weight + ")")
        )
    else:
        samples[sampleName]["name"].append((obj[0], obj[1], "(" + weight + ")"))


DataRun = [
    ["B", "Run2016B-02Apr2020_ver2-v1"],
    ["C", "Run2016C-02Apr2020-v1"],
    ["D", "Run2016D-02Apr2020-v1"],
    ["E", "Run2016E-02Apr2020-v1"],
    ["F", "Run2016F-02Apr2020-v1"],
    ["G", "Run2016G-02Apr2020-v1"],
    ["H", "Run2016H-02Apr2020-v1"],
]

DataSets = ["MuonEG", "SingleMuon", "SingleElectron", "DoubleMuon", "DoubleEG"]

DataTrig = {
    "MuonEG": " Trigger_ElMu",
    "SingleMuon": "!Trigger_ElMu && Trigger_sngMu",
    "SingleElectron": "!Trigger_ElMu && !Trigger_sngMu && Trigger_sngEl",
    "DoubleMuon": "!Trigger_ElMu && !Trigger_sngMu && !Trigger_sngEl && Trigger_dblMu",
    "DoubleEG": "!Trigger_ElMu && !Trigger_sngMu && !Trigger_sngEl && !Trigger_dblMu && Trigger_dblEl",
}


mcCommonWeightNoMatch = "XSWeight*SFweight*METFilter_MC"
mcCommonWeight = "XSWeight*SFweight*PromptGenLepMatch2l*METFilter_MC"


###### Zjj EWK #######

files = nanoGetSampleFiles(mcDirectory, "EWK_LLJJ_MLL-50_MJJ-120")

samples["Zjj"] = {
    "name": files,
    "weight": mcCommonWeight,
    "FilesPerJob": 1,
}


###### DY MC ######
dys = {
    "DY_hardJets": "hardJets",
    "DY_PUJets": "PUJets",
}


files = nanoGetSampleFiles(mcDirectory, "DYJetsToLL_M-50_ext2")

samples["DY"] = {
    "name": files,
    "weight": mcCommonWeight
    + "*( !(Sum(PhotonGen_isPrompt==1 && PhotonGen_pt>15 && abs(PhotonGen_eta)<2.6) > 0)) * ewknloW",
    "FilesPerJob": 5,
    "subsamples": dys,
}


###########################################
################## DATA ###################
###########################################

samples["DATA"] = {
    "name": [],
    "weight": "METFilter_DATA*LepWPCut",
    "weights": [],
    "isData": ["all"],
    "FilesPerJob": 50,
}

for _, sd in DataRun:
    for pd in DataSets:
        files = nanoGetSampleFiles(dataDirectory, pd + "_" + sd)

        samples["DATA"]["name"].extend(files)
        addSampleWeight(samples, "DATA", pd + "_" + sd, DataTrig[pd])
        # samples['DATA']['weights'].extend([DataTrig[pd]] * len(files))
# print(samples['DATA']['name'])
#
