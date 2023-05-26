class ParseCpp:
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
        return "".join(parsedS)

    @staticmethod
    def replace(parsedS, orig, new):
        return [new if x == orig else x for x in parsedS]

    @staticmethod
    def listOfVariables(parsedS):
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
