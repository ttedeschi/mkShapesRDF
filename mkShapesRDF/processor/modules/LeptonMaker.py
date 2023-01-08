import ROOT

def run(df, values, keepColumns):
    ROOT.gInterpreter.Declare("""
    ROOT::RVecF mergeLeptons(ROOT::RVecF ele_pt, ROOT::RVecF mu_pt){
        ROOT::RVecF pt (ele_pt.size() + mu_pt.size());
        for (uint i = 0; i < (unsigned int) (ele_pt.size() + mu_pt.size()); i++){
            if (i < ele_pt.size())
                pt[i] = ele_pt[i];
            else
                pt[i] = mu_pt[i];
        }
        return pt;
    }

    ROOT::RVecI sortedLeptons(ROOT::RVecF lep_pt){
        auto v1_indices = Argsort(lep_pt);
        return Reverse(v1_indices);
        //return Take(lep_pt, Reverse(v1_indices));
    }

    ROOT::RVecF sortedLeptonsColl(ROOT::RVecI indices, ROOT::RVecF coll){
        return Take(coll, indices); 
    }
    """)

    values.append(
            [df.Count(), 'begin count of LeptonMaker']
            )
    a = len(values)-1

    df = df.Filter('(nElectron + nMuon) >= 1')

    values.append(
            [df.Define('prova', 'Sum(Electron_pt) + Sum(Muon_pt)').Sum('prova'), 'Sum of Ele_pt and Muon_pt']
            )
    values.append(
            [df.Define('prova', 'Electron_pt.size() + Muon_pt.size()').Sum('prova'), 'Sum of size of Ele_pt and Muon_pt']
            )
    df = df.Define('Leptons_pt_unsort', 'mergeLeptons(Electron_pt, Muon_pt)')
    df = df.Define('Leptons_sorting', 'sortedLeptons(Leptons_pt_unsort)')
    df = df.Define('Leptons_pt', 'sortedLeptonsColl(Leptons_sorting, Leptons_pt_unsort)')
    keepColumns.append('Leptons_pt')
    df = df.Filter('Leptons_pt[0] >= 10')

    properties = ['eta', 'phi', 'pdgId']
    for prop in properties:
        df = df.Define(f'Leptons_{prop}_unsort', f'mergeLeptons(Electron_{prop}, Muon_{prop})')
        df = df.Define(f'Leptons_{prop}', f'sortedLeptonsColl(Leptons_sorting, Leptons_{prop}_unsort)')
        keepColumns.append('Leptons_{prop}')

    #df = df.Filter('Leptons_pt[0] >= Alt(Leptons_pt, 1, 10)')

    values.append(
            [df.Define('prova', 'Sum(Leptons_pt)').Sum('prova'), 'sum lepton pt']
            )

    values.append(
            [df.Define('prova', 'Leptons_pt.size()').Sum('prova'), 'lepton pt size']
            )

    values.append(
            [df.Count(), 'Count at the end of LeptonMaker']
            )
    b = len(values)-1

    def fun(a, b):
        bVal = values[b] 
        aVal = values[a] 
        if 'list' in str(type(bVal)):
            bVal = bVal[0]
        if 'list' in str(type(aVal)):
            aVal = aVal[0]
        return ['Efficiency of 1 lep cut', str(round(bVal.GetValue()/aVal.GetValue()*100, 3)) + '%']

    values.append([fun, a, b])
    return df
