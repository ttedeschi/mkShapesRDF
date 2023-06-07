import ROOT
from mkShapesRDF.processor.framework.Module import Module


class DressedLeptonProducer(Module):
    def __init__(self, cone):
        super().__init__("DressedLeptonProducer")
        self.cone = cone

    def runModule(self, df, values):
        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecI doDressedIdx(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi, ROOT::RVecF lep_mass, ROOT::RVecI lep_pid, ROOT::RVecI lep_status, ROOT::RVecF photon_pt, ROOT::RVecF photon_eta, ROOT::RVecF photon_phi, float cone){

                ROOT::RVecI dressedIdx;

                for (uint i = 0; i<lep_pt.size(); i++){
                        TLorentzVector Lep;
                        Lep.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], lep_mass[i]);
                        float minDR = 99999.;
                        float closestPhoton = -1.;
                        for (uint j = 0; j<photon_pt.size(); j++){
                                TLorentzVector Pho;
                                Pho.SetPtEtaPhiM(photon_pt[j], photon_eta[j], photon_phi[j], 0.0);
                                if ((abs(lep_pid[i])==11 || abs(lep_pid[i])==13) && lep_status[i]==1 && Pho.DeltaR(Lep)<minDR){
                                        minDR = Pho.DeltaR(Lep);
                                        closestPhoton = j;
                                }

                        }

                        if (minDR < cone){
                                dressedIdx.push_back(closestPhoton);
                        }else{
                            dressedIdx.push_back(-1);
                        }
                }
                return dressedIdx;
            }
            """
        )

        df = df.Define(
            "LeptonGen_dressedphotonIdx",
            f"doDressedIdx(LeptonGen_pt, LeptonGen_eta, LeptonGen_phi, LeptonGen_mass, LeptonGen_pdgId, LeptonGen_status, PhotonGen_pt, PhotonGen_eta, PhotonGen_phi, {self.cone})",
        )

        ROOT.gInterpreter.Declare(
            """
            std::vector<ROOT::RVecF> doDressed(ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi, ROOT::RVecF lep_mass, ROOT::RVecF photon_pt, ROOT::RVecF photon_eta, ROOT::RVecF photon_phi, ROOT::RVecI dressedIdx){

                std::vector<ROOT::RVecF> dressed;
                for (uint k = 0; k<lep_pt.size(); k++){

                        if (dressedIdx[k]==-1){
                                ROOT::RVecF tmp;
                                TLorentzVector lep;
                                lep.SetPtEtaPhiM(lep_pt[k], lep_eta[k], lep_phi[k], lep_mass[k]);
                                tmp = {float(lep.Pt()), float(lep.Eta()), float(lep.Phi()), float(lep.M())};
                                dressed.emplace_back(tmp);
                        }else{
                            ROOT::RVecF tmp;
                            TLorentzVector pho;
                            pho.SetPtEtaPhiM(photon_pt[dressedIdx[k]], photon_eta[dressedIdx[k]], photon_phi[dressedIdx[k]], 0.0);

                            TLorentzVector lep;
                            lep.SetPtEtaPhiM(lep_pt[k], lep_eta[k], lep_phi[k], lep_mass[k]);

                            tmp = {float((lep+pho).Pt()), float((lep+pho).Eta()), float((lep+pho).Phi()), float((lep+pho).M())};
                            dressed.emplace_back(tmp);
                        }
                }
                return dressed;
            }
            """
        )

        df = df.Define(
            "DressedLepton_results",
            "doDressed(LeptonGen_pt, LeptonGen_eta, LeptonGen_phi, LeptonGen_mass, PhotonGen_pt, PhotonGen_eta, PhotonGen_phi, LeptonGen_dressedphotonIdx)",
        )

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecF getDressed_pt(std::vector<ROOT::RVecF> results){
                ROOT::RVecF dressed_pt;
                for (uint i = 0; i<results.size(); i++){
                        dressed_pt.push_back(results[i][0]);
                }
                return dressed_pt;
            }
           """
        )

        df = df.Define("DressedLepton_pt", "getDressed_pt(DressedLepton_results)")

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecF getDressed_eta(std::vector<ROOT::RVecF> results){
                ROOT::RVecF dressed_eta;
                for (uint i = 0; i<results.size(); i++){
                        dressed_eta.push_back(results[i][1]);
                }
                return dressed_eta;
            }
            """
        )

        df = df.Define("DressedLepton_eta", "getDressed_eta(DressedLepton_results)")

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecF getDressed_phi(std::vector<ROOT::RVecF> results){
                ROOT::RVecF dressed_phi;
                for (uint i = 0; i<results.size(); i++){
                        dressed_phi.push_back(results[i][2]);
                }
                return dressed_phi;
            }
            """
        )

        df = df.Define("DressedLepton_phi", "getDressed_phi(DressedLepton_results)")

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecF getDressed_mass(std::vector<ROOT::RVecF> results){
                ROOT::RVecF dressed_mass;
                for (uint i = 0; i<results.size(); i++){
                        dressed_mass.push_back(results[i][3]);
                }
                return dressed_mass;
            }
            """
        )

        df = df.Define("DressedLepton_mass", "getDressed_mass(DressedLepton_results)")

        df = df.Define("DressedLepton_pdgId", "LeptonGen_pdgId")

        df = df.DropColumns("LeptonGen_dressedphotonIdx")
        df = df.DropColumns("DressedLepton_results")

        return df
