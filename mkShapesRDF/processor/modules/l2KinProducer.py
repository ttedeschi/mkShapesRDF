from mkShapesRDF.processor.framework.Module import Module


class l2KinProducer(Module):
    def __init__(self):
        super().__init__("l2KinProducer")
        
    def runModule(self, df, values):
        df = df.Define('Lepton_4DV',
                       'ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>'
                       '(Lepton_pt, Lepton_eta, Lepton_phi, '
                       'ROOT::RVecF(Lepton_pt.size(), 0))'
                       )

        df = df.Define('CleanJet_4DV',
                       'ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>'
                       '(CleanJet_pt, CleanJet_eta, CleanJet_phi, '
                       'Take(Jet_mass, CleanJet_jetIdx))'
                       )

        df = df.Define('MET_4DV',
                       'ROOT::Math::PtEtaPhiMVector'
                       '(PuppiMET_pt, 0, PuppiMET_phi, 0)')

        df = df.Define('TkMET_4DV',
                       'ROOT::Math::PtEtaPhiMVector'
                       '(TkMET_pt, 0, TkMET_phi, 0)')

        # df = df.Define('Lep_ok', '(Lepton_pt[Lepton_pt > 0].size() >= 2))
        # df = df.Define(' ', '(MET_4DV.E() > 0) && '
        #                '(TkMET_4DV.E() > 0) && '
        #                '(CleanJet_pt[CleanJet_pt > 0].size() >= 1)')
        
        df.DropColumns('Lepton_4DV')
        df.DropColumns('CleanJet_4DV')
        df.DropColumns('MET_4DV')
        df.DropColumns('TkMET_4DV')

        return df
