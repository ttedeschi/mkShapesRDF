cuts = {}

preselections = '          Lepton_pt[0]>30 \
                        && Lepton_pt[1]>20 \
                        && abs(Lepton_eta[0])<2.4 && abs(Lepton_eta[1])<2.4 \
                        && ((Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11) || (Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)) \
                        && Alt(CleanJet_pt, 1, 0)>30 \
                        && abs(CleanJet_eta[0])<4.7 && abs(CleanJet_eta[1])<4.7 \
                        && abs(CleanJet_pt[0])>50 && abs(CleanJet_pt[1])>30 \
                        '

"""
cuts['top'] = {
    'expr': 'topcr',
    'categories':{
        'eemm': '1',
    }
}

cuts['vv'] = {
    'expr': 'bVeto && abs(mll-91)>15 ',
    'categories':{
        'eemm': '1',
        'pure_eemm': 'PuppiMET_pt > 60'
    }
}
"""

cuts['dy_pu'] = {
    'expr': 'bVeto && abs(mll-91)<15 && dphijj < 2 && abs(ZeppenfeldDilepton)>1',
    'categories':{
        'eemm': '1',
    }
}

cuts['dy_hard'] = {
    'expr': 'bVeto && abs(mll-91)<15 && dphijj > 2 && abs(ZeppenfeldDilepton)>1',
    'categories':{
        'eemm': '1',
    }
}

cuts['sr'] = {
    'expr': 'bVeto && abs(mll-91)<15 && dphijj > 2 && abs(ZeppenfeldDilepton)<1 && mjj>200',
    'categories':{
        'eemm': '1',
        #'pure_eemm': 'Alt(CleanJet_pt, 0, 0) > 100 && Alt(CleanJet_pt, 1, 0) > 100 && mjj > 400'
#        'ee': ' (Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11) \
#                && abs(Lepton_eta[0])<2.1 && abs(Lepton_eta[1])<2.1 \
#                ',
#        'mm': ' (Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13) \
#                && abs(Lepton_eta[0])<2.4 && abs(Lepton_eta[1])<2.4 \
#                '
    }
}
