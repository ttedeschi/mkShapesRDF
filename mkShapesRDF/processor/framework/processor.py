import sys
import subprocess
from mkShapesRDF.processor.framework.Steps_cfg import Steps
from mkShapesRDF.processor.framework.Productions_cfg import Productions
from mkShapesRDF.lib.SearchFiles import SearchFiles
import os
from pathlib import Path
from math import ceil
from textwrap import dedent


class Processor:
    def __init__(
        self,
        condorDir,
        eosDir,
        prodName,
        step,
        sampleName,
        inputFolder="",
        redirector="",
        maxFilesPerJob=1,
        limitFiles=-1,
        dryRun=0,
    ):
        self.condorDir = condorDir
        self.eosDir = eosDir
        self.searchFiles = SearchFiles()
        self.prodName = prodName
        self.sampleName = sampleName
        self.step = step
        self.inputFolder = inputFolder
        self.redirector = redirector
        self.maxFilesPerJob = maxFilesPerJob
        self.limitFiles = limitFiles
        self.dryRun = dryRun
        self.path = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "/"

    def getFiles_cfg(self):
        if self.inputFolder == "":
            # if no inputFolder is given -> DAS
            return {
                "process": self.Samples[self.sampleName]["nanoAOD"],
                "instance": self.Samples[self.sampleName].get("instance", ""),
            }
        else:
            return {
                "redirector": self.redirector,
                "folder": self.inputFolder,
                "process": "*" + self.sampleName + "*.root",
            }

    def addDeclareLines(self, step):
        if step not in Steps.keys():
            print(f"Error, step {step} not found in Steps")
            sys.exit()
        if "selection" in Steps[step].keys():
            self.fPy += "df = df.Filter(" + Steps[step]["selection"] + ")\n"
        if Steps[step]["isChain"]:
            for subtarget in Steps[step]["subTargets"]:
                self.addDeclareLines(subtarget)
        elif "declare" in Steps[step].keys():
            self.fPy += "from " + Steps[step]["import"] + " import *\n"
            self.fPy += Steps[step]["declare"] + "\n"
            self.fPy += "module = " + Steps[step]["module"] + "\n"
            self.fPy += "df = module.run(df, values) \n"

    def run(self):
        global fPy
        self.fPy = dedent(
            """
        import ROOT
        ROOT.EnableImplicitMT()
        ROOT.gROOT.SetBatch(True)
        """
        )
        self.fPy += "from mkShapesRDF.processor.framework.mRDF import mRDF\n"

        if Productions[self.prodName]["isData"]:
            self.fPy += (
                'lumiFile = "'
                + os.path.abspath(self.path + Productions[self.prodName]["jsonFile"])
                + '"\n'
            )
        else:
            xsFile = Productions[self.prodName]["xsFile"]
            with open(self.path + xsFile) as file:
                exec(file.read(), globals())
            self.fPy += "xs_db = " + str(xs_db) + "\n"  # noqa F821

        with open(self.path + Productions[self.prodName]["samples"]) as file:
            exec(file.read(), globals())

        self.Samples = Samples  # noqa F821

        files_cfg = self.getFiles_cfg()
        files = []
        if self.inputFolder == "":
            files = self.searchFiles.searchFilesDAS(**files_cfg)
        else:
            files = self.searchFiles.searchFiles(**files_cfg)
        files = files[: self.limitFiles]

        if len(files) == 0:
            print("No files found for", self.sampleName)
            sys.exit()

        print(files[0])

        fSh = ""
        with open(self.path + "../../../start.sh") as file:
            fSh += file.read()

        if self.inputFolder == "":
            cmd = "voms-proxy-info"
            proc = subprocess.Popen(
                cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True
            )
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

            os.system("cp " + proxypath + " " + os.environ["HOME"] + "/.proxy")

            fSh += f"export X509_USER_PROXY={os.environ['HOME']}/.proxy\n"

        fSh += "time python script.py\n"

        folderPathEos = self.eosDir + "/" + self.prodName + "/" + self.step
        Path(folderPathEos).mkdir(parents=True, exist_ok=True)

        fSh += "cp output.root " + folderPathEos + "/" + "${1}.root\n"
        fSh += "rm output.root\n"

        print(fSh)

        jobDir = self.condorDir + "/" + self.prodName + "/" + self.step + "/"
        Path(jobDir).mkdir(parents=True, exist_ok=True)

        with open(jobDir + "run.sh", "w") as file:
            file.write(fSh)

        os.system("chmod +x " + jobDir + "run.sh")

        nParts = ceil(len(files) / self.maxFilesPerJob)

        fJdl = (
            dedent(
                """
        universe = vanilla
        executable = run.sh
        arguments = $(Folder)

        should_transfer_files = YES
        transfer_input_files = $(Folder)/script.py

        output = $(Folder)/out.txt
        error  = $(Folder)/err.txt
        log    = $(Folder)/log.txt

        request_cpus   = 1
        +JobFlavour = "workday"

        queue 1 Folder in """
            )
            + ", ".join(
                list(
                    map(
                        lambda k: self.sampleName + "__part" + str(k),
                        list(range(nParts)),
                    )
                )
            )
        )

        with open(jobDir + "/submit.jdl", "w") as f:
            f.write(fJdl)

        frameworkPath = "/".join(
            os.path.abspath(os.path.dirname(__file__)).split("/")[:-2]
        )

        self.fPy += "sampleName = '" + self.sampleName + "'\n"

        self.fPy += "files = RPLME_FILES\n"
        self.fPy += f"ROOT.gInterpreter.Declare('#include \"{frameworkPath}/include/headers.hh\"')\n"

        self.fPy += "df = mRDF()\n"
        self.fPy += 'df = df.readRDF("Events", files)\n'

        self.fPy += "values = []\n"

        self.addDeclareLines(self.step)

        self.fPy += dedent(
            """
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
        )

        self.fPy = self.fPy.replace("RPLME_FW", frameworkPath)

        if "RPLME_genEventSumw" in self.fPy:
            import ROOT

            ROOT.gROOT.SetBatch(True)
            ROOT.EnableImplicitMT()
            df2 = ROOT.RDataFrame("Runs", files)
            genEventSumw = df2.Sum("genEventSumw").GetValue()
            self.fPy = self.fPy.replace("RPLME_genEventSumw", str(genEventSumw))

        for part in range(nParts):
            _files = files[
                part * self.maxFilesPerJob : (part + 1) * self.maxFilesPerJob
            ]
            _fPy = self.fPy.replace("RPLME_FILES", str(_files))

            jobDirPart = jobDir + self.sampleName + "__part" + str(part) + "/"
            Path(jobDirPart).mkdir(parents=True, exist_ok=True)

            with open(jobDirPart + "/script.py", "w") as f:
                f.write(_fPy)

        if self.dryRun == 0:
            proc = subprocess.Popen(
                f"cd {jobDir}; condor_submit submit.jdl;", shell=True
            )
            proc.wait()
