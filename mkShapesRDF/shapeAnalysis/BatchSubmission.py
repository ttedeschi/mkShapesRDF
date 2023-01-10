import subprocess
from pathlib import Path
import os
print(os.getcwd())


class BatchSumbission:
    def __init__(self, batchFolder, tag, samples, aliases, variables, preselections, cuts, nuisances, lumi):
        self.batchFolder = batchFolder
        self.tag = tag

        self.samples = samples
        self.aliases = aliases
        self.variables = variables
        self.preselections = preselections
        self.cuts = mergedCuts
        self.nuisances = nuisances
        self.lumi = lumi
        self.folders = []


    def createBatch(self, sample):
        # 1. create submission folder
        # 2. create executable python file
        # 3. create bash file
        # 4. create condor file
        # 5. append condor file to submit files

        # submission folder
        sampleName = sample[0]
        i = sample[3]
        Path(f'{self.batchFolder}/{self.tag}/{sampleName}_{str(i)}').mkdir(parents=True, exist_ok=True)
        self.folders.append(f'{sampleName}_{str(i)}')
        # python file

        txtpy = 'from collections import OrderedDict\n'
        # since at the 4th position there is the i, which is not needed by the runner
        #_sample = sample[:3] + sample[4:]
        _samples = [sample]
        """
        _samples = {}
        _samples[sampleName] = {
                'name': [(sampleName, filesType[1])],
                'weight': filesType[0],
                }
        if 'subsamples' in list(samples[sampleName].keys()):
            _samples[sampleName]['subsamples'] = samples[sampleName]['subsamples']
        if 'isData' in list(samples[sampleName].keys()):
            _samples[sampleName]['isData'] = samples[sampleName]['isData']
        """

        txtpy += f'samples = {str(_samples)}\n'
        txtpy += f'aliases = {str(self.aliases)}\n'
        txtpy += f'variables = {str(self.variables)}\n'
        txtpy += f'cuts = {str(self.cuts)}\n'
        txtpy += f'nuisances = {str(self.nuisances)}\n'
        txtpy += f'preselections = \'{self.preselections}\' \n'
        txtpy += f'lumi = {self.lumi} \n'
        with open(f'{self.batchFolder}/{self.tag}/{sampleName}_{str(i)}/script.py', 'w') as f:
            f.write(txtpy)

    def createBatches(self):
        for sample in self.samples:
            self.createBatch(sample)

    def submit(self, dryRun=0):

        txtsh = '#!/bin/bash\n'
        txtsh += 'source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh\n'
        txtsh += 'time python runner.py\n'
        with open(f'{self.batchFolder}/{self.tag}/run.sh', 'w') as file:
            file.write(txtsh)
        process = subprocess.Popen(
            f'chmod +x {self.batchFolder}/{self.tag}/run.sh', shell=True)
        process.wait()

        txtjdl = 'universe = vanilla \n'
        txtjdl += 'executable = run.sh\n'
        #txtjdl += 'arguments = $(Folder)\n'
        # FIXME what's the path to runner and headers?
        txtjdl += f'transfer_input_files = $(Folder)/script.py, {os.getcwd()}/headers.hh, {os.getcwd()}/runner.py\n'

        txtjdl += 'output = $(Folder)/out.txt\n'
        txtjdl += 'error  = $(Folder)/err.txt\n'
        txtjdl += 'log    = $(Folder)/log.txt\n'
        #txtjdl += 'transfer_input_files = $(File)\n'
        txtjdl += 'should_transfer_files = yes\n'
        txtjdl += f'transfer_output_remaps = "output.root = {os.getcwd()}/{folder}/{outputFolder}/mkShapes__{tag}__ALL__$(Folder).root"\n'
        txtjdl += 'when_to_transfer_output = ON_EXIT\n'
        txtjdl += 'request_cpus   = 1\n'
        txtjdl += '+JobFlavour = "workday"\n'

        txtjdl += f'queue 1 Folder in {", ".join(self.folders)}\n'
        with open(f'{self.batchFolder}/{self.tag}/submit.jdl', 'w') as file:
            file.write(txtjdl)
        if dryRun != 1:
            process = subprocess.Popen(
                f'cd {self.batchFolder}/{self.tag}; condor_submit submit.jdl; cd -', shell=True)
            process.wait()

