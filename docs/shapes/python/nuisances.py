"""
Defines the nuisances.

Examples
--------

>>> from mkShapesRDF.lib.search_files import SearchFiles
>>> searchFiles = SearchFiles()
>>> redirector = ""

>>> nuisances = {}
>>> 
>>> nuisances['lumi_Uncorrelated'] = {
>>>     'name': 'lumi_13TeV_2018',
>>>     'type': 'lnN',
>>>     'samples': dict((skey, '1.015') for skey in mc if skey not in ['WW', 'top', 'dyll', 'dytt'])
>>> }
>>> 
>>> 
>>> nuisances['electronpt'] = {
>>>     'name': 'CMS_scale_e_2018',
>>>     'kind': 'suffix',
>>>     'type': 'shape',
>>>     'mapUp': 'ElepTup',
>>>     'mapDown': 'ElepTdo',
>>>     'samples': dict((skey, ['1', '1']) for skey in mc),
>>>     'folderUp': makeMCDirectory('ElepTup_suffix'),
>>>     'folderDown': makeMCDirectory('ElepTdo_suffix'),
>>>     'separator': '_', # used as Nominal + separator + variation
>>>     'AsLnN': '1'
>>> }
"""
