import ROOT
from mkShapesRDF.processor.framework.Module import Module


class GenVarProducer(Module):
    def __init__(self):
        super().__init__("GenVarProducer")

    def runModule(self, df, values):
        ### Redefinition here  # noqa: E266
        '''
        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecB bitExpr(ROOT::RVecF variable, int vvalue){
                ROOT::RVecB r;
                bool c = false;
                for (uint i = 0; i < variable.size(); i++){
                    if (vvalue == 0){
                        c = bool(int(variable[i]) & 1);
                    }else{
                        c = bool((int(variable[i]) >> vvalue) & 1);
                        r.push_back(c);
                    }
                }
                return r;
            }
            """
        )


        ROOT.gInterpreter.Declare(
            """
            bool noMother(ROOT::RVecI variable){
                bool no_mother = false;
                for (uint i = 0; i < variable.size(); i++){
                    if (variable[i]>-1){
                        continue;
                    }else{
                        no_mother = true;
                    }
                }
                return no_mother;
            }
            """
        )
        '''

        # GenPart_statusFlags     Int_t   gen status flags stored bitwise, bits are: 0 : isPrompt, 1 : isDecayedLeptonHadron, 2 : isTauDecayProduct, 3 : isPromptTauDecayProduct, 4 : isDirectTauDecayProduct, 5 : isDirectPromptTauDecayProduct, 6 : isDirectHadronDecayProduct, 7 : isHardProcess, 8 : fromHardProcess, 9 : isHardProcessTauDecayProduct, 10 : isDirectHardProcessTauDecayProduct, 11 : fromHardProcessBeforeFSR, 12 : isFirstCopy, 13 : isLastCopy, 14 : isLastCopyBeforeFSR,

        df = df.Define(
            "LeptonGen_mask",
            "((abs(GenPart_pdgId) == 11 || abs(GenPart_pdgId) == 13) && (bitExpr(GenPart_statusFlags, 0) || bitExpr(GenPart_statusFlags, 2) || bitExpr(GenPart_statusFlags, 3) || bitExpr(GenPart_statusFlags, 4)))",
        )

        Quantities = ["pt", "eta", "phi", "pdgId"]

        for prop in Quantities:
            df = df.Define(f"LeptonGenTmp_{prop}", f"GenPart_{prop}[LeptonGen_mask]")

        ROOT.gInterpreter.Declare(
            """
            float gen_ptllmet(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi, float met_pt, float met_phi){
                if (lep_pt[lep_pt > 0.f].size() < 2){
                        return -9999.0;
                }
                TLorentzVector L1,L2;
                L1.SetPtEtaPhiM(lep_pt[0], lep_eta[0], lep_phi[0], 0.0);
                L2.SetPtEtaPhiM(lep_pt[1], lep_eta[1], lep_phi[1], 0.0);
                TLorentzVector MET;
                MET.SetPtEtaPhiM(met_pt , 0, met_phi, 0.);
                return (L1+L2+MET).Pt();
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            float gen_mlvlv(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi, float met_pt, float met_phi){
                if (lep_pt[lep_pt > 0.f].size() < 2){
                        return -9999.0;
                }
                TLorentzVector L1,L2;
                L1.SetPtEtaPhiM(lep_pt[0], lep_eta[0], lep_phi[0], 0.0);
                L2.SetPtEtaPhiM(lep_pt[1], lep_eta[1], lep_phi[1], 0.0);
                TLorentzVector MET;
                MET.SetPtEtaPhiM(met_pt , 0, met_phi, 0.);
                return (L1+L2+MET).M();
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            float gen_ptll(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi){
                if (lep_pt[lep_pt > 0.f].size() < 2){
                        return -9999.0;
                }
                TLorentzVector L1,L2;
                L1.SetPtEtaPhiM(lep_pt[0], lep_eta[0], lep_phi[0], 0.0);
                L2.SetPtEtaPhiM(lep_pt[1], lep_eta[1], lep_phi[1], 0.0);
                return (L1+L2).Pt();
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            float gen_mll(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi){
                if (lep_pt[lep_pt > 0.f].size() < 2){
                        return -9999.0;
                }
                TLorentzVector L1,L2;
                L1.SetPtEtaPhiM(lep_pt[0], lep_eta[0], lep_phi[0], 0.0);
                L2.SetPtEtaPhiM(lep_pt[1], lep_eta[1], lep_phi[1], 0.0);
                return (L1+L2).M();
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            int gen_llchannel(ROOT::RVecF lep_pt, ROOT::RVecF lep_pid){
                if (lep_pt[lep_pt > 0.f].size() < 2){
                        return -9999.0;
                }
                return lep_pid[0]*lep_pid[1];
            }
            """
        )

        df = df.Define(
            "gen_ptllmet",
            "gen_ptllmet(LeptonGenTmp_pt, LeptonGenTmp_eta, LeptonGenTmp_phi, GenMET_pt, GenMET_phi)",
        )

        df = df.Define(
            "gen_mlvlv",
            "gen_mlvlv(LeptonGenTmp_pt, LeptonGenTmp_eta, LeptonGenTmp_phi, GenMET_pt, GenMET_phi)",
        )

        df = df.Define(
            "gen_ptll", "gen_ptll(LeptonGenTmp_pt, LeptonGenTmp_eta, LeptonGenTmp_phi)"
        )

        df = df.Define(
            "gen_mll", "gen_mll(LeptonGenTmp_pt, LeptonGenTmp_eta, LeptonGenTmp_phi)"
        )

        df = df.Define(
            "gen_llchannel", "gen_llchannel(LeptonGenTmp_pt, LeptonGenTmp_pdgId)"
        )

        df = df.DropColumns("LeptonGen_mask")
        df = df.DropColumns("LeptonGenTmp_*")

        return df
