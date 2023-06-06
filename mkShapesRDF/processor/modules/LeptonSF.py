import ROOT
from mkShapesRDF.processor.framework.module import Module
import correctionlib

correctionlib.register_pyroot_binding()


class LeptonSF(Module):
    # def __init__(self, LepFilter, nLF):
    def __init__(self, pathToJson):
        super().__init__("LeptonSF")
        self.pathToJson = pathToJson
        # self.LepFilter = LepFilter
        # self.nLF = nLF

    def runModule(self, df, values):
        # path = os.path.abspath('../data/scale_factor/Full2018v9/electron.json.gz')
        ROOT.gInterpreter.Declare(
            f'auto csetEl = correction::CorrectionSet::from_file("{self.pathToJson}");'
        )
        ROOT.gInterpreter.Declare(
            'auto csetEl_2018preID = csetEl->at("UL-Electron-ID-SF");'
        )
        df = df.Filter("nElectron >= 1 && Electron_pt[0] > 10.").Define(
            "leadElSF",
            (
                'csetEl_2018preID->evaluate({"2018", "sf", "wp90iso", '
                "std::abs(Electron_eta[0]), Electron_pt[0]})"
            ),
        )
        return df
