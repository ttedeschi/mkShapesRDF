import ROOT
from fnmatch import fnmatch
from mkShapesRDF.processor.framework.module import Module
import sys


class Snapshot(Module):
    def __init__(
        self,
        columns,
        eosPath,
        outputFilename,
        includeVariations=True,
        splitVariations=True,
        storeNominals=True,
    ):
        super().__init__("Snapshot")
        self.columns = columns

        self.eosPath = eosPath
        self.outputFilename = outputFilename

        self.includeVariations = includeVariations
        self.splitVariations = splitVariations
        self.storeNominals = storeNominals

    def SplitVariations(self, df):
        # create separate files for each variation and tag
        for variationName in df.variations:
            for tag in df.variations[variationName]["tags"]:
                tmp_varied_cols = df.GetVariedColumns_oneVariation(
                    self.saveColumns, variationName, tag
                )
                outputFilename = self.outputFilename.split(".")
                outputFilename[-2] += "__" + variationName + "_" + tag
                outputFilename = ".".join(outputFilename)
                self.snapshots.append(
                    [
                        variationName + "_" + tag,
                        tmp_varied_cols,
                        outputFilename,
                        self.eosPath + "__" + variationName + "_" + tag,
                        self.outputFilename,
                    ]
                )

    def StoreNominals(self, df):
        # store only nominals and remove variations from the list
        tmp_varied_cols = df.GetVariedColumns(self.saveColumns)
        saveColumns = list(set(self.saveColumns).difference(set(tmp_varied_cols)))
        self.snapshots.append(
            [
                "nominal",
                saveColumns,
                self.outputFilename,
                self.eosPath,
                self.outputFilename,
            ]
        )

    def StoreNominalsAndVariations(self, df):
        # store variation in the same files as nominal
        tmp_varied_cols = df.GetVariedColumns(self.saveColumns)
        self.snapshots.append(
            [
                "nominal and varied",
                saveColumns + tmp_varied_cols,
                self.outputFilename,
                self.eosPath,
                self.outputFilename,
            ]
        )

    def runModule(self, df, values):
        print("Snapshotting to", self.outputFilename, "columns:\n", self.columns)

        cols = df.GetColumnNames()
        saveColumns = []
        for pattern in self.columns:
            tmp_cols = list(set(filter(lambda k: fnmatch(k, pattern), cols)))
            if len(tmp_cols) == 0:
                print("Warning: no columns found to snapshot with pattern", pattern)
            saveColumns = list(set(saveColumns).union(set(tmp_cols)))

        self.saveColumns = list(set(saveColumns))

        self.snapshots = []

        if self.includeVariations and self.splitVariations and self.storeNominals:
            self.SplitVariations(df)
            self.StoreNominals(df)

        if self.includeVariations and self.splitVariations and not self.storeNominals:
            self.SplitVariations(df)

        if (
            self.includeVariations
            and not self.splitVariations
            and not self.storeNominals
        ):
            print(
                "Cannot snapshot variations all together without storing nominal\nEither set storeNominals=True or splitVariations=True",
                file=sys.stderr,
            )
            sys.exit(1)

        if (
            not self.includeVariations
            and not self.splitVariations
            and not self.storeNominals
        ):
            print(
                "Snapshot without variations and without storing nominal is not supported",
                file=sys.stderr,
            )
            sys.exit(1)

        if (
            not self.includeVariations
            and self.splitVariations
            and not self.storeNominals
        ):
            print(
                "Snapshot without variations and with split variations is not supported\nTurn on includeVariations",
                file=sys.stderr,
            )
            sys.exit(1)

        if not self.includeVariations and self.splitVariations and self.storeNominals:
            print(
                "Snapshot without variations and with split variations is not supported\nTurn on includeVariations",
                file=sys.stderr,
            )
            sys.exit(1)

        if (
            not self.includeVariations
            and not self.splitVariations
            and self.storeNominals
        ):
            self.StoreNominals(df)

        if self.includeVariations and not self.splitVariations and self.storeNominals:
            self.StoreNominalsAndVariations(df)

        for snapshot in self.snapshots:
            _cols = sorted(list(set(snapshot[1])))
            print("Final list of variables for snapshot", snapshot[0], _cols)
            opts = ROOT.RDF.RSnapshotOptions()
            opts.fLazy = True
            values.append(
                [
                    "snapshot",
                    df.Snapshot("Events", snapshot[2], _cols, opts),
                    [
                        snapshot[2],
                        snapshot[3],
                        snapshot[4],
                    ],
                ]
            )

        return df
