import os
import sys


class types:
    @staticmethod
    def isStr(t):
        return type(t) == type("")

    @staticmethod
    def isTuple(t):
        return type(t) == type((0,))

    @staticmethod
    def isOrderedDict(t):
        return "OrderedDict" in str(type(t))


class ConfigLib:
    @staticmethod
    def loadConfig(filesToExec, globs, imports=[]):
        for i in imports:
            if types.isStr(i):
                exec(f"import {i}", globs, globs)
            else:
                exec(f"from {i[0]} import {i[1]}", globs, globs)
        for f in filesToExec:
            exec(open(f).read(), globs, globs)

    @staticmethod
    def createConfigDict(varsToKeep, objects):
        # given all the variables stored in memory, dump the ones the user wants to keep to a dictionary
        from collections import OrderedDict

        config = OrderedDict()
        for var in varsToKeep:
            if types.isStr(var):
                config[var] = objects[var]
            elif types.isTuple(var):
                d = {}
                if len(var) != 2:
                    print("Tuple should have lenght = 2! (nameOfVar, dict)")
                    sys.exit()
                for item in list(var[1].items()):
                    d[item[0]] = objects[item[1]]

                config[var[0]] = d
        return config

    @staticmethod
    def cleanConfig(varsToDelete, globs):
        for var in varsToDelete:
            if var in globs.keys():
                exec(f'del globs["{var}"]')
                del globs[var]
            else:
                del var

    @staticmethod
    def dumpConfigDict(config, filepath, doJson=False):
        if doJson:
            import json

            with open(filepath + ".json", "w") as file:
                json.dump(config, file, indent=2)
        else:
            import cloudpickle
            import zlib

            with open(filepath + ".pkl", "wb") as file:
                file.write(zlib.compress(cloudpickle.dumps(config)))

    @staticmethod
    def dumpConfig(varsToKeep, objects, filepath):
        # given all the variables stored in memory, dump the ones the user wants to keep to a json file
        from collections import OrderedDict

        config = OrderedDict()
        for var in varsToKeep:
            if types.isStr(var):
                config[var] = objects[var]
            elif types.isTuple(var):
                d = {}
                if len(var) != 2:
                    print("Tuple should have lenght = 2! (nameOfVar, dict)")
                    sys.exit()
                for item in list(var[1].items()):
                    d[item[0]] = objects[item[1]]

                config[var[0]] = d

        import json

        with open(filepath, "w") as file:
            json.dump(config, file, indent=2)

    @staticmethod
    def convertOrderedDict(d):
        return list(d.items())

    @staticmethod
    def loadDict(d, globs):
        globs["d"] = d
        for var in d.keys():
            exec(f'{var} = d["{var}"]', globs)

    @staticmethod
    def findLatestFile(folderPath, extension=".pkl"):
        import glob

        lFile = list(
            filter(
                lambda k: os.path.isfile(k), glob.glob(folderPath + "/*" + extension)
            )
        )
        lFile.sort(key=lambda x: os.path.getmtime(x))
        if len(lFile) == 0:
            print(
                f"No file found in {folderPath} with extension: {extension}\nTry compiling first with `-c 1`"
            )
            sys.exit()
        lFile = lFile[-1]
        return lFile

    @staticmethod
    def loadPickle(filePath, globs):
        import cloudpickle
        import zlib

        global d
        with open(filePath, "rb") as file:
            d = cloudpickle.loads(zlib.decompress(file.read()))
        # ConfigLib.loadDict(globs['d'], globs)
        ConfigLib.loadDict(d, globs)
        # exec('d = d', globs)
        print(globs["batchVars"])
        return d

    @staticmethod
    def loadLatestPickle(folderPath, globs):
        lFile = ConfigLib.findLatestFile(folderPath, extension=".pkl")
        return ConfigLib.loadPickle(lFile, globs)
