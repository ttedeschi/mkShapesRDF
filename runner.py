import ROOT
ROOT.gROOT.SetBatch(True)
import glob
from collections import OrderedDict
import os
import argparse
import sys
ROOT.gInterpreter.Declare('#include "headers.hh"')
from pathlib import Path



def runAnalysis(samples, aliases, variables, preselections, cuts, nuisances, lumi, limit=-1, outputFileMap='single'):
    #print(type(nuisances))
    #print(nuisances)

    _incr = [0]
    def mergeResults(results, resultsSingle):
        d = {}
        if len(list(results.keys())) != 0:
            for cut_cat in list(results.keys()):
                d[cut_cat] = {}
                for var in list(results[cut_cat].keys()):
                    d[cut_cat][var] = results[cut_cat][var]
                    for hname in list(d[cut_cat][var]['objects'].keys()):
                        d[cut_cat][var]['objects'][hname].Add(resultsSingle[cut_cat][var]['objects'][hname])

        else:
            for cut_cat in list(resultsSingle.keys()):
                d[cut_cat] = {}
                for var in list(resultsSingle[cut_cat].keys()):
                    d[cut_cat][var] = resultsSingle[cut_cat][var]

        return d

    def saveResults(results, sampleName):
        if type(outputFileMap) != type(''):
            print('Saving results to: ', outputFileMap(sampleName))
            f = ROOT.TFile(outputFileMap(sampleName), 'recreate')
        else:
            f = ROOT.TFile('output.root', 'recreate')
        if not 'subsamples' in list(samples[sampleName].keys()):
            _results = results[sampleName]
            for cut_cat in list(_results.keys()):
                _cut_cat = f.mkdir(cut_cat)
                for var in list(_results[cut_cat].keys()):
                    _cut_cat.mkdir(var)
                    f.cd('/' + cut_cat + '/' + var)
                    for hname in list(_results[cut_cat][var]['objects'].keys()):
                        if hname == 'nominal':
                            _results[cut_cat][var]['objects'][hname].SetName('histo_' + sampleName)
                        else:
                            _results[cut_cat][var]['objects'][hname].SetName('histo_' + sampleName + '_' + hname)
                        _results[cut_cat][var]['objects'][hname].Write()
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
                        for hname in list(_results[cut_cat][var]['objects'].keys()):
                            if hname == 'nominal':
                                _results[cut_cat][var]['objects'][hname].SetName('histo_' + sampleName + '_' + subsample)
                            else:
                                _results[cut_cat][var]['objects'][hname].SetName('histo_' + sampleName + '_' + subsample + '_' + hname)
                        _results[cut_cat][var]['objects'][hname].Write()
        f.Close()
        


    def create_cuts_vars(results, df):

        mergedCuts = {}
        for cut in list(cuts.keys()):
            __cutExpr = ''
            if type(cuts[cut]) == dict:
                __cutExpr = cuts[cut]['expr']
                for cat in list(cuts[cut]['categories'].keys()):
                    mergedCuts[cut + '_' + cat] = __cutExpr  + ' && ' + cuts[cut]['categories'][cat]
            elif type(cuts[cut]) == str:
                __cutExpr = cuts[cut]
                mergedCuts[cut] = __cutExpr

        for cut in mergedCuts.keys():
            df_cat = df.Filter(mergedCuts[cut])
            results[cut] = {}
            for var in list(variables.keys()):
                _h = df_cat.Histo1D((cut + '_' + var,'') + variables[var]['range'], var, "weight")
                results[cut][var] = {
                        'type': 'th1',
                        'object': _h
                }

        for cut in mergedCuts.keys():
            for var in list(variables.keys()):
                _s = results[cut][var]['object']
                _s_var = ROOT.RDF.Experimental.VariationsFor(_s)
                results[cut][var]['object'] = _s_var


                        

        for cut in mergedCuts.keys():
            for var in list(variables.keys()):
                    _s_var = results[cut][var]['object']
                    _histos = {}
                    for _variation in list(map(lambda k: str(k) , _s_var.GetKeys())):
                        _h_name = _variation.replace(':', '_')
                        _h = 0
                        _h = _s_var[_variation] 
                        fold = variables[var].get('fold', -1)
                        if fold == 1 or fold == 3 :
                            _h.SetBinContent(1, _h.GetBinContent(0) + _h.GetBinContent(1))
                            _h.SetBinContent(0, 0)
                        if fold == 2 or fold == 3 :
                            lastBin = _h.GetNbinsX()
                            _h.SetBinContent(lastBin-1, _h.GetBinContent(lastBin-1) + _h.GetBinContent(lastBin))
                            _h.SetBinContent(lastBin-1, 0)
                        _histos[_h_name] = _h.Clone()
                        del _h
                    del  results[cut][var]['object']
                    results[cut][var]['objects'] = _histos


    """
    def nanoGetSampleFiles(path, name):
        _files = glob.glob(path + f"/nanoLatino_{name}__part*.root")
        if limitFiles != -1 and len(_files) > limitFiles:
            return [(name, _files[:limitFiles])]
        else:
            return  [(name, _files)]
    """
    
    def varyWeight(df, name, down, up):
        # in Latinos XSWeight will be weight
        expression = 'ROOT::RVecF{'+ f'static_cast<float>(weight*{str(down)}), static_cast<float>(weight*{str(up)})' +'}'
        return df.Vary('weight', 
                expression, 
                ['down', 'up'], name)
        
    def getTTreeNomAndFriends(fnom, friends):
        tnom = ROOT.TChain('Events')
        for f in fnom:
            tnom.Add(f)
        for friend in friends:
            _tfriend = ROOT.TChain('Events')
            for f in friend:
                _tfriend.Add(f)
            tnom.AddFriend(_tfriend)
        return tnom

    def varyExpression(nameDown, nameUp, _type):
        _typeString = ''
        if _type == 'float':
            _typeString = 'F'
        elif _type == 'double':
            _typeString = 'D'
        elif _type == 'int':
            _typeString = 'I'
        elif _type == 'bool':
            _typeString = 'B'
        else:
            _typeString = '<' + _type + '>'
        return f'ROOT::RVec{_typeString}' + '{' + f'{nameDown}, {nameUp}' + '}'

    def getNuisanceFiles(nuisance, files):
        _files = list(map(lambda k: k.split('/')[-1], files))
        nuisanceFilesDown = list(map(lambda k: nuisance['folderDown'] + '/' + k, _files))
        nuisanceFilesUp = list(map(lambda k: nuisance['folderUp'] + '/' + k, _files))
        return [nuisanceFilesDown, nuisanceFilesUp]
        #return [nanoGetSampleFiles(nuisance['folderDown'], sampleName)[0][1], nanoGetSampleFiles(nuisance['folderUp'], sampleName)[0][1]]

    def loadSystematics(df, nuisances, sampleName, columnNames):
        for nuisanceName, nuisance in list(nuisances.items()):
            if sampleName not in nuisance.get('samples', {sampleName:[]}):
                continue
            if nuisance.get('type', '') == 'shape':
                if nuisance.get('kind', '') == 'suffix':
                    variation = nuisance['mapDown']
                    variedCols = list(filter(lambda k: k.endswith(variation), columnNames))
                    if len(variedCols) == 0:
                        print(f'No varied columns for {variation}')
                        sys.exit()
                    baseCols = list(map(lambda k: '_'.join(k.split('.')[-1].split('_')[:-(1 + variation.count('_'))]), variedCols ))
                    for baseCol in baseCols:
                        if 'bool' not in str(df.GetColumnType(baseCol)).lower() :
                            varNameDown = baseCol + '_' + nuisance['mapDown'] + '*' + nuisance['samples'][sampleName][1]
                            varNameUp   = baseCol + '_' + nuisance['mapUp'] + '*' + nuisance['samples'][sampleName][0]
                        else:
                            varNameDown = baseCol + '_' + nuisance['mapDown']
                            varNameUp   = baseCol + '_' + nuisance['mapUp']

                        #_type = ''
#                        if   df.GetColumnType(baseCol) == 'ROOT::VecOps::RVec<Float_t>':
#                            expr = varyExpression(baseCol + '_' + nuisance['mapDown'],baseCol + '_' + nuisance['mapUp'], 'ROOT::VecOps::RVec<Float_t>')
#                        elif df.GetColumnType(baseCol) == 'ROOT::VecOps::RVec<Int_t>':
#                            expr = varyExpression(baseCol + '_' + nuisance['mapDown'],baseCol + '_' + nuisance['mapUp'], 'ROOT::VecOps::RVec<Int_t>')
#                        elif df.GetColumnType(baseCol) == 'Float_t':
#                            expr = varyExpression(baseCol + '_' + nuisance['mapDown'],baseCol + '_' + nuisance['mapUp'], 'Float_t')
#                        else:
#                            expr = varyExpression(baseCol + '_' + nuisance['mapDown'],baseCol + '_' + nuisance['mapUp'], df.GetColumnType(baseCol))
#                            #print('Not known type for variation of nominal column ', baseCol)
#                            #sys.exit()
                        _type = df.GetColumnType(baseCol)
                        expr = varyExpression(varNameDown, varNameUp , _type)
                        df = df.Vary(baseCol, expr, variationTags=["down", "up"], variationName=nuisance['name'])

                elif nuisance.get('kind', '') == 'weight':
                    weights = nuisance['samples'].get(sampleName, None)
                    if  weights != None:
                        variedNames = []
                        if weights[0] not in columnNames:
                            df = df.Define(nuisance['name']+'_up', weights[0]) 
                            variedNames.append(nuisance['name'] + '_up')
                        else:
                            variedNames.append(weights[0])

                        if weights[1] not in columnNames:
                            df = df.Define(nuisance['name']+'_down', weights[1]) 
                            variedNames.append(nuisance['name'] + '_down')
                        else:
                            variedNames.append(weights[1])
                            
                        expr =  f'ROOT::RVecD' + '{(double)' + f'{variedNames[1]},(double) {variedNames[0]}' + '}'
                        df = df.Vary('weight', expr, variationTags=["down", "up"], variationName=nuisance['name'])
                else:
                    print("Unsupported nuisance")
                    sys.exit()

        return df



    def analyse(samples, sampleName, filesType):
        files = list(map(lambda k: k[1], filesType))
        files =  [el for sublist in files for el in sublist]

        print(sampleName)
        friendsFiles = []
        for nuisance in nuisances.values():
            if sampleName not in nuisance.get('samples', {sampleName:[]}):
                continue
            if nuisance.get('type', '') == 'shape':
                if nuisance.get('kind', '') == 'suffix':
                    #friendsFiles += getNuisanceFiles(nuisance, sampleName)
                    friendsFiles += getNuisanceFiles(nuisance, files)

        tnom = getTTreeNomAndFriends(files, friendsFiles)
                    

        #print(files, len(files))

        #df = ROOT.RDataFrame("Events", files)

        if limit != -1:
            df = ROOT.RDataFrame(tnom)
            df = df.Range(limit)
        else:
            ROOT.EnableImplicitMT()
            df = ROOT.RDataFrame(tnom)


        columnNames = list(map(lambda k: str(k), df.GetColumnNames()))

        if 'isData' not in list(samples[sampleName].keys()):
            aliases['weight'] = {
                        #'expr': '(float) ' + samples[sampleName]['weight'] + ' * ' + str(lumi) + ' * ' + filesType[0][2] + ''
                        'expr': samples[sampleName]['weight'] + ' * ' + str(lumi) + ' * ' + filesType[0][2]
                        }
        else:
            aliases['weight'] = {
                        'expr': samples[sampleName]['weight'] + ' * ' + filesType[0][2]
                        }

        print('\n\n', sampleName, '\n\n', aliases['weight'])

        define_string = "df"
        for alias in list(aliases.keys()):
            if 'samples' in list(aliases[alias]):
                if not sampleName in aliases[alias]['samples']:
                    continue
            #print('Defining alias for sample ', sampleName, alias, aliases[alias])
            if alias in columnNames:
                print(f'Alias {alias} cannot be defined, column with that name already exists')
                sys.exit()

            for line in aliases[alias].get('linesToAdd', []):
                if line.startswith('.L'):
                    ls = line.split(' ')
                    if len(ls)!= 2:
                        print('Don\'t know hot to read line', line, 'from alias ', alias)
                        sys.exit()
                    ROOT.gInterpreter.Declare(f'#include "{ls[1]}"')
                else:
                    print('Only ".L" in linesToAdd is supported')
                    sys.exit()

            if 'expr' in list(aliases[alias].keys()):
                define_string += f".Define('{alias}', '{aliases[alias]['expr']}') \\\n\t"
            elif 'class' in list(aliases[alias].keys()):
                define_string += f".Define('{alias}', '{aliases[alias]['class']} ( {aliases[alias].get('args', '')}  )') \\\n\t"
            else:
                print('Only aliases with expr or class are supported')
                sys.exit()
        #print(define_string)

        df1 = eval(define_string)

        print('\n\nLoaded all aliases\n\n')



        columnNames = list(map(lambda k: str(k), df1.GetColumnNames()))

        df2 = loadSystematics(df1, nuisances, sampleName, columnNames)

        df2 = df2.Filter(preselections)

        results = {}
        
        for var in list(variables.keys()):
            #if variables[var]['name'] != '1':
            if var in columnNames:
                _var = '__' + var
                variables[_var] = variables[var]
                del variables[var]


        print(variables)
        for var in list(variables.keys()):
            if variables[var]['name'] not in columnNames:
                df2 = df2.Define(var, variables[var]['name'])
            elif var not in columnNames:
                df2 = df2.Alias(var, variables[var]['name'])
            else:
                print("Error, cannot define variable")
                sys.exit()
            """
            elif var not in columnNames:
                df2 = df2.Alias(var, variables[var]['name'])
            else:
            """


        if 'subsamples' in list(samples[sampleName].keys()):
            for subsample in list(samples[sampleName]['subsamples'].keys()):
                __results = {}
                df3 = df2.Filter(samples[sampleName]['subsamples'][subsample])
                create_cuts_vars(__results, df3)
                results[sampleName + '_' + subsample] = __results
        else:
            create_cuts_vars(results, df2)


        return results


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
        #print(results)
        saveResults(results, sampleName)
    #print(results)

if __name__ == '__main__':
    exec(open('script.py').read())
    runAnalysis(samples, aliases, variables, preselections, cuts, nuisances, lumi)
