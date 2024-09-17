import ROOT
from mkShapesRDF.processor.framework.module import Module
#from mkShapesRDF.processor.modules.LeptonMaker import LeptonMaker 


# Dictionary for FatJet cuts  
FatJetFilter_dict = {
   'default' : { 'pt_min': 0 , 'pt_max' : 5000, 'max_eta' : 2.4, 'max_tau21': 1000, 'mass_range' : [0 , 10000],
               'DeltaRlep' : 0.4, 'DeltaRjet' : 0.4, 'jet_id' : 0},
}

class FatJetSel(Module):

    def __init__(self, Mask=True, dict=FatJetFilter_dict, Era = "default"):
        super().__init__("FatJetSel")   
        cuts = dict[Era]
        self.max_pt = cuts['pt_max']
        self.min_pt = cuts['pt_min']
        self.max_eta = cuts['max_eta']
        self.max_tau21 = cuts['max_tau21']
        self.mass_range = cuts['mass_range']
        self.DeltaRjet = cuts['DeltaRjet']
        self.DeltaRlep = cuts['DeltaRlep']
        self.jet_id = cuts['jet_id']
        #self.lepMake = LeptonMaker(10)



    def CheckCuts(self, df): 
        goodFatJet =( f"CleanFatJet_pt >= {self.min_pt} && CleanFatJet_pt <= {self.max_pt} && " +
                     f"abs(CleanFatJet_eta) <= {self.max_eta} && " + 
                     f"(CleanFatJet_tau21 <= {self.max_tau21} && CleanFatJet_tau1 > 0) && " +
                     f"CleanFatJet_msoftdrop >= {self.mass_range[0]} && CleanFatJet_msoftdrop <= {self.mass_range[1]} && " +
                     f"CleanFatJet_jetId > {self.jet_id} && " +
                     f"CheckDeltaR(CleanFatJet_phi, CleanJet_phi, CleanFatJet_eta, CleanJet_eta, {self.DeltaRjet})"
                    )
        return goodFatJet


    # *********************************************************** #
    # ********************* RUN MODULE ************************** #
    # *********************************************************** #
    def runModule(self, df, values):
        columnsToDrop = []

        # // Define CLeanJet, CleanFatJet, Lepton columns
        # df = self.lepMake.runModule(df, values)
        '''
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

        columnsToDrop.append("isCleanJet")
        columnsToDrop.append("CleanJet_sorting")  
        # //////////////////////////////////////// #
 

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

        columnsToDrop.append("isCleanFatJet")
        columnsToDrop.append("CleanFatJet_sorting")
        columnsToDrop.append("CleanFatJet_tau21")
        # //////////////////////////////////////// #

        '''
        # //////////////////////////////////////// #
        # // apply cuts 
        CheckDeltaR = (""" 
         ROOT::RVec<Bool_t> CheckDeltaR(ROOT::RVec<double> phi1, ROOT::RVec<double> phi2, ROOT::RVec<double> eta1, ROOT::RVec<double> eta2, double DeltaRcuts) {
         ROOT::RVec<double> deltaR_values;
         for (size_t i = 0; i <  phi1.size() ; ++i) {
            double dphi = phi1[i] - phi2[i];
            if (dphi > ROOT::Math::Pi()) dphi -= 2 * ROOT::Math::Pi();
            if (dphi < -ROOT::Math::Pi()) dphi += 2 * ROOT::Math::Pi();
            double deta = eta1[i] - eta2[i];
            double deltaR = sqrt(deta*deta + dphi*dphi);
            deltaR_values.push_back(deltaR < DeltaRcuts);
         }
        return deltaR_values;
        }
        """)
        ROOT.gInterpreter.Declare(CheckDeltaR)   
        

        cut_FatJets  = self.CheckCuts(df)
        df = df.Define("CleanFatJetMask", cut_FatJets)  
        # //////////////////////////////////////// #

        # store jets that are not fatjets
        df = df.Define("isCleanJetNotFat", f" ! CheckDeltaR(CleanJet_phi, CleanFatJet_phi, CleanJet_eta, CleanFatJet_eta, {self.DeltaRjet})")
       # df = df.Define("CleanJetNotFat_Idx", "CleanJet_jetIdx[isCleanJetNotFat]")
        df = df.Define("isLeptonNotFat", f" ! CheckDeltaR(Lepton_phi, CleanFatJet_phi, Lepton_eta, CleanFatJet_eta, {self.DeltaRjlep})")
        df = df.Define("MuonNotFat_Idx", "Lepton_electronIdx[isLeptonNotFat]")
        df = df.Define("ElectronNotFat_Idx", "Lepton_muonIdx[isLeptonNotFat]")
    


        # apply mask
        CleanFatJet_variables = ["jetId",  "pt", "eta", "mass", "phi" , "msoftdrop", "tau1", "tau2", "tau21"]
        for var in CleanFatJet_variables:
            df = df.Redefine(
                f"CleanFatJet_{var}", f"CleanFatJet_{var}[CleanFatJetMask]"
            )

    
        # remove columns
        ''' 
        columnsToDrop.extend(DroppedColumns)
        for col in columnsToDrop:
            df = df.DropColumns(col)
        '''
        return df
    # ********************* END RUN MODULE *********************** #
    # ************************************************************ #
