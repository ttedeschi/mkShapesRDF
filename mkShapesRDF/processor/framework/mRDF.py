import ROOT
from fnmatch import fnmatch
from mkShapesRDF.lib.parse_cpp import ParseCpp


class mRDF:
    r"""Private version of RDataFrame that allows to define new columns, drop columns, and use Vary together with Snapshot."""

    def __init__(self):
        r"""Initialize the mRDF object."""
        self.df = 0  #: df stores the RDataFrame object
        self.cols = []  #: cols stores the list of columns
        self.cols_d = []  #: cols_d stores the list of columns that were dropped
        self.variations = {}  #: variations stores the list of variations

    def setNode(self, dfNode, cols, cols_d, variations):
        r"""Set internal variables of an ``mRDF`` object to the provided ones

        Parameters
        ----------
        dfNode : ROOT.RDataFrame
            The RDataFrame object

        cols : `list of str`
            The list of columns of the RDataFrame

        cols_d : `list of str`
            The list of columns that were dropped

        variations : dict
            The `dict` of variations

        Returns
        -------
        mRDF
            The ``mRDF`` object with the internal variables set to the provided ones

        """
        self.df = dfNode
        self.cols = cols
        self.cols_d = cols_d
        self.variations = variations
        return self

    def Copy(self):
        r"""Copy the ``mRDF`` object

        Returns
        -------
        mRDF
            The copy of the ``mRDF`` object
        """

        c = mRDF()
        c.setNode(self.df, self.cols.copy(), self.cols_d.copy(), self.variations.copy())
        return c

    def readRDF(self, *ar, **kw):
        r"""Read the RDataFrame object and create the special column ``CUT`` used to hold the different Filters

        Parameters
        ----------
        ar : list
            The list of arguments to be passed to the RDataFrame constructor

        kw : dict
            The dictionary of keyword arguments to be passed to the RDataFrame constructor

        Returns
        -------
        mRDF
            The ``mRDF`` object with the new RDataFrame object stored

        """
        self.df = ROOT.RDataFrame(*ar, **kw).Define("CUT", "true")
        self.cols = list(map(lambda k: str(k), self.df.GetColumnNames()))
        return self

    def Define(self, a, b, includeVariations=True):
        r"""Define a new column, if the column already exists redefine it.

        Parameters
        ----------
        a : str
            The name of the new column

        b : str
            The expression to be evaluated to define the new column

        includeVariations : bool, optional, default: True
            Whether to include variations or not

        Returns
        -------
        mRDF
            The ``mRDF`` object with the new column defined

        Notes
        -----
        If ``includeVariations`` is ``True``, the define expression (``b``) will be checked for variations.
        If variations of the define expression are found, they will be defined for the new column as well.
        """

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
        """ """
        return self.Define(a, b)

    def Vary(self, colName, expression, variationTags=["down", "up"], variationName=""):
        """
        Define variations for an existing column, given an expression

        Parameters
        ----------
        colName : str
            nominal column name
        expression : str
            a valid C++ expression that defines the variations
        variationTags : list, optional, default: ``["down", "up"]``
            list of tags to be used for the variations (len must be 2)
        variationName : str, optional, default: ""
            name of the variation

        Returns
        -------
        mRDF
            The ``mRDF`` object with the variations defined

        Notes
        -----
        ``Vary`` will call ``Define`` internally to define a temporary variable that contains the varied expression.
        Since also ``Define`` will call ``Vary`` internally, the user should be careful to not end up in an infinite loop!

        Examples
        --------
        When defining the same variation twice for different nominal variables, the tags must be the same (order does not matter)

        >>> df = df.Vary("var", "var + 1", ["down", "up"], "var_JER_0")
        >>> df = df.Vary("var2", "var2 + 2", [ "up", "down"], "var_JER_0")

        References
        ----------
        See the official ``RDataFrame::Vary()`` `documentation <https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#a84d15369c945e4fe85e919224a0fc99f>`_
        even if not used here (not compatible with ``Snapshot``).

        """

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
        """
        Filter the mRDF, the filter is sensitive to Variations through the use of ``CUT``, see the notes.

        Parameters
        ----------
        string : str
            the filter expression

        Returns
        -------
        mRDF
            The ``mRDF`` object with the filter applied

        Notes
        -----
        If the filter expression contains a variable for which variation are already defined,
        the ``CUT`` will be varied accordingly. Only events that pass at least one of the varied ``CUT`` (or the nominal)
        will be considered.
        """
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
        """ """
        return self.cols

    def GetVariations(self):
        """ """
        return self.variations

    def GetVariationsForCol(self, column):
        """
        Get the list of variations for a given column

        Parameters
        ----------
        column : str
            the nominal column name

        Returns
        -------
        list
            list of all variations defined for the given column
        """
        variations = []
        for variationName in self.variations:
            if column in self.variations[variationName]:
                variations.append(variationName)
        return variations

    def DropColumns(self, pattern, includeVariations=True):
        """
        Drop columns that match the given pattern

        Parameters
        ----------
        pattern : str
            the pattern to be matched
        includeVariations : bool, optional, default: True
            whether to include variations or not

        Returns
        -------
        mRDF
            The ``mRDF`` object with the columns dropped

        Notes
        -----
        The columns from ``self.cols`` matching the pattern will be dropped and added to ``self.cols_d``.
        If ``includeVariations`` is ``True``, the variations of the dropped columns will be dropped as well.
        """
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
        r"""Count the number of events

        Returns
        -------
        `Proxy<Long64_t>`
            The number of events (need to apply ``GetValue()`` to get the actual value)
        """
        return self.df.Count()

    def Sum(self, string):
        r"""Sum the values of a column

        Parameters
        ----------
        string : str
            the column name

        Returns
        -------
        `Proxy<Float_t>`
            The sum of the values of the column (need to apply ``GetValue()`` to get the actual value)

        """
        return self.df.Sum(string)

    def Snapshot(self, *args, **kwargs):
        """
        Produce a Snapshot of the mRDF and return it

        Parameters
        ----------
        *args : list
            list of arguments to be passed to the ``RDataFrame::Snapshot`` method

        **kwargs : dict
            dictionary of keyword arguments to be passed to the ``RDataFrame::Snapshot`` method


        Returns
        -------
        `Snapshot` or `Proxy<Snapshot>`
            The ``Snapshot`` object, or a ``Proxy<Snapshot>`` if ``lazy=True`` is passed as a keyword argument
        """
        return self.df.Snapshot(*args, **kwargs)
