import subprocess
from pathlib import Path
import os
import shutil


class BatchSubmission:
    @staticmethod
    def resubmitJobs(batchFolder, tag, samples, dryRun):
        """
        Resubmit failed jobs and rename the old error file to err-1.txt
        Args:
            batchFolder (string): path to the batch folder
            tag (string): string used to tag the configuration
            samples (list of strings): samples to be resubmitted in the form of ['DY_0', ...]
        """
        
        #Path(f'{self.batchFolder}/{self.tag}/{sampleName}_{str(i)}').mkdir(parents=True, exist_ok=False)
        for sample in samples:
            if os.path.exists(f'{batchFolder}/{tag}/{sample}/err.txt'):
                os.rename(f'{batchFolder}/{tag}/{sample}/err.txt', f'{batchFolder}/{tag}/{sample}/err-1.txt')
        with open(f'{batchFolder}/{tag}/submit.jdl') as file:
            txt = file.read()
        lines = txt.split('\n')
        line = list(filter(lambda k: k.startswith('queue'), lines))[0]
        lines[lines.index(line)] = f'queue 1 Folder in {", ".join(samples)}\n '
        with open(f'{batchFolder}/{tag}/submit.jdl', 'w') as file:
            file.write('\n'.join(lines))

        if dryRun != 1:
            process = subprocess.Popen(
                f'cd {batchFolder}/{tag}; condor_submit submit.jdl; cd -', shell=True)
            process.wait()
        
        
    def __init__(self, outputPath, batchFolder, headersPath, runnerPath, tag, samples, d, batchVars):
        self.outputPath  = outputPath
        self.batchFolder = batchFolder
        self.headersPath = headersPath
        self.runnerPath  = runnerPath
        self.tag         = tag

        self.samples     = samples
        self.d           = d
        self.batchVars   = batchVars

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
        try:
            Path(f'{self.batchFolder}/{self.tag}/{sampleName}_{str(i)}').mkdir(parents=True, exist_ok=False)
        except:
            print('Removing dir:', os.path.abspath(f'{self.batchFolder}/{self.tag}'))
            shutil.rmtree(os.path.abspath(f'{self.batchFolder}/{self.tag}'))
            Path(f'{self.batchFolder}/{self.tag}/{sampleName}_{str(i)}').mkdir(parents=True, exist_ok=False)
        self.folders.append(f'{sampleName}_{str(i)}')
        # python file

        txtpy = 'from collections import OrderedDict\n'

        _samples = [sample]

        txtpy += f'samples = {str(_samples)}\n'

        for var in self.batchVars:
            _var = var
            if type(var) != type(''):
                _var = var[0]


            print('\n\nvar', _var)
            if _var == 'samples':
                continue
            if type(self.d[_var]) == type(0) or type(self.d[_var])  == type(0.0):
                txtpy += f'{_var} = {self.d[_var]}\n'
            else:
                txtpy += f'{_var} = {str(self.d[_var])}\n'

        with open(f'{self.batchFolder}/{self.tag}/{sampleName}_{str(i)}/script.py', 'w') as f:
            f.write(txtpy)

    def createBatches(self):
        for sample in self.samples:
            self.createBatch(sample)

    def submit(self, dryRun=0):

        txtsh = '#!/bin/bash\n'
        txtsh += 'source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh\n'

        if self.d.get('mountEOS', False):
            txtsh += 'export KRB5CCNAME=/gwpool/users/gpizzati/krb5cc_`id -u gpizzati`\n'
            txtsh += 'eosfusebind -g\n'

        txtsh += 'time python runner.py\n'
        with open(f'{self.batchFolder}/{self.tag}/run.sh', 'w') as file:
            file.write(txtsh)
        process = subprocess.Popen(
            f'chmod +x {self.batchFolder}/{self.tag}/run.sh', shell=True)
        process.wait()

        txtjdl = 'universe = vanilla \n'
        txtjdl += 'executable = run.sh\n'

        txtjdl += f'transfer_input_files = $(Folder)/script.py, {self.headersPath}, {self.runnerPath}\n'

        txtjdl += 'output = $(Folder)/out.txt\n'
        txtjdl += 'error  = $(Folder)/err.txt\n'
        txtjdl += 'log    = $(Folder)/log.txt\n'
        txtjdl += 'should_transfer_files = yes\n'

        outputFileTrunc = '.'.join(self.d['outputFile'].split('.')[:-1])
        txtjdl += f'transfer_output_remaps = "output.root = {self.outputPath}/{outputFileTrunc}__ALL__$(Folder).root"\n'
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


