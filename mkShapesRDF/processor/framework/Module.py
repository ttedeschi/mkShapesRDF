class Module:
    def __init__(self, name):
        self.name = name

    def runModule(self, df, values):
        return df

    def run(self, df, values):
        values.append([df.Count(), "begin count of " + self.name])
        a = len(values) - 1

        df = self.runModule(df, values)

        values.append([df.Count(), "end count of " + self.name])
        b = len(values) - 1

        def fun(a, b):
            bVal = values[b]
            aVal = values[a]
            if "list" in str(type(bVal)):
                bVal = bVal[0]
            if "list" in str(type(aVal)):
                aVal = aVal[0]
            return [
                f"Efficiency of {self.name} module",
                str(round(bVal.GetValue() / aVal.GetValue() * 100, 3)) + "%",
            ]

        values.append([fun, a, b])
        return df
