import pytest
import subprocess
from mkShapesRDF.lib.utils import getFrameworkPath
import sys

fwPath = getFrameworkPath()


def test_Full2018v9():
    r"""Test the execution of ``mkPostporc`` for

    - Production: ``Summer20UL18_106x_nAODv9_Full2018v9``
    - Step: ``MCFull2018v9``
    - Sample: ``EWKZ2Jets_ZToLL_M-50_MJJ-120``

    on 100 events.
    """
    prod = "Summer20UL18_106x_nAODv9_Full2018v9"
    step = "MCFull2018v9"
    sample = "EWKZ2Jets_ZToLL_M-50_MJJ-120"

    condorPath = f"{fwPath}/mkShapesRDF/processor/condor/{prod}/{step}/{sample}__part0/"

    postProcCommand = (
        f"mkPostProc -o 0 -p {prod} -s {step} -sN {sample} --limitFiles 1 --dryRun 1"
    )

    proc = subprocess.Popen(
        rf"cd {fwPath} \
        && source start.sh; \
        {postProcCommand} \
        && cd {condorPath} \
        && mkdir -p test \
        && cd test \
        && cp ../script.py . \
        && sed -i -E 's|(readRDF\(.*\))|\1\ndf.df = df.df.Range(100)|g' script.py \
        && sed -i -E 's|(^.*EnableImplicit.*)|# \1|g' script.py \
        && head -n -2 ../../run.sh > run.sh \
        && chmod +x run.sh \
        && ./run.sh",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        executable="/bin/bash",
    )
    out, err = proc.communicate()
    print(out.decode("utf-8"), file=sys.stderr)
    print(err.decode("utf-8"), file=sys.stderr)
    assert proc.returncode == 0
