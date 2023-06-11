#!/bin/bash


sourceCommand="source /home/gpizzati/.bashrc; mamba activate latest-mkShapesRDF"

cp install.sh install2.sh
sed -i -E "s|(^sourceCommand=).+$|\1\"${sourceCommand}\"|g" install2.sh

./install2.sh

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


if [[ $pipStatus -eq 0 ]] && [[ $pipStatus2 -eq 0 ]] && [[ $flakeStatus2 -eq 0 ]] && [[ $blackStatus2 -eq 0 ]] && [[ $pytestStatus == 0 ]];
then
    exit 0
else
    exit 1
fi
