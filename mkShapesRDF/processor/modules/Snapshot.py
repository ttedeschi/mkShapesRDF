import ROOT
from fnmatch import fnmatch
from mkShapesRDF.processor.framework.module import Module


class Snapshot(Module):
    def __init__(self, pathFile, columns, includeVariations=True):
        super().__init__("Snapshot")
        self.pathFile = pathFile
        self.columns = columns
        self.includeVariations = includeVariations

    def runModule(self, df, values):
        print("Snapshotting to", self.pathFile, "columns:\n", self.columns)

        cols = list(map(lambda k: str(k), df.GetColumnNames()))
        saveColumns = []
        for col in self.columns:
            tmp_cols = list(filter(lambda k: fnmatch(k, col), cols))
            if len(tmp_cols) == 0:
                print("Warning: no columns found to snapshot with pattern", col)
            saveColumns.extend(tmp_cols)

        if self.includeVariations:
            variations = df.GetVariations()
            for variationName in variations.keys():
                tmp_varied_cols = list(
                    set(saveColumns).intersection(set(variations[variationName]))
                )
                tmp_varied_cols = list(
                    map(lambda k: k + "__" + variationName, tmp_varied_cols)
                )
                varied_cols = []
                for tag in ["up", "down"]:
                    varied_cols += list(map(lambda k: k + "_" + tag, tmp_varied_cols))
                saveColumns += varied_cols

        saveColumns = sorted(list(set(saveColumns)))
        print("Final list of variables for snapshot", saveColumns)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fLazy = True
        values.append(
            ["snapshot", df.Snapshot("Events", self.pathFile, saveColumns, opts)]
        )

        return df
