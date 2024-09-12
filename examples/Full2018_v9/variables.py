# variables

variables = {}
# variables['nvtx']  = {   'name': 'PV_npvsGood',
#                        'range' : (20,0,100),
#                        'xaxis' : 'nvtx',
#                         'fold' : 3
#                      }
variables["NewFatJet_pt1"] = {
    'name' : '(Sum(FatJet_pt>10)>0)*(Alt(FatJet_pt, 0, 0)) - (Sum(FatJet_pt>30)==0)*99',
    'range':(100,0,100),
    'xaxis': 'First FatJet_pt [GeV]',
    'fold' : 1,
}
variables["NewFatJet_n"] = {
    'name' : "Sum(CleanFatJet_pt>10)",
    'range' : (5,0,5),
    'xaxis': 'CleanFatJet_n',
    'fold' : 1,    
    
}
variables["NewFatJet_pt1"] = {
    'name' : 'CleanFatJet_pt[0]',
    'range':(100,0,100),
    'xaxis': 'First FatJet_pt [GeV]',
    'fold' : 1,
}
variables["NewFatJet_pt2"] = {
    'name' : 'CleanFatJet_pt[1]',
    'range':(100,0,100),
    'xaxis' : 'second FatJet_pt',
    'fold': 0,
    
    }
variables["CleanJet_pt1"] = {
    'name' : '(Sum(CleanJet_pt>10)>0)*(Alt(CleanJet_pt, 0, 0)) - (Sum(CleanJet_pt>30)==0)*99',
    'range':(100,0,100),
    'xaxis': 'First CleanJet_pt [GeV]',
    'fold' : 1,
}
variables["ptll_eta_phi"] = {
    "name": "Lepton_pt[0]:Lepton_eta[0]:Lepton_phi[0]",
    "range": (7, 15, 150, 5, -2.5, 2.5, 6, -3.14, 3.14),
    "xaxis": "ptll:etall:phill",
    "fold": 3,
}

variables["mll"] = {
    "name": "mll",  #   variable name
    "range": (20, 80, 100),  #   variable range
    "xaxis": "m_{ll} [GeV]",  #   x axis name
    "fold": 0,
}

variables["ptll"] = {
    "name": "ptll",
    "range": (20, 0, 200),
    "xaxis": "p_{T}^{ll} [GeV]",
    "fold": 0,
}
variables["ptll_more"] = {
    "name": "ptll",
    "range": (50, 0, 100),
    "xaxis": "p_{T}^{ll} [GeV]",
    "fold": 0,
}
variables["pt1"] = {
    "name": "Lepton_pt[0]",
    "range": (20, 0, 100),
    "xaxis": "p_{T} 1st lep",
    "fold": 3,
}
variables["pt2"] = {
    "name": "Lepton_pt[1]",
    "range": (20, 0, 100),
    "xaxis": "p_{T} 2nd lep",
    "fold": 3,
}

variables["eta1"] = {
    "name": "Lepton_eta[0]",
    "range": (20, -3, 3),
    "xaxis": "#eta 1st lep",
    "fold": 3,
}

variables["eta2"] = {
    "name": "Lepton_eta[1]",
    "range": (20, -3, 3),
    "xaxis": "#eta 2nd lep",
    "fold": 3,
}


variables["phi1"] = {
    "name": "Lepton_phi[0]",
    "range": (20, -3.2, 3.2),
    "xaxis": "#phi 1st lep",
    "fold": 3,
}

variables["phi2"] = {
    "name": "Lepton_phi[1]",
    "range": (20, -3.2, 3.2),
    "xaxis": "#phi 2nd lep",
    "fold": 3,
}

variables["puppimet"] = {
    "name": "PuppiMET_pt",
    "range": (20, 0, 100),
    "xaxis": "puppimet [GeV]",
    "fold": 3,
}

variables["njet"] = {
    "name": "Sum(CleanJet_pt>30)",
    "range": (5, 0, 5),
    "xaxis": "Number of jets",
    "fold": 2,
}

variables["jetpt1"] = {
    "name": "(Sum(CleanJet_pt>30)>0)*(Alt(CleanJet_pt, 0, 0)) - (Sum(CleanJet_pt>30)==0)*99",
    "range": (20, 0, 200),
    "xaxis": "p_{T} 1st jet",
    "fold": 0,
}

variables["jetpt2"] = {
    "name": "(Sum(CleanJet_pt>30)>1)*(Alt(CleanJet_pt, 1, 0)) - (Sum(CleanJet_pt>30)<=1)*99",
    "range": (20, 0, 200),
    "xaxis": "p_{T} 2nd jet",
    "fold": 0,
}

variables["jetpt1_more"] = {
    "name": "(Sum(CleanJet_pt>30)>0)*(Alt(CleanJet_pt, 0, 0)) - (Sum(CleanJet_pt>30)==0)*99",
    "range": (40, 0, 200),
    "xaxis": "p_{T} 1st jet",
    "fold": 0,
}

variables["jetpt2_more"] = {
    "name": "(Sum(CleanJet_pt>30)>1)*(Alt(CleanJet_pt, 1, 0)) - (Sum(CleanJet_pt>30)<=1)*99",
    "range": (40, 0, 200),
    "xaxis": "p_{T} 2nd jet",
    "fold": 0,
}

variables["jeteta1"] = {
    "name": "(Sum(CleanJet_pt>30)>0)*(Alt(CleanJet_eta, 0, 0)) - (Sum(CleanJet_pt>30)==0)*99",
    "range": (20, -5.0, 5.0),
    "xaxis": "#eta 1st jet",
    "fold": 0,
}

variables["jeteta2"] = {
    "name": "(Sum(CleanJet_pt>30)>1)*(Alt(CleanJet_eta, 1, 0)) - (Sum(CleanJet_pt>30)<=1)*99",
    "range": (20, -5.0, 5.0),
    "xaxis": "#eta 2nd jet",
    "fold": 0,
}

variables["trkMet"] = {
    "name": "TkMET_pt",
    "range": (20, 0, 200),
    "xaxis": "trk met [GeV]",
    "fold": 3,
}

variables["mpmet"] = {
    "name": "mpmet",
    "range": (20, 0, 200),
    "xaxis": "min proj met [GeV]",
    "fold": 3,
}
variables['NewFatJet_n'] = {
    'name': 'Sum(CleanFatJet_pt>30)',
    'range': (10,0,10),
    'xaxis': 'number of FatJet p_{T}>30',
    'fold' : 1,
}

variables["NewFatJet_pt2"] = {
    'name' : 'CleanFatJet_pt[1]',
    'range':(50,0,300),
    'xaxis': 'Second FatJet_pt [GeV]',
    'fold' : 1,
}
variables["NewFatJet_eta1"] = {
    'name' : 'CleanFatJet_eta[0]',
    'range': (50,0,2.5),
    'xaxis': '1st FatJet |eta|',    
    'fold' : 1,
}
variables["NewFatJet_eta2"] = {
    'name' : 'CleanFatJet_eta[1]',
    'range': (50,0,2.5),
    'xaxis': '2nd FatJet |eta|',    
    'fold' : 1,
}
variables["NewFatJet_eta"] = {
    'name' : 'CleanFatJet_eta',
    'range': (50,0,2.5),
    'xaxis': '2nd FatJet |eta|',    
    'fold' : 1,
}
variables["NewFatJet_mass1"] = {
    'name':'CleanFatJet_mass[0]',
    'range':(50,0,200),
    'xaxis':'1st FatJet_mass',    
    'fold' : 1,
}
variables["NewFatJet_mass2"] = {
    'name':'CleanFatJet_mass[1]',
    'range':(50,0,200),
    'xaxis':'2nd FatJet_mass',    
    'fold' : 1,
}
variables["NewCleanJetNotFat_deltaR"] = {
    'name': 'CleanJetNotFat_deltaR',
    'range': (50, 0 ,2),
    'xaxis': 'JetNotFat deltaR',
    'fold' : 1,
}

