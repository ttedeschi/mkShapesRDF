from mkShapesRDF.processor.framework.module import Module
import correctionlib._core as core

# module to clean fatjets
# clean fatjets with kinamatic cuts: min_pt, max_eta, max_tau21, mass_range of reconstructed Jet
# check overlapping with leptons 
# check if FatJets overlaps with Jet, radius distance must be set. 

#
# passing elements of a dictionary ???
# to move on a configuration file in ../processor/data/
FatJetFilter_dict = {
   'default' : { 'pt_min': 200.0 , 'pt_max' : 0, 'max_eta' : 2.4, 'max_tau21': 0.45, 'mass_range' : [65 , 105],
               'DeltaRlep' : 0.8, 'DeltaRjet' : 0.8, 'jet_id' : 0},
}

# da aggiungere in lepton maker : tau21
class FatJetSel(Module):
    def __init__(self, Era = "default", FatJetFilter_dict):
        cuts = FatJetFilter_dict[Era]
        super().__init__("FatJetSel")   
        self.max_pt = cuts['pt_max']
        self.min_pt = cuts['pt_min']
        self.max_eta = cuts['max_eta']
        self.max_tau21 = cuts['max_tau21'] # ratio between tau1 and tau2 for N subjettiness algorithm 
        self.mass_range = cuts['mass_range']
        self.DeltaRjet = cuts['DeltaRjet']
        self.DeltaRlep = cuts['DeltaRlep']
        self.jet_id = cuts['jet_id']

    
    def getDeltaR(self, phi1, phi2, eta1, eta2):
        dphi = phi1 - phi2
        if dphi > ROOT.TMath.Pi(): dphi -= 2*ROOT.TMath.Pi()
        if dphi < -ROOT.TMath.Pi(): dphi += 2*ROOT.TMath.Pi()
        deta = eta1 - eta2
        deltaR = sqrt((deta*deta) + (dphi*dphi))
        return deltaR

    def CheckCuts(self, df):
        # ***** not defined in LeptonMaker, deleted at the end ***** #
        columnsToDrop = []
        cut_variables = ["tau1", "tau2"]
        columns = df.GetColumnNames()
        for i in cut_variables:
            if f"CleanFatJet_{i}" not in columns:
                columnsToDrop.append(f"CleanFatJet_{i}")
                df = df.Define(f"CleanFatJet_{i}", f"FatJet_{i}[isCleanFatJet]" )
                df = df.Redefine(f"CleanFatJet_{i}", f"Take(CleanFatJet_{i}, CleanFatJet_sorting)")
        df = df.Define(f"CleanFatJet_tau21", "CleanFatJet_tau1/CleanFatJet_tau2")
        df = df.Redefine("CleanFatJet_tau21", "Take(CleanFatJet_tau21, CleanFatJet_sorting)")
        columnsToDrop.append(f"CleanFatJet_tau21")
        # ********************************************************** #
 
        goodFatJet = f"CleanFatJet_pt >= {self.min_pt} && CleanFatJet_pt <= {self.max_pt} && " +
                     f"abs(CleanFatJet_eta) <= {self.max_eta}) && " + 
                     f"(CleanFatJet_tau21 <= {self.max_tau21} && CleanFatJet_tau1 > 0) && " +
                     f"CleanFatJet_msoftdrop >= {self.mass_range[0]} && CleanFatJet_msoftdrop <= {self.mass_range[1]} && " +
                     f"CleanFatJet_Id > {self.jetid} && " + 
                     f"CheckDeltaR({self.getDeltaR(CleanFatJet_phi, Lepton_phi, CleanFatJet_eta, Lepton_eta)}, {self.DeltaRlep}) && " +
                     f"CheckDeltaR({self.getDeltaR(CleanFatJet_phi, CleanJet_phi, CleanFatJet_eta, CleanJet_eta)},{self.DeltaRjet})"
        return goodFatJet, columnsToDrop

    def runModule(self, df, values):
        columnsToDrop = []

        CheckDeltaR = ("""
         bool CheckDeltaR(double deltaR, double DeltaRcuts) {
            return deltaR < DeltaRcuts;
         }
        """)
        ROOT.gInterpreter.Declare(CheckDeltaR)

        # apply mask 
        cut_FatJets, columnsToDrop  = self.CheckCuts(df)
        df = df.Define("CleanFatJetMask", cut_FatJets)  

    # CleanJet not fat, CleanJet-CleanFatJet distance 
        df = df.Define("isCleanJetNotFat", f"! CheckDeltaR({self.getDeltaR(CleanFatJet_phi, CleanJet_phi, CleanFatJet_eta, CleanJet_eta)}, {self.DeltaRjet})")
        df = df.Define("CleanJetNotFat_idx", "CleanJet_jetIdx[isCleanJetNotFat]")
        df = df.Define("CleanJetNotFat_deltaR", f"{self.getDeltaR(CleanFatJet_phi, CleanJet_phi, CleanFatJet_eta, CleanJet_eta)}[isCleanJetNotFat]")

        CleanFatJet_variables = ["jetId", "pt", "eta", "mass", "msoftdrop"]
        for var in CleanFatJet_variables:
            df = df.Redefine(
                f"CleanFatJet_{var}", f"CleanFatJet_{var}[CleanFatJetMask]"
            )

        for col in columnsToDrop:
            df = df.DropColumns(col)


        return df
