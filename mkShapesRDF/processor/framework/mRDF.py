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
        c = self.Copy()
        c.df = c.df.Redefine(a, b)
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
