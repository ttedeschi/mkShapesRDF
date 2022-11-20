import ROOT
import glob
from collections import OrderedDict
import os
import argparse
import sys
ROOT.EnableImplicitMT()
ROOT.gInterpreter.Declare('#include "headers.hh"')

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


parser = argparse.ArgumentParser()
parser.add_argument("-a","--doAn", help="Do analysis" , required=False, default=False)
parser.add_argument("-p","--doP", help="Do plots" , required=False, default=False)
parser.add_argument("-f","--folder", help="Path to folder" , required=False, default='plotsconfig')
parser.add_argument("-l","--limitFiles", help="Max number of files" , required=False, default='-1')

args = parser.parse_args()
folder     = args.folder

exec(open(f'{folder}/configuration.py').read())

limitFiles = int(args.limitFiles)
exec(open(f'{folder}/{samplesFile}').read())

exec(open(f'{folder}/{aliasesFile}').read())
exec(open(f'{folder}/{variablesFile}').read())
exec(open(f'{folder}/{cutsFile}').read())
exec(open(f'{folder}/{plotFile}').read())

doAnalysis = args.doAn
doPlot     = args.doP

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
        

_results = {}

if doAnalysis:
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
                print("Error", sampleName, filesType)
                print("Either the sample proc you specified has no files, or the weight had problems")
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



    """
    remap results sorting the samples based on yields in cut_cat:
    {
        "cut_cat": {
            "var1": OrderedDict({
                "sample1": {
                    "type": "th1"
                    "object": ""
                    }
                }),
        }
    }
    """
    for sampleName in list(results.keys()):
        for cut_cat in list(results[sampleName].keys()):
            if cut_cat not in list(_results.keys()):
                _results[cut_cat] = {}
            for var in list(results[sampleName][cut_cat].keys()):
                if var not in list(_results[cut_cat].keys()):
                    _results[cut_cat][var] = {}
                _results[cut_cat][var][sampleName] = results[sampleName][cut_cat][var]
    #print(_results)

    f = ROOT.TFile(folder + '/' + outputFile, "recreate")
    for cut_cat in list(_results.keys()):
        _cut_cat = f.mkdir(cut_cat)
        f.cd(cut_cat)
        #_cut_cat.cd()
        for var in list(_results[cut_cat].keys()):
            _var = _cut_cat.mkdir(var)
            f.cd('/' + cut_cat + '/' + var)
            #_var.cd()
            for sampleName in list(_results[cut_cat][var].keys()):
                h = _results[cut_cat][var][sampleName]['object'].Clone()
                h.SetName('histo_' + sampleName)
                h.Write()
    f.Write()
    f.Close()



if doPlot:
    print('',''.join(['#' for _ in range(20)]), '\n\n', 'Doing plots', '\n\n', ''.join(['#' for _ in range(20)]))
    if not doAnalysis:
    
        f = ROOT.TFile(folder + '/' + outputFile, "read")
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
                    print('adding data tu histPlots')
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
    if not doAnalysis:
        f.Close()



