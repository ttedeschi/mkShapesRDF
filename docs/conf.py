# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os
import inspect
from mkShapesRDF.lib.utils import getFrameworkPath

modpath = getFrameworkPath()
linkcode_url = "https://github.com/latinos/mkShapesRDF/blob/master/{filepath}#L{linestart}-L{linestop}"

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "mkShapesRDF"
copyright = "2024, Latinos"
author = "Latinos"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "numpydoc",
    # "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    # "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.viewcode",
    "sphinx.ext.ifconfig",
    "sphinx.ext.imgmath",
    "sphinxarg.ext",
]


def linkcode_resolve(domain, info):
    if domain != "py" or not info["module"]:
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        print(info, "exception submod is none", file=sys.stderr)
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except Exception:
            print(info, "exception getattr", file=sys.stderr)
            return None

    try:
        filepath = os.path.relpath(inspect.getsourcefile(obj), modpath)
        if filepath is None:
            print(info, "exception filepath is none", file=sys.stderr)
            return
    except Exception:
        print(info, "exception for modpath and filepath", file=sys.stderr)
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        print(info, "exception for getsourcelines", file=sys.stderr)
        return None
    else:
        linestart, linestop = lineno, lineno + len(source) - 1

    return linkcode_url.format(
        filepath=filepath, linestart=linestart, linestop=linestop
    )


templates_path = ["_templates"]
exclude_patterns = []

numpydoc_xref_param_type = True
numpydoc_xref_ignore = {"optional", "type_without_description", "BadException"}
# numpydoc_show_class_members = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/devdocs/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "alabaster"
html_title = "mkShapesRDF"
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/latinos/mkShapesRDF",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
    ],
}

sys.path.insert(0, os.path.abspath("shapes/python"))
sys.path.insert(0, os.path.abspath("../tests"))
autodoc_member_order = 'bysource'
