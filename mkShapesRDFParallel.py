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
import subprocess



def createBatch(samples, sampleName, filesType, i):
    # 1. create submission folder
    # 2. create executable python file
    # 3. create bash file
    # 4. create condor file
    # 5. append condor file to submit files
    
    # submission folder
    Path(f'{batchFolder}/{sampleName}_{str(i)}').mkdir(parents=True, exist_ok=True)
    folders.append(f'{sampleName}_{str(i)}')
    # python file
    
    txtpy = 'from collections import OrderedDict\n'
    #print(''.join(['#' for _ in range(50)]))
    _samples = {}
    _samples[sampleName] = {
            'name': [(sampleName, filesType[1])],
            'weight': filesType[0],
            }
    if 'subsamples' in list(samples[sampleName].keys()):
        _samples[sampleName]['subsamples'] = samples[sampleName]['subsamples']
    if 'isData' in list(samples[sampleName].keys()):
        _samples[sampleName]['isData'] = samples[sampleName]['isData']



    txtpy += f'samples = {str(_samples)}\n'
    txtpy += f'aliases = {str(aliases)}\n'
    txtpy += f'variables = {str(variables)}\n'
    txtpy += f'cuts = {str(cuts)}\n'
    txtpy += f'preselections = \'{preselections}\' \n'
    txtpy += f'lumi = {lumi} \n'
    with open(f'{batchFolder}/{sampleName}_{str(i)}/script.py', 'w') as f:
        f.write(txtpy)
    
def submit():

    txtsh  = '#!/bin/bash\n'
    txtsh += 'source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh\n'
    txtsh += 'python runner.py\n'
    with open(f'{batchFolder}/run.sh', 'w') as file:
        file.write(txtsh)
    process = subprocess.Popen(f'chmod +x {batchFolder}/run.sh', shell=True)
    process.wait()
        
     
    txtjdl  =  'universe = vanilla \n'
    txtjdl +=  'executable = run.sh\n'
    #txtjdl += 'arguments = $(Folder)\n'
    txtjdl += f'transfer_input_files = $(Folder)/script.py, {os.getcwd()}/headers.hh, {os.getcwd()}/runner.py\n'

    txtjdl += 'output = $(Folder)/out.txt\n'
    txtjdl += 'error  = $(Folder)/err.txt\n'
    txtjdl += 'log    = $(Folder)/log.txt\n'
    #txtjdl += 'transfer_input_files = $(File)\n'
    txtjdl += 'should_transfer_files = yes\n'
    txtjdl += f'transfer_output_remaps = "output.root = {os.getcwd()}/{folder}/{outputFolder}/mkShapes__{tag}__ALL__$(Folder).root"\n'
    txtjdl += 'when_to_transfer_output = ON_EXIT\n'
    txtjdl += 'request_cpus   = 1\n'
    txtjdl += '+JobFlavour = "workday"\n'


    txtjdl += f'queue 1 Folder in {", ".join(folders)}\n'
    with open(f'{batchFolder}/submit.jdl', 'w') as file:
        file.write(txtjdl)

    process = subprocess.Popen(f'cd {batchFolder}; condor_submit submit.jdl; cd -', shell=True)
    process.wait()
    
    
    
parser = argparse.ArgumentParser()
parser.add_argument("-o","--operationMode", help="0 do analysis in batch, 1 hadd root files, 2 plot" , required=True, default='-1')
#parser.add_argument("-a","--doAn", help="Do analysis" , required=False, default=False)
#parser.add_argument("-p","--doP", help="Do plots" , required=False, default=False)
parser.add_argument("-f","--folder", help="Path to folder" , required=False, default='plotsconfig')
parser.add_argument("-l","--limitFiles", help="Max number of files" , required=False, default='-1')

args = parser.parse_args()
folder     = args.folder
operationMode = int(args.operationMode)

exec(open(f'{folder}/configuration.py').read())

batchFolder  = f'{folder}/{batchFolder}'
outputFolder = f'{outputFolder}'
Path(f'{folder}/{outputFolder}').mkdir(parents=True, exist_ok=True)

if operationMode == 0 and not os.path.exists(f'{folder}/{outputFolder}'):
    print('You didn\'t create outputFolder ', outputFolder)
    sys.exit()

if operationMode == 1 and os.path.exists(f'{folder}/{outputFolder}/{outputFile}'):
    print('Can\'t merge files, output already exists')
    print(f'You can run: rm {folder}/{outputFolder}/{outputFile}')
    sys.exit()

limitFiles = int(args.limitFiles)
exec(open(f'{folder}/{samplesFile}').read())

exec(open(f'{folder}/{aliasesFile}').read())
exec(open(f'{folder}/{variablesFile}').read())
exec(open(f'{folder}/{cutsFile}').read())
exec(open(f'{folder}/{plotFile}').read())


#print(samf'{folder}



# PROCESSING

"""
results will be like:
{
    "top": {
        "sr_ee": {
            "met": {
                "type": "th1", 
                "object": 0x00f1,
            },
        }
    },
    "dy": {
        "sr_ee": {
            "met": {
                "type": "th1"
                "object": 0x0ff20
            }
        }
    }
}
dict of dict of dict
"""


folders = []
_results = {}

if operationMode == 0:
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

        i = 0
        for _type in list(types.keys()):
            __files = list(map(lambda k: k[1], types[_type]))
            __files = [item for sublist in __files for item in sublist] # flatted list of files
            dim = 1
            if 'FilesPerJob' in list(samples[sampleName].keys()):
                dim = samples[sampleName]['FilesPerJob']
            else:
                dim = len(__files)

            __files = [__files[j: j+dim] for j in range(0, len(__files), dim)]

            for ___files in __files:
                sampleType = [types[_type][0][2], ___files]
                sampleType[0] = '( ' + samples[sampleName]['weight'] + ' ) * ( ' + sampleType[0] + ' )'
                createBatch(samples, sampleName, sampleType, i) 
                i+=1

    submit()

elif operationMode == 1:
    print('',''.join(['#' for _ in range(20)]), '\n\n', 'Merging root files', '\n\n', ''.join(['#' for _ in range(20)]))
    #results = {}
    filesToMerge = []
    for sampleName in list(samples.keys()):
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
                print("Error", sampleName, filesType)
                print("Either the sample proc you specified has no files, or the weight had problems")
                sys.exit()

        i = 0
        for _type in list(types.keys()):
            __files = list(map(lambda k: k[1], types[_type]))
            __files = [item for sublist in __files for item in sublist] # flatted list of files
            dim = 1
            if 'FilesPerJob' in list(samples[sampleName].keys()):
                dim = samples[sampleName]['FilesPerJob']
            else:
                dim = len(__files)

            __files = [__files[j: j+dim] for j in range(0, len(__files), dim)]

            for ___files in __files:
                f = f'{folder}/{outputFolder}/mkShapes__{tag}__ALL__{sampleName}_{str(i)}.root'
                if not os.path.exists(f):
                    print("Error missing file ", f, sampleName, _type)
                    sys.exit()
                filesToMerge.append(f)
                i+=1
    print(f'Hadding files into {folder}/{outputFolder}/{outputFile}')
    process = subprocess.Popen(f'hadd {folder}/{outputFolder}/{outputFile} {" ".join(filesToMerge)}', shell=True)
    process.wait()
        



elif operationMode == 2:
    print('',''.join(['#' for _ in range(20)]), '\n\n', 'Doing plots', '\n\n', ''.join(['#' for _ in range(20)]))
    f = ROOT.TFile(f'{folder}/{outputFolder}/{outputFile}', "read")
    for cut_cat in [k.GetName() for k in f.GetDirectory('/').GetListOfKeys()]:
        _results[cut_cat] = {}
        #f.cd(cut_cat)
        for var in [k.GetName() for k in f.GetDirectory('/' + cut_cat).GetListOfKeys()]:
            _results[cut_cat][var] = {}
            #f.cd('/' + cut_cat + '/' + var)
            #_var.cd()
            #for sampleName in [k.GetName() for k in f.GetDirectory('/' + cut_cat + '/' + var).GetListOfKeys()]:
            for sampleName in list(groupPlot.keys()):
                h = 0
                if groupPlot[sampleName].get('isData', False):
                    h = f.Get('/' + cut_cat + '/' + var + '/histo_' + sampleName)
                else:
                    if len(groupPlot[sampleName]['samples']) > 1:
                        for subSample in  groupPlot[sampleName]['samples']:
                            hname = 'histo_' + subSample
                            if hname in [k.GetName() for k in f.GetDirectory('/' + cut_cat + '/' + var).GetListOfKeys()]:
                                if h != 0:
                                    _h = f.Get('/' + cut_cat + '/' + var + '/histo_' + subSample)
                                    h.Add(_h)
                                else:
                                    h = f.Get('/' + cut_cat + '/' + var + '/histo_' + subSample)
                            else:
                                print('Missing histo', cut_cat, var, subSample)
                                sys.exit()
                    else:
                        h = f.Get('/' + cut_cat + '/' + var + '/histo_' + groupPlot[sampleName]['samples'][0])

                _results[cut_cat][var][sampleName] = {
                        'object': h,
                        'isData': groupPlot[sampleName].get('isData', 0)==1,
                        'isSignal': groupPlot[sampleName].get('isSignal', 0)==1
                }
    #print(_results)

    histPlots = {}

    for cut_cat in list(_results.keys()):
        sampleNamesSorted = list(filter(lambda k: not k[1]['isSignal'] and not k[1]['isData'],  _results[cut_cat]['events'].items() ))
        #sampleNamesSorted = list(sorted(_results[cut_cat]['events'].items(), key=lambda k:k[1]['object'].GetBinContent(1) ))
        sampleNamesSorted = list(sorted(sampleNamesSorted, key=lambda k:k[1]['object'].GetBinContent(1) ))
        sampleNamesSorted = list(map(lambda k: k[0], sampleNamesSorted))
        sigName = list(filter(lambda k: k[1]['isSignal'],  _results[cut_cat]['events'].items() ))
        #sigName = list(filter(_results[cut_cat]['events'].items(), key=lambda k: k[1]['isSignal']))
        if len(sigName)==0 or len(sigName)>=2:
            print("Either no signal or many signals")
        else:
            print(sigName[0])
            sampleNamesSorted.append(sigName[0][0])
        dataName = list(filter(lambda k: k[1]['isData'],  _results[cut_cat]['events'].items() ))
        #dataName = list(filter(_results[cut_cat]['events'].items(), key=lambda k: k[1]['isData']))
        #if len(dataName)>0 and len(dataName)<2:
        if len(dataName)==0 or len(dataName)>=2:
            print("Either no data or many data histograms")
        else:
            sampleNamesSorted.append(dataName[0][0])

        #print(sampleNamesSorted)

        if cut_cat not in list(histPlots.keys()):
            histPlots[cut_cat] = {}
        for var in list(_results[cut_cat].keys()):
            if var not in list(histPlots[cut_cat].keys()):
                histPlots[cut_cat][var] = {
                        'thstack': ROOT.THStack(cut_cat + '_' + var,""),
                        'data': 0,
                        'sig': 0,
                        'min': 1000,
                        'max': 0
                        }
            d = OrderedDict()
            for sampleName in sampleNamesSorted:
                #_results[cut_cat][var][sampleName] = results[sampleName][cut_cat][var]
                h = _results[cut_cat][var][sampleName]['object']
                #h.SetMarkerColor(groupPlot[sampleName]['color'])
                if _results[cut_cat][var][sampleName]['isData']:
                    print('adding data to histPlots')
                    h.SetMarkerColor(ROOT.kBlack)
                    h.SetLineColor(ROOT.kBlack)
                    histPlots[cut_cat][var]['data'] = h
                else:
                    h.SetLineColor(groupPlot[sampleName]['color'])
                    h.SetFillColorAlpha(groupPlot[sampleName]['color'], 0.6)
                    histPlots[cut_cat][var]['thstack'].Add(h)
                if _results[cut_cat][var][sampleName]['isSignal']:
                    histPlots[cut_cat][var]['sig'] = h
                d[sampleName] = _results[cut_cat][var][sampleName]
            _results[cut_cat][var] = d

            histPlots[cut_cat][var]['min'] = _results[cut_cat][var][sampleNamesSorted[0]]['object'].GetMinimum()
            histPlots[cut_cat][var]['max'] = histPlots[cut_cat][var]['thstack'].GetMaximum()



    def Pad2TAxis(hist):
             xaxis = hist.GetXaxis()
             xaxis.SetLabelFont ( 42)
             xaxis.SetLabelOffset( 0.025)
             xaxis.SetLabelSize ( 0.1)
             xaxis.SetNdivisions ( 505)
             xaxis.SetTitleFont ( 42)
             xaxis.SetTitleOffset( 1.35)   
             xaxis.SetTitleSize ( 0.11)
           
             yaxis = hist.GetYaxis()
             #yaxis.CenterTitle ( )
             yaxis.SetLabelFont ( 42)
             yaxis.SetLabelOffset( 0.02)
             yaxis.SetLabelSize ( 0.1)
             yaxis.SetNdivisions ( 505)
             yaxis.SetTitleFont ( 42)
             yaxis.SetTitleOffset( .4)
             yaxis.SetTitleSize ( 0.11)

    for cut_cat in list(histPlots.keys()):
        for var in list(histPlots[cut_cat].keys()):
            cnv = ROOT.TCanvas("c","c1", 800,800)

            cnv.cd()
            canvasPad1Name = 'pad1'
            pad1 = ROOT.TPad(canvasPad1Name,canvasPad1Name, 0.0, 1-0.72, 1.0, 1-0.05)
            pad1.SetTopMargin(0.)
            pad1.SetBottomMargin(0.020) 
            pad1.Draw()
            pad1.cd()

            _min = histPlots[cut_cat][var]['min'] * 1e-2
            _max = histPlots[cut_cat][var]['max'] * 1e+2
            #minXused = h.GetBinLowEdge(1)
            #maxXused = h.GetBinUpEdge(h.GetNbinsX())
            minXused = variables[var]['range'][1]
            maxXused = variables[var]['range'][2]

            frameDistro = pad1.DrawFrame(minXused, 0.0, maxXused, 1.0)
            frameDistro.SetTitleSize(0)

            xAxisDistro = frameDistro.GetXaxis()
            xAxisDistro.SetNdivisions(6,5,0)
            xAxisDistro.SetLabelSize(0)

            #frameDistro.GetXaxis().SetTitle(var)
            frameDistro.GetYaxis().SetTitle("Events / bin")


            frameDistro.GetYaxis().SetLabelOffset( 0.0)
            frameDistro.GetYaxis().SetLabelSize ( 0.05)
            #frameDistro.GetYaxis().SetNdivisions ( 505)
            frameDistro.GetYaxis().SetTitleFont ( 42)
            frameDistro.GetYaxis().SetTitleOffset( 0.8)
            frameDistro.GetYaxis().SetTitleSize ( 0.06)

            frameDistro.GetYaxis().SetRangeUser( max(1e-3, _min), _max)
            #frameDistro.GetYaxis().SetRangeUser(1e-3, 1e+5)
            #h.GetYaxis().SetRangeUser( min(1e-3, _min), _max)

            tlegend = ROOT.TLegend(0.20, 0.75, 0.80, 0.98)
            #tlegend.SetFillColor(0)
            tlegend.SetTextFont(42)
            tlegend.SetTextSize(0.035)
            tlegend.SetLineColor(0)
            tlegend.SetFillStyle(0)

            #tlegend.SetShadowColor(0)
            for sampleName in list(_results[cut_cat][var].keys()):
                name = groupPlot[sampleName]['nameHR'] + f' [{str(round(_results[cut_cat][var][sampleName]["object"].Integral(),1))}]'
                if _results[cut_cat][var][sampleName]['isData']:
                    tlegend.AddEntry(_results[cut_cat][var][sampleName]['object'], name, "lep")
                else:
                    tlegend.AddEntry(_results[cut_cat][var][sampleName]['object'], name, "f")

            tlegend.SetNColumns(2)

            h = histPlots[cut_cat][var]['thstack']
            h.Draw('same hist')
            hdata = 0 
            if histPlots[cut_cat][var]['data'] != 0:
                print('Data hist exists, plotting it')
                hdata = histPlots[cut_cat][var]['data']
                hdata.Draw('same p0')
            tlegend.Draw()
            pad1.RedrawAxis()
            pad1.SetLogy()


            cnv.cd()
            if hdata == 0:
                for sampleName in list(_results[cut_cat][var].keys()):
                    if hdata == 0:
                        hdata = _results[cut_cat][var][sampleName]['object'].Clone()
                    else:
                        hdata.Add(_results[cut_cat][var][sampleName]['object'].Clone())
            hmc = 0
            for sampleName in list(_results[cut_cat][var].keys()):
                if _results[cut_cat][var][sampleName]['isData'] or _results[cut_cat][var][sampleName]['isSignal']:
                    continue
                if hmc == 0:
                    hmc = _results[cut_cat][var][sampleName]['object'].Clone()
                else:
                    hmc.Add(_results[cut_cat][var][sampleName]['object'].Clone())

            h_err = hdata.Clone()
            h_err.Divide(hdata)
            rp = hdata.Clone()
            rp.Divide(hmc)
            rp.SetMarkerColor(ROOT.kBlack)



               
                

            canvasPad2Name = 'pad2'
            pad2 = ROOT.TPad(canvasPad2Name,canvasPad2Name,0.0,0,1,1-0.72)
            pad2.SetTopMargin(0.06)
            pad2.SetBottomMargin(0.292)
            pad2.Draw()
            pad2.cd()

            frameRatio = pad2.DrawFrame(minXused, 0.0, maxXused, 2.0)
            xAxisDistro = frameRatio.GetXaxis()
            xAxisDistro.SetNdivisions(6,5,0)
            frameRatio.GetYaxis().SetTitle("DATA / MC")
            frameRatio.GetYaxis().SetRangeUser( 0.0, 2 )
            frameRatio.GetXaxis().SetTitle(variables[var]['xaxis'])
            Pad2TAxis(frameRatio)

            h_err.SetFillColorAlpha(ROOT.kBlack, 0.5)
            h_err.SetFillStyle(3004)
            h_err.Draw("same e4")

            rp.Draw("same e")

            pad2.RedrawAxis()
            pad2.SetGrid()

            ROOT.gStyle.SetOptStat(0)

            outfile = cut_cat + '_' + var + '.png'
            cnv.SetLogy()

            cnv.SaveAs("{}/{}".format(path, outfile))
    f.Close()



