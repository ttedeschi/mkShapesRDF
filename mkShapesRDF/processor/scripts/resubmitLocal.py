import os
import subprocess

resubmitLine = "queue 1 Folder in DoubleMuon_Run2018A-UL2018-v1__part11 DoubleMuon_Run2018A-UL2018-v1__part5"
condorFolder = "../condor/Run2018_UL2018_nAODv9_Full2018v9/DATAl1loose2018v9"

samples = resubmitLine[len("queue 1 Folder in ") :].split(" ")
print(str(samples))

condorFolder = os.path.abspath(condorFolder)

proc = subprocess.Popen(
    "which python3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
out, err = proc.communicate()
out = out.decode("utf-8")
frameworkPath = "/".join(out.split("\n")[0].split("/")[:-3]) + "/"


for sample in samples:
    fSh = "#!/bin/bash\n"
    fSh += f"cd {condorFolder}/{sample}\n"
    fSh += "mkdir tmp\n"
    fSh += "cd tmp\n"
    fSh += "cp ../script.py . \n"
    fSh += "cp ../../run.sh . \n"
    fSh += 'echo "run locally" > err.txt\n'
    fSh += f"./run.sh {sample} 2>../err.txt 1>../out.txt\n"
    fSh += "cd ..; rm -r tmp\n"

    fileName = f"tmp_run_{sample}.sh"

    with open(fileName, "w") as file:
        file.write(fSh)

    proc = subprocess.Popen(
        f"chmod +x {fileName}; ./{fileName}; rm {fileName}", shell=True
    )
    proc.wait()
