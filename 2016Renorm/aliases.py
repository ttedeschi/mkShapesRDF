mc = [skey for skey in samples if skey not in ('Fake', 'DATA', 'Dyemb')]
mc_emb = [skey for skey in samples if skey not in ('Fake', 'DATA')]

eleWP = 'mva_90p_Iso2016'
muWP = 'cut_Tight80x_tthmva_80'

aliases = OrderedDict()




aliases['LepWPCut'] = {
            'expr': 'LepCut2l__ele_'+eleWP+'__mu_'+muWP,
            'samples': mc_emb + ['DATA']
            }
# Fake leptons transfer factor
aliases['fakeW'] = {
    'expr': 'fakeW2l_ele_'+eleWP+'_mu_'+muWP,
    'samples': ['Fake']
}


aliases['Jet_PUIDSF'] = { 
          'expr' : 'TMath::Exp(Sum((Jet_jetId>=2)*LogVec(Jet_PUIDSF_loose)))',
          'samples': mc
          }

aliases['gstarLow'] = {
    'expr': 'Gen_ZGstar_mass >0 && Gen_ZGstar_mass < 4',
    'samples': ['VgS']
}

aliases['gstarHigh'] = {
    'expr': 'Gen_ZGstar_mass <0 || Gen_ZGstar_mass > 4',
    'samples': ['VgS']
}
aliases['PromptGenLepMatch2l'] = {
            'expr': 'Alt(Lepton_promptgenmatched, 0, 0) * Alt(Lepton_promptgenmatched, 1, 0)',
            'samples': mc
            }

aliases['zeroJet'] = {
    'expr': 'Alt(CleanJet_pt, 0, 0) < 30.'
}

aliases['oneJet'] = {
    'expr': 'Alt(CleanJet_pt, 0, 0) > 30.'
}

aliases['multiJet'] = {
    'expr': 'Alt(CleanJet_pt, 1, 0) > 30.'
}

aliases['bVeto'] = {
    'expr': 'Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5 && Take(Jet_btagDeepB, CleanJet_jetIdx) > 0.2217) == 0'
}
aliases['bReq'] = { 
    'expr': 'Sum(CleanJet_pt > 30. && abs(CleanJet_eta) < 2.5 && Take(Jet_btagDeepB, CleanJet_jetIdx) > 0.2217) >= 1'
}

aliases['topcr'] = {
    'expr' : 'abs(mll-91)>15 && bReq'
}

aliases['bVetoSF'] = {
    'expr': 'TMath::Exp(Sum(LogVec((CleanJet_pt>20 && abs(CleanJet_eta)<2.5)*Take(Jet_btagSF_deepcsv_shape, CleanJet_jetIdx)+1*(CleanJet_pt<20 || abs(CleanJet_eta)>2.5))))',
    'samples': mc
}

aliases['bReqSF'] = {
    'expr': 'TMath::Exp(Sum(LogVec((CleanJet_pt>30 && abs(CleanJet_eta)<2.5)*Take(Jet_btagSF_deepcsv_shape, CleanJet_jetIdx)+1*(CleanJet_pt<30 || abs(CleanJet_eta)>2.5))))',
    #'expr': 'TMath::Exp(Sum(TMath::Log((CleanJet_pt>30 && abs(CleanJet_eta)<2.5)*Jet_btagSF_deepcsv_shape[CleanJet_jetIdx]+1*(CleanJet_pt<30 || abs(CleanJet_eta)>2.5))))',
    'samples': mc
}

aliases['btagSF'] = {
    #'expr': '(bVeto || (topcr && zeroJet))*bVetoSF + (topcr && !zeroJet)*bReqSF',
    'expr': 'bVeto*bVetoSF + topcr*bReqSF',
    'samples': mc
}

aliases['Top_pTrw'] = {
    'expr': '(topGenPt * antitopGenPt > 0.) * (TMath::Sqrt((0.103*TMath::Exp(-0.0118*topGenPt) - 0.000134*topGenPt + 0.973) * (0.103*TMath::Exp(-0.0118*antitopGenPt) - 0.000134*antitopGenPt + 0.973))) * (TMath::Sqrt(TMath::Exp(1.61468e-03 + 3.46659e-06*topGenPt - 8.90557e-08*topGenPt*topGenPt) * TMath::Exp(1.61468e-03 + 3.46659e-06*antitopGenPt - 8.90557e-08*antitopGenPt*antitopGenPt))) + (topGenPt * antitopGenPt <= 0.)', # Same Reweighting as other years, but with additional fix for tune CUET -> CP5
    'samples': ['top']
}

aliases['SFweight'] = {
            'expr': ' * '.join(['SFweight2l','LepWPCut', 'LepSF2l__ele_' + eleWP + '__mu_' + muWP, 'btagSF', 'PrefireWeight', 'Jet_PUIDSF']),
            'samples': mc
            }

"""
aliases['hardJets'] = {
    'expr': 'Jet_genJetIdx[CleanJet_jetIdx[0]] >= 0 && Jet_genJetIdx[CleanJet_jetIdx[1]] >= 0 && GenJet_pt[Jet_genJetIdx[CleanJet_jetIdx[0]]] > 25 && GenJet_pt[Jet_genJetIdx[CleanJet_jetIdx[1]]] > 25',
    'samples': ['DY']
}

aliases['PUJets'] = {
    'expr': '!(Jet_genJetIdx[CleanJet_jetIdx[0]] >= 0 && Jet_genJetIdx[CleanJet_jetIdx[1]] >= 0 && GenJet_pt[Jet_genJetIdx[CleanJet_jetIdx[0]]] > 25 && GenJet_pt[Jet_genJetIdx[CleanJet_jetIdx[1]]] > 25)',
    'samples': ['DY']
}
"""

aliases['ptj1'] = {
        'expr': 'Alt(CleanJet_pt, 0, -100)',
        'samples': mc + ['Fake', 'DATA']
        }

aliases['ptj2'] = {
        'expr': 'Alt(CleanJet_pt, 1, -100)',
        'samples': mc + ['Fake', 'DATA']
        }

aliases['etaj1'] = {
        'expr': 'Alt(CleanJet_eta, 0, -100)',
        'samples': mc + ['Fake', 'DATA']
        }

aliases['etaj2'] = {
        'expr': 'Alt(CleanJet_eta, 1, -100)',
        'samples': mc + ['Fake', 'DATA']
        }

aliases['DY_weight'] = {
            #'expr': 'hardJets * 0.90439916 + PUJets * 1.39377741',
            #'expr': 'hardJets *0.94624362 + PUJets * 0.75531033 ',
            #'expr': 'hardJets *0.91468444 + PUJets *1.06607322',
            #'expr': 'hardJets * 1.0 + PUJets * 1.0',
            'expr': '1.0',
            'samples': ['DY']
            }

aliases['top_weight'] = {
            #'expr': 'hardJets * 0.90439916 + PUJets * 1.39377741',
            #'expr': '1.22273458',
            'expr': '1.0',
            'samples': ['top']
            }

aliases['nJets'] = {
        'expr': 'Sum(CleanJet_pt > 20)',
        'samples': mc + ['Fake', 'DATA']
        }


aliases['R_jj'] = {
        'expr': 'TMath::Sqrt(TMath::Power(Alt(CleanJet_eta, 0,-9999.)-Alt(CleanJet_eta, 1,-9999.),2)+TMath::Power(Alt(CleanJet_phi, 0,-9999.)-Alt(CleanJet_phi, 1,-9999.),2))',
        'samples': mc + ['Fake', 'DATA']
}

