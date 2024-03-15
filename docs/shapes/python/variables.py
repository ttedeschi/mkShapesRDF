"""
Defines the variables in ``variables.py``.

Examples
--------

First define an empty variables dict:

>>> variables = {}

>>> variables['mll'] = {
>>>     'name': 'mll',            #   variable name
>>>     'range' : (20,80,100),    #   variable range as (nbins, xmin, xmax)
>>>     'xaxis' : 'm_{ll} [GeV]',  #   x axis name
>>>     'fold' : 0
>>> }

>>> variables['ptll'] = {
>>>     'name': 'ptll',            #   variable name
>>>     'range' : ([20, 50, 100, 400], ),  
>>>     # variable range as (list_of_bin_edges,)
>>>     'xaxis' : 'p^T_{ll} [GeV]',  #   x axis name
>>>     'fold' : 0
>>> }

>>> variables['ptll_detall'] = {
>>>     'name': 'ptll:detall',            #   variable name
>>>     'range' : (5, 20, 400, 6, 0, 5),    
>>>     # variable range as (nbins_x, xmin, xmax, nbins_y, ymin, ymax)
>>>     'xaxis' : 'p^T_{ll}:eta_{ll}',  #   x axis name
>>>     'fold' : 0
>>> }

>>> variables['ptll_detall'] = {
>>>     'name': 'ptll:detall',            #   variable name
>>>     'range' : ([20, 50, 100, 400], [0, 0.5, 1.5, 2.5, 5.0],),   
>>>     # variable range as (list_of_bin_edges_var1,list_of_bin_edges_var2)
>>>     'xaxis' : 'p^T_{ll}:eta_{ll}',  #   x axis name
>>>     'fold' : 0
>>> }

Save ntuples branches, special column ``weight`` is always saved


>>> dnn_branches = {
>>>     # single leptons
>>>     "ptl1": "Lepton_pt[0]",
>>>     "ptl2": "Lepton_pt[1]",
>>>     "etal1": "Lepton_eta[0]",
>>>     "etal2": "Lepton_eta[1]",
>>>     "phil1": "Lepton_phi[0]",
>>>     "phil2": "Lepton_phi[1]",
>>> }
>>> 
>>> variables['test_ntuples'] = {
>>>     'tree': dnn_branches, # dictionary of branches to be saved
>>>     'cuts': ['sr'] # specify cut after which the events will be saved
>>> }
>>> 

"""