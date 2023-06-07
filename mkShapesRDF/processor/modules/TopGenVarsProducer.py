import ROOT
from mkShapesRDF.processor.framework.Module import Module


class TopGenVarsProducer(Module):
    def __init__(self):
        super().__init__("TopGenVarsProducer")

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
            int TopSelect(ROOT::RVecI variable, ROOT::RVecF values){
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
            "top_mask", "(GenPart_pdgId == 6 && bitExpr(GenPart_statusFlags, 13))"
        )

        df = df.Define(
            "antitop_mask", "(GenPart_pdgId == -6 && bitExpr(GenPart_statusFlags, 13))"
        )

        df = df.Define("topGenPt", "TopSelect(top_mask, GenPart_pt)")

        df = df.Define("topGenEta", "TopSelect(top_mask, GenPart_eta)")

        df = df.Define("topGenPhi", "TopSelect(top_mask, GenPart_phi)")

        df = df.Define("topGenMass", "TopSelect(top_mask, GenPart_mass)")

        df = df.Define("antitopGenPt", "TopSelect(antitop_mask, GenPart_pt)")

        df = df.Define("antitopGenEta", "TopSelect(antitop_mask, GenPart_eta)")

        df = df.Define("antitopGenPhi", "TopSelect(antitop_mask, GenPart_phi)")

        df = df.Define("antitopGenMass", "TopSelect(antitop_mask, GenPart_mass)")

        df = df.DropColumns("top_mask")
        df = df.DropColumns("antitop_mask")

        return df
