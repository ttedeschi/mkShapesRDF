import sys
from pathlib import Path
import argparse
import os
from collections import OrderedDict
import glob
import textwrap
import tabulate
import ROOT
ROOT.gROOT.SetBatch(True)
# ROOT.EnableImplicitMT()
import inspect
#print(os.getcwd())
#print(os.path.realpath(os.path.dirname(__file__)))
runnerPath = os.path.realpath(os.path.dirname(__file__)) + '/runner.py'
headersPath = os.path.dirname(os.path.dirname(runnerPath)) + '/include/headers.hh'
print('runner path:', runnerPath, 'headersPath', headersPath)
ROOT.gInterpreter.Declare(f'#include "{headersPath}"')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputFile", help="Path to input file",
                        required=True)
    parser.add_argument("-f", "--folder", help="Path to folder",
                        required=True) 

    args = parser.parse_args()
    folder = args.folder
    print(os.getcwd())
    print(os.path.abspath(f'{folder}/configuration.py'))
    if not os.path.exists(folder) or not os.path.exists(f'{folder}/configuration.py'):
        print("Error, configuration folder does not exists!")
        sys.exit()

    exec(open(f'{folder}/configuration.py').read(), globals(), globals())
    global batchFolder
    global outputFolder
    batchFolder = f'{folder}/{batchFolder}'
    outputFolder = f'{outputFolder}'
    print(folder)
    print(batchFolder)
    print(outputFolder)
    
    inputFile = os.path.abspath(args.inputFile)
    if not os.path.exists(f'{inputFile}'):
        print('Input file does not exist', inputFile)
        sys.exit()


    #limitFiles = int(args.limitFiles)
    limitFiles = -1
    #print(folder)
    exec(open(f'{folder}/{samplesFile}').read(),globals(), globals() )
    #print(folder)

    exec(open(f'{folder}/{aliasesFile}').read(),globals(), globals() )
    exec(open(f'{folder}/{variablesFile}').read(), None, globals())
    exec(open(f'{folder}/{cutsFile}').read(), None, globals())

    exec(open(f'{folder}/{nuisancesFile}').read(), None, globals())
#    if 'nuisancesFile' in dir():
#        exec(open(f'{folder}/{nuisancesFile}').read(), None, globals())
#    else:
#        nuisances = {}

    exec(open(f'{folder}/{structureFile}').read(), None, globals())


    # PROCESSING

    _results = {}

    # merge cuts
    mergedCuts = [] 
    for cut in list(cuts.keys()):
        __cutExpr = ''
        if type(cuts[cut]) == dict:
            __cutExpr = cuts[cut]['expr']
            for cat in list(cuts[cut]['categories'].keys()):
                mergedCuts.append(cut + '_' + cat)
        elif type(cuts[cut]) == str:
            mergedCuts.append(cut)

    print(mergedCuts)

    # Since sample may be splitted into subsamples need to create samples as sampleName + subsampleName -> store them in mergedSamples
    # originalSamples is a dict where the keys are the elements of mergedSamples, values are the original cuts
    originalSamples = {} 
    mergedSamples = []
    for sampleName in samples.keys():
        subsamples = samples[sampleName].get('subsamples', [])
        if len(subsamples) != 0:
            for subsample in subsamples:
                mergedSamples.append(sampleName + '_' + subsample)
                originalSamples[sampleName + '_' + subsample] = sampleName
        else:
            mergedSamples.append(sampleName)
            originalSamples[sampleName] = sampleName
    print(mergedSamples)

    f = ROOT.TFile(inputFile)
#    cut = mergedCuts[0]
#    variable = list(variables.keys())[0]

    for cut in mergedCuts:
        for variable in variables.keys():

            datacard = '''
            ## Shape input card
            imax 1 number of channels
            jmax * number of background
            kmax * number of nuisance parameters
            '''
            datacard = str(textwrap.dedent(datacard[1:]))
            datacard += '-' * 80 + '\n'
            table = []
            table.append(['bin', cut])
            table.append(['observation', str(int(f.Get('/' + cut + '/' + variable + '/histo_DATA').Integral()))])

            table.append(['shapes', '*', '*', f'shapes/histos_{cut}.root', 'histo_$PROCESS', 'histo_$PROCESS_$SYSTEMATIC'])
            table.append(['shapes', 'data_obs', '*', f'shapes/histos_{cut}.root', 'histo_Data'])

            tabulated = tabulate.tabulate(table).split('\n')[1:-1]

            datacard += '\n'.join(tabulated) + '\n'


            table = []





            
            #print(cut, variable, mergedSamples)
            sortedSamples = []
            for sample in mergedSamples:
                if not sample in structure.keys():
                    print(f'Sample {sample} not included in structure file')
                    sys.exit()
                if not 'isSignal' in structure[sample].keys() or not 'isData' in structure[sample].keys(): 
                    print(f'Structure for sample {sample} does not contain isData or isSignal keys')
                    sys.exit()
                if structure[sample]['isData'] != 0:
                    continue
                if structure[sample]['isSignal'] != 0: 
                    sortedSamples.insert(0, sample)
                else:
                    sortedSamples.append(sample)

            #print(sortedSamples)


            rates = []
            for sample in sortedSamples:
                rate = str(round(float(f.Get('/' + cut + '/' + variable + '/histo_' + sample).Integral()), 4))
                rates.append(rate)

            table.append(['bin', '','',  '']     + ([cut for _ in range(len(sortedSamples))]))
            table.append(['process', '','',  ''] + (sortedSamples))
            table.append(['process', '','',  ''] + ([str(i) for i in range(len(sortedSamples))]))
            table.append(['rate', '', '', '']    + (rates))



            #datacard += '-' * 80 + '\n'
            #print(nuisances)

            for nuisance in nuisances.keys():
                # FIXME need to treat also asLnN and asShape?
                if not cut in nuisances[nuisance].get('cuts', mergedCuts):
                    continue
                if nuisances[nuisance]['type'] == 'rateParam':
                    samplesNuisance = list(list(nuisances[nuisance]['samples'].items())[0])
                    if len(samplesNuisance) != 2:
                        print('rateParam', nuisance, 'must have only 1 sampleName and 1 value', samplesNuisance)
                        sys.exit()
                    values = [nuisances[nuisance]['name'], 'rateParam', cut] + samplesNuisance
                elif nuisances[nuisance]['type'] == 'auto':
                    values = [cut, 'autoMCStats', nuisances[nuisance]['maxPoiss'], nuisances[nuisance]['includeSignal']] 
                else:
                    if nuisances[nuisance].get('name', '') == '':
                        print(nuisance, nuisances[nuisance])
                        sys.exit(0)
                    values = [nuisances[nuisance]['name'], '','',  nuisances[nuisance]['type']]
                    if 'samples' in nuisances[nuisance].keys():
                        for sample in mergedSamples:
                            # check that the mergedSample or the originalSample is inside the samples of this nuisance
                            value = nuisances[nuisance]['samples'].get(sample, nuisances[nuisance]['samples'].get(originalSamples[sample], None))
                            if value != None:
                                values.append(str(value))
                            else:
                                values.append('-')
                table.append(values)

                #datacard += nuisance + '\n' 

            tabulated = tabulate.tabulate(table).split('\n')[1:-1]
            for i in range(len(tabulated)):
                if tabulated[i].startswith('rate'):
                    tabulated.insert(i+1, '-'*80)
                    break


            datacard += '\n'.join(tabulated)
            datacard += '\n' + '-' * 80 + '\n'

            cardFolder = os.path.abspath(f'{folder}/datacards/{cut}/{variable}')
            shapesFolder = cardFolder + '/shapes'
            Path(cardFolder).mkdir(parents=True, exist_ok=True)
            Path(shapesFolder).mkdir(parents=True, exist_ok=True)

            with open(cardFolder + '/datacard.txt', 'w') as file:
                file.write(datacard)

            
            f2 = ROOT.TFile(shapesFolder + f'/histos_{cut}.root', 'recreate')
            #print([k.GetName() for k in f.GetDirectory('/' + cut + '/' + variable).GetListOfKeys()])
            for sample in mergedSamples:
                _h = f.Get('/' + cut + '/' + variable + '/histo_' + sample)
                h = _h.Clone()
                integral = h.Integral() # this is just a check that h is actually a TH1
                if structure[sample]['isData'] != 0: 
                    h.SetName('histo_Data')
                f2.cd()
                h.Write()
            f2.Close()

            


