import ROOT
ROOT.EnableImplicitMT()
import json
#modules = ['LeptonMaker.py']
modules = ['LeptonMaker', 'LeptonSel']

with open('dataset.json') as file:
    dataset = json.load(file)

redirector = 'root://xrootd-cms.infn.it/'
files = dataset['2018']['samples']['zjj']['files']
files = list(map(lambda k: redirector + k, files))
print(files[0])
ROOT.gInterpreter.Declare(f'#include "../include/headers.hh"')
df = ROOT.RDataFrame('Events', files[0])
values = []
keepColumns = []
#exec(open(f'modules/{modules[0]}').read())

import sys
sys.path.insert(1, 'modules')
for module in modules:
    s = f'from {module} import run'
    exec(s)
    df = run(df, values, keepColumns)
#from LeptonMaker import run
#df = run(df, values, keepColumns)

def sciNot(value):
    # scientific notation
    return '{:.3e}'.format(value)
data = []
for val in values:
    if 'list' in str(type(val)):
        if str(type(val[0])) == "<class 'function'>":
            data.append(val[0](*val[1:]))
        else:
            #elif 'list' in str(type(val)):
            #print(val[1], round(val[0].GetValue(), 3))
            #print(val[1], sciNot(val[0].GetValue()))
            data.append([val[1], sciNot(val[0].GetValue())])
    else:
        #print(round(val.GetValue(), 3))
        #print(sciNot(val.GetValue()))
        data.append('', sciNot(val.GetValue()))
#print(df.Filter('nElectron>=2 || nMuon >=2').Count().GetValue())

from tabulate import tabulate
print(tabulate(data, headers=['desc.', 'value']))

