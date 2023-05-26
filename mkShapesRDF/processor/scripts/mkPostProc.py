from mkShapesRDF.processor.framework.processor import Processor
import argparse
import os
from sys import argv
import glob
import subprocess
import tabulate

condorDir = (
    "/".join(os.path.abspath(os.path.dirname(__file__)).split("/")[:-1]) + "/condor"
)
print(condorDir)
eosDir = "/eos/user/g/gpizzati/mkShapesRDF_nanoAOD"


def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "-o",
        "--operationMode",
        type=int,
        choices=[0, 1],
        help="0 do analysis in batch, 1 check for errors in batch submission",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--prod",
        type=str,
        help="Production to run on",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--step",
        type=str,
        help="Step to run",
        required=True,
    )

    parser.add_argument(
        "-sN",
        "--sampleName",
        type=str,
        help="Sample to process",
        required=True,
    )

    if len(argv) < 1 + 2 * 4:
        # just give the parser error
        args = parser.parse_args()
    else:
        real_args = argv[1 : 1 + 2 * 4]
        args = parser.parse_args(real_args)

    opMode = args.operationMode
    prodName = args.prod
    step = args.step
    sampleName = args.sampleName

    if opMode == 0:
        parser0 = argparse.ArgumentParser(parents=[parser])

        parser0.add_argument(
            "-i",
            "--inputFolder",
            help="Input folder to search for files",
            required=False,
            default="",
        )

        parser0.add_argument(
            "--maxFilesPerJob",
            type=int,
            help="Max number of input files per job (will merge input files)",
            required=False,
            default=1,
        )

        parser0.add_argument(
            "-l",
            "--limitFiles",
            type=int,
            help="Limit number of files to process",
            required=False,
            default=-1,
        )

        parser0.add_argument(
            "-dR",
            "--dryRun",
            choices=[0, 1],
            type=int,
            help="1 do not submit to condor",
            required=False,
            default=0,
        )

        parser0.add_argument(
            "--useRedirector",
            choices=[0, 1],
            type=int,
            help="0 do not use redirector, 1 use it",
            required=False,
            default=0,
        )

        args = parser0.parse_args()

        inputFolder = args.inputFolder
        maxFilesPerJob = args.maxFilesPerJob
        limitFiles = args.limitFiles
        dryRun = args.dryRun
        useRedirector = args.useRedirector

        redirector = ""
        if useRedirector == 1:
            redirector = "root://cms-xrd-global.cern.ch/"

        a = Processor(
            condorDir=condorDir,
            eosDir=eosDir,
            prodName=prodName,
            sampleName=sampleName,
            step=step,
            inputFolder=inputFolder,
            redirector=redirector,
            maxFilesPerJob=maxFilesPerJob,
            limitFiles=limitFiles,
            dryRun=dryRun,
        )

        a.run()
    elif opMode == 1:
        parser1 = argparse.ArgumentParser(parents=[parser])

        parser1.add_argument(
            "-r",
            "--resubmit",
            type=int,
            choices=[0, 1],
            help="0 do not resubmit, 1 resubmit",
            required=True,
            default=0,
        )
        args = parser1.parse_args()
        resubmit = args.resubmit
        print("Should check for errors")

        folder = "../condor/Summer20UL18_106x_nAODv9_Full2018v9/MCFull2018v9/"
        folder = condorDir + "/" + prodName + "/" + step + "/"

        folder = os.path.abspath(folder)

        errs = glob.glob(f"{folder}/{sampleName}/err.txt")
        files = glob.glob(f"{folder}/{sampleName}/script.py")

        errsD = list(map(lambda k: "/".join(k.split("/")[:-1]), errs))
        filesD = list(map(lambda k: "/".join(k.split("/")[:-1]), files))
        # print(files)
        notFinished = list(set(filesD).difference(set(errsD)))
        print(notFinished)
        tabulated = []
        tabulated.append(["Total jobs", "Finished jobs", "Running jobs"])
        tabulated.append([len(files), len(errs), len(notFinished)])

        print(tabulate.tabulate(tabulated))
        # print('queue 1 Folder in ' + ' '.join(list(map(lambda k: k.split('/')[-1], notFinished))))
        normalErrs = """Warning in <TClass::Init>: no dictionary for class edm::ProcessHistory is available
        Warning in <TClass::Init>: no dictionary for class edm::ProcessConfiguration is available
        Warning in <TClass::Init>: no dictionary for class edm::ParameterSetBlob is available
        Warning in <TClass::Init>: no dictionary for class edm::Hash<1> is available
        Warning in <TClass::Init>: no dictionary for class pair<edm::Hash<1>,edm::ParameterSetBlob> is available
        Warning in <TInterpreter::ReadRootmapFile>: class  podio::
        real
        user
        sys
        run locally
        No TTree was created for
        Warning in <Snapshot>: A lazy Snapshot action was booked but never triggered.
        """
        normalErrs = normalErrs.split("\n")
        normalErrs = list(map(lambda k: k.strip(" ").strip("\t"), normalErrs))
        normalErrs = list(filter(lambda k: k != "", normalErrs))

        toResubmit = []

        def normalErrsF(k):
            for s in normalErrs:
                if s in k:
                    return True
                elif k.startswith(s):
                    return True
            return False

        for err in errs:
            with open(err) as file:
                lines = file.read()
            txt = lines.split("\n")
            # txt = list(filter(lambda k: k not in normalErrs, txt))
            txt = list(filter(lambda k: not normalErrsF(k), txt))
            txt = list(filter(lambda k: k.strip() != "", txt))
            if len(txt) > 0:
                print("Found unusual error in")
                print(err)
                print("\n")
                # print("\n".join(txt))
                print("\n\n")
                toResubmit.append(err)
        toResubmit = list(map(lambda k: "".join(k.split("/")[-2]), toResubmit))
        print(toResubmit)
        if len(toResubmit) > 0:
            print("\n\nShould resubmit the following files\n")
            print(
                "queue 1 Folder in "
                + " ".join(list(map(lambda k: k.split("/")[-1], toResubmit)))
            )
            if resubmit == 1:
                with open(f"{folder}/submit.jdl") as file:
                    txt = file.read()

                lines = txt.split("\n")
                line = list(filter(lambda k: k.startswith("queue"), lines))[0]
                lines[
                    lines.index(line)
                ] = f'queue 1 Folder in {", ".join(toResubmit)}\n '
                with open(f"{folder}/submit.jdl", "w") as file:
                    file.write("\n".join(lines))
                proc = subprocess.Popen(
                    f"cd {folder}; condor_submit submit.jdl", shell=True
                )
                proc.wait()

    else:
        print("Invalid operation mode")


if __name__ == "__main__":
    main()
