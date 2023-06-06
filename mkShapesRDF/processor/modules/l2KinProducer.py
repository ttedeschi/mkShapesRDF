from mkShapesRDF.processor.framework.module import Module


class l2KinProducer(Module):
    def __init__(self):
        super().__init__("l2KinProducer")

    def runModule(self, df, values):
        df = df.Define(
            "Lepton_4DV",
            "ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>"
            "(Lepton_pt, Lepton_eta, Lepton_phi, "
            "ROOT::RVecF(Lepton_pt.size(), 0))",
        )

        df = df.Define(
            "CleanJet_4DV",
            "ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>"
            "(CleanJet_pt, CleanJet_eta, CleanJet_phi, "
            "Take(Jet_mass, CleanJet_jetIdx))",
        )

        df = df.Define(
            "MET_4DV", "ROOT::Math::PtEtaPhiMVector" "(PuppiMET_pt, 0, PuppiMET_phi, 0)"
        )

        df = df.Define(
            "TkMET_4DV", "ROOT::Math::PtEtaPhiMVector" "(TkMET_pt, 0, TkMET_phi, 0)"
        )

        df = df.Define("_isOk", "Lepton_pt[Lepton_pt > 0].size() >= 2 && MET_4DV.E()>0")
        df = df.Define("_lepOk", "Lepton_pt[Lepton_pt > 0].size()")
        df = df.Define("_tkMetOk", "TkMET_4DV.E() > 0")
        df = df.Define("_jetOk", "CleanJet_pt[CleanJet_pt > 0].size()")

        # FIXME complete l2kin module!

        # dilepton variables
        prefix = "new_fw_"
        df = df.Define(
            prefix + "ptll", "_isOk ? (Lepton_4DV[0] + Lepton_4DV[1]).Pt() : -9999.0"
        )
        df = df.Define(
            prefix + "mll", "_isOk ? (Lepton_4DV[0] + Lepton_4DV[1]).M() : -9999.0"
        )
        df = df.Define(
            prefix + "dphill",
            "_isOk ? DeltaPhi(Lepton_phi[0], Lepton_phi[1]) : -9999.0",
        )
        df = df.Define(
            prefix + "drll",
            "_isOk ? DeltaR(Lepton_eta[0], Lepton_eta[1], Lepton_phi[0], Lepton_phi[1]) : -9999.0",
        )
        df = df.Define(
            prefix + "detall", "_isOk ? abs(Lepton_eta[0] - Lepton_eta[1]) : -9999.0"
        )

        df = df.Define(prefix + "pt1", "Lepton_pt[0] > 0 ? Lepton_pt[0] : -9999.0")
        df = df.Define(prefix + "eta1", "Lepton_pt[0] > 0 ? Lepton_eta[0] : -9999.0")
        df = df.Define(prefix + "phi1", "Lepton_pt[0] > 0 ? Lepton_phi[0] : -9999.0")
        df = df.Define(prefix + "pt2", "_isOk ? Lepton_pt[1] : -9999.0")
        df = df.Define(prefix + "eta2", "_isOk ? Lepton_eta[1] : -9999.0")
        df = df.Define(prefix + "phi2", "_isOk ? Lepton_phi[1] : -9999.0")

        # dijets variables
        df = df.Define(
            prefix + "njet",
            "CleanJet_pt [CleanJet_pt > 30 && CleanJet_eta < 4.7].size()",
        )
        df = df.Define(
            prefix + "ptjj",
            "_jetOk >=2 ? (CleanJet_4DV[0] + CleanJet_4DV[1]).Pt() : -9999.0",
        )
        df = df.Define(
            prefix + "mjj",
            "_jetOk >=2 ? (CleanJet_4DV[0] + CleanJet_4DV[1]).M() : -9999.0",
        )
        df = df.Define(
            prefix + "dphijj",
            "_jetOk >= 2 ? DeltaPhi(CleanJet_phi[0], CleanJet_phi[1]) : -9999.0",
        )
        df = df.Define(
            prefix + "drjj",
            "_isOk ? DeltaR(CleanJet_eta[0], CleanJet_eta[1], CleanJet_phi[0], CleanJet_phi[1]) : -9999.0",
        )
        df = df.Define(
            prefix + "detajj",
            "_jetOk >=2 ? abs(CleanJet_eta[0] - CleanJet_eta[1]) : -9999.0",
        )
        df = df.DropColumns("Lepton_4DV")
        df = df.DropColumns("CleanJet_4DV")
        df = df.DropColumns("MET_4DV")
        df = df.DropColumns("TkMET_4DV")

        df = df.DropColumns("_isOk")
        df = df.DropColumns("_lepOk")
        df = df.DropColumns("_tkMetOk")
        df = df.DropColumns("_jetOk")

        return df
