from mkShapesRDF.processor.framework.module import Module
from mkShapesRDF.processor.framework.mRDF import mRDF
import ROOT


class Histogram(Module):
    def __init__(self, outputFilename, variables):
        super().__init__("Histogram")
        self.outputFilename = outputFilename
        self.variables = variables

    def runModule(self, df, values):
        for variable in self.variables:
            c = df.Copy()
            for variationName in c.GetVariationsForCol(variable[1]):
                tags = c.variations[variationName]["tags"]
                expr = "ROOT::RVecD {"
                expr += mRDF.variationNaming(variationName, tags[0], variable[1])
                expr += ", "
                expr += mRDF.variationNaming(variationName, tags[1], variable[1])
                expr += "}"
                c.df = c.df.Vary(
                    variable[1], expr, variationTags=tags, variationName=variationName
                )

            c.df = c.df.Define("__weight__", variable[2])

            values.append(
                [
                    "variables",
                    variable[1],
                    ROOT.RDF.Experimental.VariationsFor(
                        c.df.Histo1D(variable[0], variable[1], "__weight__")
                    ),
                ]
            )
        return df
