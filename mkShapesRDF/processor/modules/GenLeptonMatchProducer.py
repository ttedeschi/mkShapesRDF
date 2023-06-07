import ROOT
from mkShapesRDF.processor.framework.Module import Module


class GenLeptonMatchProducer(Module):
    def __init__(self):
        super().__init__("GenLeptonMatchProducer")

    def runModule(self, df, values):
        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecB isMatched(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi, ROOT::RVecF genlep_pt, ROOT::RVecF genlep_eta, ROOT::RVecF genlep_phi, ROOT::RVecF genlep_pdgId, ROOT::RVecF genlep_status){
                ROOT::RVecB matched_leptons;
                for (uint i = 0; i < lep_pt.size(); i++){
                        TLorentzVector lepp4;
                        lepp4.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], 0);
                        TLorentzVector gen_lepp4;
                        bool matched = false;
                        for (uint j = 0; j < genlep_pt.size(); j++){
                                gen_lepp4.SetPtEtaPhiM(genlep_pt[j], genlep_eta[j], genlep_phi[j], 0.0);
                                if ((abs(genlep_pdgId[j]) == 11 || abs(genlep_pdgId[j]) == 13) && genlep_status[j] == 1 && gen_lepp4.DeltaR(lepp4)<0.3){
                                        matched = true;
                                }
                        }
                        matched_leptons.push_back(matched);
                }
                return matched_leptons;
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecB isPromptMatched(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi, ROOT::RVecF genlep_pt, ROOT::RVecF genlep_eta,
                                        ROOT::RVecF genlep_phi, ROOT::RVecF genlep_pdgId, ROOT::RVecF genlep_status, ROOT::RVecF genlep_isprompt, ROOT::RVecF genlep_istau){
                ROOT::RVecB matched_leptons;
                for (uint i = 0; i < lep_pt.size(); i++){
                        TLorentzVector lepp4;
                        lepp4.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], 0);
                        TLorentzVector gen_lepp4;
                        bool matched = false;
                        for (uint j = 0; j < genlep_pt.size(); j++){
                                gen_lepp4.SetPtEtaPhiM(genlep_pt[j], genlep_eta[j], genlep_phi[j], 0.0);
                                if ((abs(genlep_pdgId[j]) == 11 || abs(genlep_pdgId[j]) == 13) && genlep_status[j] == 1 && gen_lepp4.DeltaR(lepp4)<0.3 && (genlep_isprompt[j] || genlep_istau[j])){
                                        matched = true;
                                }
                        }
                        matched_leptons.push_back(matched);
                }
                return matched_leptons;
            }
            """
        )

        df = df.Define(
            "Lepton_genmatched",
            "isMatched(Lepton_pt, Lepton_eta, Lepton_phi, LeptonGen_pt, LeptonGen_eta, LeptonGen_phi, LeptonGen_pdgId, LeptonGen_status)",
        )

        df = df.Define(
            "Lepton_promptgenmatched",
            "isPromptMatched(Lepton_pt, Lepton_eta, Lepton_phi, LeptonGen_pt, LeptonGen_eta, LeptonGen_phi, LeptonGen_pdgId, LeptonGen_status, LeptonGen_isPrompt, LeptonGen_isDirectPromptTauDecayProduct)",
        )

        return df
