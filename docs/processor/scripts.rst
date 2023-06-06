
Scripts for processor
=====================



mkPostProc
----------

.. automodule:: mkShapesRDF.processor.scripts.mkPostProc
   :members:
   :show-inheritance:


Basic arguments
~~~~~~~~~~~~~~~

.. argparse::
   :module: mkShapesRDF.processor.scripts.mkPostProc
   :func: defaultParser
   :prog: mkPostProc
   :nodefault:


Operation mode 0 arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. argparse::
   :module: mkShapesRDF.processor.scripts.mkPostProc
   :func: operationMode0Parser
   :prog: mkPostProc -o 0 -p PROD -s STEP -sN SAMPLENAME
   :nodefault:

Operation mode 1 arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. argparse::
   :module: mkShapesRDF.processor.scripts.mkPostProc
   :func: operationMode1Parser
   :prog: mkPostProc -o 1 -p PROD -s STEP -sN SAMPLENAME
   :nodefault:
