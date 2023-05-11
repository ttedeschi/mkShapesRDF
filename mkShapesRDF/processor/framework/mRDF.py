import ROOT
from fnmatch import fnmatch


def searchList(l, pattern):
    return list(filter(lambda k: fnmatch(k, pattern), l))


def searchListReg(l, pattern):
    import re

    return list(filter(lambda k: re.match(pattern, k), l))


class mRDF:
    def __init__(self):
        self.df = 0
        self.cols = []
        self.cols_d = []
        self.variations = {}

    @staticmethod
    def parseCpp(string):
        import re

        vars = re.split(" |\(|\)|\+|\-|>|<|=|&&|\/|\*|\.|,|!|\|\|", string)
        vars = list(filter(lambda k: k != "", vars))
        vars = list(filter(lambda k: not k.isnumeric(), vars))

        return vars

    @staticmethod
    def RVecExpression(_type):
        """Creates a string for RVec with the specified _type

        Args:
            _type (str): string version of the type of the RVec

        Returns:
            str: string with the expression to be used for RVec<type>
        """
        _typeString = ""
        if _type == "float":
            _typeString = "F"
        elif _type == "double":
            _typeString = "D"
        elif _type == "int":
            _typeString = "I"
        elif _type == "bool":
            _typeString = "B"
        else:
            _typeString = "<" + _type + ">"
        return f"ROOT::RVec{_typeString}"

    def setNode(self, dfNode, cols, cols_d):
        self.df = dfNode
        self.cols = cols
        self.cols_d = cols_d
        return self

    def Copy(self):
        c = mRDF()
        c.setNode(self.df, self.cols.copy(), self.cols_d.copy())
        return c

    def readRDF(self, *ar, **kw):
        self.df = ROOT.RDataFrame(*ar, **kw)
        self.cols = list(map(lambda k: str(k), self.df.GetColumnNames()))
        return self

    def Define(self, a, b):
        c = self.Copy()

        # check variations
        depVars = mRDF.parseCpp(b)
        variations = {}
        for variationName in c.variations.keys():
            s = list(filter(lambda k: k in depVars, c.variations[variationName].keys()))
            if len(s) > 0:
                # only register variations if they have an impact on "a" variable
                variations[variationName] = s

        tags = ["up", "down"]
        for variationName in variations.keys():
            varied_bs = []
            for tag in tags:
                varied_b = b + ""
                for variable in variations[variationName]:
                    varied_b = varied_b.replace(
                        variable, variable + "__" + variationName + "_" + tag
                    )
                varied_bs.append(varied_b)
            _type = c.df.GetColumnType(a)
            expression = mRDF.RVecExpression(_type) + " {" + ", ".join(varied_bs) + "}"
            c = c.Vary(a, expression, tags, variationName)

        if not a in (c.cols + c.cols_d):
            c.df = c.df.Define(a, b)
        else:
            if a in c.cols:
                print(f"Warning, {a} was already defined, redefining it")
            c.df = c.df.Redefine(a, b)
        # print('Defined col', a)
        c.cols = list(set(c.cols + [a]))

        return c

    def Redefine(self, a, b):
        return self.Define(a, b)

    def Vary(self, colName, expression, variationTags=["down", "up"], variationName=""):
        # variationTags could be either [down, up] or [up, down]
        c = self.Copy()
        if not variationName in c.variations.keys():
            c.variations[variationName] = []
        c.variations[variationName] = list(set(c.variations[variationName] + [colName]))

        # define a column that will contain the two variations in a vector of len 2
        c = c.Define(colName + "__" + variationName, expression)

        for i, variationTag in enumerate(variationTags):
            c = c.Define(
                colName + "__" + variationName + "_" + variationTag,
                colName + "__" + variationName + "[" + str(i) + "]",
            )

        c.DropColumns(colName + "__" + variationName)

        return c

    def Filter(self, string):
        c = self.Copy()
        c.df = c.df.Filter(string)
        return c

    def GetColumnNames(self):
        return self.cols

    def DropColumns(self, pattern):
        tmp_cols_d = list(filter(lambda k: fnmatch(k, pattern), self.cols))
        # print('Deleting columns', tmp_cols_d)
        self.cols_d = list(set(self.cols_d + tmp_cols_d))
        self.cols = list(
            set(list(filter(lambda k: not fnmatch(k, pattern), self.cols)))
        )
        return self.cols

    def Count(self):
        return self.df.Count()

    def Sum(self, string):
        return self.df.Sum(string)

    def Snapshot(self, *args, **kwargs):
        # print('Producing snapshot and returning the pointer')
        return self.df.Snapshot(*args, **kwargs)
