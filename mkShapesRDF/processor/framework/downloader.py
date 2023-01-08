import subprocess
import sys
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile",
                    help="Path to input file", required=True)
parser.add_argument("-o", "--outputFile",
                    help="Path to output file", required=True)
parser.add_argument(
    "-v", "--verbose", help="0 (default) don't print, 1 print", required=False, default='0')

args = parser.parse_args()

inputFile = args.inputFile
outputFile = args.outputFile
verbose = int(args.verbose)

with open(inputFile) as file:
    dataset = json.load(file)

if os.path.exists(outputFile):
    # load the already built dataset and update the input one if queries are the same
    with open(outputFile) as file:
        dataset2 = json.load(file)

    for year in dataset.keys():
        for sample in dataset[year]['samples'].keys():
            yearString = dataset[year]['samples'][sample].get('queryYear', dataset[year]['string'])
            sampleString = dataset[year]['samples'][sample]['query']

            yearString2 = dataset2[year]['samples'][sample].get('queryYear', dataset2[year]['string'])
            sampleString2 = dataset2[year]['samples'][sample]['query']

            query = f'/{sampleString}/{yearString}/'
            query2 = f'/{sampleString2}/{yearString2}/'
            if len(dataset[year]['samples'][sample].get('files', [])) != 0 and \
                query == query2:
                dataset[year]['samples'][sample]['files'] = dataset2[year]['samples'][sample]['files']



"""
dataset = {
        '2018':
            {
                'string' : '*20UL18NanoAODv9*',
                'samples': {
                    'zjj': {
                        'query': 'EWK_LLJJ*dipole*'
                        }
                    }
                }
            }
"""

def exit():
    print('Now exiting')
    if verbose == 1:
        print(json.dumps(dataset, indent=4))

    with open(outputFile, 'w') as file:
        json.dump(dataset, file, indent=4)
    sys.exit()

for year in dataset.keys():
    for sample in dataset[year]['samples'].keys():
        yearString = dataset[year]['samples'][sample].get('queryYear', dataset[year]['string'])
        sampleString = dataset[year]['samples'][sample]['query']
        if len(dataset[year]['samples'][sample].get('files', [])) != 0:
            continue
        print(f'Searching {sample} for year {year} with dataset=/{sampleString}/{yearString}/NANOAODSIM')
        procString = f'dasgoclient --query="dataset=/{sampleString}/{yearString}/NANOAODSIM"'
        proc = subprocess.Popen(procString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        err = err.decode('utf-8')
        if len(err) != 0:
            print('There were some errors:')
            print(err)
            exit()
        out = out.decode('utf-8')
        out = out.split('\n')
        out = list(filter(lambda k: k.strip() != '', out))
        if len(out) == 1:
            # search files for the sample
            process = out[0]
            print(f'Searching files for {sample} for year {year} with "file dataset={process}"')
            procString = f'dasgoclient --query="file dataset={process}"'
            proc = subprocess.Popen(procString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out1, err1 = proc.communicate()
            out1 = out1.decode('utf-8')
            out1 = out1.split('\n')
            out1 = list(filter(lambda k: k.strip() != '', out1))
            print(out1, len(out1))
            err1 = err1.decode('utf-8')
            if len(err1) != 0:
                print('There were some errors:')
                print(err1)
                exit()
            dataset[year]['samples'][sample]['files'] = out1

            

        else:
            print(f'Sample {sample} does not uniquely define a sample, please choose from the followings and update the query')
            print('\n'.join(out))
            exit()

exit()
