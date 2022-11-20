cuts = {}

preselections = '          Lepton_pt[0]>30 \
                        && Lepton_pt[1]>20 \
                        && abs(Lepton_eta[0])<2.4 && abs(Lepton_eta[1])<2.4 \
                        && ((Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11) || (Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13)) \
                        && mll>76 \
                        && mll<106 \
                        && Alt(CleanJet_pt, 1, 0)>30 \
                        && abs(CleanJet_eta[0])<4.7 && abs(CleanJet_eta[1])<4.7 \
                        && abs(CleanJet_pt[0])>50 && abs(CleanJet_pt[1])>30 \
                        && mjj > 200 \
                        '
cuts['sr'] = {
    'expr': '1',
    'categories':{
        'ee': ' (Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11) \
                && abs(Lepton_eta[0])<2.1 && abs(Lepton_eta[1])<2.1 \
                ',
        'mm': ' (Lepton_pdgId[0]*Lepton_pdgId[1] == -13*13) \
                && abs(Lepton_eta[0])<2.4 && abs(Lepton_eta[1])<2.4 \
                '
    }
}
