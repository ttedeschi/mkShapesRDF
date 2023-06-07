import ROOT
from mkShapesRDF.processor.framework.Module import Module


class HiggsGenVarsProducer(Module):
    def __init__(self):
        super().__init__("HiggsGenVarsProducer")

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
            int HiggsSelect(ROOT::RVecI variable, ROOT::RVecF values){
                for (uint i = 0; i < variable.size(); i++){
                        if (variable[i]==true){
                           return values[i];
                    }
                }
                return -9999.0;
            }
            """
        )

        df = df.Define(
            "Higgs_mask", "GenPart_pdgId == 25 && bitExpr(GenPart_statusFlags, 13)"
        )

        df = df.Define("higgsGenPt", "HiggsSelect(Higgs_mask, GenPart_pt)")

        df = df.Define("higgsGenEta", "HiggsSelect(Higgs_mask, GenPart_eta)")

        df = df.Define("higgsGenPhi", "HiggsSelect(Higgs_mask, GenPart_phi)")

        df = df.Define("higgsGenMass", "HiggsSelect(Higgs_mask, GenPart_mass)")

        df = df.Define(
            "V_mask",
            "((abs(GenPart_pdgId) == 23 || abs(GenPart_pdgId) == 24) && bitExpr(GenPart_statusFlags, 13) && Take(GenPart_pdgId, GenPart_genPartIdxMother)!=25)",
        )

        df = df.Define("genVPt", "HiggsSelect(V_mask, GenPart_pt)")

        df = df.DropColumns("V_mask")
        df = df.DropColumns("Higgs_mask")

        return df
