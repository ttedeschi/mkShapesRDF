#!/bin/bash

# source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/setup.sh
sourceCommand="source /root/.bashrc && mamba activate cern"

bash -c "$sourceCommand"
python -m venv --system-site-packages myenv
source myenv/bin/activate

python -m pip install -e .

python -m pip install --no-binary=correctionlib correctionlib
cat << EOF > start.sh
$sourceCommand
source `pwd`/myenv/bin/activate
EOF

chmod +x start.sh
