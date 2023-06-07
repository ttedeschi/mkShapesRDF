import ROOT
from mkShapesRDF.processor.framework.Module import Module


class PromptParticlesGenVarsProducer(Module):
    def __init__(self):
        super().__init__("PromptParticlesGenVarsProducer")

    def runModule(self, df, values):
        '''
        ROOT.gInterpreter.Declare(
            """
            ROOT::RVecI sortedIndices(ROOT::RVecF variable){
                // return sortedIndices based on variable
                return Reverse(Argsort(variable));
            }
            """
        )
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
                    }
                    r.push_back(c);
                }
                return r;
            }
            """
        )

        particleTypes = ["LeptonGen", "NeutrinoGen", "PhotonGen"]
        intQuantities = ["MotherPID", "MotherStatus", "pdgId", "status"]
        floatQuantities = ["eta", "phi", "mass"]
        boolQuantities = [
            "fromHardProcess",
            "isDirectHadronDecayProduct",
            "isDirectPromptTauDecayProduct",
            "isPrompt",
            "isTauDecayProduct",
        ]

        df = df.Define(
            "LeptonGen_mask",
            "((abs(GenPart_pdgId) == 11 || abs(GenPart_pdgId) == 13) && GenPart_status == 1) || (abs(GenPart_pdgId) == 15 && bitExpr(GenPart_statusFlags, 1) && bitExpr(GenPart_statusFlags, 13))",
        )

        df = df.Define(
            "NeutrinoGen_mask",
            "(abs(GenPart_pdgId) == 12 || abs(GenPart_pdgId) == 14 || abs(GenPart_pdgId) == 16) && GenPart_status == 1 ",
        )

        df = df.Define("PhotonGen_mask", "GenPart_pdgId == 22 and GenPart_status == 1")

        df = df.Define("GenPart_fromHardProcess", "bitExpr(GenPart_statusFlags, 8)")

        df = df.Define(
            "GenPart_isDirectHadronDecayProduct", "bitExpr(GenPart_statusFlags, 6)"
        )

        df = df.Define(
            "GenPart_isDirectPromptTauDecayProduct", "bitExpr(GenPart_statusFlags, 5)"
        )

        df = df.Define("GenPart_isPrompt", "bitExpr(GenPart_statusFlags, 0)")

        df = df.Define("GenPart_isTauDecayProduct", "bitExpr(GenPart_statusFlags, 3)")

        df = df.Define(
            "GenPart_MotherPID", "Take(GenPart_pdgId, GenPart_genPartIdxMother)"
        )

        df = df.Define(
            "GenPart_MotherStatus", "Take(GenPart_status, GenPart_genPartIdxMother)"
        )

        for pType in particleTypes:
            df = df.Define(f"{pType}_pt", f"GenPart_pt[{pType}_mask]")
            df = df.Define(f"{pType}_sorting", f"sortedIndices({pType}_pt)")
            df = df.Redefine(f"{pType}_pt", f"Take({pType}_pt, {pType}_sorting)")

        branches = intQuantities + floatQuantities + boolQuantities
        for pType in particleTypes:
            for prop in branches:
                df = df.Define(f"{pType}_{prop}", f"GenPart_{prop}[{pType}_mask]")
                df = df.Redefine(
                    f"{pType}_{prop}", f"Take({pType}_{prop}, {pType}_sorting)"
                )

        df = df.DropColumns("LeptonGen_sorting")
        df = df.DropColumns("NeutrinoGen_sorting")
        df = df.DropColumns("PhotonGen_sorting")
        df = df.DropColumns("LeptonGen_mask")
        df = df.DropColumns("NeutrinoGen_mask")
        df = df.DropColumns("PhotonGen_mask")

        return df
