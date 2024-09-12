from mkShapesRDF.lib.search_files import SearchFiles
import os


searchFiles = SearchFiles()
def GetLatinoNanoAOD(path, name):
    _files = searchFiles.searchFiles(path, name, redirector=redirector)
    return [(name, _files)]

def makeMCDirectory(var=""):
    _treeBaseDir = treeBaseDir + ""


treeBaseDir = "/eos/cms/store/group//phys_higgs/cmshww/HWWNano"
dataRun3 = ["Run2023_Prompt_nAODv12_Full2023v12"]
dataSteps = ["DATAl1loose2023v12__addTnPElectron", "DATAl1loose2023v12__addTnPMuon"]
MCRun3 = " "
MC_Steps = ["   ", "  "]

for item in dataSteps:
    dataDirectory = os.path.join(treeBaseDir, dataRun3, item)
for itemMC in MC_Steps:
    MC_Directory = os.path.join(treeBaseDir, MCRun3, itemMC)


samples = {}


