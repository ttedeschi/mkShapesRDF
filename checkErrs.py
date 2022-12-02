import glob
import subprocess

resubmit = 1
folder = "2016Corr/condor2_new_vbf_16_2/"
#folder = "nanoAOD_11"
proc  = "vbf_zjj_2018"
proc  = "eft_zjj_2018"
proc  = "extract_new_17"
proc  = "vbf_zjj_2016_2"
proc  = "vbf_zjj_withcorr_2018"
proc  = "vbf_zjj_2016_norew"
proc  = "extract_new_16"
proc  = "new_vbf_16"
proc  = "new_vbf_18"
proc  = "vbf_zjj_2017"
#proc  = "dnn_zjj_2016"
proc = "extract_new_17"
proc  = "new_vbf_16"
proc = "extract_dnn_17"
proc = "dnn_2017"
proc = "onlyPresel_vbf_16"
proc  = "new_vbf_16_2"
#proc  = "dnn_zjj_2016"
#proc  = "eft_zjj_ew_qcd_18"
#proc  = "vbf_zjj_2016"
#proc = "vbf_zjj_withcorr_2018"
#proc  = "eft_zjj_2018"
#proc  = "eft_zjj_2016"
#proc = "extract_new2_16"
errs = glob.glob("{}/*/*err*".format(folder))
files = glob.glob("{}/*/script.py".format(folder))
errsD = list(map(lambda k: '/'.join(k.split('/')[:-1]), errs))
filesD = list(map(lambda k: '/'.join(k.split('/')[:-1]), files))
#print(files)
notFinished = list(set(filesD).difference(set(errsD)))
print(notFinished)
print(len(files), len(errs), len(notFinished))
print('queue 1 Folder in ' + ' '.join(list(map(lambda k: k.split('/')[-1], notFinished))))
normalErrs = """Warning in <TClass::Init>: no dictionary for class edm::ProcessHistory is available
Warning in <TClass::Init>: no dictionary for class edm::ProcessConfiguration is available
Warning in <TClass::Init>: no dictionary for class edm::ParameterSetBlob is available
Warning in <TClass::Init>: no dictionary for class edm::Hash<1> is available
Warning in <TClass::Init>: no dictionary for class pair<edm::Hash<1>,edm::ParameterSetBlob> is available
"""
normalErrs = normalErrs.split('\n')
normalErrs = list(filter(lambda k: k!='', normalErrs))

toResubmit = []
def normalErrsF(k):
    for s in normalErrs:
        if s in k:
            return True
    return False

for err in errs:
    with open(err) as file:
        l = file.read()
    txt = l.split("\n")
    #txt = list(filter(lambda k: k not in normalErrs, txt))
    txt = list(filter(lambda k: not normalErrsF(k), txt))
    txt = list(filter(lambda k: k.strip() != '' , txt))
    if len(txt) > 0:
        print(err)
        print("\n")
        print("\n".join(txt))
        print("\n\n")
        toResubmit.append(err)
print(toResubmit)

"""
normalErrs = [
"Error in <TSystem::ExpandFileName>: input: $HOME/.root.mimes, output: $HOME/.root.mimes",
"Info in <ACLiC>: unmodified script has already been compiled and loaded",
"I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA"
]
"""
