from mkShapesRDF.processor.framework.module import Module


class BaseW(Module):
    def __init__(self, sampleName, files, xs_db, genEventSumw):
        super().__init__("BaseW")
        self.sampleName = sampleName
        self.files = files
        self.xs_db = xs_db
        self.genEventSumw = genEventSumw

    def runModule(self, df, values):
        xs = float(self.xs_db[self.sampleName][0].split("=")[1])

        baseW = xs * 1000 / self.genEventSumw
        df = df.Define("baseW", f"{baseW}")

        def fun(a, b):
            return [a, b]

        values.append([fun, "New baseW", str(baseW)])

        return df
