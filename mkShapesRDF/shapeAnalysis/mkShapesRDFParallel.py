import sys
from pathlib import Path
import argparse
import os
from collections import OrderedDict
import glob
import subprocess
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
    parser.add_argument("-o", "--operationMode",
                        help="0 do analysis in batch, 1 hadd root files, 2 plot", required=True)
    parser.add_argument(
        "-b", "--doBatch", help="0 (default) runs on local, 1 runs with condor", required=False, default='0')

    parser.add_argument(
        "-dR", "--dryRun", help="1 do not submit to condor", required=False, default='0')

    parser.add_argument("-f", "--folder", help="Path to folder",
                        required=False, default='plotsconfig')

    parser.add_argument("-l", "--limitEvents",
                        help="Max number of events", required=False, default='-1')

    parser.add_argument("-r", "--resubmit",
                        help="Resubmit jobs", required=False, default='0')

    parser.add_argument("-lin", "--linPlots",
                        help="Create lin scaled plots", required=False, default='0')
    parser.add_argument("-log", "--logPlots",
                        help="Create log scaled plots", required=False, default='1')

    parser.add_argument("-pdf", "--savePdf",
                        help="Save pdf of plots", required=False, default='-1')

    args = parser.parse_args()
    
    resubmit = int(args.resubmit)
    savePdf = int(args.savePdf)
    linPlots = int(args.linPlots)
    logPlots = int(args.logPlots)

    folder = args.folder
    print(os.getcwd())
    print(os.path.abspath(f'{folder}/configuration.py'))
    if not os.path.exists(folder) or not os.path.exists(f'{folder}/configuration.py'):
        print("Error, configuration folder does not exists!")
        sys.exit()
    operationMode = int(args.operationMode)
    doBatch = int(args.doBatch)
    dryRun = int(args.dryRun)

    exec(open(f'{folder}/configuration.py').read(), globals(), globals())
    global batchFolder
    global outputFolder
    batchFolder = f'{folder}/{batchFolder}'
    outputFolder = f'{outputFolder}'
    print(folder)
    print(batchFolder)
    print(outputFolder)
    

    #FIXME one of the two following line should be removed
    Path(f'{folder}/{outputFolder}').mkdir(parents=True, exist_ok=True)

    if operationMode == 0 and not os.path.exists(f'{folder}/{outputFolder}'):
        print('You didn\'t create outputFolder ', outputFolder)
        sys.exit()

    if operationMode == 2 and os.path.exists(f'{folder}/{outputFolder}/{outputFile}'):
        print('Can\'t merge files, output already exists')
        print(f'You can run: rm {folder}/{outputFolder}/{outputFile}')
        sys.exit()

    #limitFiles = int(args.limitFiles)
    limitFiles = -1
    limit = int(args.limitEvents)
    #print(folder)
    exec(open(f'{folder}/{samplesFile}').read(),globals(), globals() )
    #print(folder)

    exec(open(f'{folder}/{aliasesFile}').read(),globals(), globals() )
    exec(open(f'{folder}/{variablesFile}').read(), None, globals())
    exec(open(f'{folder}/{cutsFile}').read(), None, globals())
    exec(open(f'{folder}/{plotFile}').read(), None, globals())
    if 'nuisancesFile' in dir():
        exec(open(f'{folder}/{nuisancesFile}').read(), None, globals())
    else:
        nuisances = {}


    # PROCESSING

    _results = {}

    if operationMode == 0:
        print('#'*20, '\n\n', '   Doing analysis', '\n\n', '#'*20)
        if doBatch == 1:

            print('#'*20, '\n\n', ' Running on condor  ', '\n\n', '#'*20)

            from mkShapesRDF.shapeAnalysis.runner import RunAnalysis
            _samples = RunAnalysis.splitSamples(samples)

            from mkShapesRDF.shapeAnalysis.BatchSubmission import BatchSubmission

            outputPath = os.path.abspath(outputFolder)
            #print('ouput path:', outputPath)

            batch = BatchSubmission(outputPath, batchFolder, headersPath, runnerPath, tag, _samples, aliases, variables, preselections, cuts, nuisances, lumi)
            batch.createBatches()
            batch.submit(dryRun)

        else:
            print('#'*20, '\n\n', ' Running on local machine  ', '\n\n', '#'*20)
            from mkShapesRDF.shapeAnalysis.runner import RunAnalysis
            outputFileMap = f'{folder}/{outputFolder}/{outputFile}'

            _samples = RunAnalysis.splitSamples(samples, False)
            print(len(_samples))

            runner = RunAnalysis(_samples, aliases, variables, preselections,
                                 cuts, nuisances, lumi, limit, outputFileMap)
            runner.run()

    elif operationMode == 1:
        #condorFolder = folder + '/' + batchFolder

        errs = glob.glob("{}/{}/*/err.txt".format(batchFolder, tag))
        files = glob.glob("{}/{}/*/script.py".format(batchFolder, tag))
        #print(files[:3], len(files))
        errsD = list(map(lambda k: '/'.join(k.split('/')[:-1]), errs))
        filesD = list(map(lambda k: '/'.join(k.split('/')[:-1]), files))
        # print(files)
        notFinished = list(set(filesD).difference(set(errsD)))
        print(notFinished)
        tabulated = []
        tabulated.append(['Total jobs', 'Finished jobs', 'Running jobs'])
        tabulated.append([len(files), len(errs), len(notFinished)])
        import tabulate
        print(tabulate.tabulate(tabulated))
        #print('queue 1 Folder in ' + ' '.join(list(map(lambda k: k.split('/')[-1], notFinished))))
        normalErrs = """Warning in <TClass::Init>: no dictionary for class edm::ProcessHistory is available
        Warning in <TClass::Init>: no dictionary for class edm::ProcessConfiguration is available
        Warning in <TClass::Init>: no dictionary for class edm::ParameterSetBlob is available
        Warning in <TClass::Init>: no dictionary for class edm::Hash<1> is available
        Warning in <TClass::Init>: no dictionary for class pair<edm::Hash<1>,edm::ParameterSetBlob> is available
        real
        user
        sys
        """
        normalErrs = normalErrs.split('\n')
        normalErrs = list(map(lambda k: k.strip(' ').strip('\t'), normalErrs))
        normalErrs = list(filter(lambda k: k != '', normalErrs))

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
            #txt = list(filter(lambda k: k not in normalErrs, txt))
            txt = list(filter(lambda k: not normalErrsF(k), txt))
            txt = list(filter(lambda k: k.strip() != '', txt))
            if len(txt) > 0:
                print('Found unusual error in')
                print(err)
                print("\n")
                print("\n".join(txt))
                print("\n\n")
                toResubmit.append(err)
        toResubmit = list(map(lambda k: ''.join(k.split('/')[-2]), toResubmit))
        print(toResubmit)
        if len(toResubmit) > 0:
            print('\n\nShould resubmit the following files\n')
            print('queue 1 Folder in ' +
                  ' '.join(list(map(lambda k: k.split('/')[-1], toResubmit))))
            if resubmit == 1:
                from mkShapesRDF.shapeAnalysis.BatchSubmission import BatchSubmission
                BatchSubmission.resubmitJobs(batchFolder, tag, toResubmit, dryRun)


    elif operationMode == 2:
        print('', ''.join(['#' for _ in range(20)]), '\n\n',
              'Merging root files', '\n\n', ''.join(['#' for _ in range(20)]))
        #results = {}
        filesToMerge = []
        for sampleName in list(samples.keys()):
            types = {}
            for filesType in samples[sampleName]['name']:
                if len(filesType) == 2 and len(filesType[1]) > 0:
                    if '1' not in list(types.keys()):
                        types['1'] = []
                    types['1'].append(filesType + ('1',))
                elif len(filesType) == 3 and len(filesType[1]) > 0:
                    if filesType[2] not in list(types.keys()):
                        types[filesType[2]] = []
                    types[filesType[2]].append(filesType)
                else:
                    print("Error", sampleName, filesType)
                    print(
                        "Either the sample proc you specified has no files, or the weight had problems")
                    sys.exit()

            i = 0
            for _type in list(types.keys()):
                __files = list(map(lambda k: k[1], types[_type]))
                # flatted list of files
                __files = [item for sublist in __files for item in sublist]
                dim = 1
                if 'FilesPerJob' in list(samples[sampleName].keys()):
                    dim = samples[sampleName]['FilesPerJob']
                else:
                    dim = len(__files)

                __files = [__files[j: j+dim]
                           for j in range(0, len(__files), dim)]

                for ___files in __files:
                    f = f'{folder}/{outputFolder}/mkShapes__{tag}__ALL__{sampleName}_{str(i)}.root'
                    if not os.path.exists(f):
                        print("Error missing file ", f, sampleName, _type)
                        sys.exit()
                    filesToMerge.append(f)
                    i += 1
        print(f'Hadding files into {folder}/{outputFolder}/{outputFile}')
        process = subprocess.Popen(
            f'hadd -j {folder}/{outputFolder}/{outputFile} {" ".join(filesToMerge)}', shell=True)
        process.wait()

    elif operationMode == 3:
        print('', ''.join(['#' for _ in range(20)]), '\n\n',
              'Doing plots', '\n\n', ''.join(['#' for _ in range(20)]))
        f = ROOT.TFile(f'{folder}/{outputFolder}/{outputFile}', "read")
        for cut_cat in [k.GetName() for k in f.GetDirectory('/').GetListOfKeys()]:
            _results[cut_cat] = {}
            # f.cd(cut_cat)
            for var in [k.GetName() for k in f.GetDirectory('/' + cut_cat).GetListOfKeys()]:
                _results[cut_cat][var] = {}
                #f.cd('/' + cut_cat + '/' + var)
                # _var.cd()
                # for sampleName in [k.GetName() for k in f.GetDirectory('/' + cut_cat + '/' + var).GetListOfKeys()]:
                for sampleName in list(groupPlot.keys()):
                    h = 0
                    isBlind = plot.get(sampleName, {}).get('blind', {}).get(cut_cat, '') == 'full'
                    if groupPlot[sampleName].get('isData', False):
                        h = f.Get('/' + cut_cat + '/' +
                                  var + '/histo_' + sampleName)
                    else:
                        if len(groupPlot[sampleName]['samples']) > 1:
                            for subSample in groupPlot[sampleName]['samples']:
                                hname = 'histo_' + subSample
                                plotScaleFactor = plot.get(subSample, {'scale': 1}).get('scale', 1) * plot.get(subSample, {'scale': 1}).get('cuts', {}).get(cut_cat, 1)

                                if plotScaleFactor != 1:
                                    print('\n\nscaling plot\n\n', plotScaleFactor)
                                if hname in [k.GetName() for k in f.GetDirectory('/' + cut_cat + '/' + var).GetListOfKeys()]:
                                    if h != 0:
                                        _h = f.Get('/' + cut_cat + '/' +
                                                   var + '/histo_' + subSample).Clone()
                                        if plotScaleFactor != 1:
                                            _h.Scale(plotScaleFactor)
                                        h.Add(_h)
                                    else:
                                        h = f.Get('/' + cut_cat + '/' +
                                                  var + '/histo_' + subSample).Clone()
                                        if plotScaleFactor != 1:
                                                h.Scale(plotScaleFactor)
                                else:
                                    print('Missing histo',
                                          cut_cat, var, subSample)
                                    sys.exit()
                        else:
                            plotScaleFactor = plot.get(sampleName, {'scale': 1}).get('scale', 1) * plot.get(sampleName, {'scale': 1}).get('cuts', {}).get(cut_cat, 1)

                            #plotScaleFactor = plot.get(sampleName, {'scale': 1}).get('scale', 1)
                            if plotScaleFactor != 1:
                                print('\n\nscaling plot\n\n', sampleName, plotScaleFactor)
                            h = f.Get('/' + cut_cat + '/' + var + '/histo_' +
                                      groupPlot[sampleName]['samples'][0]).Clone()
                            if plotScaleFactor != 1:
                                    h.Scale(plotScaleFactor)
                    if isBlind:
                        for iBin in range(h.GetNbinsX()+1):
                            h.SetBinContent(iBin, 0)
                    _results[cut_cat][var][sampleName] = {
                        'object': h,
                        'isData': groupPlot[sampleName].get('isData', 0) == 1,
                        'isSignal': groupPlot[sampleName].get('isSignal', 0) == 1
                    }
        # print(_results)

        histPlots = {}

        for cut_cat in list(_results.keys()):
            sampleNamesSorted = list(filter(lambda k: not k[1]['isSignal'] and not k[1]['isData'],  _results[cut_cat][list(
                _results[cut_cat].keys())[0]].items()))
            #sampleNamesSorted = list(sorted(_results[cut_cat]['events'].items(), key=lambda k:k[1]['object'].GetBinContent(1) ))
            print(cut_cat, sampleNamesSorted)
            sampleNamesSorted = list(
                sorted(sampleNamesSorted, key=lambda k: k[1]['object'].Integral()))
            sampleNamesSorted = list(map(lambda k: k[0], sampleNamesSorted))
            sigName = list(filter(lambda k: k[1]['isSignal'], _results[cut_cat][list(
                _results[cut_cat].keys())[0]].items()))
            #sigName = list(filter(_results[cut_cat]['events'].items(), key=lambda k: k[1]['isSignal']))
            if len(sigName) == 0 or len(sigName) >= 2:
                print("Either no signal or many signals")
            else:
                print(sigName[0])
                sampleNamesSorted.append(sigName[0][0])
            dataName = list(filter(lambda k: k[1]['isData'], _results[cut_cat][list(
                _results[cut_cat].keys())[0]].items()))
            #dataName = list(filter(_results[cut_cat]['events'].items(), key=lambda k: k[1]['isData']))
            # if len(dataName)>0 and len(dataName)<2:
            if len(dataName) == 0 or len(dataName) >= 2:
                print("Either no data or many data histograms")
            else:
                sampleNamesSorted.append(dataName[0][0])

            # print(sampleNamesSorted)

            if cut_cat not in list(histPlots.keys()):
                histPlots[cut_cat] = {}
            for var in list(_results[cut_cat].keys()):
                if var not in list(histPlots[cut_cat].keys()):
                    histPlots[cut_cat][var] = {
                        'thstack': ROOT.THStack(cut_cat + '_' + var, ""),
                        'data': 0,
                        'sig': 0,
                        'min': 1000,
                        'max': 0
                    }
                d = OrderedDict()
                for sampleName in sampleNamesSorted:
                    #_results[cut_cat][var][sampleName] = results[sampleName][cut_cat][var]
                    h = _results[cut_cat][var][sampleName]['object']
                    # h.SetMarkerColor(groupPlot[sampleName]['color'])
                    if _results[cut_cat][var][sampleName]['isData']:
                        print('adding data to histPlots')
                        h.SetMarkerColor(ROOT.kBlack)
                        h.SetLineColor(ROOT.kBlack)
                        h.SetMarkerColor(ROOT.kBlack)
                        h.SetMarkerSize(1)
                        h.SetMarkerStyle(20)
                        histPlots[cut_cat][var]['data'] = h
                    else:
                        h.SetLineColor(groupPlot[sampleName]['color'])
                        h.SetFillColorAlpha(
                            groupPlot[sampleName]['color'], 0.6)
                        histPlots[cut_cat][var]['thstack'].Add(h)
                    if _results[cut_cat][var][sampleName]['isSignal']:
                        histPlots[cut_cat][var]['sig'] = h
                    d[sampleName] = _results[cut_cat][var][sampleName]
                _results[cut_cat][var] = d

                histPlots[cut_cat][var]['min'] = _results[cut_cat][var][sampleNamesSorted[0]
                                                                        ]['object'].GetMinimum()
                histPlots[cut_cat][var]['max'] = histPlots[cut_cat][var]['thstack'].GetMaximum(
                )

        def Pad2TAxis(hist):
            xaxis = hist.GetXaxis()
            xaxis.SetLabelFont(42)
            xaxis.SetLabelOffset(0.025)
            xaxis.SetLabelSize(0.1)
            xaxis.SetNdivisions(505)
            xaxis.SetTitleFont(42)
            xaxis.SetTitleOffset(1.35)
            xaxis.SetTitleSize(0.11)

            yaxis = hist.GetYaxis()
            #yaxis.CenterTitle ( )
            yaxis.SetLabelFont(42)
            yaxis.SetLabelOffset(0.02)
            yaxis.SetLabelSize(0.1)
            yaxis.SetNdivisions(505)
            yaxis.SetTitleFont(42)
            yaxis.SetTitleOffset(.4)
            yaxis.SetTitleSize(0.11)


        # the user may specify to plot 
        # a) only logs
        # b) only lins
        # c) both logs and lins
        # save in plotsLog list if he wants logs or not

        if logPlots==1 and linPlots == 0:
            plotLogs = [True]
        elif logPlots==0 and linPlots == 1:
            plotLogs = [False]
        else:
            #plot both log and lins
            plotLogs = [True, False]

        for cut_cat in list(histPlots.keys()):
            for _var in list(histPlots[cut_cat].keys()):
                for plotLog in plotLogs:
                    cnv = ROOT.TCanvas("c", "c1", 800, 800)
                    var = _var.replace('__', '')
                    cnv.cd()
                    canvasPad1Name = 'pad1'
                    pad1 = ROOT.TPad(canvasPad1Name, canvasPad1Name,
                                     0.0, 1-0.72, 1.0, 1-0.05)
                    pad1.SetTopMargin(0.)
                    pad1.SetBottomMargin(0.020)
                    pad1.Draw()
                    pad1.cd()

                    _min = histPlots[cut_cat][_var]['min'] * 1e-2
                    _max = histPlots[cut_cat][_var]['max'] * 1e+2
                    #minXused = h.GetBinLowEdge(1)
                    #maxXused = h.GetBinUpEdge(h.GetNbinsX())
                    if  len(variables[var]['range']) == 1:
                        # custom binning
                        minXused = variables[var]['range'][0][0]
                        maxXused = variables[var]['range'][0][-1]
                    else:
                        minXused = variables[var]['range'][1]
                        maxXused = variables[var]['range'][2]

                    frameDistro = pad1.DrawFrame(minXused, 0.0, maxXused, 1.0)
                    frameDistro.SetTitleSize(0)

                    xAxisDistro = frameDistro.GetXaxis()
                    xAxisDistro.SetNdivisions(6, 5, 0)
                    xAxisDistro.SetLabelSize(0)

                    # frameDistro.GetXaxis().SetTitle(var)
                    frameDistro.GetYaxis().SetTitle("Events / bin")

                    frameDistro.GetYaxis().SetLabelOffset(0.0)
                    frameDistro.GetYaxis().SetLabelSize(0.05)
                    #frameDistro.GetYaxis().SetNdivisions ( 505)
                    frameDistro.GetYaxis().SetTitleFont(42)
                    frameDistro.GetYaxis().SetTitleOffset(0.8)
                    frameDistro.GetYaxis().SetTitleSize(0.06)

                    frameDistro.GetYaxis().SetRangeUser(max(1, _min), _max)
                    #frameDistro.GetYaxis().SetRangeUser(1e-3, 1e+5)
                    #h.GetYaxis().SetRangeUser( min(1e-3, _min), _max)

                    tlegend = ROOT.TLegend(0.20, 0.75, 0.80, 0.98)
                    # tlegend.SetFillColor(0)
                    tlegend.SetTextFont(42)
                    tlegend.SetTextSize(0.035)
                    tlegend.SetLineColor(0)
                    tlegend.SetFillStyle(0)

                    # tlegend.SetShadowColor(0)
                    for sampleName in list(_results[cut_cat][_var].keys()):
                        name = groupPlot[sampleName]['nameHR'] + \
                            f' [{str(round(_results[cut_cat][_var][sampleName]["object"].Integral(),1))}]'
                        if _results[cut_cat][_var][sampleName]['isData']:
                            tlegend.AddEntry(
                                _results[cut_cat][_var][sampleName]['object'], name, "lep")
                        else:
                            tlegend.AddEntry(
                                _results[cut_cat][_var][sampleName]['object'], name, "f")

                    tlegend.SetNColumns(2)

                    h = histPlots[cut_cat][_var]['thstack']
                    h.Draw('same hist')
                    hdata = 0
                    if histPlots[cut_cat][_var]['data'] != 0:
                        print('Data hist exists, plotting it')
                        hdata = histPlots[cut_cat][_var]['data']
                        hdata.Draw('same p0')
                    if histPlots[cut_cat][_var]['sig'] != 0:
                        hsig = histPlots[cut_cat][_var]['sig']
                        #hdata.Draw('hist same L')
                        hsig.Draw('hist same noclear')
                    tlegend.Draw()

                    pad1.RedrawAxis()

                    if plotLog:
                        pad1.SetLogy()
                    else:
                        frameDistro.GetYaxis().SetRangeUser(max(1, _min/1e-2), _max/1e+2)


                    if variables[_var].get('setLogx', 0) != 0:
                        pad1.SetLogx()

                    cnv.cd()
                    if hdata == 0:
                        for sampleName in list(_results[cut_cat][_var].keys()):
                            if hdata == 0:
                                hdata = _results[cut_cat][_var][sampleName]['object'].Clone(
                                )
                            else:
                                hdata.Add(_results[cut_cat][_var]
                                          [sampleName]['object'].Clone())
                    hmc = 0
                    for sampleName in list(_results[cut_cat][_var].keys()):
    #                    # IMPORTANT: Signal not included in ratio!
    #                    if _results[cut_cat][_var][sampleName]['isData'] or _results[cut_cat][_var][sampleName]['isSignal']:
    #                        continue
                        #IMPORTANT2 now Signal is included in ratio
                        if _results[cut_cat][_var][sampleName]['isData']: 
                            continue
                        if hmc == 0:
                            hmc = _results[cut_cat][_var][sampleName]['object'].Clone()
                        else:
                            hmc.Add(_results[cut_cat][_var]
                                    [sampleName]['object'].Clone())

                    h_err = hmc.Clone()
                    for j in range(h_err.GetNbinsX()):
                        h_err.SetBinError(j, 0)
                    h_err.Divide(hmc)
                    rp = hdata.Clone()
                    rp.Divide(hmc)
                    rp.SetMarkerColor(ROOT.kBlack)

                    canvasPad2Name = 'pad2'
                    pad2 = ROOT.TPad(
                        canvasPad2Name, canvasPad2Name, 0.0, 0, 1, 1-0.72)
                    pad2.SetTopMargin(0.008)
                    pad2.SetBottomMargin(0.31)
                    pad2.Draw()
                    pad2.cd()

                    frameRatio = pad2.DrawFrame(minXused, 0.0, maxXused, 2.0)
                    xAxisDistro = frameRatio.GetXaxis()
                    xAxisDistro.SetNdivisions(6, 5, 0)
                    frameRatio.GetYaxis().SetTitle("DATA / MC")
                    frameRatio.GetYaxis().SetRangeUser(minRatio, maxRatio)
                    frameRatio.GetXaxis().SetTitle(variables[var]['xaxis'])
                    Pad2TAxis(frameRatio)

                    h_err.SetFillColorAlpha(ROOT.kBlack, 0.5)
                    h_err.SetFillStyle(3004)
                    h_err.GetYaxis().SetRangeUser(0.6, 1.4)

                    #h_err.Draw("same e3")
                    h_err.Draw("same e2")
                    rp.GetYaxis().SetRangeUser(0.6, 1.4)

                    rp.Draw("same e")

                    pad2.RedrawAxis()
                    if variables[_var].get('setLogx', 0) != 0:
                        pad2.SetLogx()
                    pad2.SetGrid()

                    ROOT.gStyle.SetOptStat(0)

                    cnv.SetLogy()

                    if plotLog:
                        outfile = 'log_'
                    else:
                        outfile = 'lin_'
                    outfile += cut_cat + '_' + var + '.png'
                    cnv.SaveAs("{}/{}".format(plotPath, outfile))
                    if savePdf == 1:
                        outfile = cut_cat + '_' + var + '.pdf'
                        cnv.SaveAs("{}/{}".format(plotPath, outfile))
        f.Close()


if __name__ == '__main__':
    main()
