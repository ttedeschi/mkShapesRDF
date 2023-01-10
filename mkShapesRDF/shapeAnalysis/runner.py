from copy import deepcopy
import sys
from collections import OrderedDict
import ROOT
ROOT.gROOT.SetBatch(True)


class RunAnalysis:

    @staticmethod
    def splitSamples(samples, useFilesPerJob=True):
        """static methods, takes a dictionary of samples and split them based on their weights and max num. of files

        Args:
            samples (dict): dictionary of samples
            useFilesPerJob (bool, optional): if you want to further split the samples based on max num. of files. Defaults to True.

        Returns:
            (list of tuples): each tuple will have a lenght of 5 (6 if subsamples are present), where the first element is the name of the sample, the second the list of files, the third the weight, and the fourth the index of this tuple compared to the other tuples of the same sample type, the fifth will be the isData flag (True if the sample is data, False otherwise). If subsamples are present, the sixth element will be the dict of subsamples
        """
        # will contain all the different samples splitted based on their weights and max num. of files
        splittedSamples = []
        for sampleName in list(samples.keys()):
            types = {}  # this will contain the the different type of files with their special weights for this sampleName
            # recall that samples[sampleName]['name'] contain a list of tuples, where a single tuple can have a size of 2 or 3:
            # first position for name of the process (DYJetsToLL_M-50), second list of files, third a possible special weight
            for filesType in samples[sampleName]['name']:
                # no special weight (will use '1'), and at least one file found
                if len(filesType) == 2 and len(filesType[1]) > 0:
                    if '1' not in list(types.keys()):
                        types['1'] = []
                    types['1'].append(filesType + ('1',))
                elif len(filesType) == 3 and len(filesType[1]) > 0:
                    if filesType[2] not in list(types.keys()):
                        types[filesType[2]] = []
                    types[filesType[2]].append(filesType)
                else:
                    print("Error", sampleName, filesType, file=sys.stderr)
                    print(
                        "Either the sample proc you specified has no files, or the weight had problems", file=sys.stderr)
                    sys.exit()

            i = 0
            for _type in list(types.keys()):
                # split files based on FilesPerJob or include them all
                __files = list(map(lambda k: k[1], types[_type]))
                # flatted list of files
                __files = [item for sublist in __files for item in sublist]
                if useFilesPerJob:
                    dim = samples[sampleName].get('FilesPerJob', len(__files))
                else:
                    dim = len(__files)
                __files = [__files[j: j+dim]
                           for j in range(0, len(__files), dim)]
                for ___files in __files:
                    # the weights for these files will be the product of the weight inside this sampele (i.e. samples[sampleName]['weight'])
                    # and the product of the special weights that is in common to all of those files (i.e. sampleType[0])
                    # the common special weight can be retrived from the first of the list of files with this weight
                    # remember that the tuple has always size 3 now, the last position is for the special weight
                    weight = '( ' + samples[sampleName]['weight'] + \
                        ' ) * ( ' + types[_type][0][2] + ' )'
                    isData = samples[sampleName].get('isData', False)
                    sampleType = (sampleName, ___files, weight, i, isData)
                    if 'subsamples' in list(samples[sampleName].keys()):
                        sampleType += (samples[sampleName]['subsamples'],)
                    splittedSamples.append(sampleType)
                    i += 1
        return splittedSamples

    @staticmethod
    def getTTreeNomAndFriends(fnom, friends):
        """Create a TChain with the nominal files and the friends files (nuisances TTrees with varied branches)

        Args:
            fnom (list): list of nominal files
            friends (list of list): list of list of friends files

        Returns:
            TChain: TChain with nominal files and friends files
        """
        tnom = ROOT.TChain('Events')
        for f in fnom:
            tnom.Add(f)
        for friend in friends:
            _tfriend = ROOT.TChain('Events')
            for f in friend:
                _tfriend.Add(f)
            tnom.AddFriend(_tfriend)
        return tnom

    @staticmethod
    def varyExpression(nameDown, nameUp, _type):
        """Creates a string with the expression to be used in the RDataFrame.Vary() method

        Args:
            nameDown (str): down varied branch name
            nameUp (str): up varied branch name
            _type (str): string version of nominal column type

        Returns:
            str: string with the expression to be used in the RDataFrame.Vary() method
        """
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

    @staticmethod
    def getNuisanceFiles(nuisance, files):
        """Searches in the provided nuisance folder for the files with the same name of the nominal files

        Args:
            nuisance (dict): dict with the nuisance information
            files (list): list of nominal files

        Returns:
            list of list: list with the down and up varied list of files
        """
        _files = list(map(lambda k: k.split('/')[-1], files))
        nuisanceFilesDown = list(
            map(lambda k: nuisance['folderDown'] + '/' + k, _files))
        nuisanceFilesUp = list(
            map(lambda k: nuisance['folderUp'] + '/' + k, _files))
        return [nuisanceFilesDown, nuisanceFilesUp]

    def __init__(self, samples, aliases, variables, preselections, cuts, nuisances, lumi, limit=-1, outputFileMap='output.root'):
        """
        Stores arguments in the class attributes and creates all the RDataFrame objects
        Args:
            samples (list of tuples): same type as the return of the splitSamples method
            aliases (dict): dict of aliases
            variables (dict): dict of variables
            preselections (str): string with the preselections
            cuts (dict): dict of cuts
            nuisances (dict): dict of nuisances
            lumi (float): lumi in fb-1
            limit (int, optional): limit of events to be processed. Defaults to -1.
            outputFileMap (str, optional): full path + filename of the output root file. Defaults to 'output.root'.

        Returns:
            (void): void 
        """
        self.samples = samples
        self.aliases = aliases
        self.variables = variables
        self.preselections = preselections
        mergedCuts = {}
        for cut in list(cuts.keys()):
            __cutExpr = ''
            if type(cuts[cut]) == dict:
                __cutExpr = cuts[cut]['expr']
                for cat in list(cuts[cut]['categories'].keys()):
                    mergedCuts[cut + '_' + cat] = {'parent': cut}
                    mergedCuts[cut + '_' + cat]['expr'] = __cutExpr + \
                        ' && ' + cuts[cut]['categories'][cat]
            elif type(cuts[cut]) == str:
                __cutExpr = cuts[cut]
                mergedCuts[cut] = {'expr': __cutExpr, 'parent': cut}
        self.cuts = mergedCuts
        self.nuisances = nuisances
        self.lumi = lumi
        self.limit = limit
        self.outputFileMap = outputFileMap

        self.dfs = {}
        """
        dfs is a dictionary containing as keys the sampleNames. The structure should look like this:
        dfs = {
            'DY':{
                0: {
                    'df': obj,
                    'columnNames': [...],
                    'ttree': obj2, # needed otherwise seg fault in root
                },
                ...
            }
        """

        # sample here is a tuple, first el is the sampleName, second list of files,
        # third the special weight, forth is the index of tuple for the same sample,
        # fifth if present the dict of subsamples
        for sample in samples:
            files = sample[1]
            sampleName = sample[0]
            print(sampleName)
            friendsFiles = []
            for nuisance in self.nuisances.values():
                if sampleName not in nuisance.get('samples', {sampleName: []}):
                    continue
                if nuisance.get('type', '') == 'shape':
                    if nuisance.get('kind', '') == 'suffix':
                        friendsFiles += RunAnalysis.getNuisanceFiles(
                            nuisance, files)

            tnom = RunAnalysis.getTTreeNomAndFriends(files, friendsFiles)

            if limit != -1:
                df = ROOT.RDataFrame(tnom)
                df = df.Range(limit)
            else:
                ROOT.EnableImplicitMT()
                df = ROOT.RDataFrame(tnom)
            if not sampleName in self.dfs.keys():
                self.dfs[sample[0]] = {}
            self.dfs[sampleName][sample[3]] = {'df': df, 'ttree': tnom}
            #self.dfs[sample[0]] = {'df' :df, 'ttree': tnom}

        print('\n\nLoaded dataframes\n\n')

    def loadAliases(self):
        """
        Load aliases in the dataframes. It creates also the special alias `weight` 
        """
        samples = self.samples
        aliases = self.aliases
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                df = self.dfs[sampleName][index]['df']
                print('accessing columns')
                self.dfs[sampleName][index]['columnNames'] = list(
                    map(lambda k: str(k), df.GetColumnNames()))
                print('done accessing columns')
                sample = list(
                    filter(lambda k: k[0] == sampleName and k[3] == index, samples))[0]
                weight = sample[2]
                isData = sample[4]
                if not isData:
                    aliases['weight'] = {
                        # 'expr': samples[sampleName]['weight'] + ' * ' + str(self.lumi) + ' * ' + weight
                        'expr': str(self.lumi) + ' * ' + weight
                    }
                else:
                    aliases['weight'] = {
                        # 'expr': samples[sampleName]['weight'] + ' * ' + weight
                        'expr': weight
                    }

                print('\n\n', sampleName, '\n\n', aliases['weight'])

                define_string = "df"
                for alias in list(aliases.keys()):
                    if 'samples' in list(aliases[alias]):
                        if not sampleName in aliases[alias]['samples']:
                            continue
                    if alias in self.dfs[sampleName][index]['columnNames']:
                        print(
                            f'Alias {alias} cannot be defined, column with that name already exists')
                        sys.exit()

                    for line in aliases[alias].get('linesToAdd', []):
                        if line.startswith('.L'):
                            ls = line.split(' ')
                            if len(ls) != 2:
                                print('Don\'t know hot to read line',
                                      line, 'from alias ', alias)
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
                print('\nDebug 1\n')

                df1 = eval(define_string)
                self.dfs[sampleName][index]['df'] = df1

                print(
                    f'\n\nLoaded all aliases for {sampleName} index {index}\n\n')

                self.dfs[sampleName][index]['columnNames'] = list(
                    map(lambda k: str(k), df1.GetColumnNames()))

    def loadSystematics(self):
        """
        Loads systematics in the dataframes. Supported nuisance types are suffix and weight.
        """
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                df = self.dfs[sampleName][index]['df']
                columnNames = self.dfs[sampleName][index]['columnNames']
                nuisances = self.nuisances
                # nuisance key is not used
                for _, nuisance in list(nuisances.items()):
                    if sampleName not in nuisance.get('samples', {sampleName: []}):
                        continue
                    if nuisance.get('type', '') == 'shape':
                        if nuisance.get('kind', '') == 'suffix':
                            variation = nuisance['mapDown']
                            variedCols = list(
                                filter(lambda k: k.endswith(variation), columnNames))
                            if len(variedCols) == 0:
                                print(f'No varied columns for {variation}')
                                sys.exit()
                            baseCols = list(map(lambda k: '_'.join(
                                k.split('.')[-1].split('_')[:-(1 + variation.count('_'))]), variedCols))
                            for baseCol in baseCols:
                                if 'bool' not in str(df.GetColumnType(baseCol)).lower():
                                    varNameDown = baseCol + '_' + \
                                        nuisance['mapDown'] + '*' + \
                                        nuisance['samples'][sampleName][1]
                                    varNameUp = baseCol + '_' + \
                                        nuisance['mapUp'] + '*' + \
                                        nuisance['samples'][sampleName][0]
                                else:
                                    varNameDown = baseCol + \
                                        '_' + nuisance['mapDown']
                                    varNameUp = baseCol + \
                                        '_' + nuisance['mapUp']

                                _type = df.GetColumnType(baseCol)
                                expr = RunAnalysis.varyExpression(
                                    varNameDown, varNameUp, _type)
                                df = df.Vary(baseCol, expr, variationTags=[
                                    "down", "up"], variationName=nuisance['name'])

                        elif nuisance.get('kind', '') == 'weight':
                            weights = nuisance['samples'].get(sampleName, None)
                            if weights != None:
                                variedNames = []
                                if weights[0] not in columnNames:
                                    df = df.Define(
                                        nuisance['name']+'_up', weights[0])
                                    variedNames.append(
                                        nuisance['name'] + '_up')
                                else:
                                    variedNames.append(weights[0])

                                if weights[1] not in columnNames:
                                    df = df.Define(
                                        nuisance['name']+'_down', weights[1])
                                    variedNames.append(
                                        nuisance['name'] + '_down')
                                else:
                                    variedNames.append(weights[1])

                                if df.GetColumnType('weight') == 'double':
                                    expr = f'ROOT::RVecD' + \
                                        '{(double)' + \
                                        f'{variedNames[1]},(double) {variedNames[0]}' + '}'
                                elif df.GetColumnType('weight') == 'float':
                                    expr = f'ROOT::RVecF' + \
                                        '{(float)' + \
                                        f'{variedNames[1]},(float) {variedNames[0]}' + '}'
                                else:
                                    print('Weight column has unknown type:', df.GetColumnType(
                                        'weight'), 'while varied is: ', df.GetColumnType(variedNames[1]))
                                    sys.exit()

                                df = df.Vary('weight', expr, variationTags=[
                                    "down", "up"], variationName=nuisance['name'])
                        else:
                            print("Unsupported nuisance")
                            sys.exit()
                self.dfs[sampleName][index]['df'] = df

    def loadVariables(self):
        """
        Loads variables (not ones with the 'tree' key in them) and checks if they are already in the dataframe columns, if so it adds `__` at the beginning of the name.
        Since variables are shared but not the aliases, it could happen that a variable's name or expression is already defined for a given df but not for another one -> need to determine a common and compatible set of variables for all the many dfs. This is done by gathering the largest set of column names. 
        """

        bigColumnNames = set()
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                columnNames = self.dfs[sampleName][index]['columnNames']
                bigColumnNames = bigColumnNames.union(set(columnNames))

        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                for var in list(self.variables.keys()):
                    if 'tree' in self.variables[var].keys():
                        continue
                    if var in bigColumnNames and var != self.variables[var]['name']:
                        # here I want to define a variable whose key is already in the column name list
                        # and its expression is different from its name
                        # therefore we will either create a Define or an Alias

                        # need to rename the new variable!
                        print('changing variable', var,'to __'+var)
                        _var = '__' + var
                        self.variables[_var] = self.variables[var]
                        del self.variables[var]

        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                df = self.dfs[sampleName][index]['df']
                for var in list(self.variables.keys()):
                    if 'tree' in self.variables[var].keys():
                        continue
                    if self.variables[var]['name'] not in bigColumnNames:
                        # the variable expr does not exist, create it
                        df = df.Define(var, self.variables[var]['name'])
                    elif var not in bigColumnNames:
                        # the variable expr exists in the df, but not the variable key
                        # use alias
                        df = df.Alias(var, self.variables[var]['name'])
                    elif var == self.variables[var]['name'] and var in bigColumnNames:
                        # since the variable name and expression are equal and are already present in the df don't do anything
                        pass
                    else:
                        #FIXME 
                        print("Error, cannot define variable")
                        sys.exit()
                self.dfs[sampleName][index]['df'] = df
                self.dfs[sampleName][index]['columnNames'] = list(
                    map(lambda k: str(k), df.GetColumnNames()))

    def loadBranches(self):
        """
        Loads branches for TTrees/SnapShots and checks if they are already in the dataframe columns, if so it adds `__` at the beginning of the name.
        """
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                df = self.dfs[sampleName][index]['df']
                columnNames = self.dfs[sampleName][index]['columnNames']
                for var in list(self.variables.keys()):
                    if not 'tree' in self.variables[var].keys():
                        continue
                    for branchName in self.variables[var]['tree'].keys():

                        if branchName in columnNames:
                            _var = '__' + branchName
                            self.variables[_var] = self.variables[var]
                            del self.variables[var]

                print(self.variables)
                for var in list(self.variables.keys()):
                    if 'tree' in self.variables[var].keys():
                        continue
                    if self.variables[var]['name'] not in columnNames:
                        df = df.Define(var, self.variables[var]['name'])
                    elif var not in columnNames:
                        df = df.Alias(var, self.variables[var]['name'])
                    else:
                        print("Error, cannot define variable")
                        sys.exit()
                self.dfs[sampleName][index]['df'] = df

    def createResults(self):
        """
        Create empty dictionary for results, will store all the different histos
        """
        self.results = {}
        for cut in self.cuts.keys():
            self.results[cut] = {}
            for variable in self.variables.keys():
                self.results[cut][variable] = {}

    def splitSubsamples(self):
        """
        Split samples into subsamples if needed
        """
        sampleNames = set(
            list(map(lambda k: k[0], list(filter(lambda k: len(k) == 6, self.samples)))))
        for sampleName in sampleNames:
            _sample = list(
                filter(lambda k: k[0] == sampleName, self.samples))[0]
            for subsample in list(_sample[5].keys()):
                self.dfs[sampleName + '_' + subsample] = {}
                for index in self.dfs[sampleName].keys():
                    self.dfs[sampleName + '_' + subsample][index] = {}
                    self.dfs[sampleName + '_' + subsample][index]['df'] = self.dfs[sampleName][index]['df'].Filter(
                        _sample[5][subsample])
                    self.dfs[sampleName + '_' +
                             subsample][index]['columnNames'] = self.dfs[sampleName][index]['columnNames']
                    self.dfs[sampleName + '_' +
                             subsample][index]['ttree'] = self.dfs[sampleName][index]['ttree']

            del self.dfs[sampleName]

    def create_cuts_vars(self):
        """
        Defines Histo1D for each variable and cut and dataframe. It also creates dictionary for variations through `VariationsFor()`
        """
        mergedCuts = self.cuts
        variables = self.variables
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                df = self.dfs[sampleName][index]['df']

                for cut in mergedCuts.keys():
                    df_cat = df.Filter(mergedCuts[cut]['expr'])
                    opts = ROOT.RDF.RSnapshotOptions() 
                    opts.fLazy = True

                    for var in list(variables.keys()):
                        if 'tree' in variables[var].keys():
                            if not mergedCuts[cut]['parent'] in variables[var]['cuts']:
                                del df_cat
                                continue
                            # FIXME output tree should follow DY_0 type of filename
                            _h = df_cat.Snapshot('Events', self.outputFileMap, list(self.variables[var]['tree'].keys()), opts)
                        else:
                            _h = df_cat.Histo1D((cut + '_' + var, '') +
                                                variables[var]['range'], var, "weight")
                        if sampleName not in self.results[cut][var].keys():
                            self.results[cut][var][sampleName] = {}
                        self.results[cut][var][sampleName][index] = _h

                for cut in mergedCuts.keys():
                    for var in list(variables.keys()):
                        if not 'tree' in variables[var].keys():
                            _s = self.results[cut][var][sampleName][index]
                            _s_var = ROOT.RDF.Experimental.VariationsFor(_s)
                            self.results[cut][var][sampleName][index] = _s_var

    def convertResults(self):
        mergedCuts = self.cuts
        variables = self.variables
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                for cut in mergedCuts.keys():
                    for var in list(variables.keys()):
                        if 'tree' in variables[var].keys():
                            # no need to process SnapShots
                            continue
                        _s_var = self.results[cut][var][sampleName][index]
                        _histos = {}
                        for _variation in list(map(lambda k: str(k), _s_var.GetKeys())):
                            _h_name = _variation.replace(':', '_')
                            _h = 0
                            _h = _s_var[_variation]
                            fold = variables[var].get('fold', 0)
                            print(sampleName, index, _h.Integral())
                            if fold == 1 or fold == 3:
                                _h.SetBinContent(1, _h.GetBinContent(
                                    0) + _h.GetBinContent(1))
                                _h.SetBinContent(0, 0)
                            if fold == 2 or fold == 3:
                                lastBin = _h.GetNbinsX()
                                _h.SetBinContent(
                                    lastBin-1, _h.GetBinContent(lastBin-1) + _h.GetBinContent(lastBin))
                                _h.SetBinContent(lastBin, 0)
                            _histos[_h_name] = _h.Clone()
                            # del _h
                        #del self.results[cut][var][sampleName]['object']
                        # replace the object with the dictionary of histos
                        self.results[cut][var][sampleName][index] = _histos

    def saveResults(self):
        files = []
        f = ROOT.TFile(self.outputFileMap, 'recreate')
        for cut_cat in list(self.results.keys()):
            _cut_cat = f.mkdir(cut_cat)
            for var in list(self.results[cut_cat].keys()):
                if 'tree' in self.variables[var].keys():
                    # no need to process SnapShots
                    continue
                _cut_cat.mkdir(var)
                f.cd('/' + cut_cat + '/' + var)
                for sampleName in list(self.results[cut_cat][var].keys()):
                    # should first merge histos
                    mergedHistos = {}
                    for index in list(self.results[cut_cat][var][sampleName].keys()):
                        for hname in list(self.results[cut_cat][var][sampleName][index].keys()):
                            if hname not in mergedHistos.keys():
                                mergedHistos[hname] = self.results[cut_cat][var][sampleName][index][hname].Clone()
                            else:
                                mergedHistos[hname].Add(
                                    self.results[cut_cat][var][sampleName][index][hname])

                    for hname in mergedHistos.keys():
                        if hname == 'nominal':
                            mergedHistos[hname].SetName('histo_' + sampleName)
                        else:
                            mergedHistos[hname].SetName(
                                'histo_' + sampleName + '_' + hname)
                        mergedHistos[hname].Write()
        f.Close()

    def mergeAndSaveResults(self):
        f = ROOT.TFile(self.outputFileMap, 'recreate')
        for cut_cat in list(self.results.keys()):
            _cut_cat = f.mkdir(cut_cat)
            for var in list(self.results[cut_cat].keys()):
                if 'tree' in self.variables[var].keys():
                    # no need to process SnapShots
                    continue
                _cut_cat.mkdir(var)
                f.cd('/' + cut_cat + '/' + var)
                for sampleName in list(self.results[cut_cat][var].keys()):
                    # should first merge histos
                    mergedHistos = {}
                    for index in list(self.results[cut_cat][var][sampleName].keys()):
                        for hname in list(self.results[cut_cat][var][sampleName][index].keys()):
                            if hname not in mergedHistos.keys():
                                mergedHistos[hname] = self.results[cut_cat][var][sampleName][index][hname].Clone()
                            else:
                                mergedHistos[hname].Add(
                                    self.results[cut_cat][var][sampleName][index][hname])

                    for hname in mergedHistos.keys():
                        if hname == 'nominal':
                            mergedHistos[hname].SetName('histo_' + sampleName)
                        else:
                            mergedHistos[hname].SetName(
                                'histo_' + sampleName + '_' + hname)
                        mergedHistos[hname].Write()
        f.Close()

    def run(self):
        """
        Runs the analysis, first loads the aliases, filters with preselection the many dfs, loads systematics
        loads variables, creates the results dict, splits the samples, creates the cuts/var histos, runs the analysis
        and saves results.
        """
        # FIXME should handle subsamples, but how can it work with sampleName?
        self.loadAliases()
        # apply preselections
        for sampleName in self.dfs.keys():
            for index in self.dfs[sampleName].keys():
                self.dfs[sampleName][index]['df'] = self.dfs[sampleName][index]['df'].Filter(
                    self.preselections)

        self.loadSystematics()
        self.loadVariables()
        print('loaded all variables')
        self.createResults()
        print('created empty results dict')
        self.splitSubsamples()
        print('splitted samples')
        self.create_cuts_vars()
        print('created cuts')
        '''
        # FIXME RunGraphs can't handle results of VaraitionsFor, ask Vincenzo about it

        # collect all the dataframes and run them
        dfs = []
        for cut in self.cuts.keys():
            for var in self.variables.keys():
                for sampleName in self.dfs.keys():
                    for index in self.dfs[sampleName].keys():
                        # dfs.append(self.results[cut][var][sampleName][index])
                        dfs.extend(
                            list(self.results[cut][var][sampleName][index].values()))
        ROOT.RDF.RunGraphs(dfs)
        '''

        snapshots = []
        for cut in self.cuts.keys():
            for var in self.variables.keys():
                if len(self.results[cut].get(var, [])) == 0 or not 'tree' in self.variables[var].keys():
                    # no snapshots for this combination of cut variable
                    continue

                for sampleName in self.dfs.keys():
                    for index in self.dfs[sampleName].keys():
                        # dfs.append(self.results[cut][var][sampleName][index])
                        snapshots.append(
                            self.results[cut][var][sampleName][index]['df'])

        if len(snapshots) != 0:
            ROOT.RDF.RunGraphs(snapshots)

        self.convertResults()
        self.saveResults()


if __name__ == '__main__':
    ROOT.gInterpreter.Declare(f'#include "headers.hh"')
    exec(open('script.py').read())
    runner = RunAnalysis(samples, aliases, variables,
                         preselections, cuts, nuisances, lumi)
    runner.run()
