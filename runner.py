import ROOT
ROOT.gROOT.SetBatch(True)
import glob
from collections import OrderedDict
import os
import argparse
import sys
ROOT.EnableImplicitMT()
ROOT.gInterpreter.Declare('#include "headers.hh"')
from pathlib import Path


def create_cuts_vars(results, df):

    for cut in list(cuts.keys()):
        df1 = df.Filter(cuts[cut]['expr'])
        for cat in list(cuts[cut]['categories'].keys()):
            df_cat = df1.Filter(cuts[cut]['categories'][cat])
            results[cut + '_' + cat] = {}
            for var in list(variables.keys()):
                if variables[var]['name'] == '1':
                    results[cut + '_' + cat][var] = {
                            'type': 'num',
                            'object': df_cat.Sum('weight')
                    }
                else:
                    _h = df_cat.Histo1D((cut + '_' + cat + '_' + var,'') + variables[var]['range'], var, "weight")
                    results[cut + '_' + cat][var] = {
                            'type': 'th1',
                            'object': _h
                    }

    for cut in list(cuts.keys()):
        for cat in list(cuts[cut]['categories'].keys()):
            for var in list(variables.keys()):
                if variables[var]['name'] == '1':
                    _h = ROOT.TH1D(cut + '_' + cat + '_' + var + str(_incr[0]), var, *variables[var]['range'])
                    _incr[0] += 1
                    _h.Fill(1, results[cut + '_' + cat][var]['object'].GetValue())
                    #_h.SetBinContent(1, results[cut + '_' + cat][var]['object'].GetValue())
                    results[cut + '_' + cat][var]['object'] = _h
                else:
                    results[cut + '_' + cat][var]['object'] = results[cut + '_' + cat][var]['object'].GetValue()


def analyse(samples, sampleName, filesType):
    files = []

    _files = list(map(lambda k: k[1], filesType))
    for f in _files:
        files += f
    
    #print(files, len(files))

    df = ROOT.RDataFrame("Events", files)

    df1 = df.Filter(preselections)

    if 'isData' not in list(samples[sampleName].keys()):
        aliases['weight'] = {
                    'expr': samples[sampleName]['weight'] + ' * ' + str(lumi) + ' * ' + filesType[0][2]
                    }
    else:
        aliases['weight'] = {
                    'expr': samples[sampleName]['weight'] + ' * ' + filesType[0][2]
                    }

    print('\n\n', sampleName, '\n\n', aliases['weight'])

    define_string = "df1"
    for alias in list(aliases.keys()):
        if 'samples' in list(aliases[alias]):
            if not sampleName in aliases[alias]['samples']:
                continue
        #print('Defining alias for sample ', sampleName, alias, aliases[alias])
        define_string += f".Define('{alias}', '{aliases[alias]['expr']}') \\\n\t"
    #print(define_string)

    df2 = eval(define_string)
    results = {}
    
    for var in list(variables.keys()):
        if variables[var]['name'] != '1':
            df2 = df2.Define(var, variables[var]['name'])
    if 'subsamples' in list(samples[sampleName].keys()):
        for subsample in list(samples[sampleName]['subsamples'].keys()):
            __results = {}
            df3 = df2.Filter(samples[sampleName]['subsamples'][subsample])
            create_cuts_vars(__results, df3)
            results[sampleName + '_' + subsample] = __results
    else:
        create_cuts_vars(results, df2)


   
    #print(results)
    return results

_incr = [0]

exec(open('script.py').read())


def mergeResults(results, resultsSingle):
    d = {}
    if len(list(results.keys())) != 0:
        for cut_cat in list(results.keys()):
            d[cut_cat] = {}
            for var in list(results[cut_cat].keys()):
                d[cut_cat][var] = results[cut_cat][var]
                d[cut_cat][var]['object'].Add(resultsSingle[cut_cat][var]['object'])

    else:
        for cut_cat in list(resultsSingle.keys()):
            d[cut_cat] = {}
            for var in list(resultsSingle[cut_cat].keys()):
                d[cut_cat][var] = resultsSingle[cut_cat][var]

    return d
        
def saveResults(results, sampleName):
    f = ROOT.TFile(f'output.root', 'recreate')
    if not 'subsamples' in list(samples[sampleName].keys()):
        _results = results[sampleName]
        for cut_cat in list(_results.keys()):
            _cut_cat = f.mkdir(cut_cat)
            for var in list(_results[cut_cat].keys()):
                _cut_cat.mkdir(var)
                f.cd('/' + cut_cat + '/' + var)
                _results[cut_cat][var]['object'].SetName('histo_'+sampleName)
                _results[cut_cat][var]['object'].Write()
    else:
        for subsample in list(samples[sampleName]['subsamples'].keys()):
            _results = results[sampleName + '_' + subsample]
            for cut_cat in list(_results.keys()):
                if list(samples[sampleName]['subsamples'].keys()).index(subsample) == 0:
                    f.cd('/')
                    ROOT.gDirectory.mkdir(cut_cat)

                for var in list(_results[cut_cat].keys()):
                    if list(samples[sampleName]['subsamples'].keys()).index(subsample) == 0:
                        f.cd('/' + cut_cat)
                        ROOT.gDirectory.mkdir(var)
                    f.cd('/' + cut_cat + '/' + var)
                    _results[cut_cat][var]['object'].SetName('histo_'+sampleName+'_'+subsample)
                    _results[cut_cat][var]['object'].Write()
    f.Close()


_results = {}

print('',''.join(['#' for _ in range(20)]), '\n\n', '   Doing analysis', '\n\n', ''.join(['#' for _ in range(20)]))
results = {}
for sampleName in list(samples.keys()):
    __results = {}
    types = {}
    for filesType in samples[sampleName]['name']:
        if len(filesType) == 2 and len(filesType[1])>0:
            if '1' not in list(types.keys()):
                types['1'] = []
            types['1'].append(filesType + ('1',))
        elif len(filesType) == 3 and len(filesType[1])>0:
            if filesType[2] not in list(types.keys()):
                types[filesType[2]] = []
            types[filesType[2]].append(filesType)
        else:
            print("Error", sampleName, filesType, file=sys.stderr)
            print("Either the sample proc you specified has no files, or the weight had problems", file=sys.stderr)
            sys.exit()

    for _type in list(types.keys()):
        _resultsSpecial = analyse(samples, sampleName, types[_type])
        
        if not 'subsamples' in list(samples[sampleName].keys()):
            __results = mergeResults(__results, _resultsSpecial)
        else:
            for subsample in list(_resultsSpecial.keys()):
                if not subsample in list(__results.keys()):
                    __results[subsample] = {}
                __results[subsample] = mergeResults(__results[subsample], _resultsSpecial[subsample])

    if not 'subsamples' in list(samples[sampleName].keys()):
        results[sampleName] = __results
    else:
        for subsample in list(__results.keys()):
            results[subsample] = __results[subsample]
    print(results)
    saveResults(results, sampleName)
print(results)
