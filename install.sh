#!/bin/bash

# sourceCommand="source /root/.bashrc && mamba activate cern"
sourceCommand="source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/setup.sh"

eval "$sourceCommand"
python -m venv --system-site-packages myenv
source myenv/bin/activate

python -m pip install -e .[docs,dev]

python -m pip install --no-binary=correctionlib correctionlib

cat << EOF > start.sh
#!/bin/bash
$sourceCommand
source `pwd`/myenv/bin/activate
EOF

chmod +x start.sh


git clone https://gitlab.cern.ch/cms-nanoAOD/jsonpog-integration.git
mv jsonpog-integration mkShapesRDF/processor/data/
