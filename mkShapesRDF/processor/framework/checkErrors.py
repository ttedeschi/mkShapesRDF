import glob
import os
import subprocess

folder = '../condor/Run2018_UL2018_nAODv9_Full2018v9/DATAl1loose2018v9'
resubmit = 1


folder = os.path.abspath(folder)

errs = glob.glob(f"{folder}/*/err.txt")
files = glob.glob(f"{folder}/*/script.py")

errsD = list(map(lambda k: "/".join(k.split("/")[:-1]), errs))
filesD = list(map(lambda k: "/".join(k.split("/")[:-1]), files))
# print(files)
notFinished = list(set(filesD).difference(set(errsD)))
print(notFinished)
tabulated = []
tabulated.append(["Total jobs", "Finished jobs", "Running jobs"])
tabulated.append([len(files), len(errs), len(notFinished)])
import tabulate

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
        l = file.read()
    txt = l.split("\n")
    # txt = list(filter(lambda k: k not in normalErrs, txt))
    txt = list(filter(lambda k: not normalErrsF(k), txt))
    txt = list(filter(lambda k: k.strip() != "", txt))
    if len(txt) > 0:
        print("Found unusual error in")
        print(err)
        print("\n")
        print("\n".join(txt))
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


        with open(f'{folder}/submit.jdl') as file:
            txt = file.read()

        lines = txt.split('\n')
        line = list(filter(lambda k: k.startswith('queue'), lines))[0]
        lines[lines.index(line)] = f'queue 1 Folder in {", ".join(toResubmit)}\n '
        with open(f'{folder}/submit.jdl', 'w') as file:
            file.write('\n'.join(lines))
        proc = subprocess.Popen(f'cd {folder}; condor_submit submit.jdl', shell=True)
        proc.wait()

        