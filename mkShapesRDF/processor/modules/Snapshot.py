import ROOT
from fnmatch import fnmatch
from mkShapesRDF.processor.framework.Module import Module


class Snapshot(Module):

    def __init__(self, pathFile, columns):
        super().__init__('Snapshot')
        self.pathFile = pathFile
        self.columns = columns

    def runModule(self, df, values):
        print("Snapshotting to", self.pathFile, "columns:\n", self.columns)

        cols = list(map(lambda k: str(k), df.GetColumnNames()))
        saveColumns = []
        for col in self.columns:
            print(list(filter(lambda k: fnmatch(k, col), cols)))
            saveColumns.extend(list(filter(lambda k: fnmatch(k, col), cols)))

        opts = ROOT.RDF.RSnapshotOptions()
        opts.fLazy = True
        values.append(["snapshot", df.Snapshot("Events", self.pathFile, saveColumns, opts)])

        return df
