import os
import sys

class types:
    @staticmethod
    def isStr(t):
        return type(t) == type('')


    @staticmethod
    def isDict(t):
        return type(t) == type({0:1})

    @staticmethod
    def isList(t):
        return type(t) == type([])

    @staticmethod
    def isTuple(t):
        return type(t) == type((0,))

    @staticmethod
    def isSet(t):
        return type(t) == type({1,})

    @staticmethod
    def isOrderedDict(t):
        return 'OrderedDict' in str(type(t))

    @staticmethod
    def isCollection(t):
        return types.isDict(t) or types.isOrderedDict(t) or types.isList(t) or types.isTuple(t) or types.isSet(t)


    @staticmethod
    def isInt(t):
        return type(t) == type(int(1))

    @staticmethod
    def isFloat(t):
        return type(t) == type(float(1))

    @staticmethod
    def isNumber(t):
        return types.isInt(t) or types.isFloat(t)



class ConfigLib:

    @staticmethod
    def loadConfig(filesToExec, globs, imports=[]):
        for i in imports:
            if types.isStr(i):
                exec(f'import {i}', globs, globs)
            else:
                exec(f'from {i[0]} import {i[1]}', globs, globs)
        for f in filesToExec:
             exec(open(f).read(), globs, globs)

    @staticmethod
    def createConfigDict(varsToKeep, objects):
        # given all the variables stored in memory, dump the ones the user wants to keep to a json file
        from collections import OrderedDict
        config = OrderedDict()
        for var in varsToKeep:
            if types.isStr(var):
                config[var] = objects[var]
            elif types.isTuple(var):
                d = {}
                if len(var)!= 2:
                    print('Tuple should have lenght = 2! (nameOfVar, dict)')
                    sys.exit()
                for item in list(var[1].items()):
                    d[item[0]] = objects[item[1]]

                config[var[0]] = d
        return config


    @staticmethod
    def cleanConfig(varsToDelete, globs):
        for var in varsToDelete:
            if var in globs.keys():
                del globs[var]
            else:
                del var

    @staticmethod
    def dumpConfigDict(config, filepath):
        import json
        with open(filepath, 'w') as file:
            json.dump(config, file, indent=2)


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
                if len(var)!= 2:
                    print('Tuple should have lenght = 2! (nameOfVar, dict)')
                    sys.exit()
                for item in list(var[1].items()):
                    d[item[0]] = objects[item[1]]

                config[var[0]] = d

        import json
        with open(filepath, 'w') as file:
            json.dump(config, file, indent=2)

    @staticmethod
    def convertOrderedDict(d):
        return list(d.items())

    @staticmethod
    def loadDict(d, globs):
        for var in d.keys():
            print('Defining variable', var)
            if types.isStr(d[var]):
                exec(f'{var} = "{d[var]}"', globs, globs)
            elif types.isCollection(d[var]):
                exec(f'{var} = {d[var]}', globs, globs)
            elif types.isNumber(d[var]):
                exec(f'{var} = {d[var]}', globs, globs)
            else:
                print('unknown type for ', var, type(d[var]))

    # FIXME is it useful to move out of a dictionary the variables?
    @staticmethod
    def loadJSON(filepath):
        import json
        with open(filepath) as file:
            s = json.load(file)
        for var in s.keys():
            #exec(f'global {var}', globals(), globals())
            if types.isStr(s[var]):
                exec(f'{var} = "{s[var]}"', globals(), globals())
            elif types.isCollection(s[var]):
                exec(f'{var} = {s[var]}', globals(), globals())
            elif types.isNumber(s[var]):
                exec(f'{var} = {s[var]}', globals(), globals())
            else:
                print('unknown type for ', var, type(s[var]))

#ConfigLib.load('prova.json')

"""
folder = '.'
folder = os.path.abspath(folder)
configVars1 = dict(list(globals().items()) + list(locals().items()))
ConfigLib.loadConfig(['configuration.py'])

ConfigLib.loadConfig(filesToExec, imports)
varsToKeep += ['folder']
import datetime
dt = datetime.datetime.now()
fileName = configsFolder + '/config_'+ dt.strftime('%y-%m-%d_%H_%M_%S') + '.json'

ConfigLib.dumpConfig(varsToKeep, dict(list(globals().items()) + list(locals().items())), fileName)
configVars2 = dict(list(globals().items()) + list(locals().items()))
print(set(configVars2.keys()).difference(set(configVars1.keys())))
"""
