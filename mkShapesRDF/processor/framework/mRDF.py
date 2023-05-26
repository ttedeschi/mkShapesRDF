import ROOT
from fnmatch import fnmatch
from mkShapesRDF.lib.parseCpp import ParseCpp


class mRDF:
    def __init__(self):
        self.df = 0
        self.cols = []
        self.cols_d = []
        self.variations = {}

    def setNode(self, dfNode, cols, cols_d, variations):
        self.df = dfNode
        self.cols = cols
        self.cols_d = cols_d
        self.variations = variations
        return self

    def Copy(self):
        c = mRDF()
        c.setNode(self.df, self.cols.copy(), self.cols_d.copy(), self.variations.copy())
        return c

    def readRDF(self, *ar, **kw):
        self.df = ROOT.RDataFrame(*ar, **kw).Define("CUT", "true")
        self.cols = list(map(lambda k: str(k), self.df.GetColumnNames()))
        return self

    def Define(self, a, b, includeVariations=True):
        c = self.Copy()

        # store nominal value in a special temporary column
        colName = a + "_tmp_SPECIAL_NOMINAL"
        if colName not in (c.cols + c.cols_d):
            c.df = c.df.Define(colName, b)
        else:
            c.df = c.df.Redefine(colName, b)
        c.cols = list(set(c.cols + [colName]))

        if includeVariations:
            # check variations
            depVars = ParseCpp.listOfVariables(ParseCpp.parse(b))
            variations = {}
            for variationName in c.variations.keys():
                s = list(
                    filter(
                        lambda k: k in depVars, c.variations[variationName]["variables"]
                    )
                )
                if len(s) > 0:
                    # only register variations if they have an impact on "a" variable
                    variations[variationName] = {
                        "tags": c.variations[variationName]["tags"],
                        "variables": s,
                    }

            for variationName in variations.keys():
                varied_bs = []
                for tag in variations[variationName]["tags"]:
                    varied_b = ParseCpp.parse(b)
                    for variable in variations[variationName]["variables"]:
                        varied_b = ParseCpp.replace(
                            varied_b,
                            variable,
                            variable + "__" + variationName + "_" + tag,
                        )
                    varied_bs.append(ParseCpp.format(varied_b))
                _type = c.df.GetColumnType(colName)
                expression = (
                    ParseCpp.RVecExpression(_type) + " {" + ", ".join(varied_bs) + "}"
                )
                c = c.Vary(
                    a, expression, variations[variationName]["tags"], variationName
                )

        # move back nominal value to the right column name -> a
        if a not in (c.cols + c.cols_d):
            c.df = c.df.Define(a, colName)
        else:
            c.df = c.df.Redefine(a, colName)
        c = c.DropColumns(colName, includeVariations=False)
        c.cols = list(set(c.cols + [a]))

        return c

    def Redefine(self, a, b):
        return self.Define(a, b)

    def Vary(self, colName, expression, variationTags=["down", "up"], variationName=""):
        # variationTags could be in whatever order and whatever format
        # but must be all equal for a certain variationName

        c = self.Copy()
        if variationName not in c.variations.keys():
            c.variations[variationName] = {"tags": variationTags, "variables": []}
        else:
            if not (
                variationTags[0] in c.variations[variationName]["tags"]
                and variationTags[1] in c.variations[variationName]["tags"]
            ):
                print("Using different tags for same variation is not allowed")
                print("You should use tags", c.variations[variationName]["tags"])

        c.variations[variationName]["variables"] = list(
            set(c.variations[variationName]["variables"] + [colName])
        )

        # define a column that will contain the two variations in a vector of len 2
        c = c.Define(
            colName + "__" + variationName, expression, includeVariations=False
        )

        for i, variationTag in enumerate(variationTags):
            c = c.Define(
                colName + "__" + variationName + "_" + variationTag,
                colName + "__" + variationName + "[" + str(i) + "]",
                includeVariations=False,
            )

        c = c.DropColumns(colName + "__" + variationName)

        return c

    def Filter(self, string):
        c = self.Copy()
        c = c.Define("CUT", "CUT && (" + string + ")")

        # consider only events that pass at least one of the varied CUT
        variationNames = c.GetVariationsForCol("CUT")
        varied_bs = []
        for variationName in variationNames:
            for tag in c.variations[variationName]["tags"]:
                varied_bs.append("CUT" + "__" + variationName + "_" + tag)

        nom_and_variations = ["CUT"] + varied_bs
        filterExpr = " || ".join(nom_and_variations)
        c.df = c.df.Filter(filterExpr)
        return c

    def GetColumnNames(self):
        return self.cols

    def GetVariations(self):
        return self.variations

    def GetVariationsForCol(self, column):
        variations = []
        for variationName in self.variations:
            if column in self.variations[variationName]:
                variations.append(variationName)
        return variations

    def DropColumns(self, pattern, includeVariations=True):
        c = self.Copy()
        tmp_cols_d = list(set(filter(lambda k: fnmatch(k, pattern), c.cols)))
        if len(tmp_cols_d) == 0:
            print("Warning: no columns found to drop with pattern", pattern)

        if includeVariations:
            for variationName in self.variations:
                tmp_varied_cols_d = list(
                    set(tmp_cols_d).intersection(
                        set(c.variations[variationName]["variables"])
                    )
                )
                tmp_varied_cols_d = list(
                    map(lambda k: k + "__" + variationName, tmp_varied_cols_d)
                )
                varied_cols_d = []
                for tag in c.variations[variationName]["tags"]:
                    varied_cols_d += list(
                        map(lambda k: k + "_" + tag, tmp_varied_cols_d)
                    )
                tmp_cols_d += varied_cols_d

        # print('Deleting columns', tmp_cols_d)
        c.cols_d = list(set(c.cols_d + tmp_cols_d))
        c.cols = list(set(c.cols).difference(tmp_cols_d))
        return c

    def Count(self):
        return self.df.Count()

    def Sum(self, string):
        return self.df.Sum(string)

    def Snapshot(self, *args, **kwargs):
        # print('Producing snapshot and returning the pointer')
        return self.df.Snapshot(*args, **kwargs)
