import ROOT
from mkShapesRDF.processor.framework.Module import Module


class WGammaStarProducer(Module):
    def __init__(self):
        super().__init__("WGammaStarProducer")

    def runModule(self, df, values):
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
        '''

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecF findPairs(ROOT::RVecI lep_pdgId, ROOT::RVecF lep_pt, ROOT::RVecF lep_eta, ROOT::RVecF lep_phi){
                ROOT::RVecF gstar;

                float gstarmass = 999999.;

                for (int i = 0; i < lep_pdgId.size(); i ++){
                        for (int j = 0; j < lep_pdgId.size(); j ++){
                                if (lep_pdgId[i]*lep_pdgId[j]==-lep_pdgId[i]*lep_pdgId[i]){

                                        TLorentzVector tmp4V_1;
                                        TLorentzVector tmp4V_2;

                                        if (abs(lep_pdgId[i])==11){
                                                tmp4V_1.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], 0.0005);
                                                tmp4V_2.SetPtEtaPhiM(lep_pt[j], lep_eta[j], lep_phi[j], 0.0005);
                                        }else if (abs(lep_pdgId[i])==13){
                                            tmp4V_1.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], 0.106);
                                            tmp4V_2.SetPtEtaPhiM(lep_pt[j], lep_eta[j], lep_phi[j], 0.106);
                                        }
                                        if ((tmp4V_1+tmp4V_2).M()<gstarmass){
                                                gstarmass = (tmp4V_1+tmp4V_2).M();
                                                gstar = {lep_pt[i], lep_eta[i], lep_phi[i], float(lep_pdgId[i]), lep_pt[j], lep_eta[j], lep_phi[j], float(lep_pdgId[j])};
                                }
                            }
                        }
                }
                return gstar;  // It returns the indices of the leptons after appling the lepton mask
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecI getDaugtherId(int genpart_idx, ROOT::RVecI gen_pid, ROOT::RVecI gen_status, ROOT::RVecI gen_motherIdx, ROOT::RVecI daugthers_idx){

                if (gen_status[genpart_idx] == 1 || abs(gen_pid[genpart_idx]) == 15){
                        daugthers_idx.push_back(genpart_idx);
                }else{
                    for (uint i = 0; i < gen_motherIdx.size(); i++){
                            if (gen_motherIdx[i]==genpart_idx){
                                    daugthers_idx = getDaugtherId(i, gen_pid, gen_status, gen_motherIdx, daugthers_idx);
                            }
                    }
                }
                return daugthers_idx;
            }

            ROOT::RVecI getDaugthers(int genpart_idx, ROOT::RVecI gen_pid, ROOT::RVecI gen_status, ROOT::RVecI gen_motherIdx){
                ROOT::RVecI daugthers_idx;
                daugthers_idx = getDaugtherId(genpart_idx, gen_pid, gen_status, gen_motherIdx, daugthers_idx);
                return daugthers_idx;
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecI select_lep(ROOT::RVecI init_idx, ROOT::RVecI gen_pid){

                ROOT::RVecI lepton_idx;
                for (int k=0; k<init_idx.size(); k++){
                        if (abs(gen_pid[init_idx[k]])==11 || abs(gen_pid[init_idx[k]])==13 || abs(gen_pid[init_idx[k]])==15){
                                lepton_idx.push_back(init_idx[k]);
                        }
                }
                return lepton_idx;
            }
            """
        )

        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecF GetWGStar(ROOT::RVecI gen_pid, ROOT::RVecI gen_status, ROOT::RVecI gen_statusFlags, ROOT::RVecI gen_motherIdx, ROOT::RVecF gen_pt, ROOT::RVecF gen_eta, ROOT::RVecF gen_phi){

                float genDiLeptMassZGstar = -9999.0;
                float _ZGstarDiLept_DelaR = -9999.0;
                float elec1FromGstar_pt   = -9999.0;
                float elec1FromGstar_eta  = -9999.0;
                float elec1FromGstar_phi  = -9999.0;
                float elec2FromGstar_pt   = -9999.0;
                float elec2FromGstar_eta  = -9999.0;
                float elec2FromGstar_phi  = -9999.0;
                float muon1FromGstar_pt   = -9999.0;
                float muon1FromGstar_eta  = -9999.0;
                float muon1FromGstar_phi  = -9999.0;
                float muon2FromGstar_pt   = -9999.0;
                float muon2FromGstar_eta  = -9999.0;
                float muon2FromGstar_phi  = -9999.0;
                int mom_pdgId           = 9999;
                int mom_status          = 9999;

                bool fromG_HP = false;
                bool fromZ = false;
                bool fromW = false;
                bool fromG_PS = false;
                bool fromG = false;

                ROOT::RVecF gstar;

                ROOT::RVecI fromHardProcessLeptons;
                for (uint i = 0; i < gen_pid.size(); i++){

                        if (abs(gen_pid[i])==22 && bool(int(gen_statusFlags[i] >> 7) & 1)){
                                fromG_HP = true;
                                fromG_PS = false;
                                fromZ = false;
                                ROOT::RVecI daugthers;
                                ROOT::RVecI lepton_idx;
                                ROOT::RVecI lepton_pid;
                                ROOT::RVecF lepton_pt;
                                ROOT::RVecF lepton_eta;
                                ROOT::RVecF lepton_phi;
                                daugthers = getDaugthers(i, gen_pid, gen_status, gen_motherIdx);
                                lepton_idx = select_lep(daugthers, gen_pid);
                                lepton_pid = ROOT::VecOps::Take(gen_pid, lepton_idx);
                                lepton_pt = ROOT::VecOps::Take(gen_pt, lepton_idx);
                                lepton_eta = ROOT::VecOps::Take(gen_eta, lepton_idx);
                                lepton_phi = ROOT::VecOps::Take(gen_phi, lepton_idx);
                                gstar = findPairs(lepton_pid, lepton_pt, lepton_eta, lepton_phi);
                                if (gstar.size()!=0){
                                        mom_pdgId = gen_pid[i];
                                        mom_status = 0;
                                }
                        }
                        if (abs(gen_pid[i])==23 && !fromG_HP){
                                ROOT::RVecI daugthers;
                                ROOT::RVecI lepton_idx;
                                daugthers = getDaugthers(i, gen_pid, gen_status, gen_motherIdx);
                                lepton_idx = select_lep(daugthers, gen_pid);
                                ROOT::RVecI lepton_pid;
                                ROOT::RVecF lepton_pt;
                                ROOT::RVecF lepton_eta;
                                ROOT::RVecF lepton_phi;
                                lepton_pid = ROOT::VecOps::Take(gen_pid, lepton_idx);
                                lepton_pt = ROOT::VecOps::Take(gen_pt, lepton_idx);
                                lepton_eta = ROOT::VecOps::Take(gen_eta, lepton_idx);
                                lepton_phi = ROOT::VecOps::Take(gen_phi, lepton_idx);
                                gstar = findPairs(lepton_pid, lepton_pt, lepton_eta, lepton_phi);
                                if (gstar.size()!=0){
                                        fromZ = true;
                                        mom_pdgId = gen_pid[i];
                                        if (daugthers.size()==1){
                                                mom_status = 1;
                                        }else{
                                            mom_status = 2;
                                        }
                                }
                        }
                        if (abs(gen_pid[i])==24 && !fromG_HP && !fromZ){
                                ROOT::RVecI daugthers;
                                ROOT::RVecI lepton_idx;
                                daugthers = getDaugthers(i, gen_pid, gen_status, gen_motherIdx);
                                if (daugthers.size()!=4){
                                        continue;
                                }
                                lepton_idx = select_lep(daugthers, gen_pid);
                                ROOT::RVecI lepton_pid;
                                ROOT::RVecF lepton_pt;
                                ROOT::RVecF lepton_eta;
                                ROOT::RVecF lepton_phi;
                                lepton_pid = ROOT::VecOps::Take(gen_pid, lepton_idx);
                                lepton_pt = ROOT::VecOps::Take(gen_pt, lepton_idx);
                                lepton_eta = ROOT::VecOps::Take(gen_eta, lepton_idx);
                                lepton_phi = ROOT::VecOps::Take(gen_phi, lepton_idx);
                                gstar = findPairs(lepton_pid, lepton_pt, lepton_eta, lepton_phi);
                                if (gstar.size()!=0){
                                        fromW = true;
                                        mom_pdgId = gen_pid[i];
                                        mom_status = 4;
                                }
                        }
                        if (abs(gen_pid[i])==22 && !bool(int(gen_statusFlags[i] >> 8) & 1) && !fromG_HP && !fromZ && !fromW){
                                ROOT::RVecI daugthers;
                                ROOT::RVecI lepton_idx;
                                daugthers = getDaugthers(i, gen_pid, gen_status, gen_motherIdx);
                                if (daugthers.size()!=2){
                                        continue;
                                }
                                lepton_idx = select_lep(daugthers, gen_pid);
                                ROOT::RVecI lepton_pid;
                                ROOT::RVecF lepton_pt;
                                ROOT::RVecF lepton_eta;
                                ROOT::RVecF lepton_phi;
                                lepton_pid = ROOT::VecOps::Take(gen_pid, lepton_idx);
                                lepton_pt = ROOT::VecOps::Take(gen_pt, lepton_idx);
                                lepton_eta = ROOT::VecOps::Take(gen_eta, lepton_idx);
                                lepton_phi = ROOT::VecOps::Take(gen_phi, lepton_idx);
                                gstar = findPairs(lepton_pid, lepton_pt, lepton_eta, lepton_phi);
                                if (gstar.size()!=0){
                                        fromG =true;
                                        mom_pdgId = gen_pid[i];
                                        mom_status = 5;
                                }
                        }
                        if ((((abs(gen_pid[i])==11 || abs(gen_pid[i])==13) && gen_status[i]==1) || abs(gen_pid[i])==15) && bool(int(gen_statusFlags[i]) & 1)){
                                fromHardProcessLeptons.push_back(i);
                        }
                }
                if (!fromG_HP && !fromZ){
                        ROOT::RVecI lepton_idx;
                        lepton_idx = select_lep(fromHardProcessLeptons, gen_pid);
                        ROOT::RVecI lepton_pid;
                        ROOT::RVecF lepton_pt;
                        ROOT::RVecF lepton_eta;
                        ROOT::RVecF lepton_phi;
                        lepton_pid = ROOT::VecOps::Take(gen_pid, lepton_idx);
                        lepton_pt = ROOT::VecOps::Take(gen_pt, lepton_idx);
                        lepton_eta = ROOT::VecOps::Take(gen_eta, lepton_idx);
                        lepton_phi = ROOT::VecOps::Take(gen_phi, lepton_idx);
                        gstar = findPairs(lepton_pid, lepton_pt, lepton_eta, lepton_phi);
                        fromZ = true;
                        if (gstar.size()!=0){
                                mom_pdgId = 23;
                                mom_status = 3;
                        }
                }
                if (gstar.size()!=0){
                        TLorentzVector L1;
                        TLorentzVector L2;
                        if (abs(gstar[3]) == 13){
                                muon1FromGstar_pt = gstar[0];
                                muon1FromGstar_eta = gstar[1];
                                muon1FromGstar_phi = gstar[2];
                                muon2FromGstar_pt = gstar[4];
                                muon2FromGstar_eta = gstar[5];
                                muon2FromGstar_phi = gstar[6];
                                L1.SetPtEtaPhiM(gstar[0], gstar[1], gstar[2], 0.106);
                                L2.SetPtEtaPhiM(gstar[4], gstar[5], gstar[6], 0.106);
                                _ZGstarDiLept_DelaR = ROOT::VecOps::DeltaR(gstar[1], gstar[5], gstar[2], gstar[6]);
                                genDiLeptMassZGstar = (L1+L2).M();
                        }else{
                            elec1FromGstar_pt = gstar[0];
                            elec1FromGstar_eta = gstar[1];
                            elec1FromGstar_phi = gstar[2];
                            elec2FromGstar_pt = gstar[4];
                            elec2FromGstar_eta = gstar[5];
                            elec2FromGstar_phi = gstar[6];
                            L1.SetPtEtaPhiM(gstar[0], gstar[1], gstar[2], 0.0005);
                            L2.SetPtEtaPhiM(gstar[4], gstar[5], gstar[6], 0.0005);
                            _ZGstarDiLept_DelaR = ROOT::VecOps::DeltaR(gstar[1], gstar[5], gstar[2], gstar[6]);
                            genDiLeptMassZGstar = (L1+L2).M();
                        }
                }

                ROOT::RVecF results {genDiLeptMassZGstar, _ZGstarDiLept_DelaR, elec1FromGstar_pt  , elec1FromGstar_eta , elec1FromGstar_phi , elec2FromGstar_pt  , elec2FromGstar_eta , elec2FromGstar_phi , muon1FromGstar_pt  , muon1FromGstar_eta , muon1FromGstar_phi , muon2FromGstar_pt  , muon2FromGstar_eta , muon2FromGstar_phi , float(mom_pdgId) , float(mom_status)};
                return results;
            }
            """
        )

        df = df.Define(
            "Tmp_results",
            "GetWGStar(GenPart_pdgId, GenPart_status, GenPart_statusFlags, GenPart_genPartIdxMother, GenPart_pt, GenPart_eta, GenPart_phi)",
        )

        df = df.Define("Gen_ZGstar_mu1_pt", "Tmp_results[8]")

        df = df.Define("Gen_ZGstar_mu1_eta", "Tmp_results[9]")

        df = df.Define("Gen_ZGstar_mu1_phi", "Tmp_results[10]")

        df = df.Define("Gen_ZGstar_mu2_pt", "Tmp_results[11]")

        df = df.Define("Gen_ZGstar_mu2_eta", "Tmp_results[12]")

        df = df.Define("Gen_ZGstar_mu2_phi", "Tmp_results[13]")

        df = df.Define("Gen_ZGstar_ele1_pt", "Tmp_results[2]")

        df = df.Define("Gen_ZGstar_ele1_eta", "Tmp_results[3]")

        df = df.Define("Gen_ZGstar_ele1_phi", "Tmp_results[4]")

        df = df.Define("Gen_ZGstar_ele2_pt", "Tmp_results[5]")

        df = df.Define("Gen_ZGstar_ele2_eta", "Tmp_results[6]")

        df = df.Define("Gen_ZGstar_ele2_phi", "Tmp_results[7]")

        df = df.Define("Gen_ZGstar_mass", "Tmp_results[0]")

        df = df.Define("Gen_ZGstar_deltaR", "Tmp_results[1]")

        df = df.Define("Gen_ZGstar_MomId", "Tmp_results[14]")

        df = df.Define("Gen_ZGstar_MomStatus", "Tmp_results[15]")

        df = df.DropColumns("Tmp_results")

        return df
