cuts = {}

preselections = '          Lepton_pt[0]>25 \
                        && Lepton_pt[1]>13 \
                        && Alt(Lepton_pt, 2, 0) < 10 \
                        && abs(Lepton_eta[0])<2.5 && abs(Lepton_eta[1])<2.5 \
                        && ((Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11) || (Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)) \
                        && Alt(CleanJet_pt, 1, 0)>30 \
                        && abs(CleanJet_eta[0])<4.7 && abs(CleanJet_eta[1])<4.7 \
                        '

#&& abs(CleanJet_pt[0])>30 && abs(CleanJet_pt[1])>20 \

"""
cuts['dy_pu'] = {
    'expr': 'bVeto && abs(mll-91)<15 && dphijj < 2 && (Alt(CleanJet_pt, 0, 0) < 100) && ( Alt(CleanJet_pt, 1, 0) < 100)',
    'categories':{
        'ee': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11)',
        'mm': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)',
    }
}
"""

cuts['topcr'] = {
    'expr': 'topcr',
    'categories':{
        'ee': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11)',
        'mm': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)',
    }
}

cuts['vvcr'] = {
    'expr': 'abs(mll-91)>15 && bVeto && mth>60 && mtw2>30',
    'categories':{
        'ee': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11)',
        'mm': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)',
    }
}

cuts['dycr'] = {
    'expr': 'abs(mll-91)<15 && bVeto && detajj < 3',
    'categories':{
        'ee': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11)',
        'mm': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)',
    }
}

cuts['sr'] = {
    'expr': 'abs(mll-91)<15 && bVeto && detajj >= 3',
    'categories':{
        'ee': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11)',
        'mm': '(Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)',
    }
}
