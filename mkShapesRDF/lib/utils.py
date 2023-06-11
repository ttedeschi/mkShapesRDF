def getFrameworkPath():
    r"""Utility function to get the absolute path to the mkShapesRDF framework

    Returns
    -------
        string
            absolute path to the mkShapesRDF framework (ends with ``/``)
    """
    import os
    import inspect

    fwPath = os.path.realpath(inspect.getfile(inspect.currentframe()))  # this file
    fwPath = os.path.dirname(fwPath)  # lib
    fwPath = os.path.dirname(fwPath)  # mkShapesRDF (source code)
    fwPath = os.path.dirname(fwPath)  # mkShapesRDF
    fwPath = os.path.abspath(fwPath)  # abs path to mkShapesRDF

    if not fwPath.endswith("/"):
        fwPath += "/"
    return fwPath
