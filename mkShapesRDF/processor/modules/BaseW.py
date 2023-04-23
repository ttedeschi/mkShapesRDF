import ROOT
from mkShapesRDF.processor.framework.Module import Module


class BaseW(Module):
    def __init__(self, sampleName, files, xs_db):
        super().__init__("BaseW")
        self.sampleName = sampleName
        self.files = files
        self.xs_db = xs_db

    def runModule(self, df, values):

        df2 = ROOT.RDataFrame("Runs", self.files)
        genEventSumw = df2.Sum("genEventSumw").GetValue()

        xs = float(self.xs_db[self.sampleName][0].split('=')[1])

        baseW = xs * 1000 / genEventSumw
        df = df.Define("baseW", f"{baseW}")

        def fun(a, b):
            return [a, b]
        values.append([fun, "New baseW", str(baseW)])

        return df
