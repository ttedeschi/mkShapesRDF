class ParseCpp:
    r"""A utility class to parse C++ expression, replace variables and format back to a C++ expression."""
    #: delimeters is a list of strings that are used to split the expression.
    delimiters = [
        " ",
        "(",
        ")",
        "+",
        "-",
        ">",
        "<",
        "=",
        "&&",
        "/",
        "*",
        ".",
        ",",
        "!",
        "[",
        "]",
        "||",
    ]

    @staticmethod
    def parse(string):
        r"""Parse a C++ expression and return a list of strings containing the expression split by the delimiters.

        Parameters
        ----------

            string : str
                C++ expression to be parsed

        Returns
        -------

            `list of str`
                list of variables and delimiter that compose the expression

        """

        r = [string]
        for delimiter in ParseCpp.delimiters:
            _r = []
            for i in range(len(r)):
                while delimiter in r[i]:
                    pos = r[i].index(delimiter)
                    if len(r[i][:pos]) > 0:
                        _r.append(r[i][:pos])
                    if len(r[i][pos : pos + len(delimiter)]) > 0:
                        _r.append(r[i][pos : pos + len(delimiter)])
                    r[i] = r[i][pos + len(delimiter) :]
                if len(r[i]) > 0:
                    _r += [r[i]]
            r = _r.copy()
        return r

    @staticmethod
    def format(parsedS):  # noqa A003
        r"""Format back a parsed C++ expression to a string.

        Parameters
        ----------

            parsedS : `list of str`
                list of variables and delimiters that compose the expression

        Returns
        -------
            str
                formatted C++ expression
        """
        return "".join(parsedS)

    @staticmethod
    def replace(parsedS, orig, new):
        r"""Replace a variable in a parsed C++ expression.

        Parameters
        ----------

            parsedS : `list of str`
                parsed C++ expression

            orig : str
                original variable name

            new : str
                new variable name

        Returns
        -------
            `list of str`
                parsed C++ expression with the variable replaced

        """
        return [new if x == orig else x for x in parsedS]

    @staticmethod
    def listOfVariables(parsedS):
        r"""Return the list of variables in a parsed C++ expression.

        Parameters
        ----------

            parsedS : `list of str`
                parsed C++ expression

        Returns
        -------

            `list of str`
                list of variables in the parsed C++ expression

        """
        return sorted(
            list(
                set(
                    [
                        x
                        for x in parsedS
                        if (x not in ParseCpp.delimiters and not x.isnumeric())
                    ]
                )
            )
        )

    @staticmethod
    def RVecExpression(_type):
        r"""Creates a string for RVec with the specified _type

        Parameters
        ----------
            _type : str
                string version of the type of the RVec

        Returns
        -------

            str
                string with the expression to be used for ``RVec<type>``
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
