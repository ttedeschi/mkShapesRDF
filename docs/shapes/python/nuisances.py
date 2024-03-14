"""
Defines the nuisances.

Examples
--------

>>> nuisances = {}

Example of simple lnN (no processing needed)


>>> nuisances['lumi_Uncorrelated'] = {
>>>     'name': 'lumi_13TeV_2018',
>>>     'type': 'lnN',
>>>     'samples': dict((skey, '1.015') for skey in mc if skey not in ['WW', 'top', 'dyll', 'dytt'])
>>> }


Example of suffix nuisance


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


Example of weight nuisance


>>> nuisances['eff_e'] = {
>>>     'name': 'CMS_eff_e_2018',
>>>     'kind': 'weight',
>>>     'type': 'shape',
>>>     'samples': dict((skey, ['SFweightEleUp', 'SFweightEleDown']) for skey in mc)
>>> }
"""
