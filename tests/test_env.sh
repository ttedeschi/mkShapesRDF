#!/bin/bash


source /home/gpizzati/.bashrc

mamba env create --quiet -n latest-mkShapesRDF --file environment.yml

mamba activate latest-mkShapesRDF

python -m venv --system-site-packages myenv
source myenv/bin/activate


cat << EOF > start.sh
#!/bin/bash
source /home/gpizzati/.bashrc
pushd /cvmfs/cms.cern.ch/ > /dev/null; source cmsset_default.sh; popd > /dev/null
mamba activate latest-mkShapesRDF
source `pwd`/myenv/bin/activate
EOF

chmod +x start.sh

source start.sh


python -m pip install -e .[dev]
pipStatus=$?
echo "pip install mkShapesRDF and deps status"
echo $pipStatus

python -m pip install --no-binary=correctionlib correctionlib
pipStatus2=$?
echo "pip install correctionlib status"
echo $pipStatus2

python -m flake8 . 
flakeStatus=$?
echo "flake status"
echo $flakeStatus

python -m black . 
blackStatus=$?
echo "black status"
echo $blackStatus

python -m pytest -n auto
pytestStatus=$?

echo "pytest status"
echo $pytestStatus

deactivate

mamba deactivate

mamba env remove -n latest-mkShapesRDF
rm -r /mnt/c/gpizzati/mambaforge/envs/latest-mkShapesRDF

if [[ $pipStatus -eq 0 ]] && [[ $pipStatus2 -eq 0 ]] && [[ $flakeStatus2 -eq 0 ]] && [[ $blackStatus2 -eq 0 ]] && [[ $pytestStatus == 0 ]];
then
    exit 0
else
    exit 1
fi
