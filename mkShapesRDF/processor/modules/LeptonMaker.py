import ROOT

from mkShapesRDF.processor.framework.module import Module


class LeptonMaker(Module):
    def __init__(self, min_lep_pt=10.0):
        super().__init__("LeptonMaker")
        self.min_lep_pt = min_lep_pt

    def runModule(self, df, values):
        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecI sortedIndices(ROOT::RVecF variable){
                // return sortedIndices based on variable
                return Reverse(Argsort(variable));
            }
        """
        )
        # df = df.Filter("(nElectron + nMuon) >= 1")

        df = df.Define("Lepton_pt", "ROOT::VecOps::Concatenate(Electron_pt, Muon_pt)")
        df = df.Define("Lepton_sorting", "sortedIndices(Lepton_pt)")
        df = df.Redefine("Lepton_pt", "Take(Lepton_pt, Lepton_sorting)")

        Lepton_var = ["eta", "phi", "pdgId"]
        for prop in Lepton_var:
            df = df.Define(
                f"Lepton_{prop}",
                f"ROOT::VecOps::Concatenate(Electron_{prop}, Muon_{prop})",
            )
            df = df.Redefine(f"Lepton_{prop}", f"Take(Lepton_{prop}, Lepton_sorting)")

        # special treatment for ElectronIdx and muonIdx
        df = df.Define(
            "Lepton_electronIdx",
            "ROOT::VecOps::Concatenate((ROOT::RVecI)ROOT::VecOps::Range(nElectron) , ROOT::RVecI(nMuon, -1))",
        )
        df = df.Redefine(
            "Lepton_electronIdx", "Take(Lepton_electronIdx, Lepton_sorting)"
        )

        df = df.Define(
            "Lepton_muonIdx",
            "ROOT::VecOps::Concatenate(ROOT::RVecI(nElectron, -1), (ROOT::RVecI)ROOT::VecOps::Range(nMuon))",
        )
        df = df.Redefine("Lepton_muonIdx", "Take(Lepton_muonIdx, Lepton_sorting)")

        df = df.Filter(f"Lepton_pt[0] > {self.min_lep_pt}")

        df = df.Define("VetoLepton_pt", "Lepton_pt")
        for prop in Lepton_var + ["electronIdx", "muonIdx"]:
            df = df.Define(f"VetoLepton_{prop}", f"Lepton_{prop}")

        # DEBUGGIN AND CHECKS

        values.append(
            [
                df.Define("test", "Sum(Electron_pt) + Sum(Muon_pt)").Sum("test"),
                "Sum of Ele_pt and Muon_pt",
            ]
        )
        values.append(
            [
                df.Define("test", "Electron_pt.size() + Muon_pt.size()").Sum("test"),
                "Sum of size of Ele_pt and Muon_pt",
            ]
        )

        values.append(
            [df.Define("test", "Sum(Lepton_pt)").Sum("test"), "sum lepton pt"]
        )

        values.append(
            [df.Define("test", "Lepton_pt.size()").Sum("test"), "lepton pt size"]
        )

        df = df.DropColumns("Lepton_sorting")

        # //////////////////////////////////////// #
        # // CleanJets Columns Definitions   
        df = df.Define("isCleanJet", "ROOT::RVecB(Jet_pt.size(), true)")
        df = df.Define("CleanJet_pt", "Jet_pt[isCleanJet]")
        df = df.Define("CleanJet_sorting", "sortedIndices(CleanJet_pt)")
        df = df.Define("CleanJet_jetIdx", "ROOT::VecOps::Range(nJet)[isCleanJet]")
        df = df.Redefine("CleanJet_jetIdx", "Take(CleanJet_jetIdx, CleanJet_sorting)")

        CleanJet_var = ["eta", "phi", "mass"]
        for prop in CleanJet_var:
            df = df.Define(f"CleanJet_{prop}", f"Jet_{prop}[isCleanJet]")
            df = df.Redefine(
                f"CleanJet_{prop}", f"Take(CleanJet_{prop}, CleanJet_sorting)"
            )

        # //////////////////////////////////////// #
        # // CleanFatJets Columns Definitions   
        df = df.Define("isCleanFatJet", "ROOT::RVecB(FatJet_pt.size(), true)")
        df = df.Define("CleanFatJet_pt", "FatJet_pt[isCleanFatJet]")
        df = df.Define("CleanFatJet_sorting", "sortedIndices(CleanFatJet_pt)")
        df = df.Define("CleanFatJet_jetIdx", "ROOT::VecOps::Range(nFatJet)[isCleanFatJet]")
        df = df.Redefine("CleanFatJet_jetIdx", "Take(CleanFatJet_jetIdx, CleanFatJet_sorting)")
        FatJet_vars = ["eta", "phi", "mass", "jetId", "msoftdrop", "tau1", "tau2"]
        for var in FatJet_vars:
            df = df.Define(f"CleanFatJet_{var}", f"FatJet_{var}[isCleanFatJet]")
            df = df.Redefine(
                f"CleanFatJet_{var}", f"Take(CleanFatJet_{var}, CleanFatJet_sorting)"
            )
        df = df.Define("CleanFatJet_tau21", "CleanFatJet_tau1/CleanFatJet_tau2")
        df = df.Redefine("CleanFatJet_tau21", f"Take(CleanFatJet_tau21, CleanFatJet_sorting)")
        # //////////////////////////////////////// #

        return df


