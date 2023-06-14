
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


Operation mode 0 arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. argparse::
   :module: mkShapesRDF.processor.scripts.mkPostProc
   :func: operationMode0Parser
   :prog: mkPostProc -o 0 -p PROD -s STEP -sN SAMPLENAME

Operation mode 1 arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. argparse::
   :module: mkShapesRDF.processor.scripts.mkPostProc
   :func: operationMode1Parser
   :prog: mkPostProc -o 1 -p PROD -s STEP -sN SAMPLENAME

Example usage:

.. code:: bash

   mkPostProc -o 0 -p Summer20UL18_106x_nAODv9_Full2018v9 -s MCFull2018v9 -T EWKZ2Jets_ZToLL_M-50_MJJ-120 \
   --limitFiles 1 --dryRun 1
