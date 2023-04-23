import sys
import subprocess
from mkShapesRDF.processor.framework.Steps_cfg import Steps
from mkShapesRDF.processor.framework.Productions_cfg import Productions
import os
from pathlib import Path

condorDir = "/".join(os.path.abspath(".").split("/")[:-1]) + "/condor"


def getFiles(process):
    procString = f'dasgoclient --query="file dataset={process}"'
    proc = subprocess.Popen(
        procString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out1, err1 = proc.communicate()
    out1 = out1.decode("utf-8")
    out1 = out1.split("\n")
    out1 = list(filter(lambda k: k.strip() != "", out1))
    print(out1, len(out1))
    err1 = err1.decode("utf-8")
    if len(err1) != 0:
        print("There were some errors in retriexing file:")
        print(err1)
        sys.exit()

    # FIXME limit files
    files = out1[:1]
    return files


procName = "Run2018_UL2018_nAODv9_Full2018v9"
sampleName = "DoubleMuon_Run2018A-UL2018-v1"
step = "DATAl1loose2018v9"

procName = "Summer20UL18_106x_nAODv9_Full2018v9"
sampleName = "EWKZ2Jets_ZToLL_M-50_MJJ-120"
step = "MCFull2018v9"

fPy = """
import ROOT
ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)
"""
fPy += "from mkShapesRDF.processor.framework.mRDF import mRDF\n"

if Productions[procName]["isData"]:
    fPy += 'lumiFile = "' + os.path.abspath(Productions[procName]["jsonFile"]) + '"\n'
else:
    xsFile = Productions[procName]["xsFile"]
    with open(xsFile) as file:
        exec(file.read())
    fPy += "xs_db = " + str(xs_db) + "\n"

with open(Productions[procName]["samples"]) as file:
    exec(file.read())


jobDir = condorDir + "/" + procName + "/" + step + "/" + sampleName + "/"
Path(jobDir).mkdir(parents=True, exist_ok=True)

frameworkPath = "/".join(os.path.abspath(".").split("/")[:-2])

cmd = "voms-proxy-info"
proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
out, err = proc.communicate()

if "Proxy not found" in err.decode("utf-8"):
    print("WARNING: No GRID proxy -> Get one first with:")
    print("voms-proxy-init -voms cms -rfc --valid 168:0")
    sys.exit()

proxypath = " xxx "
for line in out.decode("utf-8").split("\n"):
    if "path" in line:
        proxypath = line.split(":")[1].strip()
print(proxypath)

os.system("cp " + proxypath + " " + os.environ['HOME'] + "/.proxy")

fSh = f"""#!/bin/bash
export X509_USER_PROXY={os.environ['HOME']}/.proxy
"""
fSh += "cd " + "/".join(frameworkPath.split("/")[:-1]) + \
    "; . ./start.sh; cd -;\n"

fSh += "python script.py\n"

print(fSh)

with open(jobDir + "run.sh", "w") as file:
    file.write(fSh)

os.system("chmod +x " + jobDir + "run.sh")


fPy += "sampleName = '" + sampleName + "'\n"

process = Samples[sampleName]["nanoAOD"]

files = getFiles(process)
redirector = "root://cms-xrd-global.cern.ch/"
files = list(map(lambda k: redirector + k, files))
print(files[0])
fPy += "files = " + str(files) + "\n"
fPy += f"ROOT.gInterpreter.Declare('#include \"{frameworkPath}/include/headers.hh\"')\n"

fPy += "df = mRDF()\n"
fPy += 'df = df.readRDF("Events", files)\n'

fPy += "values = []\n"


def addDeclareLines(step):
    global fPy
    if step not in Steps.keys():
        print(f"Error, step {step} not found in Steps")
        sys.exit()
    if Steps[step]["isChain"]:
        for subtarget in Steps[step]["subTargets"]:
            addDeclareLines(subtarget)
    elif "declare" in Steps[step].keys():
        fPy += "from " + Steps[step]["import"] + " import *\n"
        fPy += Steps[step]["declare"] + "\n"
        fPy += "module = " + Steps[step]["module"] + "\n"
        fPy += "df = module.run(df, values) \n"


addDeclareLines(step)

fPy += """
snapshots = []
for val in values:
    if "snapshot" == val[0]:
        snapshots.append(val[1])

if len(snapshots) != 0:
    ROOT.RDF.RunGraphs(snapshots)

def sciNot(value):
    # scientific notation
    return "{:.3e}".format(value)

data = []
for val in values:
    if "snapshot" == val[0]:
        continue
    if "list" in str(type(val)):
        if str(type(val[0])) == "<class 'function'>":
            data.append(val[0](*val[1:]))
        else:
            data.append([val[1], sciNot(val[0].GetValue())])
    else:
        data.append("", sciNot(val.GetValue()))

from tabulate import tabulate

print(tabulate(data, headers=["desc.", "value"]))
"""

with open(jobDir + "/script.py", "w") as f:
    f.write(fPy)
